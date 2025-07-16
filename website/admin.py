from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['maintenance_mode']

    def has_add_permission(self, request):
        # Impede criar se já existir uma configuração
        return not SiteConfiguration.objects.exists()
