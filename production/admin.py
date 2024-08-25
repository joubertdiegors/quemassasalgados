from django.contrib import admin
from .models import Production, ProductionOrder

class ProductionInline(admin.TabularInline):
    model = Production
    extra = 1

class ProductionOrderAdmin(admin.ModelAdmin):
    inlines = [ProductionInline]
    list_display = ['order_date']
    search_fields = ['order_date']

admin.site.register(ProductionOrder, ProductionOrderAdmin)
admin.site.register(Production)
