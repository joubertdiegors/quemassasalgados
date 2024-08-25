from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name']  # Permite a busca pelo nome do produto

admin.site.register(Product, ProductAdmin)
