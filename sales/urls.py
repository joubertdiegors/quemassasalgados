from django.urls import path
from . import views

urlpatterns = [
    path('sales/list', views.SalesOrderListView.as_view(), name='sales_order_list'),
    path('sales/<int:pk>/', views.SalesOrderDetailView.as_view(), name='sales_order_detail'),
    path('sales/create/', views.SalesOrderCreateView.as_view(), name='sales_order_create'),
    path('sales/edit/<int:pk>/', views.sales_order_update_view, name='sales_order_update'),
    path('sales/delete/<int:pk>/', views.SalesOrderDeleteView.as_view(), name='sales_order_delete'),
]
