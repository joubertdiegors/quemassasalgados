from django.db import models
from products.models import Product
from datetime import date

class FinishedOrder(models.Model):
    finished_date = models.DateField(default=date.today)

    def __str__(self):
        return f'Finalizado em - {self.finished_date}'

class FinishedProduct(models.Model):
    order = models.ForeignKey(FinishedOrder, on_delete=models.CASCADE, related_name='finished_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    finished_date = models.DateField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} finalizados em {self.finished_date}'
