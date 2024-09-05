from django.db import models
from products.models import Product
from django.utils import timezone

class SalesOrder(models.Model):
    sale_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Vendido em - {self.sale_date}'

class SalesProduct(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='sales_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_date = models.DateField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} vendidos em {self.sale_date}'
