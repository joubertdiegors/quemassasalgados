from django.contrib import admin
from .models import FinishedOrder, FinishedProduct

class FinishedProductInline(admin.TabularInline):
    model = FinishedProduct
    extra = 1  # Número de produtos adicionais para exibir por padrão no formulário
    fields = ['product', 'quantity', 'finished_date']
    search_fields = ['product__name']  # Adiciona o campo de busca pelo nome do produto

class FinishedOrderAdmin(admin.ModelAdmin):
    inlines = [FinishedProductInline]
    list_display = ['finished_date']
    search_fields = ['finished_date']
    date_hierarchy = 'finished_date'

admin.site.register(FinishedOrder, FinishedOrderAdmin)
admin.site.register(FinishedProduct)
