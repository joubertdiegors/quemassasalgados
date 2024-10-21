from django.urls import path
from . import views

urlpatterns = [
    path('sales/list', views.SalesOrderListView.as_view(), name='sales_order_list'),
    path('sales/<int:pk>/', views.SalesOrderDetailView.as_view(), name='sales_order_detail'),
    path('sales/create/', views.SalesOrderCreateView.as_view(), name='sales_order_create'),
    path('sales/edit/<int:pk>/', views.sales_order_update_view, name='sales_order_update'),
    path('sales/delete/<int:pk>/', views.SalesOrderDeleteView.as_view(), name='sales_order_delete'),

    path('upload/', views.sales_order_upload, name='sales_order_upload'),

    path('leftover/list', views.LeftoverOrderListView.as_view(), name='leftover_order_list'),
    path('leftover/<int:pk>/', views.LeftoverOrderDetailView.as_view(), name='leftover_order_detail'),
    path('leftover/create/', views.LeftoverOrderCreateView.as_view(), name='leftover_order_create'),
    path('leftover/edit/<int:pk>/', views.leftover_order_update_view, name='leftover_order_update'),
    path('leftover/delete/<int:pk>/', views.LeftoverOrderDeleteView.as_view(), name='leftover_order_delete'),
]
