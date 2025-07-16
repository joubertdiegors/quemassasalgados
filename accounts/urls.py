from django.urls import path
from .views import login_by_code, login_cliente
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_by_code, name='login'),
    path('login-cliente/', login_cliente, name='login_cliente'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
