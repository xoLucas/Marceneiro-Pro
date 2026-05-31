from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from collections import defaultdict
from typing import Dict, List, Tuple


@dataclass
class PecaExpandida:
    id: int
    nome: str
    largura_mm: int
    altura_mm: int
    pode_rotacionar: bool

    @property
    def area(self) -> int:
        return self.largura_mm * self.altura_mm


def calcular_aproveitamento(area_total_pecas: float, area_total_chapas: float) -> Tuple[Decimal, Decimal]:
    if area_total_chapas <= 0:
        return Decimal("0.00"), Decimal("100.00")
    aproveitamento = (Decimal(str(area_total_pecas)) / Decimal(str(area_total_chapas))) * Decimal("100")
    aproveitamento = aproveitamento.quantize(Decimal("0.01"))
    perda = (Decimal("100.00") - aproveitamento).quantize(Decimal("0.01"))
    return aproveitamento, perda


def _orientacoes_possiveis(peca: PecaExpandida) -> List[Tuple[int, int]]:
    orientacoes = [(peca.largura_mm, peca.altura_mm)]
    if peca.pode_rotacionar and peca.largura_mm != peca.altura_mm:
        orientacoes.append((peca.altura_mm, peca.largura_mm))
    return orientacoes


def _cabe_em_alguma_orientacao(peca: PecaExpandida, chapa_largura_mm: int, chapa_altura_mm: int) -> bool:
    for largura, altura in _orientacoes_possiveis(peca):
        if largura <= chapa_largura_mm and altura <= chapa_altura_mm:
            return True
    return False


def otimizar_plano_corte(
    pecas: List[PecaExpandida],
    chapa_largura_mm: int,
    chapa_altura_mm: int,
    kerf_mm: float,
) -> Dict:
    kerf = max(0, int(round(kerf_mm)))
    pecas_invalidas = [p for p in pecas if not _cabe_em_alguma_orientacao(p, chapa_largura_mm, chapa_altura_mm)]
    pecas_validas = [p for p in pecas if _cabe_em_alguma_orientacao(p, chapa_largura_mm, chapa_altura_mm)]
    ordenadas = sorted(pecas_validas, key=lambda p: p.area, reverse=True)
    chapas: List[Dict] = []

    contagem_invalidas: Dict[Tuple[str, int, int], int] = defaultdict(int)
    for p in pecas_invalidas:
        contagem_invalidas[(p.nome, p.largura_mm, p.altura_mm)] += 1
    for peca in ordenadas:
        colocada = False
        for chapa in chapas:
            for prateleira in chapa["prateleiras"]:
                y = prateleira["y"]
                x_cursor = prateleira["x_cursor"]
                altura_prateleira = prateleira["altura"]
                for largura, altura in _orientacoes_possiveis(peca):
                    cabe_largura = x_cursor + largura <= chapa_largura_mm
                    cabe_altura = y + max(altura_prateleira, altura) <= chapa_altura_mm
                    if cabe_largura and cabe_altura:
                        prateleira["pecas"].append(
                            {
                                "id": peca.id,
                                "nome": peca.nome,
                                "x": x_cursor,
                                "y": y,
                                "largura_mm": largura,
                                "altura_mm": altura,
                            }
                        )
                        prateleira["x_cursor"] = x_cursor + largura + kerf
                        prateleira["altura"] = max(altura_prateleira, altura)
                        colocada = True
                        break
                if colocada:
                    break
            if colocada:
                break

            y_prateleiras = sum(s["altura"] + kerf for s in chapa["prateleiras"])
            for largura, altura in _orientacoes_possiveis(peca):
                cabe = (largura <= chapa_largura_mm) and (y_prateleiras + altura <= chapa_altura_mm)
                if cabe:
                    nova = {
                        "y": y_prateleiras,
                        "altura": altura,
                        "x_cursor": largura + kerf,
                        "pecas": [
                            {
                                "id": peca.id,
                                "nome": peca.nome,
                                "x": 0,
                                "y": y_prateleiras,
                                "largura_mm": largura,
                                "altura_mm": altura,
                            }
                        ],
                    }
                    chapa["prateleiras"].append(nova)
                    colocada = True
                    break
            if colocada:
                break

        if colocada:
            continue

        nova_chapa = {
            "prateleiras": [],
        }

        orientacao_escolhida = None
        for largura, altura in _orientacoes_possiveis(peca):
            if largura <= chapa_largura_mm and altura <= chapa_altura_mm:
                orientacao_escolhida = (largura, altura)
                break

        if not orientacao_escolhida:
            contagem_invalidas[(peca.nome, peca.largura_mm, peca.altura_mm)] += 1
            continue

        largura, altura = orientacao_escolhida
        nova_chapa["prateleiras"].append(
            {
                "y": 0,
                "altura": altura,
                "x_cursor": largura + kerf,
                "pecas": [
                    {
                        "id": peca.id,
                        "nome": peca.nome,
                        "x": 0,
                        "y": 0,
                        "largura_mm": largura,
                        "altura_mm": altura,
                    }
                ],
            }
        )
        chapas.append(nova_chapa)

    area_total_pecas = sum(p.area for p in pecas_validas)
    area_chapa = chapa_largura_mm * chapa_altura_mm
    area_total_chapas = area_chapa * len(chapas)
    aproveitamento, perda = calcular_aproveitamento(area_total_pecas, area_total_chapas)

    chapas_saida = []
    for i, chapa in enumerate(chapas):
        pecas_chapa = []
        for prateleira in chapa["prateleiras"]:
            pecas_chapa.extend(prateleira["pecas"])
        chapas_saida.append(
            {
                "indice": i + 1,
                "largura_mm": chapa_largura_mm,
                "altura_mm": chapa_altura_mm,
                "pecas": pecas_chapa,
            }
        )

    pecas_maiores = [
        {
            "nome": nome,
            "largura_mm": largura,
            "altura_mm": altura,
            "quantidade": quantidade,
            "chapa_largura_mm": chapa_largura_mm,
            "chapa_altura_mm": chapa_altura_mm,
        }
        for (nome, largura, altura), quantidade in contagem_invalidas.items()
    ]

    erro = None
    if pecas_maiores:
        erro = "Existem pecas maiores que a chapa e que nao puderam entrar no plano de corte."

    return {
        "quantidade_chapas": len(chapas),
        "chapas": chapas_saida,
        "aproveitamento_percentual": float(aproveitamento),
        "perda_percentual": float(perda),
        "area_total_pecas": float(area_total_pecas),
        "area_total_chapas": float(area_total_chapas),
        "erro": erro,
        "pecas_maiores_que_chapa": pecas_maiores,
    }
