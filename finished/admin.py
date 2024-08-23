from django.contrib import admin
from .models import FinishedOrder, FinishedProduct

admin.site.register(FinishedOrder)
admin.site.register(FinishedProduct)