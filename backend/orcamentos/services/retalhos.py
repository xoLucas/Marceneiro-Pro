from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple
from collections import defaultdict

from orcamentos.models import Material, PecaOrcamento, Retalho


def _orientacoes_possiveis(peca: Dict) -> List[Tuple[int, int]]:
    orientacoes = [(peca["largura_mm"], peca["altura_mm"])]
    if peca["pode_rotacionar"] and peca["largura_mm"] != peca["altura_mm"]:
        orientacoes.append((peca["altura_mm"], peca["largura_mm"]))
    return orientacoes


def _expandir_pecas(pecas: List[PecaOrcamento]) -> List[Dict]:
    unidades = []
    for peca in pecas:
        for _ in range(peca.quantidade):
            unidades.append(
                {
                    "peca_id": peca.id,
                    "peca_nome": peca.nome,
                    "material_id": peca.material_id,
                    "material_nome": peca.material.nome,
                    "largura_mm": peca.largura_mm,
                    "altura_mm": peca.altura_mm,
                    "pode_rotacionar": peca.pode_rotacionar,
                    "area": peca.largura_mm * peca.altura_mm,
                }
            )
    return sorted(unidades, key=lambda p: p["area"], reverse=True)


def _tentar_alocar_em_retalho(peca: Dict, retalho_estado: Dict, kerf: int) -> Dict | None:
    for idx, rect in enumerate(retalho_estado["retangulos_livres"]):
        for larg, alt in _orientacoes_possiveis(peca):
            if larg <= rect["largura_mm"] and alt <= rect["altura_mm"]:
                x = rect["x"]
                y = rect["y"]

                retalho_estado["retangulos_livres"].pop(idx)

                sobra_direita = rect["largura_mm"] - larg - kerf
                sobra_baixo = rect["altura_mm"] - alt - kerf

                if sobra_direita > 0:
                    retalho_estado["retangulos_livres"].append(
                        {"x": x + larg + kerf, "y": y, "largura_mm": sobra_direita, "altura_mm": alt}
                    )
                if sobra_baixo > 0:
                    retalho_estado["retangulos_livres"].append(
                        {"x": x, "y": y + alt + kerf, "largura_mm": rect["largura_mm"], "altura_mm": sobra_baixo}
                    )

                return {"x": x, "y": y, "largura_mm": larg, "altura_mm": alt}
    return None


def planejar_uso_retalhos(
    pecas: List[PecaOrcamento],
    retalhos: List[Retalho],
    kerf_mm: Decimal,
    materiais_chapa_info: Dict[int, Dict[str, Decimal | int]] | None = None,
) -> Dict:
    kerf = max(0, int(round(float(kerf_mm))))
    retalhos_estados = []
    for retalho in retalhos:
        if not retalho.disponivel:
            continue
        retalhos_estados.append(
            {
                "retalho": retalho,
                "retangulos_livres": [{"x": 0, "y": 0, "largura_mm": retalho.largura_mm, "altura_mm": retalho.altura_mm}],
                "pecas_alocadas": [],
            }
        )

    pecas_unidade = _expandir_pecas(pecas)
    consumo_por_peca_id: Dict[int, int] = defaultdict(int)
    area_aproveitada_por_material: Dict[int, int] = defaultdict(int)

    for peca in pecas_unidade:
        for estado in retalhos_estados:
            retalho = estado["retalho"]
            if retalho.material_id != peca["material_id"]:
                continue

            posicao = _tentar_alocar_em_retalho(peca, estado, kerf)
            if not posicao:
                continue

            consumo_por_peca_id[peca["peca_id"]] += 1
            area_aproveitada_por_material[peca["material_id"]] += peca["area"]
            estado["pecas_alocadas"].append(
                {
                    "peca_id": peca["peca_id"],
                    "peca_nome": peca["peca_nome"],
                    "largura_mm": posicao["largura_mm"],
                    "altura_mm": posicao["altura_mm"],
                    "x": posicao["x"],
                    "y": posicao["y"],
                }
            )
            break

    retalhos_usados = []
    for estado in retalhos_estados:
        if not estado["pecas_alocadas"]:
            continue
        retalho = estado["retalho"]
        retalhos_usados.append(
            {
                "retalho_id": retalho.id,
                "material_id": retalho.material_id,
                "material": retalho.material.nome,
                "largura_mm": retalho.largura_mm,
                "altura_mm": retalho.altura_mm,
                "pecas_atendidas": estado["pecas_alocadas"],
            }
        )

    economia_estimada = Decimal("0")
    chapas_economizadas = Decimal("0")
    if materiais_chapa_info:
        for material_id, area_aproveitada in area_aproveitada_por_material.items():
            info = materiais_chapa_info.get(material_id) or {}
            area_chapa = int(info.get("area_chapa_mm2", 0))
            preco_chapa = Decimal(str(info.get("preco_chapa", 0)))
            if area_chapa > 0 and preco_chapa > 0:
                chapas_economizadas += Decimal(area_aproveitada) / Decimal(area_chapa)
                economia_estimada += (Decimal(area_aproveitada) / Decimal(area_chapa)) * preco_chapa

    return {
        "retalhos_usados": retalhos_usados,
        "quantidade_pecas_atendidas": sum(consumo_por_peca_id.values()),
        "consumo_por_peca_id": {str(k): v for k, v in consumo_por_peca_id.items()},
        "chapas_economizadas_aprox": float(chapas_economizadas.quantize(Decimal("0.01"))),
        "economia_estimada": float(economia_estimada.quantize(Decimal("0.01"))),
    }


def filtrar_retalhos_compativeis(retalhos: List[Retalho], material: Material) -> List[Retalho]:
    return [r for r in retalhos if r.material_id == material.id and r.material.espessura_mm == material.espessura_mm]
