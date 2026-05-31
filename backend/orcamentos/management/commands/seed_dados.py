from decimal import Decimal

from django.core.management.base import BaseCommand

from orcamentos.models import Cliente, Material, Orcamento, Retalho
from orcamentos.services.calculo_orcamento import calcular_orcamento_completo


class Command(BaseCommand):
    help = "Carrega dados iniciais de exemplo para o app."

    def handle(self, *args, **options):
        self.stdout.write("Criando materiais...")
        materiais = [
            ("MDF branco TX 18 mm", "mdf", 18, 2750, 1850, "chapa", "349.90"),
            ("MDF branco TX 6 mm", "mdf", 6, 2750, 1850, "chapa", "145.00"),
            ("MDF amadeirado 15 mm", "mdf", 15, 2750, 1850, "chapa", "420.00"),
            ("Fita de borda branca 22 mm", "fita_borda", 0, 0, 0, "metro", "1.50"),
            ("Fita de borda amadeirada 22 mm", "fita_borda", 0, 0, 0, "metro", "2.20"),
            ("Corrediça telescópica 45 cm", "ferragem", 0, 0, 0, "par", "22.00"),
            ("Dobradiça caneco 35 mm", "ferragem", 0, 0, 0, "unidade", "3.50"),
            ("Kit porta de correr", "ferragem", 0, 0, 0, "unidade", "280.00"),
            ("Roldana/guia para porta de correr", "ferragem", 0, 0, 0, "conjunto", "45.00"),
            ("Cabideiro", "ferragem", 0, 0, 0, "unidade", "35.00"),
            ("Suporte de cabideiro", "ferragem", 0, 0, 0, "unidade", "5.00"),
            ("Puxador simples", "ferragem", 0, 0, 0, "unidade", "12.00"),
            ("Insumos gerais", "insumo", 0, 0, 0, "unidade", "80.00"),
        ]

        mapa = {}
        for nome, tipo, esp, larg, alt, unidade, preco in materiais:
            obj, _ = Material.objects.get_or_create(
                nome=nome,
                defaults={
                    "tipo": tipo,
                    "espessura_mm": esp,
                    "largura_mm": larg,
                    "altura_mm": alt,
                    "unidade": unidade,
                    "preco_unitario": Decimal(preco),
                    "fornecedor": "Fornecedor padrao",
                    "padrao_visual": "madeirado" if "amadeirado" in nome.lower() else "liso",
                },
            )
            mapa[nome] = obj

        self.stdout.write("Criando clientes...")
        joao, _ = Cliente.objects.get_or_create(nome="João Carlos", defaults={"telefone": "(11) 99999-1111"})
        maria, _ = Cliente.objects.get_or_create(nome="Maria Souza", defaults={"telefone": "(11) 99999-2222"})
        ana, _ = Cliente.objects.get_or_create(nome="Ana Paula", defaults={"telefone": "(11) 99999-3333"})

        self.stdout.write("Criando retalhos...")
        retalhos = [
            ("MDF branco TX 18 mm", 900, 650),
            ("MDF branco TX 18 mm", 1200, 400),
            ("MDF amadeirado 15 mm", 900, 600),
        ]
        for nome_mat, larg, alt in retalhos:
            Retalho.objects.get_or_create(
                material=mapa[nome_mat],
                largura_mm=larg,
                altura_mm=alt,
                defaults={"origem": "Sobra de obra", "disponivel": True},
            )

        self.stdout.write("Criando orcamentos de exemplo...")
        orc1, _ = Orcamento.objects.get_or_create(
            cliente=joao,
            nome_projeto="Guarda-roupa João",
            defaults={
                "tipo_movel": Orcamento.TipoMovel.GUARDA_ROUPA,
                "largura_mm": 2400,
                "altura_mm": 2600,
                "profundidade_mm": 600,
                "material_principal": mapa["MDF branco TX 18 mm"],
                "material_fundo": mapa["MDF branco TX 6 mm"],
                "quantidade_portas": 3,
                "tipo_porta": Orcamento.TipoPorta.CORRER,
                "quantidade_gavetas": 4,
                "quantidade_prateleiras": 6,
                "quantidade_divisorias": 3,
                "quantidade_cabideiros": 2,
                "kerf_mm": Decimal("3.00"),
                "perda_tecnica_percentual": Decimal("10.00"),
                "margem_desejada_percentual": Decimal("35.00"),
                "quantidade_diarias": 5,
                "valor_diaria": Decimal("280.00"),
                "valor_instalacao": Decimal("300.00"),
                "valor_frete": Decimal("120.00"),
                "usar_retalhos": True,
            },
        )
        orc2, _ = Orcamento.objects.get_or_create(
            cliente=maria,
            nome_projeto="Painel de TV Maria",
            defaults={
                "tipo_movel": Orcamento.TipoMovel.PAINEL_TV,
                "largura_mm": 1800,
                "altura_mm": 1600,
                "profundidade_mm": 400,
                "material_principal": mapa["MDF amadeirado 15 mm"],
                "material_fundo": mapa["MDF branco TX 6 mm"],
                "portas_basculantes": 2,
                "quantidade_nichos": 3,
                "margem_desejada_percentual": Decimal("35.00"),
                "quantidade_diarias": 2,
                "valor_diaria": Decimal("280.00"),
                "valor_instalacao": Decimal("180.00"),
            },
        )
        orc3, _ = Orcamento.objects.get_or_create(
            cliente=ana,
            nome_projeto="Armário aéreo Ana",
            defaults={
                "tipo_movel": Orcamento.TipoMovel.ARMARIO_AEREO,
                "largura_mm": 1200,
                "altura_mm": 700,
                "profundidade_mm": 320,
                "material_principal": mapa["MDF branco TX 18 mm"],
                "material_fundo": mapa["MDF branco TX 6 mm"],
                "quantidade_portas": 3,
                "tipo_porta": Orcamento.TipoPorta.ABRIR,
                "quantidade_prateleiras": 1,
                "margem_desejada_percentual": Decimal("35.00"),
                "quantidade_diarias": 1,
                "valor_diaria": Decimal("280.00"),
                "valor_instalacao": Decimal("120.00"),
            },
        )

        for orc in [orc1, orc2, orc3]:
            calcular_orcamento_completo(orc)

        self.stdout.write(self.style.SUCCESS("Seed carregada com sucesso."))
