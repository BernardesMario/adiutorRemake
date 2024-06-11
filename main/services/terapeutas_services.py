from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpRequest
from typing import Union, List
from main.models import (CustomUser, CadastroProfissionais, ProntuariosIndividuais, HistoricoAcademico,
                         ProfissionaisMedia)
from datetime import date
from django.db.models.query import QuerySet


def get_terapeutas_group() -> Group:

    terapeutas_group = Group.objects.get(name='Terapeutas')

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
    terapeuta_group = get_terapeutas_group()
    try:
        terapeuta.usuario_codigo_id = new_user.id
        terapeuta.email = new_user.email
        terapeuta.telefone_numero = new_user.phone_number
        new_user.groups.add(terapeuta_group)
        terapeuta.save()
        return True

    except Exception as e:
        print("erro em associate_new_user_to_cadastro_profissional", str(e))
        return False


def producao_generator(current_terapeuta: CadastroProfissionais, data_inicial: date,
                       data_final: Union[date, None]) -> QuerySet:
    """ Faz uma Query de todas as consultas registradas por determinado terapeuta
    dentro de um espaço de tempo
    """

    if not data_final:
        data_final = date.today()

    producao = ProntuariosIndividuais.objects.filter(data_consulta__gte=data_inicial,
                                                     data_consulta__lte=data_final,
                                                     autor=current_terapeuta)

    return producao


def producao_detalhamento(producao: QuerySet) -> dict:
    """
    Gera um dict onde as keys são Pacientes, e valores são dict contendo os detalhes do paciente
    e uma listagem de consultas para cada paciente
    """
    results_dict = {}

    for atendimento in producao:
        current_paciente = atendimento.numero
        consulta_dict = {
            'consulta_data': atendimento.data_consulta,
            'entrada_data': atendimento.data_entrada,
        }

        if current_paciente.nome not in results_dict:
            results_dict[current_paciente.nome] = {
                'consulta_paciente': current_paciente.nome,
                'consulta_convênio': current_paciente.convenio,
                'convenio_identificador': current_paciente.carteirinha_convenio,
                'consultas': [consulta_dict]
            }
        else:
            results_dict[current_paciente.nome]['consultas'].append(consulta_dict)

    return results_dict


def get_terapeuta_by_codigo(terapeuta_codigo: str) -> CadastroProfissionais:

    terapeuta = CadastroProfissionais.objects.get(conselho_codigo=terapeuta_codigo)

    return terapeuta


def get_terapeuta_historico_academico(terapeuta: CadastroProfissionais) -> QuerySet:

    historico_academico = HistoricoAcademico.objects.filter(terapeuta=terapeuta)

    return historico_academico


def get_current_terapeuta_pdf_media(current_terapeuta: CadastroProfissionais) -> QuerySet:

    terapeuta_pdf_media = ProfissionaisMedia.objects.filter(terapeuta=current_terapeuta).exclude(pdf_file='n/d')

    return terapeuta_pdf_media


def get_current_terapeuta_image_media(current_terapeuta: CadastroProfissionais) -> QuerySet:

    terapeuta_image_media = ProfissionaisMedia.objects.filter(terapeuta=current_terapeuta).exclude(image_file='n/d')

    return terapeuta_image_media


def get_terapeuta_by_user(user: CustomUser) -> CadastroProfissionais:

    terapeuta = CadastroProfissionais.objects.get(usuario_codigo=user)

    return terapeuta
