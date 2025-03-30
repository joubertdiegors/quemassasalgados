from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import UserProfile  # ajuste se estiver em outro lugar

def under_construction_view(request):
    if request.method == 'POST':
        code = request.POST.get('access_code')
        profile = UserProfile.objects.filter(access_code=code).first()

        if profile:
            login(request, profile.user)
            return redirect('dashboard')  # ou outro destino após login

        messages.warning(request, 'Código inválido ou sem permissão.')

    return render(request, 'under_construction.html')
