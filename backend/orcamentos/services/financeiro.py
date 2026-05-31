from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from orcamentos.models import Orcamento


def arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_preco_sugerido(custo_total: Decimal, margem_desejada_percentual: Decimal) -> Decimal:
    margem = margem_desejada_percentual / Decimal("100")
    if margem >= Decimal("1"):
        return Decimal("0.00")
    if margem <= Decimal("0"):
        return arredondar(custo_total)
    return arredondar(custo_total / (Decimal("1") - margem))


def calcular_lucro_margem_por_preco(custo_total: Decimal, preco_final: Decimal) -> Dict[str, Decimal]:
    if preco_final <= 0:
        return {"lucro": Decimal("0.00"), "margem_real": Decimal("0.00")}
    lucro = preco_final - custo_total
    margem = lucro / preco_final
    return {"lucro": arredondar(lucro), "margem_real": arredondar(margem * Decimal("100"))}


def calcular_resumo_financeiro(orcamento: Orcamento, custo_total: Decimal) -> Dict:
    preco_sugerido = calcular_preco_sugerido(custo_total, orcamento.margem_desejada_percentual)
    preco_final = orcamento.preco_final_manual if orcamento.preco_final_manual is not None else preco_sugerido
    lucro_margem = calcular_lucro_margem_por_preco(custo_total, preco_final)

    margem_minima_segura = Decimal("25")
    preco_minimo_seguro = calcular_preco_sugerido(custo_total, margem_minima_segura)
    entrada = arredondar(preco_final * Decimal("0.5"))
    restante = arredondar(preco_final - entrada)

    return {
        "custo_total": float(arredondar(custo_total)),
        "preco_sugerido": float(preco_sugerido),
        "preco_final": float(arredondar(preco_final)),
        "lucro_estimado": float(lucro_margem["lucro"]),
        "margem_real_percentual": float(lucro_margem["margem_real"]),
        "preco_minimo_seguro": float(preco_minimo_seguro),
        "sugestao_pagamento": [
            {"descricao": "Entrada (50%)", "valor": float(entrada)},
            {"descricao": "Restante na entrega", "valor": float(restante)},
        ],
    }
