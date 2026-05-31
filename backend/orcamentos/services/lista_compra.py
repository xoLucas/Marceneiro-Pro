from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from orcamentos.models import ItemCustoOrcamento


def gerar_lista_compra(itens: List[ItemCustoOrcamento]) -> List[Dict]:
    agrupado: Dict[str, Dict] = {}
    for item in itens:
        chave = f"{item.nome}|{item.unidade}|{item.preco_unitario}|{item.fornecedor}"
        if chave not in agrupado:
            agrupado[chave] = {
                "nome": item.nome,
                "quantidade": Decimal("0"),
                "unidade": item.unidade,
                "preco_unitario": item.preco_unitario,
                "total": Decimal("0"),
                "fornecedor": item.fornecedor,
            }
        agrupado[chave]["quantidade"] += item.quantidade
        agrupado[chave]["total"] += item.preco_total

    saida = []
    for _, dados in agrupado.items():
        saida.append(
            {
                "nome": dados["nome"],
                "quantidade": float(dados["quantidade"].quantize(Decimal("0.001"))),
                "unidade": dados["unidade"],
                "preco_unitario": float(dados["preco_unitario"]),
                "total": float(dados["total"].quantize(Decimal("0.01"))),
                "fornecedor": dados["fornecedor"],
            }
        )
    return sorted(saida, key=lambda x: x["nome"])
