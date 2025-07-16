from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.CASCADE
    )
    show_on_website = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_full_path()

    def get_full_path(self):
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    minimum_stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    show_on_website = models.BooleanField(default=False)
    use_in_production = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Kit(models.Model):
    name = models.CharField(max_length=100)
    description = CKEditor5Field('Descrição', config_name='default')
    image = models.ImageField(upload_to='kits/')
    is_active = models.BooleanField(default=True)
    show_on_website = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class KitOption(models.Model):
    kit = models.ForeignKey(Kit, related_name='options', on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    max_choices = models.PositiveIntegerField(help_text="Quantos itens dessa categoria o cliente pode escolher.")

    def __str__(self):
        return f"{self.kit.name} - {self.category.get_full_path()} (até {self.max_choices})"
