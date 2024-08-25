from django.urls import path
from . import views

urlpatterns = [
    path('finished/list', views.FinishedOrderListView.as_view(), name='finished_order_list'),
    path('finished/<int:pk>/', views.FinishedOrderDetailView.as_view(), name='finished_order_detail'),
    path('finished/create/', views.FinishedOrderCreateView.as_view(), name='finished_order_create'),
    path('finished/edit/<int:pk>/', views.finished_order_update_view, name='finished_order_update'),
    path('finished/delete/<int:pk>/', views.FinishedOrderDeleteView.as_view(), name='finished_order_delete'),

    path('upload/', views.finished_order_upload, name='finished_order_upload'),
]
