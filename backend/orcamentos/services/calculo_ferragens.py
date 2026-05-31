from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from orcamentos.models import ItemCustoOrcamento, Material, Orcamento


def calcular_dobradicas_por_altura(altura_mm: int) -> int:
    if altura_mm <= 900:
        return 2
    if altura_mm <= 1600:
        return 3
    if altura_mm <= 2200:
        return 4
    return 5


def _material_por_nome(materiais: List[Material], termo: str) -> Material | None:
    termo_low = termo.lower()
    for material in materiais:
        if termo_low in material.nome.lower():
            return material
    return None


def _criar_item(
    orcamento: Orcamento,
    nome: str,
    quantidade: Decimal,
    unidade: str,
    material: Material | None,
    categoria: str = ItemCustoOrcamento.Categoria.FERRAGEM,
) -> None:
    if quantidade <= 0:
        return
    preco = material.preco_unitario if material else Decimal("0")
    fornecedor = material.fornecedor if material else ""
    nome_final = material.nome if material else nome

    ItemCustoOrcamento.objects.create(
        orcamento=orcamento,
        categoria=categoria,
        nome=nome_final,
        quantidade=quantidade,
        unidade=unidade,
        preco_unitario=preco,
        preco_total=(quantidade * preco).quantize(Decimal("0.01")),
        fornecedor=fornecedor,
    )


def gerar_custos_ferragens(orcamento: Orcamento, materiais_ativos: List[Material]) -> Dict:
    resultado: Dict[str, Decimal] = {}

    qtd_gavetas = Decimal(orcamento.quantidade_gavetas)
    qtd_portas = Decimal(orcamento.quantidade_portas)
    qtd_cabideiros = Decimal(orcamento.quantidade_cabideiros)

    corredica = _material_por_nome(materiais_ativos, "corredi")
    dobradica = _material_por_nome(materiais_ativos, "dobradi")
    kit_correr = _material_por_nome(materiais_ativos, "kit porta de correr")
    roldana = _material_por_nome(materiais_ativos, "roldana")
    cabideiro = _material_por_nome(materiais_ativos, "cabideiro")
    suporte_cabideiro = _material_por_nome(materiais_ativos, "suporte de cabideiro")
    puxador = _material_por_nome(materiais_ativos, "puxador")

    if qtd_gavetas > 0:
        _criar_item(orcamento, "Par de corrediça", qtd_gavetas, "par", corredica)
        _criar_item(orcamento, "Puxador de gaveta", qtd_gavetas, "unidade", puxador)
        resultado["gavetas"] = qtd_gavetas

    if orcamento.tipo_porta == Orcamento.TipoPorta.ABRIR and qtd_portas > 0:
        dobradicas_por_porta = calcular_dobradicas_por_altura(orcamento.altura_mm)
        total_dobradicas = Decimal(int(qtd_portas) * dobradicas_por_porta)
        _criar_item(orcamento, "Dobradiça", total_dobradicas, "unidade", dobradica)
        _criar_item(orcamento, "Puxador de porta", qtd_portas, "unidade", puxador)
        resultado["dobradicas"] = total_dobradicas

    if orcamento.tipo_porta == Orcamento.TipoPorta.CORRER and qtd_portas > 0:
        _criar_item(orcamento, "Kit porta de correr", Decimal("1"), "unidade", kit_correr)
        _criar_item(orcamento, "Roldana/guia", qtd_portas, "conjunto", roldana)
        _criar_item(orcamento, "Perfil puxador", qtd_portas, "unidade", puxador)
        resultado["kits_correr"] = Decimal("1")

    if qtd_cabideiros > 0:
        _criar_item(orcamento, "Cabideiro", qtd_cabideiros, "unidade", cabideiro)
        _criar_item(orcamento, "Suporte de cabideiro", qtd_cabideiros * Decimal("2"), "unidade", suporte_cabideiro)
        resultado["cabideiros"] = qtd_cabideiros

    return resultado
