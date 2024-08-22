from django.urls import path
from . import views

urlpatterns = [
    path('product/list/', views.ProductListView.as_view(), name='product_list'),
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),
]
