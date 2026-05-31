from decimal import Decimal

from django.test import TestCase

from orcamentos.models import Cliente, Material, Orcamento, PecaOrcamento
from orcamentos.services.calculo_ferragens import calcular_dobradicas_por_altura
from orcamentos.services.calculo_fita import calcular_total_fita_metros
from orcamentos.services.financeiro import calcular_preco_sugerido
from orcamentos.services.gerador_pecas import gerar_pecas_automaticas
from orcamentos.services.otimizador_corte import PecaExpandida, calcular_aproveitamento, otimizar_plano_corte
from orcamentos.services.retalhos import planejar_uso_retalhos
from orcamentos.models import Retalho


class OrcamentoServicesTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Cliente Teste")
        self.material = Material.objects.create(
            nome="MDF branco TX 18 mm",
            tipo=Material.Tipo.MDF,
            espessura_mm=18,
            largura_mm=2750,
            altura_mm=1850,
            unidade=Material.Unidade.CHAPA,
            preco_unitario=Decimal("349.90"),
            permite_rotacao_padrao=True,
        )
        self.material_fundo = Material.objects.create(
            nome="MDF branco TX 6 mm",
            tipo=Material.Tipo.MDF,
            espessura_mm=6,
            largura_mm=2750,
            altura_mm=1850,
            unidade=Material.Unidade.CHAPA,
            preco_unitario=Decimal("145.00"),
            permite_rotacao_padrao=True,
        )

    def test_calculo_preco_sugerido(self):
        custo = Decimal("4442")
        margem = Decimal("35")
        preco = calcular_preco_sugerido(custo, margem)
        self.assertEqual(preco, Decimal("6833.85"))

    def test_calculo_fita_borda(self):
        orcamento = Orcamento.objects.create(
            cliente=self.cliente,
            nome_projeto="Teste fita",
            tipo_movel=Orcamento.TipoMovel.GUARDA_ROUPA,
            material_principal=self.material,
        )
        peca = PecaOrcamento.objects.create(
            orcamento=orcamento,
            nome="Peca X",
            material=self.material,
            largura_mm=2550,
            altura_mm=800,
            quantidade=1,
            espessura_mm=18,
            pode_rotacionar=True,
            fita_topo=True,
            fita_baixo=True,
            fita_esquerda=True,
            fita_direita=True,
        )
        total_m = calcular_total_fita_metros([peca], Decimal("10"))
        self.assertEqual(total_m, Decimal("7.370"))

    def test_geracao_pecas_guarda_roupa(self):
        orcamento = Orcamento.objects.create(
            cliente=self.cliente,
            nome_projeto="Guarda teste",
            tipo_movel=Orcamento.TipoMovel.GUARDA_ROUPA,
            largura_mm=2400,
            altura_mm=2600,
            profundidade_mm=600,
            material_principal=self.material,
            material_fundo=self.material_fundo,
            quantidade_portas=3,
            tipo_porta=Orcamento.TipoPorta.CORRER,
            quantidade_gavetas=4,
            quantidade_prateleiras=6,
            quantidade_divisorias=3,
        )
        pecas = gerar_pecas_automaticas(orcamento)
        nomes = [p["nome"] for p in pecas]
        self.assertIn("Lateral esquerda", nomes)
        self.assertIn("Lateral direita", nomes)
        self.assertEqual(sum(1 for n in nomes if n.startswith("Porta")), 3)

    def test_regra_dobradicas_por_altura(self):
        self.assertEqual(calcular_dobradicas_por_altura(800), 2)
        self.assertEqual(calcular_dobradicas_por_altura(1200), 3)
        self.assertEqual(calcular_dobradicas_por_altura(2000), 4)
        self.assertEqual(calcular_dobradicas_por_altura(2500), 5)

    def test_plano_corte_simples(self):
        pecas = [
            PecaExpandida(id=1, nome="A", largura_mm=1200, altura_mm=500, pode_rotacionar=True),
            PecaExpandida(id=2, nome="B", largura_mm=1000, altura_mm=500, pode_rotacionar=True),
        ]
        resultado = otimizar_plano_corte(pecas, 2750, 1850, 3)
        self.assertGreaterEqual(resultado["quantidade_chapas"], 1)
        self.assertIn("chapas", resultado)

    def test_calculo_aproveitamento(self):
        aproveitamento, perda = calcular_aproveitamento(50, 100)
        self.assertEqual(aproveitamento, Decimal("50.00"))
        self.assertEqual(perda, Decimal("50.00"))

    def test_plano_corte_informa_peca_maior_que_chapa(self):
        pecas = [PecaExpandida(id=1, nome="Painel gigante", largura_mm=4000, altura_mm=2200, pode_rotacionar=True)]
        resultado = otimizar_plano_corte(pecas, 2750, 1850, 3)
        self.assertEqual(resultado["quantidade_chapas"], 0)
        self.assertTrue(resultado["pecas_maiores_que_chapa"])
        self.assertIn("Painel gigante", resultado["pecas_maiores_que_chapa"][0]["nome"])

    def test_planejamento_retalho_atende_parte_da_quantidade(self):
        retalho = Retalho.objects.create(material=self.material, largura_mm=1000, altura_mm=700, disponivel=True)
        orcamento = Orcamento.objects.create(
            cliente=self.cliente,
            nome_projeto="Teste retalho",
            tipo_movel=Orcamento.TipoMovel.GUARDA_ROUPA,
            material_principal=self.material,
        )
        peca = PecaOrcamento.objects.create(
            orcamento=orcamento,
            nome="Prateleira",
            material=self.material,
            largura_mm=900,
            altura_mm=600,
            quantidade=4,
            espessura_mm=18,
            pode_rotacionar=True,
        )

        resultado = planejar_uso_retalhos(
            pecas=[peca],
            retalhos=[retalho],
            kerf_mm=Decimal("3"),
            materiais_chapa_info={
                self.material.id: {
                    "preco_chapa": self.material.preco_unitario,
                    "area_chapa_mm2": self.material.largura_mm * self.material.altura_mm,
                }
            },
        )
        self.assertGreaterEqual(resultado["quantidade_pecas_atendidas"], 1)
        self.assertGreaterEqual(resultado["consumo_por_peca_id"].get(str(peca.id), 0), 1)
