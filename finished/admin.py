from django.contrib import admin
from .models import FinishedOrder, FinishedProduct

class FinishedProductInline(admin.TabularInline):
    model = FinishedProduct
    extra = 1  # Número de produtos adicionais para exibir por padrão no formulário
    fields = ['product', 'quantity', 'finished_date']
    search_fields = ['product__name']  # Adiciona o campo de busca pelo nome do produto

    def delete_queryset(self, request, queryset):
        # Garantir que cada FinishedProduct seja corretamente deletado
        for obj in queryset:
            obj.delete()  # Invoca o método delete customizado do model

class FinishedOrderAdmin(admin.ModelAdmin):
    inlines = [FinishedProductInline]
    list_display = ['finished_date']
    search_fields = ['finished_date']

    def delete_model(self, request, obj):
        # Certifica que o FinishedOrder e seus produtos relacionados sejam deletados corretamente
        for finished_product in obj.finished_products.all():
            finished_product.delete()  # Deleta cada produto relacionado primeiro
        obj.delete()  # Depois de deletar os produtos, deletar o pedido

    def delete_queryset(self, request, queryset):
        # Exclusão em massa: garantir que cada pedido e seus produtos relacionados sejam deletados corretamente
        for obj in queryset:
            for finished_product in obj.finished_products.all():
                finished_product.delete()  # Deleta cada produto relacionado
            obj.delete()  # Depois, deleta o pedido

admin.site.register(FinishedOrder, FinishedOrderAdmin)
admin.site.register(FinishedProduct)
