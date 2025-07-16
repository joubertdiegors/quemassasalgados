from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import redirect

def custom_404(request, exception):
    return redirect('finished_order_list')

handler404 = custom_404

urlpatterns = [
    path('', include('website.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    
    path('admin/', admin.site.urls),

    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('production/', include('production.urls')),
    path('finished/', include('finished.urls')),
    path('sales/', include('sales.urls')),


]

# Servir arquivos estáticos e de mídia em modo DEBUG
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
