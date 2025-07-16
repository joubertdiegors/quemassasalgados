from django.contrib import admin
from .models import Product, ProductCategory, Kit, KitOption
from django_ckeditor_5.fields import CKEditor5Field
from django_ckeditor_5.widgets import CKEditor5Widget

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'stock_quantity', 'minimum_stock', 'show_on_website', 'use_in_production']
    search_fields = ['name']
    list_filter = ['category', 'show_on_website', 'use_in_production']
    autocomplete_fields = ['category']
    readonly_fields = ['stock_quantity']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'show_on_website']
    search_fields = ['name']
    list_filter = ['show_on_website']
    autocomplete_fields = ['parent']

class KitOptionInline(admin.TabularInline):
    model = KitOption
    extra = 1
    autocomplete_fields = ['category']

@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    inlines = [KitOptionInline]
    formfield_overrides = {
        CKEditor5Field: {'widget': CKEditor5Widget},
    }
    actions = ['duplicate_kit']

    def duplicate_kit(self, request, queryset):
        for kit in queryset:
            original_options = kit.options.all()

            # Cria o novo kit (sem imagem)
            new_kit = Kit.objects.create(
                name=f"{kit.name} (Cópia)",
                description=kit.description,
                is_active=kit.is_active,
                show_on_website=kit.show_on_website,
            )

            # Duplica as opções do kit
            for option in original_options:
                KitOption.objects.create(
                    kit=new_kit,
                    category=option.category,
                    max_choices=option.max_choices
                )

        self.message_user(request, "Kits duplicados com sucesso!")

    duplicate_kit.short_description = "Duplicar kits selecionados"
