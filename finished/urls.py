from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.FinishedOrderListView.as_view(), name='finished_order_list'),
    path('<int:pk>/', views.FinishedOrderDetailView.as_view(), name='finished_order_detail'),
    path('create/', views.FinishedOrderCreateView.as_view(), name='finished_order_create'),
    path('edit/<int:pk>/', views.finished_order_update_view, name='finished_order_update'),
    path('delete/<int:pk>/', views.FinishedOrderDeleteView.as_view(), name='finished_order_delete'),

    path('upload/', views.finished_order_upload, name='finished_order_upload'),
]
