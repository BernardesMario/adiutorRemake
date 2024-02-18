from django.db.models import Q
from datetime import date
from main.models import CadastroGrupos, CadastroPacientes, Prontuarios, ProntuariosGrupos, PresencasGrupo
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from main.utils import get_selected_items


def get_selected_pacientes(selected_items):
    """ Retorna os pacientes selecionados em um Request"""
    selected_pacs = CadastroPacientes.objects.filter(id__in=selected_items)

    return selected_pacs


def registro_pacs_add_grp(request, current_group, current_user_terapeuta, data_grupo):
    """ Cria um registro no prontuário individual de um paciente que foi
    adicionado a um grupo"""
    selected_items = get_selected_items(request)
    pacs_add = get_selected_pacientes(selected_items)
    grupo_add = current_group

    for paciente in pacs_add:
        grupo = grupo_add
        entrada_prontuario_individual = Prontuarios(
            numero=paciente,
            autor=current_user_terapeuta,
            data_consulta=data_grupo,
            entrada=str(f"Paciente {paciente.nome}  foi adicionado ao grupo {current_group.label} "
                        f" {grupo.prontuario_grupo_numero} por {current_user_terapeuta} em {data_grupo}.")
        )
        entrada_prontuario_individual.save()


def filter_active_pacs():
    """ Filtrar todos Pacientes ativos
    """
    active_pacientes = CadastroPacientes.objects.filter(desligado=False)
    return active_pacientes


def filter_inactive_pacs():
    """ Filtrar todos Pacientes inativos
    """
    inactive_pacientes = CadastroPacientes.objects.filter(desligado=True)
    return inactive_pacientes


def filter_active_grupos():
    """ Filtrar todos Grupos ativos
    """
    active_groups = CadastroGrupos.objects.filter(desligado=False)
    return active_groups


def filter_inactive_grupos():
    """ Filtrar todos Grupos inativos
    """
    inactive_groups = CadastroGrupos.objects.filter(desligado=True)
    return inactive_groups


def filter_active_pacs_by_terapeuta(terapeuta_id):
    """ Filtrar pacientes ativos por terapeuta
    """
    active_pacs_terapeuta = CadastroPacientes.objects.filter(terapeuta=terapeuta_id, desligado=False)

    return active_pacs_terapeuta


def filter_inactive_pacs_by_terapeuta(terapeuta_id):
    """ Filtrar pacientes inativos por terapeuta
    """
    inactive_pacs_terapeuta = CadastroPacientes.objects.filter(terapeuta=terapeuta_id, desligado=True)

    return inactive_pacs_terapeuta


def filter_active_grps_by_terapeuta(terapeuta_id):
    """ Filtrar grupos ativos por terapeuta ou terapeuta auxiliar
    """
    active_grps_terapeuta = CadastroGrupos.objects.filter(
        Q(terapeuta_responsavel=terapeuta_id) | Q(terapeuta_auxiliar=terapeuta_id),
        desligado=False)

    return active_grps_terapeuta


def filter_inactive_grps_by_terapeuta(terapeuta_id):
    """ Filtrar grupos ativos por terapeuta ou terapeuta auxiliar
    """
    inactive_grps_terapeuta = CadastroGrupos.objects.filter(
        Q(terapeuta_responsavel=terapeuta_id) | Q(terapeuta_auxiliar=terapeuta_id),
        desligado=True)

    return inactive_grps_terapeuta


def get_current_pac(prontuario_numero) -> CadastroPacientes:
    """ Retorna um objeto "Paciente" da model CadastroPacientes
    baseado no numero de Prontuario
    """
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)

    return current_paciente


def get_current_pac_prontuario(prontuario_numero):
    """ Retorna um objeto "Prontuario" da model Prontuarios
    baseado no numero do prontuario
    """
    current_paciente_prontuario = Prontuarios.objects.filter(numero_id=prontuario_numero).order_by('-data_consulta')

    return current_paciente_prontuario


def get_current_group(prontuario_grupo_numero) -> CadastroGrupos:
    """ Retorna um objeto "Grupo" da model CadastroGrupos
    baseado no número de prontuario do grupo
    """
    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)

    return current_grupo


def get_current_group_prontuario(prontuario_grupo_numero):
    """Retorna um objeto "Prontuario" da model ProntuariosGrupo
    baseado no numerp do prontuario"""
    current_grupo_prontuario = ProntuariosGrupos.objects.filter(numero_id=prontuario_grupo_numero)

    return current_grupo_prontuario


def get_ultima_entrada_prontuarios_grupos(prontuario_grupo_numero):
    """Obtem a data da ultima entrada no prontuario de um Grupo,
    caso exista, através do numero de prontuario
    """
    current_grupo = get_current_group(prontuario_grupo_numero)

    ultima_entrada = ProntuariosGrupos.objects.filter(
        numero=current_grupo.prontuario_grupo_numero
    ).order_by('-data_consulta').first()

    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None

    return ultima_entrada_data


def date_validator_entrada_prontuario_grupo(prontuario_grupo_numero: str, entrada_form):
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de grupos não é anterior a data da última consulta registrada
    """
    data_nova_entrada = entrada_form.cleaned_data['data_consulta']

    if not is_data_nova_consulta_group_valid(prontuario_grupo_numero, data_nova_entrada):
        entrada_form.add_error('data_consulta', 'O paciente possui consultas posteriores a data informada!')


def is_data_nova_consulta_group_valid(prontuario_grupo_numero: str, data_nova_entrada):
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de grupos não é anterior a data da última consulta registrada
    """
    ultima_entrada_data = get_ultima_entrada_prontuarios_grupos(prontuario_grupo_numero)

    if not ultima_entrada_data:
        return True

    is_valid = data_nova_entrada > ultima_entrada_data

    return is_valid


def get_ultima_entrada_prontuarios_pacs(current_pac):
    """Obtem a data da ultima entrada no prontuario de um paciente individual,
    caso exista, através do numero de prontuario
    """

    ultima_entrada = Prontuarios.objects.filter(
        numero=current_pac.prontuario_numero
    ).order_by('-data_consulta').first()

    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None

    return ultima_entrada_data


# entrada_prontuario_grupo_form.py
def date_validator_entrada_prontuario_pacs(current_pac: CadastroPacientes, entrada_form):
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de grupos não é anterior a data da última consulta registrada
    """
    data_nova_entrada = entrada_form.cleaned_data['data_consulta']

    if is_data_nova_consulta_valid(current_pac, data_nova_entrada):
        entrada_form.add_error('data_consulta', 'O paciente possui consultas posteriores a data informada!')
        # TODO: remove boolean return, since the form method will raise an exception
        return False

    # TODO: remove boolean return, since the form method will raise an exception
    return True

# paciente_service.py
def is_data_nova_consulta_valid(current_pac: CadastroPacientes, data_nova_consulta) -> bool:
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de grupos não é anterior a data da última consulta registrada
    """
    ultima_entrada_data = get_ultima_entrada_prontuarios_pacs(current_pac)

    is_valid = ultima_entrada_data and data_nova_consulta < ultima_entrada_data
    return is_valid


def save_desligamento(current_pac):
    """Desliga um paciente
    """
    current_pac.desligado = True
    current_pac.save()


def desligamento_registro_prontuario(current_user_terapeuta, current_pac, desligamento_form):
    """ Cria um registro do desligamento no Prontuario de um paciente indiviual
    """
    entrada_text = desligamento_form.cleaned_data.get('entrada_text')
    data_final = desligamento_form.cleaned_data.get('data_final')

    Prontuarios.objects.create(numero=current_pac.prontuario_numero,
                               autor=current_user_terapeuta,
                               data_consulta=data_final,
                               entrada=f"Paciente {current_pac.nome} foi desligado por "
                                       f"{current_user_terapeuta}"
                                       f" em {data_final}. "
                                       f"\n Motivo: {entrada_text}", )


def get_pacs_grp(current_grp):
    """ Obtém todos os pacientes ativos que fazem parte de um determinado grupo"""
    pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=current_grp.id, desligado=False)

    return pacientes_grupo


def save_desligamento_grp(current_grp, desligamento_form):
    """ Desliga um determinado grupo"""

    data_final = desligamento_form.cleaned_data.get('data_final')
    current_grp.desligado = True
    current_grp.data_final = data_final

    current_grp.save()

    return current_grp


def registro_desligamento_grupos(pacientes_grupo, current_grp, desligamento_form, current_user_terapeuta):
    """Cria um registro de desligamento do grupo no Prontuário individuaol
    dos participantes
    """

    entrada_text = desligamento_form.cleaned_data.get('entrada_text')
    data_final = desligamento_form.cleaned_data.get('data_final')

    for paciente in pacientes_grupo:
        Prontuarios.objects.create(numero=paciente,
                                   autor=current_user_terapeuta,
                                   data_consulta=data_final,
                                   entrada=f"Grupo {current_grp.label} "
                                           f"prontuário {current_grp.prontuario_grupo_numero} "
                                           f"foi desligado por {current_user_terapeuta} "
                                           f"em {data_final}."
                                           f"\n Motivo: {entrada_text}", )
    return pacientes_grupo


def registro_transferencia_pac(current_pac, transfer_form, current_user_terapeuta):
    """ Cria uma registro de transferencia no prontuario de pacientes individuais
    """

    entrada_text = transfer_form.cleaned_data.get('entrada_text')
    novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']
    data_transfer = date.today()

    Prontuarios.objects.create(numero=current_pac.prontuario_numero,
                               autor=current_user_terapeuta,
                               data_consulta=data_transfer,
                               entrada=f"Paciente {current_pac.nome} foi transferido por "
                                       f"{current_user_terapeuta} para {novo_terapeuta} em {data_transfer}."
                                       f"\n Motivo: {entrada_text}", )


def relig_pacs(current_pac, relig_form):
    """ Reativa um paciente que retornou para atendimento
    """

    novo_terapeuta = relig_form.cleaned_data['novo_terapeuta']

    current_pac.terapeuta = novo_terapeuta
    current_pac.desligado = False
    current_pac.modalidade_atendimento = 0
    current_pac.save()


def registro_relig_pac(current_pac, relig_form):
    """Cria um registro no prontuario de um paciente que está retomando o tratamento
    """

    novo_terapeuta = relig_form.cleaned_data['novo_terapeuta']
    data_religamento = relig_form.cleaned_data['data_retorno']

    Prontuarios.objects.create(numero=current_pac,
                               autor=novo_terapeuta,
                               data_consulta=data_religamento,
                               entrada=f"Paciente {current_pac.nome} reiniciou o processo no dia"
                                       f"{data_religamento} com  {novo_terapeuta}."
                               )
    return current_pac


def get_current_user_terapeuta(request):
    """Obtem o objeto Terapeuta relacionado ao Usuário responsável pela Request"""
    try:
        user_terapeuta = request.user.Terapeutas.get()
        current_user_terapeuta = user_terapeuta
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Usuário não associado a um profissional Terapeuta!")

    return current_user_terapeuta


def get_pacs_no_grp():
    """Filtra todos os pacientes que não estão em grupos"""
    pacientes = CadastroPacientes.objects.filter(grupo__isnull=True)

    return pacientes


def register_presencas_consulta_grupo(entrada_form, selected_pacs, prontuario_grupo_numero):
    """ Registra as presenças do grupo em uma data determinada
    na model PresencasGrupo
    """
    nova_consulta = entrada_form
    current_grupo = get_current_group(prontuario_grupo_numero)

    presencas_grupo_entry = PresencasGrupo(
        consulta=nova_consulta,
        grupo_prontuario=current_grupo,
        data=nova_consulta.data_consulta,
    )

    presencas_grupo_entry.pacientes.set(selected_pacs)

    return selected_pacs


def save_new_entrada_prontuario_grupo_pacs_individual(entrada_form,
                                                      current_grupo,
                                                      current_user_terapeuta,
                                                      selected_pacs):
    """Cria um cópia da entrada do prontuario do grupo nos
    prontuarios individuais dos pacientes presentes nas sessão
    """

    new_entry = entrada_form.save(commit=False)

    new_entry.numero_id = current_grupo.prontuario_grupo_numero
    new_entry.autor = current_user_terapeuta
    new_entry.save()

    pacs_presentes = selected_pacs

    for paciente in pacs_presentes:
        entrada_prontuario_individual = Prontuarios(
            numero=paciente,
            autor=current_user_terapeuta,
            data_consulta=new_entry.data_consulta,
            entrada=new_entry.entrada
        )

        entrada_prontuario_individual.save()
