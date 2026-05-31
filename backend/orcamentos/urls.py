from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orcamentos.views import (
    ClienteViewSet,
    ItemCustoOrcamentoViewSet,
    MaterialViewSet,
    OrcamentoViewSet,
    PagamentoSugeridoViewSet,
    PecaOrcamentoViewSet,
    RetalhoViewSet,
    dashboard,
)

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="clientes")
router.register("materiais", MaterialViewSet, basename="materiais")
router.register("retalhos", RetalhoViewSet, basename="retalhos")
router.register("orcamentos", OrcamentoViewSet, basename="orcamentos")
router.register("pecas-orcamento", PecaOrcamentoViewSet, basename="pecas-orcamento")
router.register("itens-custo", ItemCustoOrcamentoViewSet, basename="itens-custo")
router.register("pagamentos", PagamentoSugeridoViewSet, basename="pagamentos")

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("", include(router.urls)),
]
