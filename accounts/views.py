from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile

def login_by_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        profile = UserProfile.objects.filter(access_code=code).first()

        if profile:
            login(request, profile.user)
            return redirect('dashboard')

        messages.error(request, 'Invalid access code.')

    return render(request, 'registration/login.html')
