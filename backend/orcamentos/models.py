from decimal import Decimal
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(max_length=180)
    telefone = models.CharField(max_length=40, blank=True)
    endereco = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nome


class Material(models.Model):
    class Tipo(models.TextChoices):
        MDF = "mdf", "MDF"
        COMPENSADO = "compensado", "Compensado"
        MADEIRA = "madeira", "Madeira"
        FITA_BORDA = "fita_borda", "Fita de borda"
        FERRAGEM = "ferragem", "Ferragem"
        INSUMO = "insumo", "Insumo"
        SERVICO = "servico", "Servico"
        OUTRO = "outro", "Outro"

    class Unidade(models.TextChoices):
        CHAPA = "chapa", "Chapa"
        METRO = "metro", "Metro"
        UNIDADE = "unidade", "Unidade"
        PAR = "par", "Par"
        DIARIA = "diaria", "Diaria"
        CONJUNTO = "conjunto", "Conjunto"
        PACOTE = "pacote", "Pacote"

    class PadraoVisual(models.TextChoices):
        LISO = "liso", "Liso"
        MADEIRADO = "madeirado", "Madeirado"
        OUTRO = "outro", "Outro"

    class SentidoVeio(models.TextChoices):
        VERTICAL = "vertical", "Vertical"
        HORIZONTAL = "horizontal", "Horizontal"
        INDIFERENTE = "indiferente", "Indiferente"

    nome = models.CharField(max_length=180)
    tipo = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.MDF)
    espessura_mm = models.PositiveIntegerField(default=0)
    largura_mm = models.PositiveIntegerField(default=0)
    altura_mm = models.PositiveIntegerField(default=0)
    unidade = models.CharField(max_length=30, choices=Unidade.choices, default=Unidade.UNIDADE)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    fornecedor = models.CharField(max_length=180, blank=True)
    padrao_visual = models.CharField(max_length=30, choices=PadraoVisual.choices, default=PadraoVisual.LISO)
    permite_rotacao_padrao = models.BooleanField(default=True)
    sentido_veio = models.CharField(max_length=30, choices=SentidoVeio.choices, default=SentidoVeio.INDIFERENTE)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nome


class Retalho(models.Model):
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="retalhos")
    largura_mm = models.PositiveIntegerField()
    altura_mm = models.PositiveIntegerField()
    origem = models.CharField(max_length=180, blank=True)
    observacoes = models.TextField(blank=True)
    disponivel = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.material.nome} ({self.largura_mm}x{self.altura_mm})"


class Orcamento(models.Model):
    class TipoMovel(models.TextChoices):
        GUARDA_ROUPA = "guarda_roupa", "Guarda-roupa"
        PAINEL_TV = "painel_tv", "Painel de TV com rack"
        ARMARIO_AEREO = "armario_aereo", "Armario aereo"
        OUTRO = "outro", "Outro"

    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        CALCULADO = "calculado", "Calculado"
        ENVIADO = "enviado", "Enviado"
        APROVADO = "aprovado", "Aprovado"
        RECUSADO = "recusado", "Recusado"

    class TipoPorta(models.TextChoices):
        ABRIR = "abrir", "Abrir"
        CORRER = "correr", "Correr"
        BASCULANTE = "basculante", "Basculante"
        NENHUMA = "nenhuma", "Nenhuma"

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="orcamentos")
    nome_projeto = models.CharField(max_length=180)
    tipo_movel = models.CharField(max_length=30, choices=TipoMovel.choices, default=TipoMovel.OUTRO)
    largura_mm = models.PositiveIntegerField(default=0)
    altura_mm = models.PositiveIntegerField(default=0)
    profundidade_mm = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    material_principal = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name="orcamentos_principais", null=True, blank=True
    )
    material_fundo = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name="orcamentos_fundo", null=True, blank=True
    )
    quantidade_portas = models.PositiveIntegerField(default=0)
    tipo_porta = models.CharField(max_length=20, choices=TipoPorta.choices, default=TipoPorta.NENHUMA)
    quantidade_gavetas = models.PositiveIntegerField(default=0)
    quantidade_prateleiras = models.PositiveIntegerField(default=0)
    quantidade_divisorias = models.PositiveIntegerField(default=0)
    quantidade_cabideiros = models.PositiveIntegerField(default=0)
    portas_basculantes = models.PositiveIntegerField(default=0)
    quantidade_nichos = models.PositiveIntegerField(default=0)
    usar_retalhos = models.BooleanField(default=False)
    kerf_mm = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("3.00"))
    perda_tecnica_percentual = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("10.00"))
    margem_desejada_percentual = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("35.00"))
    valor_mao_obra = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    quantidade_diarias = models.PositiveIntegerField(default=0)
    valor_diaria = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    valor_instalacao = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    valor_frete = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    custos_extras = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    preco_final_manual = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    validade_dias = models.PositiveIntegerField(default=15)
    mostrar_detalhamento_pdf_cliente = models.BooleanField(default=False)
    resultado_calculo = models.JSONField(default=dict, blank=True)
    nota_confianca = models.PositiveIntegerField(default=100)
    data_ultima_calculacao = models.DateTimeField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nome_projeto


class PecaOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="pecas")
    nome = models.CharField(max_length=180)
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="pecas_orcamento")
    largura_mm = models.PositiveIntegerField()
    altura_mm = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField(default=1)
    espessura_mm = models.PositiveIntegerField(default=0)
    pode_rotacionar = models.BooleanField(default=True)
    fita_topo = models.BooleanField(default=False)
    fita_baixo = models.BooleanField(default=False)
    fita_esquerda = models.BooleanField(default=False)
    fita_direita = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.nome} ({self.largura_mm}x{self.altura_mm})"


class ItemCustoOrcamento(models.Model):
    class Categoria(models.TextChoices):
        MATERIAL = "material", "Material"
        CHAPA = "chapa", "Chapa"
        FERRAGEM = "ferragem", "Ferragem"
        FITA = "fita", "Fita"
        INSUMO = "insumo", "Insumo"
        MAO_OBRA = "mao_obra", "Mao de obra"
        INSTALACAO = "instalacao", "Instalacao"
        FRETE = "frete", "Frete"
        EXTRA = "extra", "Extra"

    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="itens_custo")
    categoria = models.CharField(max_length=30, choices=Categoria.choices)
    nome = models.CharField(max_length=180)
    quantidade = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.000"))
    unidade = models.CharField(max_length=30, default="unidade")
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    preco_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    fornecedor = models.CharField(max_length=180, blank=True)
    observacoes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.nome} - {self.preco_total}"


class PlanoCorte(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="planos_corte")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="planos_corte")
    quantidade_chapas = models.PositiveIntegerField(default=0)
    aproveitamento_percentual = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    perda_percentual = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    area_total_pecas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    area_total_chapas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    resultado_json = models.JSONField(default=dict, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)


class PagamentoSugerido(models.Model):
    class Status(models.TextChoices):
        PREVISTO = "previsto", "Previsto"
        PAGO = "pago", "Pago"
        ATRASADO = "atrasado", "Atrasado"

    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="pagamentos")
    descricao = models.CharField(max_length=180)
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    data_prevista = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PREVISTO)

    def __str__(self) -> str:
        return f"{self.descricao} - {self.valor}"
