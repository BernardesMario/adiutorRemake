from django.contrib.auth.models import Group
from django.shortcuts import redirect


def user_group_required(group_id):
    """ Decorator para permissão de acesso em views
        baseado no Group do Usuário
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('main:login')

            group = Group.objects.get(id=group_id)
            if not request.user.groups.filter(id=group.id).exists():

                return redirect('main:handle-error')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
