from django.contrib import admin
from .models import Product

class ProductAdmin(admin.TabularInline):
    model = Product
    fields = ['product', 'quantity', 'finished_date']
    search_fields = ['product__name']  # Adiciona o campo de busca pelo nome do produto

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Permite a busca pelo nome do produto

admin.site.register(Product, ProductAdmin)
