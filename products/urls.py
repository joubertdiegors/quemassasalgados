from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('edit/<int:pk>/', views.ProductUpdateView.as_view(), name='product_edit'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categorias/<int:pk>/excluir/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    path('kits/', views.KitListView.as_view(), name='kit_list'),
    path('kits/create/', views.KitCreateView.as_view(), name='kit_create'),
    path('kits/<int:pk>/edit/', views.KitUpdateView.as_view(), name='kit_update'),
    path('kits/<int:pk>/duplicar/', views.duplicate_kit, name='kit_duplicate'),
]
