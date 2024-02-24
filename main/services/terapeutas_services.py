from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpRequest
from typing import Union
from main.models import CustomUser, CadastroProfissionais


def get_terapeutas_group() -> Group:
    terapeutas_group_id = 1  # Conferir ID

    terapeutas_group = Group.objects.get(id=terapeutas_group_id)

    return terapeutas_group


def get_administrativo_group() -> Group:
    administrativo_group_id = 2  # conferir ID

    administrativo_group = Group.objects.get(id=administrativo_group_id)

    return administrativo_group


def get_current_user_terapeuta(request: HttpRequest) -> Union[CadastroProfissionais, HttpResponseNotFound]:
    """Obtem o objeto Terapeuta relacionado ao Usuário responsável pela Request
    """
    if request.user.is_authenticated:
        try:
            current_user_terapeuta = request.user.Terapeutas.get()
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Usuário não associado a um profissional Terapeuta!")

        return current_user_terapeuta
    else:
        return HttpResponseNotFound("Usuário não autenticado!")


def add_user_to_terapeuta_group(new_user: CustomUser) -> bool:
    """Associa um usuário ao grupo Terapeutas
    """
    try:
        terapeutas_group = get_terapeutas_group()
        new_user.groups.add(terapeutas_group)

        return True

    except Exception as e:
        print("Erro em add_user_to_terapeuta_group: ", str(e))
        return False


def associate_new_user_to_cadastro_profissional(new_user: CustomUser, terapeuta_form) -> bool:
    terapeuta = terapeuta_form.save(commit=False)
    try:
        terapeuta.usuario_codigo_id = new_user.id
        terapeuta.email = new_user.email
        terapeuta.telefone_numero = new_user.phone_number
        terapeuta.save()
        return True

    except Exception as e:
        print("erro em associate_new_user_to_cadastro_profissional", str(e))
        return False
