from __future__ import annotations

from typing import Dict, List

from orcamentos.models import Material, Orcamento


def gerar_alertas_risco(
    orcamento: Orcamento,
    materiais: List[Material],
    aproveitamento_percentual: float,
    margem_real_percentual: float,
    existe_peca_maior_chapa: bool,
    pecas_maiores_chapa: List[Dict] | None,
    retalhos_poderiam_ajudar: bool,
) -> Dict:
    alertas = []
    score = 100

    if any(m.preco_unitario <= 0 for m in materiais):
        alertas.append("Preco do material esta zerado ou nao cadastrado.")
        score -= 12

    if aproveitamento_percentual < 70:
        alertas.append("Aproveitamento de chapa abaixo de 70%.")
        score -= 10

    if margem_real_percentual < float(orcamento.margem_desejada_percentual):
        alertas.append("Margem real abaixo da margem desejada.")
        score -= 12

    if margem_real_percentual < 25:
        alertas.append("Margem real abaixo de 25%.")
        score -= 12

    if orcamento.valor_instalacao <= 0:
        alertas.append("O orcamento nao possui custo de instalacao.")
        score -= 6

    if orcamento.valor_frete <= 0:
        alertas.append("O orcamento nao possui custo de frete.")
        score -= 4

    if existe_peca_maior_chapa:
        alertas.append("Existe peca maior que a chapa disponivel. Revise as medidas ou o material/chapa selecionado.")
        for peca in (pecas_maiores_chapa or []):
            alertas.append(
                "Peca fora do limite: "
                f"{peca['nome']} ({peca['largura_mm']}x{peca['altura_mm']} mm), "
                f"qtd {peca['quantidade']}. "
                f"Chapa disponivel: {peca['chapa_largura_mm']}x{peca['chapa_altura_mm']} mm."
            )
        score -= 20

    if orcamento.material_principal and not orcamento.material_principal.permite_rotacao_padrao:
        alertas.append("Material principal nao permite rotacao, verifique sentido do veio.")
        score -= 8

    if orcamento.preco_final_manual is not None and margem_real_percentual < 15:
        alertas.append("Preco final manual reduz muito o lucro.")
        score -= 14

    if retalhos_poderiam_ajudar:
        alertas.append("Retalhos disponiveis poderiam reduzir custo.")
        score -= 5

    score = max(0, score)
    return {"alertas": alertas, "nota_confianca": score}
