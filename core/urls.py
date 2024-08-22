from django.contrib import admin
from django.urls import path, include

from django.conf.urls import handler404
from django.shortcuts import redirect

def custom_404(request, exception):
    return redirect('finished_order_list')

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('products.urls')),
    path('', include('production.urls')),
    path('', include('finished.urls')),
]
