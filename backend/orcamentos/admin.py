from django.contrib import admin
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


admin.site.register(Cliente)
admin.site.register(Material)
admin.site.register(Retalho)
admin.site.register(Orcamento)
admin.site.register(PecaOrcamento)
admin.site.register(ItemCustoOrcamento)
admin.site.register(PlanoCorte)
admin.site.register(PagamentoSugerido)
