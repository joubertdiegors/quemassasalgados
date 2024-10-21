from django.contrib import admin
from .models import SalesOrder, SalesProduct, LeftoverOrder, LeftoverProduct

class SalesProductInline(admin.TabularInline):
    model = SalesProduct
    extra = 1  # Número de produtos adicionais para exibir por padrão no formulário
    fields = ['product', 'quantity', 'sale_date']
    search_fields = ['product__name']  # Adiciona o campo de busca pelo nome do produto

class SalesOrderAdmin(admin.ModelAdmin):
    inlines = [SalesProductInline]
    list_display = ['sale_date']
    search_fields = ['sale_date']

admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesProduct)


class LeftoverProductInline(admin.TabularInline):
    model = LeftoverProduct
    extra = 1
    fields = ['product', 'quantity', 'leftover_date']
    search_fields = ['product__name']

class LeftoverOrderAdmin(admin.ModelAdmin):
    inlines = [LeftoverProductInline]
    list_display = ['leftover_date']
    search_fields = ['leftover_date']

admin.site.register(LeftoverOrder, LeftoverOrderAdmin)
admin.site.register(LeftoverProduct)