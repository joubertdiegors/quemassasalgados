from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
