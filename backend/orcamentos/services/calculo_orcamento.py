from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List

from django.db import transaction
from django.utils import timezone

from orcamentos.models import (
    ItemCustoOrcamento,
    Material,
    Orcamento,
    PagamentoSugerido,
    PecaOrcamento,
    PlanoCorte,
    Retalho,
)
from orcamentos.services.alertas import gerar_alertas_risco
from orcamentos.services.calculo_ferragens import gerar_custos_ferragens
from orcamentos.services.calculo_fita import gerar_item_custo_fita
from orcamentos.services.financeiro import calcular_resumo_financeiro
from orcamentos.services.gerador_pecas import gerar_pecas_automaticas
from orcamentos.services.lista_compra import gerar_lista_compra
from orcamentos.services.ordem_producao import gerar_ordem_producao
from orcamentos.services.otimizador_corte import PecaExpandida, otimizar_plano_corte
from orcamentos.services.retalhos import planejar_uso_retalhos


def _material_por_nome(materiais: List[Material], termo: str) -> Material | None:
    termo_low = termo.lower()
    for material in materiais:
        if termo_low in material.nome.lower():
            return material
    return None


def _criar_item_direto(
    orcamento: Orcamento,
    categoria: str,
    nome: str,
    quantidade: Decimal,
    unidade: str,
    preco_unitario: Decimal,
    fornecedor: str = "",
) -> None:
    if quantidade <= 0:
        return
    ItemCustoOrcamento.objects.create(
        orcamento=orcamento,
        categoria=categoria,
        nome=nome,
        quantidade=quantidade,
        unidade=unidade,
        preco_unitario=preco_unitario,
        preco_total=(quantidade * preco_unitario).quantize(Decimal("0.01")),
        fornecedor=fornecedor,
    )


def _gerar_pecas_salvar(orcamento: Orcamento) -> List[PecaOrcamento]:
    PecaOrcamento.objects.filter(orcamento=orcamento).delete()
    pecas_json = gerar_pecas_automaticas(orcamento)
    pecas_criadas = []
    for p in pecas_json:
        peca = PecaOrcamento.objects.create(
            orcamento=orcamento,
            nome=p["nome"],
            material_id=p["material_id"],
            largura_mm=p["largura_mm"],
            altura_mm=p["altura_mm"],
            quantidade=p["quantidade"],
            espessura_mm=p["espessura_mm"],
            pode_rotacionar=p["pode_rotacionar"],
            fita_topo=p.get("fita_frontal", False),
            fita_baixo=False,
            fita_esquerda=False,
            fita_direita=False,
            observacoes=p.get("observacoes", ""),
        )
        pecas_criadas.append(peca)
    return pecas_criadas


def _gerar_planos_corte(
    orcamento: Orcamento,
    pecas: List[PecaOrcamento],
    consumo_retalho_por_peca_id: Dict[int, int] | None = None,
) -> Dict:
    PlanoCorte.objects.filter(orcamento=orcamento).delete()
    consumo_retalho_por_peca_id = consumo_retalho_por_peca_id or {}

    grupos = defaultdict(list)
    for peca in pecas:
        grupos[peca.material_id].append(peca)

    planos_saida = []
    existe_peca_maior_chapa = False
    pecas_maiores_chapa: List[Dict] = []

    for material_id, grupo_pecas in grupos.items():
        material = grupo_pecas[0].material
        if material.largura_mm <= 0 or material.altura_mm <= 0:
            continue

        expandidas = []
        idx = 1
        for peca in grupo_pecas:
            consumo = consumo_retalho_por_peca_id.get(peca.id, 0)
            quantidade_restante = max(0, peca.quantidade - consumo)
            for _ in range(quantidade_restante):
                expandidas.append(
                    PecaExpandida(
                        id=idx,
                        nome=peca.nome,
                        largura_mm=peca.largura_mm,
                        altura_mm=peca.altura_mm,
                        pode_rotacionar=peca.pode_rotacionar,
                    )
                )
                idx += 1

        resultado = otimizar_plano_corte(
            pecas=expandidas,
            chapa_largura_mm=material.largura_mm,
            chapa_altura_mm=material.altura_mm,
            kerf_mm=float(orcamento.kerf_mm),
        )

        if resultado.get("pecas_maiores_que_chapa"):
            existe_peca_maior_chapa = True
        pecas_maiores_chapa.extend(resultado.get("pecas_maiores_que_chapa", []))

        plano = PlanoCorte.objects.create(
            orcamento=orcamento,
            material_id=material_id,
            quantidade_chapas=resultado.get("quantidade_chapas", 0),
            aproveitamento_percentual=Decimal(str(resultado.get("aproveitamento_percentual", 0))).quantize(Decimal("0.01")),
            perda_percentual=Decimal(str(resultado.get("perda_percentual", 100))).quantize(Decimal("0.01")),
            area_total_pecas=Decimal(str(resultado.get("area_total_pecas", 0))).quantize(Decimal("0.01")),
            area_total_chapas=Decimal(str(resultado.get("area_total_chapas", 0))).quantize(Decimal("0.01")),
            resultado_json=resultado,
        )

        planos_saida.append(
            {
                "id": plano.id,
                "material_id": material.id,
                "material_nome": material.nome,
                "quantidade_chapas": resultado.get("quantidade_chapas", 0),
                "aproveitamento_percentual": resultado.get("aproveitamento_percentual", 0),
                "perda_percentual": resultado.get("perda_percentual", 0),
                "area_total_pecas": resultado.get("area_total_pecas", 0),
                "area_total_chapas": resultado.get("area_total_chapas", 0),
                "chapas": resultado.get("chapas", []),
                "erro": resultado.get("erro"),
                "pecas_maiores_que_chapa": resultado.get("pecas_maiores_que_chapa", []),
            }
        )

    return {
        "planos": planos_saida,
        "existe_peca_maior_chapa": existe_peca_maior_chapa,
        "pecas_maiores_chapa": pecas_maiores_chapa,
        "aproveitamento_medio": (
            sum(float(p["aproveitamento_percentual"]) for p in planos_saida) / len(planos_saida) if planos_saida else 0
        ),
    }


@transaction.atomic
def calcular_orcamento_completo(orcamento: Orcamento) -> Dict:
    ItemCustoOrcamento.objects.filter(orcamento=orcamento).delete()
    PagamentoSugerido.objects.filter(orcamento=orcamento).delete()

    materiais_ativos = list(Material.objects.filter(ativo=True))
    pecas = _gerar_pecas_salvar(orcamento)

    retalhos_sugestao = {"retalhos_usados": [], "economia_estimada": 0.0, "chapas_economizadas_aprox": 0.0}
    retalhos_poderiam_ajudar = False
    consumo_por_peca_id: Dict[int, int] = {}
    if orcamento.usar_retalhos:
        retalhos = list(Retalho.objects.filter(disponivel=True).select_related("material"))
        if retalhos:
            materiais_chapa_info: Dict[int, Dict[str, Decimal | int]] = {}
            for mat in materiais_ativos:
                materiais_chapa_info[mat.id] = {
                    "preco_chapa": mat.preco_unitario,
                    "area_chapa_mm2": int(mat.largura_mm * mat.altura_mm),
                }
            retalhos_sugestao = planejar_uso_retalhos(
                pecas=pecas,
                retalhos=retalhos,
                kerf_mm=orcamento.kerf_mm,
                materiais_chapa_info=materiais_chapa_info,
            )
            consumo_por_peca_id = {int(k): int(v) for k, v in retalhos_sugestao.get("consumo_por_peca_id", {}).items()}
            retalhos_poderiam_ajudar = retalhos_sugestao["quantidade_pecas_atendidas"] > 0

    planos_data = _gerar_planos_corte(orcamento, pecas, consumo_retalho_por_peca_id=consumo_por_peca_id)

    for plano in planos_data["planos"]:
        material = Material.objects.get(id=plano["material_id"])
        qtd_chapas = Decimal(str(plano["quantidade_chapas"]))
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.CHAPA,
            nome=material.nome,
            quantidade=qtd_chapas,
            unidade="chapa",
            preco_unitario=material.preco_unitario,
            fornecedor=material.fornecedor,
        )

    fita_material = _material_por_nome(materiais_ativos, "fita de borda")
    gerar_item_custo_fita(orcamento, fita_material)
    gerar_custos_ferragens(orcamento, materiais_ativos)

    insumo_geral = _material_por_nome(materiais_ativos, "insumos gerais")
    if insumo_geral:
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.INSUMO,
            nome=insumo_geral.nome,
            quantidade=Decimal("1"),
            unidade=insumo_geral.unidade,
            preco_unitario=insumo_geral.preco_unitario,
            fornecedor=insumo_geral.fornecedor,
        )

    valor_mao_obra_total = (
        Decimal(orcamento.valor_mao_obra)
        if orcamento.valor_mao_obra > 0
        else Decimal(orcamento.quantidade_diarias) * Decimal(orcamento.valor_diaria)
    )
    if valor_mao_obra_total > 0:
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.MAO_OBRA,
            nome="Mao de obra",
            quantidade=Decimal("1"),
            unidade="servico",
            preco_unitario=valor_mao_obra_total,
        )

    if orcamento.valor_instalacao > 0:
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.INSTALACAO,
            nome="Instalacao",
            quantidade=Decimal("1"),
            unidade="servico",
            preco_unitario=Decimal(orcamento.valor_instalacao),
        )

    if orcamento.valor_frete > 0:
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.FRETE,
            nome="Frete",
            quantidade=Decimal("1"),
            unidade="servico",
            preco_unitario=Decimal(orcamento.valor_frete),
        )

    if orcamento.custos_extras > 0:
        _criar_item_direto(
            orcamento=orcamento,
            categoria=ItemCustoOrcamento.Categoria.EXTRA,
            nome="Custos extras",
            quantidade=Decimal("1"),
            unidade="servico",
            preco_unitario=Decimal(orcamento.custos_extras),
        )

    itens = list(ItemCustoOrcamento.objects.filter(orcamento=orcamento))
    custo_total = sum((item.preco_total for item in itens), Decimal("0.00"))
    financeiro = calcular_resumo_financeiro(orcamento, custo_total)

    alertas = gerar_alertas_risco(
        orcamento=orcamento,
        materiais=[m for m in materiais_ativos if m.id in {p.material_id for p in pecas}],
        aproveitamento_percentual=planos_data["aproveitamento_medio"],
        margem_real_percentual=financeiro["margem_real_percentual"],
        existe_peca_maior_chapa=planos_data["existe_peca_maior_chapa"],
        pecas_maiores_chapa=planos_data["pecas_maiores_chapa"],
        retalhos_poderiam_ajudar=retalhos_poderiam_ajudar,
    )

    for i, sugestao in enumerate(financeiro["sugestao_pagamento"], start=1):
        PagamentoSugerido.objects.create(
            orcamento=orcamento,
            descricao=sugestao["descricao"],
            valor=Decimal(str(sugestao["valor"])),
            status=PagamentoSugerido.Status.PREVISTO,
        )

    lista_compra = gerar_lista_compra(itens)
    ordem_producao = gerar_ordem_producao(pecas)

    resultado = {
        "pecas": [
            {
                "id": p.id,
                "nome": p.nome,
                "material_id": p.material_id,
                "material_nome": p.material.nome,
                "largura_mm": p.largura_mm,
                "altura_mm": p.altura_mm,
                "quantidade": p.quantidade,
                "fita_topo": p.fita_topo,
                "fita_baixo": p.fita_baixo,
                "fita_esquerda": p.fita_esquerda,
                "fita_direita": p.fita_direita,
            }
            for p in pecas
        ],
        "plano_corte": {
            "planos": planos_data["planos"],
            "aproveitamento_percentual": planos_data["aproveitamento_medio"],
            "pecas_maiores_chapa": planos_data["pecas_maiores_chapa"],
            "retalhos_usados": retalhos_sugestao.get("retalhos_usados", []),
        },
        "retalhos": retalhos_sugestao,
        "financeiro": financeiro,
        "alertas": alertas,
        "lista_compra": lista_compra,
        "ordem_producao": ordem_producao,
        "itens_custo": [
            {
                "id": i.id,
                "categoria": i.categoria,
                "nome": i.nome,
                "quantidade": float(i.quantidade),
                "unidade": i.unidade,
                "preco_unitario": float(i.preco_unitario),
                "preco_total": float(i.preco_total),
                "fornecedor": i.fornecedor,
            }
            for i in itens
        ],
        "pagamentos": [{"descricao": p["descricao"], "valor": p["valor"]} for p in financeiro["sugestao_pagamento"]],
    }

    orcamento.resultado_calculo = resultado
    orcamento.status = Orcamento.Status.CALCULADO
    orcamento.nota_confianca = alertas["nota_confianca"]
    orcamento.data_ultima_calculacao = timezone.now()
    orcamento.save(update_fields=["resultado_calculo", "status", "nota_confianca", "data_ultima_calculacao"])

    return resultado
