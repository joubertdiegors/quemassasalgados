from django.db import models

class SiteConfiguration(models.Model):
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return "Configurações do Site"

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"

    @classmethod
    def get_config(cls):
        return cls.objects.first() or cls.objects.create()