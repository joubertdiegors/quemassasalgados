from django.urls import path
from . import views

urlpatterns = [
    path('order/list/', views.ProductionOrderListView.as_view(), name='production_order_list'),
    path('order/<int:pk>/', views.ProductionOrderDetailView.as_view(), name='production_order_detail'),
    path('order/create/', views.ProductionOrderCreateView.as_view(), name='production_order_create'),
    path('order/edit/<int:pk>/', views.production_order_update_view, name='production_order_update'),
    path('order/delete/<int:pk>/', views.ProductionOrderDeleteView.as_view(), name='production_order_delete'),
]
