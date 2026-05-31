from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from orcamentos.models import ItemCustoOrcamento, Material, Orcamento, PecaOrcamento


def calcular_total_fita_metros(pecas: Iterable[PecaOrcamento], perda_percentual: Decimal) -> Decimal:
    total_mm = Decimal("0")
    for peca in pecas:
        lados_mm = Decimal("0")
        if peca.fita_topo:
            lados_mm += Decimal(peca.largura_mm)
        if peca.fita_baixo:
            lados_mm += Decimal(peca.largura_mm)
        if peca.fita_esquerda:
            lados_mm += Decimal(peca.altura_mm)
        if peca.fita_direita:
            lados_mm += Decimal(peca.altura_mm)
        total_mm += lados_mm * peca.quantidade

    total_m = total_mm / Decimal("1000")
    fator_perda = Decimal("1") + (Decimal(perda_percentual) / Decimal("100"))
    return (total_m * fator_perda).quantize(Decimal("0.001"))


def gerar_item_custo_fita(orcamento: Orcamento, fita_material: Material | None) -> ItemCustoOrcamento | None:
    pecas = orcamento.pecas.all()
    total_m = calcular_total_fita_metros(pecas, orcamento.perda_tecnica_percentual)
    if total_m <= 0:
        return None

    preco = fita_material.preco_unitario if fita_material else Decimal("0")
    nome = fita_material.nome if fita_material else "Fita de borda (sem material cadastrado)"
    fornecedor = fita_material.fornecedor if fita_material else ""

    return ItemCustoOrcamento.objects.create(
        orcamento=orcamento,
        categoria=ItemCustoOrcamento.Categoria.FITA,
        nome=nome,
        quantidade=total_m,
        unidade="metro",
        preco_unitario=preco,
        preco_total=(total_m * preco).quantize(Decimal("0.01")),
        fornecedor=fornecedor,
    )
