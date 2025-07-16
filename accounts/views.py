from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from website.models import SiteConfiguration

def login_by_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        profile = UserProfile.objects.filter(access_code=code).first()

        if profile:
            login(request, profile.user)

            # Redireciona se for staff
            if profile.user.is_staff or profile.user.is_superuser:
                return redirect('dashboard')

            # Se for cliente comum
            return redirect('landing')

        messages.warning(request, 'Código inválido ou sem permissão.')

    return redirect('landing')

def login_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect('dashboard')
            return redirect('landing')

        messages.error(request, 'Usuário ou senha inválidos.')

    return redirect('landing')
