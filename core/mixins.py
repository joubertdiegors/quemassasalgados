from django.contrib import messages
from django.shortcuts import redirect

class CustomPermissionDeniedMixin:
    """
    Mixin para exibir uma mensagem personalizada ao usuário quando ele
    não tem permissão para acessar a view.
    """
    permission_denied_message = "Você não tem permissão para acessar esta página."
    redirect_url = None  # Define isso na view ou ela tenta voltar para a página anterior

    def handle_no_permission(self):
        messages.warning(self.request, self.permission_denied_message)
        return redirect(
            self.redirect_url or self.request.META.get('HTTP_REFERER', '/')
        )
