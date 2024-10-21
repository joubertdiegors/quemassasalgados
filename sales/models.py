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


class LeftoverOrder(models.Model):
    leftover_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Sobras registradas em - {self.leftover_date}'

class LeftoverProduct(models.Model):
    order = models.ForeignKey(LeftoverOrder, on_delete=models.CASCADE, related_name='leftover_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    leftover_date = models.DateField()
    restock = models.BooleanField(default=False)  # False significa não restocar

    def __str__(self):
        return f'{self.product.name} - {self.quantity} sobras em {self.leftover_date}'
    
    def save(self, *args, **kwargs):
        if self.restock:  # Somente adiciona ou remove do estoque se restock for True
            if self.pk:
                old_quantity = LeftoverProduct.objects.get(pk=self.pk).quantity
                if self.quantity > old_quantity:
                    difference = self.quantity - old_quantity
                    self.product.stock_quantity += difference
                elif self.quantity < old_quantity:
                    difference = old_quantity - self.quantity
                    self.product.stock_quantity -= difference
            else:
                self.product.stock_quantity += self.quantity

            self.product.save()

        super(LeftoverProduct, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.restock:  # Somente remove do estoque se restock for True
            self.product.stock_quantity -= self.quantity
            self.product.save()

        super(LeftoverProduct, self).delete(*args, **kwargs)

