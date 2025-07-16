from django.shortcuts import redirect
from django.urls import reverse
from website.models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = SiteConfiguration.get_config()
        path = request.path
        user = request.user

        if not config.maintenance_mode:
            return self.get_response(request)

        # Libera rotas específicas (admin, login, under_construction)
        allowed_paths = [
            reverse('under_construction'),
            reverse('login'),
            reverse('logout'),
        ]
        if path in allowed_paths or path.startswith('/admin'):
            return self.get_response(request)

        # STAFF (admin, gerência etc.) tem acesso total
        if user.is_authenticated and user.is_staff:
            return self.get_response(request)

        # Usuário do grupo Atendimento/Cozinha → redireciona sempre ao dashboard
        if user.is_authenticated and user.groups.filter(name__in=['Atendimento', 'Cozinha']).exists():
            if path == '/':
                return redirect('dashboard')
            return self.get_response(request)

        # Todos os outros → bloqueados
        return redirect('under_construction')
