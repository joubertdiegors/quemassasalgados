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
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_quantity = Production.objects.get(pk=self.pk).quantity

            if self.quantity > old_quantity:
                difference = self.quantity - old_quantity
                self.product.stock_quantity += difference
            elif self.quantity < old_quantity:
                difference = old_quantity - self.quantity
                self.product.stock_quantity -= difference
        else:
            self.product.stock_quantity += self.quantity

        self.product.save()
        super(Production, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Subtrair a quantidade do estoque ao deletar
        self.product.stock_quantity -= self.quantity
        self.product.save()
        super(Production, self).delete(*args, **kwargs)
