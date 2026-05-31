from rest_framework import serializers
from .models import (
    Cliente,
    ItemCustoOrcamento,
    Material,
    Orcamento,
    PagamentoSugerido,
    PecaOrcamento,
    PlanoCorte,
    Retalho,
)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = "__all__"


class RetalhoSerializer(serializers.ModelSerializer):
    material_nome = serializers.CharField(source="material.nome", read_only=True)

    class Meta:
        model = Retalho
        fields = "__all__"


class PecaOrcamentoSerializer(serializers.ModelSerializer):
    material_nome = serializers.CharField(source="material.nome", read_only=True)

    class Meta:
        model = PecaOrcamento
        fields = "__all__"


class ItemCustoOrcamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCustoOrcamento
        fields = "__all__"


class PlanoCorteSerializer(serializers.ModelSerializer):
    material_nome = serializers.CharField(source="material.nome", read_only=True)

    class Meta:
        model = PlanoCorte
        fields = "__all__"


class PagamentoSugeridoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagamentoSugerido
        fields = "__all__"


class OrcamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)
    material_principal_nome = serializers.CharField(source="material_principal.nome", read_only=True)
    material_fundo_nome = serializers.CharField(source="material_fundo.nome", read_only=True)
    pecas = PecaOrcamentoSerializer(many=True, read_only=True)
    itens_custo = ItemCustoOrcamentoSerializer(many=True, read_only=True)
    planos_corte = PlanoCorteSerializer(many=True, read_only=True)
    pagamentos = PagamentoSugeridoSerializer(many=True, read_only=True)

    class Meta:
        model = Orcamento
        fields = "__all__"
