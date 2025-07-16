from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
from django.core.exceptions import PermissionDenied

def staff_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('landing')  # redireciona para a página principal do site
    return _wrapped_view

def group_required_any(group_names):
    def check(user):
        if user.is_authenticated and user.groups.filter(name__in=group_names).exists():
            return True
        raise PermissionDenied
    return user_passes_test(check)
