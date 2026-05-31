from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from orcamentos.models import (
    Cliente,
    ItemCustoOrcamento,
    Material,
    Orcamento,
    PagamentoSugerido,
    PecaOrcamento,
    PlanoCorte,
    Retalho,
)
from orcamentos.serializers import (
    ClienteSerializer,
    ItemCustoOrcamentoSerializer,
    MaterialSerializer,
    OrcamentoSerializer,
    PagamentoSugeridoSerializer,
    PecaOrcamentoSerializer,
    PlanoCorteSerializer,
    RetalhoSerializer,
)
from orcamentos.services.calculo_orcamento import calcular_orcamento_completo
from orcamentos.services.gerador_pecas import gerar_pecas_automaticas
from orcamentos.services.pdf_service import gerar_pdf_cliente, gerar_pdf_tecnico


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("-data_criacao")
    serializer_class = ClienteSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by("nome")
    serializer_class = MaterialSerializer


class RetalhoViewSet(viewsets.ModelViewSet):
    queryset = Retalho.objects.select_related("material").all().order_by("-data_cadastro")
    serializer_class = RetalhoSerializer


class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.select_related("cliente", "material_principal", "material_fundo").all().order_by(
        "-data_criacao"
    )
    serializer_class = OrcamentoSerializer

    @action(detail=True, methods=["post"])
    def calcular(self, request, pk=None):
        orcamento = self.get_object()
        resultado = calcular_orcamento_completo(orcamento)
        return Response(resultado)

    @action(detail=True, methods=["post"])
    def gerar_pecas(self, request, pk=None):
        orcamento = self.get_object()
        pecas = gerar_pecas_automaticas(orcamento)
        return Response({"pecas": pecas})

    @action(detail=True, methods=["get"])
    def plano_corte(self, request, pk=None):
        orcamento = self.get_object()
        planos = PlanoCorte.objects.filter(orcamento=orcamento)
        serializer = PlanoCorteSerializer(planos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def duplicar(self, request, pk=None):
        original = self.get_object()
        original.pk = None
        original.status = Orcamento.Status.RASCUNHO
        original.resultado_calculo = {}
        original.nota_confianca = 100
        original.data_ultima_calculacao = None
        original.nome_projeto = f"{original.nome_projeto} (Copia)"
        original.save()
        return Response(OrcamentoSerializer(original).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        orcamento = self.get_object()
        orcamento.status = Orcamento.Status.APROVADO
        orcamento.save(update_fields=["status"])
        return Response({"status": "aprovado"})

    @action(detail=True, methods=["post"])
    def recusar(self, request, pk=None):
        orcamento = self.get_object()
        orcamento.status = Orcamento.Status.RECUSADO
        orcamento.save(update_fields=["status"])
        return Response({"status": "recusado"})

    @action(detail=True, methods=["get"])
    def pdf_cliente(self, request, pk=None):
        orcamento = self.get_object()
        resultado = orcamento.resultado_calculo or {}
        pdf_bytes = gerar_pdf_cliente(orcamento, resultado)
        return FileResponse(
            BytesIO(pdf_bytes),
            content_type="application/pdf",
            filename=f"orcamento_cliente_{orcamento.id}.pdf",
            as_attachment=True,
        )

    @action(detail=True, methods=["get"])
    def pdf_tecnico(self, request, pk=None):
        orcamento = self.get_object()
        resultado = orcamento.resultado_calculo or {}
        pdf_bytes = gerar_pdf_tecnico(orcamento, resultado)
        return FileResponse(
            BytesIO(pdf_bytes),
            content_type="application/pdf",
            filename=f"orcamento_tecnico_{orcamento.id}.pdf",
            as_attachment=True,
        )


class PecaOrcamentoViewSet(viewsets.ModelViewSet):
    queryset = PecaOrcamento.objects.select_related("orcamento", "material").all()
    serializer_class = PecaOrcamentoSerializer


class ItemCustoOrcamentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ItemCustoOrcamento.objects.select_related("orcamento").all()
    serializer_class = ItemCustoOrcamentoSerializer


class PagamentoSugeridoViewSet(viewsets.ModelViewSet):
    queryset = PagamentoSugerido.objects.select_related("orcamento").all()
    serializer_class = PagamentoSugeridoSerializer


@api_view(["GET"])
def dashboard(request):
    total = Orcamento.objects.count()
    rascunho = Orcamento.objects.filter(status=Orcamento.Status.RASCUNHO).count()
    calculado = Orcamento.objects.filter(status=Orcamento.Status.CALCULADO).count()
    aprovado = Orcamento.objects.filter(status=Orcamento.Status.APROVADO).count()

    faturamento = Decimal("0")
    lucro = Decimal("0")
    for orcamento in Orcamento.objects.all():
        financeiro = (orcamento.resultado_calculo or {}).get("financeiro", {})
        faturamento += Decimal(str(financeiro.get("preco_final", 0)))
        lucro += Decimal(str(financeiro.get("lucro_estimado", 0)))

    return Response(
        {
            "quantidade_orcamentos": total,
            "orcamentos_rascunho": rascunho,
            "orcamentos_calculados": calculado,
            "orcamentos_aprovados": aprovado,
            "faturamento_potencial": float(faturamento.quantize(Decimal("0.01"))),
            "lucro_estimado_potencial": float(lucro.quantize(Decimal("0.01"))),
        }
    )
