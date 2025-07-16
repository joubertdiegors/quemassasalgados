from django.db.models import Q
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import UserProfile
from .models import SiteConfiguration
from products.models import ProductCategory, Product, Kit

# 🔧 View de ativação/desativação do modo manutenção
@staff_member_required
def toggle_maintenance(request):
    config = SiteConfiguration.get_config()
    config.maintenance_mode = bool(request.POST.get('maintenance_mode'))
    config.save()
    return redirect(request.META.get('HTTP_REFERER', 'under_construction'))

# 🚧 Página "em construção" com login por código
def under_construction_view(request):
    config = SiteConfiguration.get_config()

    # Se o site NÃO estiver em manutenção, redireciona para o destino padrão
    if not config.maintenance_mode:
        return redirect('dashboard')  # ou outro destino público

    # Tenta login por código
    if request.method == 'POST':
        code = request.POST.get('access_code')
        profile = UserProfile.objects.filter(access_code=code).first()

        if profile:
            login(request, profile.user)
            return redirect('dashboard')

        messages.warning(request, 'Código inválido ou sem permissão.')

    return render(request, 'under_construction.html')

def landing_view(request):
    categories = ProductCategory.objects.filter(parent__isnull=True, show_on_website=True).order_by('name')
    products_by_category = {}
    
    kits = Kit.objects.filter(is_active=True, show_on_website=True).order_by('name')

    for cat in categories:
        subcats = cat.subcategories.filter(show_on_website=True).values_list('id', flat=True)
        valid_category_ids = [cat.id] + list(subcats)

        products = Product.objects.filter(
            category_id__in=valid_category_ids,
            show_on_website=True
        )

        if products.exists():
            products_by_category[cat] = products

    menu_categories = list(products_by_category.keys())
    if kits.exists():
        menu_categories.append('kits')

    return render(request, 'landing.html', {
        'products_by_category': products_by_category,
        'kits': kits,
        'menu_categories': menu_categories,
    })
