from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ProductionOrderListView.as_view(), name='production_order_list'),
    path('<int:pk>/', views.ProductionOrderDetailView.as_view(), name='production_order_detail'),
    path('create/', views.ProductionOrderCreateView.as_view(), name='production_order_create'),
    path('edit/<int:pk>/', views.production_order_update_view, name='production_order_update'),
    path('delete/<int:pk>/', views.ProductionOrderDeleteView.as_view(), name='production_order_delete'),
]
