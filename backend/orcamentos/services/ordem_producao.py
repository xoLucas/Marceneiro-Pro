from __future__ import annotations

from typing import Dict, List

from orcamentos.models import PecaOrcamento


def gerar_ordem_producao(pecas: List[PecaOrcamento]) -> Dict:
    lista_pecas = []
    for p in pecas:
        lista_pecas.append(
            {
                "nome": p.nome,
                "material": p.material.nome,
                "medidas_mm": f"{p.largura_mm} x {p.altura_mm}",
                "quantidade": p.quantidade,
                "fita": {
                    "topo": p.fita_topo,
                    "baixo": p.fita_baixo,
                    "esquerda": p.fita_esquerda,
                    "direita": p.fita_direita,
                },
            }
        )

    passos = [
        "Cortar pecas estruturais",
        "Cortar portas",
        "Cortar gavetas",
        "Aplicar fita de borda",
        "Fazer furacoes",
        "Montar caixaria",
        "Montar gavetas",
        "Instalar portas",
        "Conferencia final",
        "Separacao para entrega",
    ]

    return {"pecas": lista_pecas, "ordem_sugerida": passos}
