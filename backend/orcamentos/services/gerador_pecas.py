from __future__ import annotations

from typing import Dict, List

from orcamentos.models import Orcamento


def _clamp_mm(valor: float, minimo: int = 10) -> int:
    return max(minimo, int(round(valor)))


def gerar_pecas_automaticas(orcamento: Orcamento) -> List[Dict]:
    if not orcamento.material_principal:
        return []

    if orcamento.tipo_movel == Orcamento.TipoMovel.GUARDA_ROUPA:
        return _gerar_pecas_guarda_roupa(orcamento)
    if orcamento.tipo_movel == Orcamento.TipoMovel.PAINEL_TV:
        return _gerar_pecas_painel_tv_rack(orcamento)
    if orcamento.tipo_movel == Orcamento.TipoMovel.ARMARIO_AEREO:
        return _gerar_pecas_armario_aereo(orcamento)
    return []


def _gerar_pecas_guarda_roupa(orcamento: Orcamento) -> List[Dict]:
    material = orcamento.material_principal
    material_fundo = orcamento.material_fundo or material
    esp = material.espessura_mm or 18
    largura = orcamento.largura_mm
    altura = orcamento.altura_mm
    profundidade = orcamento.profundidade_mm

    largura_interna = _clamp_mm(largura - (2 * esp))
    profundidade_interna = _clamp_mm(profundidade - 50)
    modulos = max(1, orcamento.quantidade_divisorias + 1)
    largura_modulo = _clamp_mm((largura_interna - (orcamento.quantidade_divisorias * esp)) / modulos)

    pecas = [
        {
            "nome": "Lateral esquerda",
            "material_id": material.id,
            "largura_mm": _clamp_mm(altura),
            "altura_mm": _clamp_mm(profundidade),
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Lateral direita",
            "material_id": material.id,
            "largura_mm": _clamp_mm(altura),
            "altura_mm": _clamp_mm(profundidade),
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Base",
            "material_id": material.id,
            "largura_mm": largura_interna,
            "altura_mm": _clamp_mm(profundidade),
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Topo",
            "material_id": material.id,
            "largura_mm": largura_interna,
            "altura_mm": _clamp_mm(profundidade),
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Fundo",
            "material_id": material_fundo.id,
            "largura_mm": _clamp_mm(largura),
            "altura_mm": _clamp_mm(altura),
            "quantidade": 1,
            "espessura_mm": material_fundo.espessura_mm,
            "pode_rotacionar": material_fundo.permite_rotacao_padrao,
            "fita_frontal": False,
        },
    ]

    for i in range(orcamento.quantidade_divisorias):
        pecas.append(
            {
                "nome": f"Divisoria {i + 1}",
                "material_id": material.id,
                "largura_mm": _clamp_mm(altura - 100),
                "altura_mm": profundidade_interna,
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": material.permite_rotacao_padrao,
                "fita_frontal": True,
            }
        )

    for i in range(orcamento.quantidade_prateleiras):
        pecas.append(
            {
                "nome": f"Prateleira {i + 1}",
                "material_id": material.id,
                "largura_mm": largura_modulo,
                "altura_mm": profundidade_interna,
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": material.permite_rotacao_padrao,
                "fita_frontal": True,
            }
        )

    largura_porta = _clamp_mm(largura / max(1, orcamento.quantidade_portas))
    altura_porta = _clamp_mm(altura - 50)
    for i in range(orcamento.quantidade_portas):
        pecas.append(
            {
                "nome": f"Porta {i + 1}",
                "material_id": material.id,
                "largura_mm": altura_porta,
                "altura_mm": largura_porta,
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": False,
                "fita_frontal": True,
            }
        )

    for i in range(orcamento.quantidade_gavetas):
        frente_largura = _clamp_mm(largura_modulo)
        pecas.extend(
            [
                {
                    "nome": f"Frente gaveta {i + 1}",
                    "material_id": material.id,
                    "largura_mm": frente_largura,
                    "altura_mm": 180,
                    "quantidade": 1,
                    "espessura_mm": esp,
                    "pode_rotacionar": material.permite_rotacao_padrao,
                    "fita_frontal": True,
                },
                {
                    "nome": f"Lateral gaveta {i + 1}",
                    "material_id": material.id,
                    "largura_mm": 450,
                    "altura_mm": 120,
                    "quantidade": 2,
                    "espessura_mm": esp,
                    "pode_rotacionar": material.permite_rotacao_padrao,
                    "fita_frontal": False,
                },
                {
                    "nome": f"Traseiro gaveta {i + 1}",
                    "material_id": material.id,
                    "largura_mm": _clamp_mm(frente_largura - 40),
                    "altura_mm": 120,
                    "quantidade": 1,
                    "espessura_mm": esp,
                    "pode_rotacionar": material.permite_rotacao_padrao,
                    "fita_frontal": False,
                },
                {
                    "nome": f"Fundo gaveta {i + 1}",
                    "material_id": material_fundo.id,
                    "largura_mm": _clamp_mm(frente_largura - 40),
                    "altura_mm": 450,
                    "quantidade": 1,
                    "espessura_mm": material_fundo.espessura_mm,
                    "pode_rotacionar": material_fundo.permite_rotacao_padrao,
                    "fita_frontal": False,
                },
            ]
        )

    return pecas


def _gerar_pecas_painel_tv_rack(orcamento: Orcamento) -> List[Dict]:
    material = orcamento.material_principal
    esp = material.espessura_mm or 15

    largura_painel = _clamp_mm(orcamento.largura_mm)
    altura_painel = _clamp_mm(orcamento.altura_mm)
    profundidade_rack = _clamp_mm(orcamento.profundidade_mm)
    altura_rack = 450

    pecas = [
        {
            "nome": "Painel principal",
            "material_id": material.id,
            "largura_mm": altura_painel,
            "altura_mm": largura_painel,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Base rack",
            "material_id": material.id,
            "largura_mm": largura_painel,
            "altura_mm": profundidade_rack,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Topo rack",
            "material_id": material.id,
            "largura_mm": largura_painel,
            "altura_mm": profundidade_rack,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Lateral rack esquerda",
            "material_id": material.id,
            "largura_mm": altura_rack,
            "altura_mm": profundidade_rack,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Lateral rack direita",
            "material_id": material.id,
            "largura_mm": altura_rack,
            "altura_mm": profundidade_rack,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
    ]

    for i in range(orcamento.quantidade_nichos):
        pecas.append(
            {
                "nome": f"Divisoria nicho {i + 1}",
                "material_id": material.id,
                "largura_mm": _clamp_mm(altura_rack - 36),
                "altura_mm": profundidade_rack,
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": material.permite_rotacao_padrao,
                "fita_frontal": True,
            }
        )

    for i in range(orcamento.portas_basculantes):
        pecas.append(
            {
                "nome": f"Porta basculante {i + 1}",
                "material_id": material.id,
                "largura_mm": 350,
                "altura_mm": _clamp_mm(largura_painel / max(1, orcamento.portas_basculantes)),
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": material.permite_rotacao_padrao,
                "fita_frontal": True,
            }
        )

    return pecas


def _gerar_pecas_armario_aereo(orcamento: Orcamento) -> List[Dict]:
    material = orcamento.material_principal
    material_fundo = orcamento.material_fundo or material
    esp = material.espessura_mm or 15
    largura = _clamp_mm(orcamento.largura_mm)
    altura = _clamp_mm(orcamento.altura_mm)
    profundidade = _clamp_mm(orcamento.profundidade_mm)
    largura_interna = _clamp_mm(largura - (2 * esp))

    pecas = [
        {
            "nome": "Lateral esquerda",
            "material_id": material.id,
            "largura_mm": altura,
            "altura_mm": profundidade,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Lateral direita",
            "material_id": material.id,
            "largura_mm": altura,
            "altura_mm": profundidade,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Base",
            "material_id": material.id,
            "largura_mm": largura_interna,
            "altura_mm": profundidade,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Topo",
            "material_id": material.id,
            "largura_mm": largura_interna,
            "altura_mm": profundidade,
            "quantidade": 1,
            "espessura_mm": esp,
            "pode_rotacionar": material.permite_rotacao_padrao,
            "fita_frontal": True,
        },
        {
            "nome": "Fundo",
            "material_id": material_fundo.id,
            "largura_mm": largura,
            "altura_mm": altura,
            "quantidade": 1,
            "espessura_mm": material_fundo.espessura_mm,
            "pode_rotacionar": material_fundo.permite_rotacao_padrao,
            "fita_frontal": False,
        },
    ]

    for i in range(orcamento.quantidade_prateleiras):
        pecas.append(
            {
                "nome": f"Prateleira {i + 1}",
                "material_id": material.id,
                "largura_mm": largura_interna,
                "altura_mm": _clamp_mm(profundidade - 30),
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": material.permite_rotacao_padrao,
                "fita_frontal": True,
            }
        )

    largura_porta = _clamp_mm(largura / max(1, orcamento.quantidade_portas))
    for i in range(orcamento.quantidade_portas):
        pecas.append(
            {
                "nome": f"Porta {i + 1}",
                "material_id": material.id,
                "largura_mm": _clamp_mm(altura - 20),
                "altura_mm": largura_porta,
                "quantidade": 1,
                "espessura_mm": esp,
                "pode_rotacionar": False,
                "fita_frontal": True,
            }
        )

    return pecas
