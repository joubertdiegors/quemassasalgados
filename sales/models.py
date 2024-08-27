from django.db import models
from products.models import Product
from django.utils import timezone

class SalesOrder(models.Model):
    sale_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Sale Order - {self.sale_date}'

class SalesProduct(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='sales_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_date = models.DateField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} vendidos em {self.sale_date}'

    def save(self, *args, **kwargs):
        if self.pk:
            old_quantity = SalesProduct.objects.get(pk=self.pk).quantity

            if self.quantity > old_quantity:
                difference = self.quantity - old_quantity
                self.product.stock_quantity -= difference
            elif self.quantity < old_quantity:
                difference = old_quantity - self.quantity
                self.product.stock_quantity += difference
        else:
            self.product.stock_quantity -= self.quantity

        self.product.save()
        super(SalesProduct, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.product.stock_quantity += self.quantity
        self.product.save()
        super(SalesProduct, self).delete(*args, **kwargs)
