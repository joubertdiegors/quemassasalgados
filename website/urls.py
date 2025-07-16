from django.urls import path
from .views import landing_view, under_construction_view, toggle_maintenance

urlpatterns = [
    path('', landing_view, name='landing'),

    path('under_construction/', under_construction_view, name='under_construction'),
    path('toggle-maintenance/', toggle_maintenance, name='toggle_maintenance'),
]
