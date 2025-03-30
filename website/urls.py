from django.urls import path
from .views import under_construction_view

urlpatterns = [
    path('', under_construction_view, name='under_construction'),
]
