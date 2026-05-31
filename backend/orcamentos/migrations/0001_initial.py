from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=180)),
                ("telefone", models.CharField(blank=True, max_length=40)),
                ("endereco", models.TextField(blank=True)),
                ("observacoes", models.TextField(blank=True)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=180)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("mdf", "MDF"),
                            ("compensado", "Compensado"),
                            ("madeira", "Madeira"),
                            ("fita_borda", "Fita de borda"),
                            ("ferragem", "Ferragem"),
                            ("insumo", "Insumo"),
                            ("servico", "Servico"),
                            ("outro", "Outro"),
                        ],
                        default="mdf",
                        max_length=30,
                    ),
                ),
                ("espessura_mm", models.PositiveIntegerField(default=0)),
                ("largura_mm", models.PositiveIntegerField(default=0)),
                ("altura_mm", models.PositiveIntegerField(default=0)),
                (
                    "unidade",
                    models.CharField(
                        choices=[
                            ("chapa", "Chapa"),
                            ("metro", "Metro"),
                            ("unidade", "Unidade"),
                            ("par", "Par"),
                            ("diaria", "Diaria"),
                            ("conjunto", "Conjunto"),
                            ("pacote", "Pacote"),
                        ],
                        default="unidade",
                        max_length=30,
                    ),
                ),
                ("preco_unitario", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("fornecedor", models.CharField(blank=True, max_length=180)),
                (
                    "padrao_visual",
                    models.CharField(
                        choices=[("liso", "Liso"), ("madeirado", "Madeirado"), ("outro", "Outro")],
                        default="liso",
                        max_length=30,
                    ),
                ),
                ("permite_rotacao_padrao", models.BooleanField(default=True)),
                (
                    "sentido_veio",
                    models.CharField(
                        choices=[("vertical", "Vertical"), ("horizontal", "Horizontal"), ("indiferente", "Indiferente")],
                        default="indiferente",
                        max_length=30,
                    ),
                ),
                ("ativo", models.BooleanField(default=True)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Orcamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome_projeto", models.CharField(max_length=180)),
                (
                    "tipo_movel",
                    models.CharField(
                        choices=[
                            ("guarda_roupa", "Guarda-roupa"),
                            ("painel_tv", "Painel de TV com rack"),
                            ("armario_aereo", "Armario aereo"),
                            ("outro", "Outro"),
                        ],
                        default="outro",
                        max_length=30,
                    ),
                ),
                ("largura_mm", models.PositiveIntegerField(default=0)),
                ("altura_mm", models.PositiveIntegerField(default=0)),
                ("profundidade_mm", models.PositiveIntegerField(default=0)),
                ("descricao", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("rascunho", "Rascunho"),
                            ("calculado", "Calculado"),
                            ("enviado", "Enviado"),
                            ("aprovado", "Aprovado"),
                            ("recusado", "Recusado"),
                        ],
                        default="rascunho",
                        max_length=20,
                    ),
                ),
                ("quantidade_portas", models.PositiveIntegerField(default=0)),
                (
                    "tipo_porta",
                    models.CharField(
                        choices=[
                            ("abrir", "Abrir"),
                            ("correr", "Correr"),
                            ("basculante", "Basculante"),
                            ("nenhuma", "Nenhuma"),
                        ],
                        default="nenhuma",
                        max_length=20,
                    ),
                ),
                ("quantidade_gavetas", models.PositiveIntegerField(default=0)),
                ("quantidade_prateleiras", models.PositiveIntegerField(default=0)),
                ("quantidade_divisorias", models.PositiveIntegerField(default=0)),
                ("quantidade_cabideiros", models.PositiveIntegerField(default=0)),
                ("portas_basculantes", models.PositiveIntegerField(default=0)),
                ("quantidade_nichos", models.PositiveIntegerField(default=0)),
                ("usar_retalhos", models.BooleanField(default=False)),
                ("kerf_mm", models.DecimalField(decimal_places=2, default=Decimal("3.00"), max_digits=6)),
                ("perda_tecnica_percentual", models.DecimalField(decimal_places=2, default=Decimal("10.00"), max_digits=6)),
                ("margem_desejada_percentual", models.DecimalField(decimal_places=2, default=Decimal("35.00"), max_digits=6)),
                ("valor_mao_obra", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("quantidade_diarias", models.PositiveIntegerField(default=0)),
                ("valor_diaria", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("valor_instalacao", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("valor_frete", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("custos_extras", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("preco_final_manual", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("validade_dias", models.PositiveIntegerField(default=15)),
                ("mostrar_detalhamento_pdf_cliente", models.BooleanField(default=False)),
                ("resultado_calculo", models.JSONField(blank=True, default=dict)),
                ("nota_confianca", models.PositiveIntegerField(default=100)),
                ("data_ultima_calculacao", models.DateTimeField(blank=True, null=True)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                (
                    "cliente",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orcamentos", to="orcamentos.cliente"),
                ),
                (
                    "material_fundo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orcamentos_fundo",
                        to="orcamentos.material",
                    ),
                ),
                (
                    "material_principal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orcamentos_principais",
                        to="orcamentos.material",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Retalho",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("largura_mm", models.PositiveIntegerField()),
                ("altura_mm", models.PositiveIntegerField()),
                ("origem", models.CharField(blank=True, max_length=180)),
                ("observacoes", models.TextField(blank=True)),
                ("disponivel", models.BooleanField(default=True)),
                ("data_cadastro", models.DateTimeField(auto_now_add=True)),
                (
                    "material",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="retalhos", to="orcamentos.material"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PecaOrcamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=180)),
                ("largura_mm", models.PositiveIntegerField()),
                ("altura_mm", models.PositiveIntegerField()),
                ("quantidade", models.PositiveIntegerField(default=1)),
                ("espessura_mm", models.PositiveIntegerField(default=0)),
                ("pode_rotacionar", models.BooleanField(default=True)),
                ("fita_topo", models.BooleanField(default=False)),
                ("fita_baixo", models.BooleanField(default=False)),
                ("fita_esquerda", models.BooleanField(default=False)),
                ("fita_direita", models.BooleanField(default=False)),
                ("observacoes", models.TextField(blank=True)),
                (
                    "material",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pecas_orcamento",
                        to="orcamentos.material",
                    ),
                ),
                (
                    "orcamento",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pecas", to="orcamentos.orcamento"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PlanoCorte",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade_chapas", models.PositiveIntegerField(default=0)),
                ("aproveitamento_percentual", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                ("perda_percentual", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=6)),
                ("area_total_pecas", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("area_total_chapas", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("resultado_json", models.JSONField(blank=True, default=dict)),
                ("data_criacao", models.DateTimeField(auto_now_add=True)),
                (
                    "material",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="planos_corte", to="orcamentos.material"),
                ),
                (
                    "orcamento",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="planos_corte", to="orcamentos.orcamento"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PagamentoSugerido",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=180)),
                ("valor", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("data_prevista", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("previsto", "Previsto"), ("pago", "Pago"), ("atrasado", "Atrasado")],
                        default="previsto",
                        max_length=20,
                    ),
                ),
                (
                    "orcamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pagamentos",
                        to="orcamentos.orcamento",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ItemCustoOrcamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("material", "Material"),
                            ("chapa", "Chapa"),
                            ("ferragem", "Ferragem"),
                            ("fita", "Fita"),
                            ("insumo", "Insumo"),
                            ("mao_obra", "Mao de obra"),
                            ("instalacao", "Instalacao"),
                            ("frete", "Frete"),
                            ("extra", "Extra"),
                        ],
                        max_length=30,
                    ),
                ),
                ("nome", models.CharField(max_length=180)),
                ("quantidade", models.DecimalField(decimal_places=3, default=Decimal("0.000"), max_digits=12)),
                ("unidade", models.CharField(default="unidade", max_length=30)),
                ("preco_unitario", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("preco_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("fornecedor", models.CharField(blank=True, max_length=180)),
                ("observacoes", models.TextField(blank=True)),
                (
                    "orcamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens_custo",
                        to="orcamentos.orcamento",
                    ),
                ),
            ],
        ),
    ]
