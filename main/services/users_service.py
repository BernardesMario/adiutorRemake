from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from main.models import CadastroProfissionais


def redirect_logged_user_to_home(current_user, terapeutas_group: Group, administrativo_group: Group):
    """Redireciona o usuário para sua respectiva área inicial conforme seu grupo.
    """
    if terapeutas_group in current_user.groups.all():
        return redirect('/main/index/')
    elif administrativo_group in current_user.groups.all():
        return redirect('/main/administrativo/')
    else:
        return redirect_to_error_page()


def redirect_user_to_otp_confirmation(current_user):
    current_user_email = current_user.email
    return redirect('/accounts/login-with-otp/?email=' + current_user_email)


def redirect_to_error_page():
    """ Pagina de erro para login
    """
    error_message = "Algo deu errado! Entre em contato com a administração!\nErro: Grupo Inválido"
    return HttpResponseForbidden(error_message)


# redundante = terapeutas_services
def get_current_user_terapeuta_id(request):
    """ Associa o usuário logado ao seu cadastro de Terapeuta
    """
    try:
        current_user = request.user
        current_user_terapeuta = CadastroProfissionais.objects.get(usuario_codigo=current_user)
        terapeuta_id = current_user_terapeuta.id

        return terapeuta_id

    except ObjectDoesNotExist:
        error_message = str("Algo deu errado!\nO usuário atual não possui atribuições de Terapeuta!")
        return HttpResponseForbidden(error_message)
