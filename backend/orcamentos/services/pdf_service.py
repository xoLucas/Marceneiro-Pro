from __future__ import annotations

from io import BytesIO
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from orcamentos.models import Orcamento


def _nova_pagina(c: canvas.Canvas, titulo: str) -> int:
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, 280 * mm, titulo)
    c.setFont("Helvetica", 10)
    return 272


def _desenhar_linhas(c: canvas.Canvas, y_inicial: int, linhas: List[str]) -> None:
    y = y_inicial
    for linha in linhas:
        if y < 20:
            c.showPage()
            y = _nova_pagina(c, "Continuidade")
        c.drawString(20 * mm, y * mm, linha[:120])
        y -= 6


def gerar_pdf_cliente(orcamento: Orcamento, resultado: Dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = _nova_pagina(c, f"Orcamento - {orcamento.nome_projeto}")

    linhas = [
        f"Cliente: {orcamento.cliente.nome}",
        f"Projeto: {orcamento.nome_projeto}",
        f"Tipo de movel: {orcamento.get_tipo_movel_display()}",
        f"Descricao: {orcamento.descricao or '-'}",
        f"Preco final: R$ {resultado.get('financeiro', {}).get('preco_final', 0):.2f}",
        f"Validade: {orcamento.validade_dias} dias",
        "",
        "Forma de pagamento sugerida:",
    ]
    for pg in resultado.get("financeiro", {}).get("sugestao_pagamento", []):
        linhas.append(f"- {pg['descricao']}: R$ {pg['valor']:.2f}")

    linhas.extend(["", "Observacoes:", "Assinatura/aceite: _______________________________"])

    if orcamento.mostrar_detalhamento_pdf_cliente:
        linhas.extend(
            [
                "",
                "Resumo tecnico:",
                f"- Quantidade de pecas: {len(resultado.get('pecas', []))}",
                f"- Aproveitamento: {resultado.get('plano_corte', {}).get('aproveitamento_percentual', 0):.2f}%",
                f"- Alertas: {len(resultado.get('alertas', {}).get('alertas', []))}",
            ]
        )

    _desenhar_linhas(c, y, linhas)
    c.showPage()
    c.save()
    return buffer.getvalue()


def gerar_pdf_tecnico(orcamento: Orcamento, resultado: Dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = _nova_pagina(c, f"PDF Tecnico - {orcamento.nome_projeto}")

    linhas = [
        f"Cliente: {orcamento.cliente.nome}",
        f"Projeto: {orcamento.nome_projeto}",
        "",
        "Resumo financeiro:",
    ]
    financeiro = resultado.get("financeiro", {})
    for chave in ["custo_total", "preco_sugerido", "preco_final", "lucro_estimado", "margem_real_percentual"]:
        linhas.append(f"- {chave}: {financeiro.get(chave, 0)}")

    linhas.extend(["", "Alertas:"])
    for alerta in resultado.get("alertas", {}).get("alertas", []):
        linhas.append(f"- {alerta}")

    linhas.extend(["", "Lista de compra:"])
    for item in resultado.get("lista_compra", [])[:30]:
        linhas.append(f"- {item['nome']} | {item['quantidade']} {item['unidade']} | R$ {item['total']:.2f}")

    linhas.extend(["", "Ordem de producao:"])
    for passo in resultado.get("ordem_producao", {}).get("ordem_sugerida", []):
        linhas.append(f"- {passo}")

    _desenhar_linhas(c, y, linhas)
    c.showPage()
    c.save()
    return buffer.getvalue()
