from django.db import models
from products.models import Product
from datetime import date

class ProductionOrder(models.Model):
    order_date = models.DateField(default=date.today)

    def __str__(self):
        return f'Pedido de Produção - {self.order_date}'

class Production(models.Model):
    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='productions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    production_date = models.DateField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} produzidos em {self.production_date}'
