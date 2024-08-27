from django.contrib import admin
from .models import SalesOrder, SalesProduct

class SalesProductInline(admin.TabularInline):
    model = SalesProduct
    extra = 1
    fields = ['product', 'quantity', 'sale_date']
    search_fields = ['product__name']

class SalesOrderAdmin(admin.ModelAdmin):
    inlines = [SalesProductInline]
    list_display = ['sale_date']
    search_fields = ['sale_date']

admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesProduct)
