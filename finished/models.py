from django.db import models
from products.models import Product
from django.utils import timezone

class FinishedOrder(models.Model):
    finished_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Finalizado em - {self.finished_date}'

class FinishedProduct(models.Model):
    order = models.ForeignKey(FinishedOrder, on_delete=models.CASCADE, related_name='finished_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    finished_date = models.DateField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} finalizados em {self.finished_date}'
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_quantity = FinishedProduct.objects.get(pk=self.pk).quantity

            if self.quantity > old_quantity:
                difference = self.quantity - old_quantity
                self.product.stock_quantity -= difference
            elif self.quantity < old_quantity:
                difference = old_quantity - self.quantity
                self.product.stock_quantity += difference
        else:
            self.product.stock_quantity -= self.quantity

        self.product.save()
        super(FinishedProduct, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Devolver a quantidade ao estoque ao deletar
        self.product.stock_quantity += self.quantity
        self.product.save()
        super(FinishedProduct, self).delete(*args, **kwargs)
