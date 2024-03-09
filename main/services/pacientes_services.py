from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from datetime import date
from typing import Union
from main.services.terapeutas_services import get_current_user_terapeuta
from main.utils import get_selected_items, calculate_age
from main.models import (CadastroGrupos, CadastroPacientes, ProntuariosIndividuais, ProntuariosGrupos, PresencasGrupo,
                         CadastroProfissionais)


def get_selected_pacientes(selected_items: list) -> QuerySet:
    """ Retorna os pacientes selecionados em um Request"""
    selected_pacs = CadastroPacientes.objects.filter(id__in=selected_items)
    return selected_pacs


def get_current_grupo_prontuario_numero(grupo_id: int) -> str:
    prontuario_grupo_numero = CadastroGrupos.objects.get(id=grupo_id).prontuario_grupo_numero

    return prontuario_grupo_numero


def when_add_pacientes_to_group_get_info_and_act(request: HttpRequest, prontuario_grupo_numero: str) -> bool:
    """Função para executar as modificações necessárias em objetos Paciente
    e objetos Prontuario quando pacientes são transferidos para grupo"""

    current_user_terapeuta = get_current_user_terapeuta(request)
    current_group = get_current_group(prontuario_grupo_numero)
    selected_items = get_selected_items(request)
    pacs_add = get_selected_pacientes(selected_items)

    update_result = update_cadastro_pacientes_when_add_to_grupo(pacs_add, current_group, current_user_terapeuta)

    registration_result = registro_prontuario_when_pacientes_add_to_group(pacs_add, current_group, current_user_terapeuta)

    if update_result and registration_result:
        return True
    else:
        if not update_result:
            print("Erro: update de cadastro falhou!")
        if not registration_result:
            print("Erro: registro de transferencia falhou!")
        return False


def update_cadastro_pacientes_when_add_to_grupo(pacs_add: QuerySet, current_group: CadastroGrupos,
                                                current_user_terapeuta: CadastroProfissionais) -> bool:
    """Faz o update dos cadastros individuais de pacientes
    quando são adicionados em grupos"""
    try:
        CadastroPacientes.objects.filter(id__in=pacs_add).update(grupo_id=current_group,
                                                                 modalidade_atendimento=1,
                                                                 terapeuta=current_user_terapeuta)
        return True

    except Exception as e:
        print(f"House um erro ao executar o update de cadastro dos pacientes addicionados!\n Erro: {e}")
        return False


def registro_prontuario_when_pacientes_add_to_group(pacs_add: QuerySet, current_group: CadastroGrupos,
                                                    current_user_terapeuta: CadastroProfissionais) -> bool:
    """ Cria um registro no prontuário individual de um paciente que foi
    adicionado a um grupo"""

    grupo_add = current_group
    data_grupo = date.today()

    try:
        for paciente in pacs_add:
            grupo = grupo_add
            entrada_prontuario_individual = ProntuariosIndividuais(
                numero=paciente,
                autor=current_user_terapeuta,
                data_consulta=data_grupo,
                entrada=str(f"Paciente {paciente.nome}  foi adicionado ao grupo {current_group.label} "
                            f" {grupo.prontuario_grupo_numero} por {current_user_terapeuta} em {data_grupo}.")
            )
            entrada_prontuario_individual.save()

        return True

    except Exception as e:
        print(f"Houve um erro ao executar registro_prontuario_when_pacs_add_to_group!\n Erro:{e}")
        return False


def filter_active_pacientes() -> QuerySet:
    """ Filtrar todos Pacientes ativos
    """
    active_pacientes = CadastroPacientes.objects.filter(desligado=False)

    return active_pacientes


def filter_inactive_pacientes() -> QuerySet:
    """ Filtrar todos Pacientes inativos
    """
    inactive_pacientes = CadastroPacientes.objects.filter(desligado=True)

    return inactive_pacientes


def filter_active_grupos() -> QuerySet:
    """ Filtrar todos Grupos ativos
    """
    active_groups = CadastroGrupos.objects.filter(desligado=False)

    return active_groups


def filter_inactive_grupos() -> QuerySet:
    """ Filtrar todos Grupos inativos
    """
    inactive_groups = CadastroGrupos.objects.filter(desligado=True)

    return inactive_groups


def filter_active_pacientes_by_terapeuta(terapeuta: CadastroProfissionais) -> QuerySet:
    """ Filtrar pacientes ativos por terapeuta
    """
    active_pacs_terapeuta = CadastroPacientes.objects.filter(terapeuta=terapeuta, desligado=False)

    return active_pacs_terapeuta


def filter_inactive_pacientes_by_terapeuta(terapeuta: CadastroProfissionais) -> QuerySet:
    """ Filtrar pacientes inativos por terapeuta
    """
    inactive_pacs_terapeuta = CadastroPacientes.objects.filter(terapeuta=terapeuta, desligado=True)

    return inactive_pacs_terapeuta


def filter_active_groups_by_terapeuta(terapeuta: CadastroProfissionais) -> QuerySet:
    """ Filtrar grupos ativos por terapeuta ou terapeuta auxiliar
    """
    active_grps_terapeuta = CadastroGrupos.objects.filter(
        Q(terapeuta_responsavel=terapeuta) | Q(terapeuta_auxiliar=terapeuta),
        desligado=False)

    return active_grps_terapeuta


def filter_inactive_groups_by_terapeuta(terapeuta: CadastroProfissionais) -> QuerySet:
    """ Filtrar grupos ativos por terapeuta ou terapeuta auxiliar
    """
    inactive_grps_terapeuta = CadastroGrupos.objects.filter(
        Q(terapeuta_responsavel=terapeuta) | Q(terapeuta_auxiliar=terapeuta),
        desligado=True)

    return inactive_grps_terapeuta


def get_current_paciente(prontuario_numero: str) -> CadastroPacientes:
    """ Retorna um objeto "Paciente" da model CadastroPacientes
    baseado no numero de Prontuario
    """
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)

    return current_paciente


def get_current_paciente_prontuario(prontuario_numero: str) -> ProntuariosIndividuais:
    """ Retorna um objeto "Prontuario" da model Prontuarios
    baseado no numero do prontuario
    """
    current_paciente_prontuario = ProntuariosIndividuais.objects.filter(numero_id=prontuario_numero).order_by('-data_consulta')

    return current_paciente_prontuario


def get_current_group(prontuario_grupo_numero: str) -> CadastroGrupos:
    """ Retorna um objeto "Grupo" da model CadastroGrupos
    baseado no número de prontuario do grupo
    """

    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)

    return current_grupo


def get_current_group_prontuario(prontuario_grupo_numero: str) -> ProntuariosGrupos:
    """Retorna um objeto "Prontuario" da model ProntuariosGrupo
    baseado no numero do prontuario"""

    current_grupo_prontuario = ProntuariosGrupos.objects.filter(numero_id=prontuario_grupo_numero)

    return current_grupo_prontuario


def get_ultima_entrada_prontuarios_grupos(prontuario_grupo_numero: str) -> Union[date, None]:
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


def is_data_nova_consulta_group_valid(prontuario_grupo_numero: str, data_nova_entrada: date) -> bool:
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de grupos não é anterior a data da última consulta registrada
    """
    ultima_entrada_data = get_ultima_entrada_prontuarios_grupos(prontuario_grupo_numero)

    if not ultima_entrada_data:
        return True

    is_valid = data_nova_entrada > ultima_entrada_data

    return is_valid


def is_paciente_menor_acompanhado(nascimento: date, responsavel_legal: Union[str, None]) -> bool:
    """ Validação para garantir que menores de idade
    estejam acompanhados por um responsável legal
    """
    idade_paciente = calculate_age(nascimento)

    if idade_paciente < 18 and not responsavel_legal:
        return False
    else:
        return True


def cpf_responsavel_required_when_responsavel(responsavel_legal: Union[str, None],
                                              cpf_responsavel_legal: Union[str, None]) -> bool:
    """ Validação para garantir que quando há responsável legal
    o campo CPF do responsável também esteja preenchido
    """
    if responsavel_legal and not cpf_responsavel_legal:
        return False
    else:
        return True


def get_ultima_entrada_prontuarios_paciente_individual(numero: str) -> Union[date, None]:
    """Obtem a data da ultima entrada no prontuario de um paciente individual,
    caso exista, através do numero de prontuario
    """

    ultima_entrada = ProntuariosIndividuais.objects.filter(
        numero=numero
    ).order_by('-data_consulta').first()

    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None

    return ultima_entrada_data


# paciente_service.py
def is_data_nova_consulta_individual_valid(numero: str, data_nova_consulta: date) -> bool:
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de Pacientes individuais não é anterior a data da última consulta registrada
    """

    ultima_entrada_data = get_ultima_entrada_prontuarios_paciente_individual(numero)

    if ultima_entrada_data is None:
        return True

    is_valid = ultima_entrada_data and data_nova_consulta > ultima_entrada_data

    return is_valid


def save_desligamento_paciente_individual(current_pac: CadastroPacientes) -> bool:
    """Desliga um paciente
    """

    current_pac.desligado = True
    current_pac.save()

    if current_pac.desligado:
        print("Paciente Desligado com sucesso!")
        return True
    else:
        print("Erro durante save_desligamento_paciente_individual")
        return False


def desligamento_paciente_registro_prontuario_individual(current_user_terapeuta: CadastroProfissionais,
                                                         current_pac: CadastroPacientes, desligamento_form) -> bool:
    """ Cria um registro do desligamento no Prontuario de um paciente indiviual
    """
    entrada_text = desligamento_form.cleaned_data.get('entrada_text')
    data_final = desligamento_form.cleaned_data.get('data_final')
    try:
        ProntuariosIndividuais.objects.create(numero=current_pac,
                                              autor=current_user_terapeuta,
                                              data_consulta=data_final,
                                              entrada=f"Paciente {current_pac.nome} foi desligado por "
                                              f"{current_user_terapeuta}"
                                              f" em {data_final}. "
                                              f"\n Motivo: {entrada_text}", )
        return True

    except Exception as e:
        print("Ocorreu um erro ao executar desligamento_registro_prontuario!", str(e))
        return False


def get_pacientes_in_group(prontuario_grupo_numero: str) -> QuerySet:
    """ Obtém todos os pacientes ativos que fazem parte de um determinado grupo"""

    current_group = get_current_group(prontuario_grupo_numero)
    pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=current_group, desligado=False)

    return pacientes_grupo


def save_desligamento_group(current_grp: CadastroGrupos, desligamento_form) -> bool:
    """ Desliga um determinado grupo
    """
    data_final = desligamento_form.cleaned_data.get('data_final')
    current_grp.desligado = True
    current_grp.data_final = data_final
    current_grp.save()

    if current_grp.desligado:
        return True
    else:
        print("Erro durante save_desligamento_grp")
        return False
    # se necessario : return current_grp


def registro_desligamento_grupos(pacientes_grupo: QuerySet, current_grp: CadastroGrupos, desligamento_form,
                                 current_user_terapeuta: CadastroProfissionais) -> bool:
    """Cria um registro de desligamento do grupo no Prontuário individuaol
    dos participantes
    """

    entrada_text = desligamento_form.cleaned_data.get('entrada_text')
    data_final = desligamento_form.cleaned_data.get('data_final')
    try:
        for paciente in pacientes_grupo:
            ProntuariosIndividuais.objects.create(numero=paciente,
                                                  autor=current_user_terapeuta,
                                                  data_consulta=data_final,
                                                  entrada=f"Grupo {current_grp.label} "
                                                  f"prontuário {current_grp.prontuario_grupo_numero} "
                                                  f"foi desligado por {current_user_terapeuta} "
                                                  f"em {data_final}."
                                                  f"\n Motivo: {entrada_text}", )
        return True  # se necessário, retornar (pacientes_grupo)

    except Exception as e:
        print("Houve um error durante registro_desligamento_grupos:", str(e))
        return False


def transfer_paciente_individual(current_paciente: CadastroPacientes, transfer_form) -> CadastroPacientes:
    """Transfere o paciente para um novo terapeuta
    """
    paciente = current_paciente
    novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']
    paciente.terapeuta = novo_terapeuta
    paciente.save()

    return paciente


def registro_prontuario_transferencia_paciente(current_pac: CadastroPacientes, transfer_form,
                                               current_user_terapeuta: CadastroProfissionais) -> bool:
    """ Cria uma registro de transferencia no prontuario de pacientes individuais
    """

    entrada_text = transfer_form.cleaned_data.get('entrada_text')
    novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']
    data_transfer = date.today()
    try:
        ProntuariosIndividuais.objects.create(numero=current_pac,
                                              autor=current_user_terapeuta,
                                              data_consulta=data_transfer,
                                              entrada=f"Paciente {current_pac.nome} foi transferido por "
                                           f"{current_user_terapeuta} para {novo_terapeuta} em {data_transfer}."
                                           f"\n Motivo: {entrada_text}", )
        return True

    except Exception as e:
        print("Erro ao executar registro_transferencia_pac:", e)
        return False


def religamento_pacientes(current_pac: CadastroPacientes, relig_form) -> bool:
    """ Reativa um paciente que retornou para atendimento
    """

    novo_terapeuta = relig_form.cleaned_data['novo_terapeuta']
    try:
        current_pac.terapeuta = novo_terapeuta
        current_pac.desligado = False
        current_pac.modalidade_atendimento = 0
        current_pac.save()
        return True

    except Exception as e:
        print("Erro ao executar relig_pacs:", e)
        return False


def registro_prontuario_religamento_paciente(current_pac: CadastroPacientes, relig_form) -> bool:
    """Cria um registro no prontuario de um paciente que está retomando o tratamento
    """

    novo_terapeuta = relig_form.cleaned_data['novo_terapeuta']
    data_religamento = relig_form.cleaned_data['data_retorno']
    try:
        ProntuariosIndividuais.objects.create(numero=current_pac,
                                              autor=novo_terapeuta,
                                              data_consulta=data_religamento,
                                              entrada=f"Paciente {current_pac.nome} reiniciou o processo no dia"
                                              f"{data_religamento} com  {novo_terapeuta}."
                                              )

        return True

    except Exception as e:
        print("error ao executgar registro_prontuario_religamento_paciente: ", e)
        return False
    # se necessario: return current_pac


def get_pacientes_sem_grupo() -> QuerySet:
    """Filtra todos os pacientes que não estão em grupos
    """

    pacientes = CadastroPacientes.objects.filter(grupo__isnull=True)

    return pacientes


def register_presencas_consulta_grupo(new_entry: ProntuariosGrupos, pacs_presentes: QuerySet,
                                      prontuario_grupo_numero: str) -> bool:
    """ Registra as presenças do grupo em uma data determinada
    na model PresencasGrupo
    """
    current_grupo = get_current_group(prontuario_grupo_numero)

    try:
        presencas_grupo_entry = PresencasGrupo(
            consulta=new_entry,
            grupo_prontuario=current_grupo,
            data=new_entry.data_consulta,
        )
        presencas_grupo_entry.save()

        presencas_grupo_entry.pacientes.set(pacs_presentes)
        return True

    except Exception as e:
        print("Erro ao executar register_presencas_consulta_grupo : ", e)
        return False
    # se necessario: return pacs_presentes


def save_new_entrada_prontuario_grupo_in_individual_prontuario(new_entry: ProntuariosGrupos,
                                                               current_user_terapeuta: CadastroProfissionais,
                                                               pacs_presentes: QuerySet) -> bool:
    """Cria um cópia da entrada do prontuario do grupo nos
    prontuarios individuais dos pacientes presentes nas sessão
    """

    try:
        for paciente in pacs_presentes:
            entrada_prontuario_individual = ProntuariosIndividuais(
                numero=paciente,
                autor=current_user_terapeuta,
                data_consulta=new_entry.data_consulta,
                entrada=new_entry.entrada
            )

            entrada_prontuario_individual.save()

        return True

    except Exception as e:
        print("Erro ao executar save_new_entrada_prontuario_grupo_pacs_individual : ", e)
        return False


def save_and_register_grupo_transfer(transfer_form, current_user_terapeuta: CadastroProfissionais,
                                     current_grupo: CadastroGrupos) -> bool:
    """Transfere o grupo de um terapeuta para outro e
    registra essa mudança no prontuario do Grupo"""

    data_transfer = date.today()
    entrada_text = transfer_form.cleaned_data.get('entrada_text')
    novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']

    try:
        current_grupo.terapeuta_responsavel = novo_terapeuta
        current_grupo.save()

        ProntuariosGrupos.objects.create(numero=current_grupo,
                                         autor=current_user_terapeuta,
                                         data_consulta=data_transfer,
                                         entrada=f"Grupo {current_grupo.label} "
                                                 f"prontuário {current_grupo.prontuario_grupo_numero} "
                                                 f"foi transferido por {current_user_terapeuta} "
                                                 f"para {novo_terapeuta} em {data_transfer}."
                                                 f"\n Motivo: {entrada_text}")

        return True
    except Exception as e:
        print("Erro ao executar save_and_register_grupo_transfer:", str(e))
        return False


def registro_prontuario_individual_transfer_grupo(transfer_form, current_grupo: CadastroGrupos,
                                                  current_user_terapeuta: CadastroProfissionais) -> bool:
    """Registra a mudança de terapeuta responsavel pelo grupo
     no prontuario individual dos membros do grupo"""

    pacientes_grupo = get_pacientes_in_group(current_grupo.prontuario_grupo_numero)
    data_transfer = date.today()

    entrada_text = transfer_form.cleaned_data.get('entrada_text')
    novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']

    try:
        for paciente in pacientes_grupo:
            paciente.terapeuta = novo_terapeuta
            paciente.save()
            ProntuariosIndividuais.objects.create(numero=paciente,
                                                  autor=current_user_terapeuta,
                                                  data_consulta=data_transfer,
                                                  entrada=f"Grupo {current_grupo.label} "
                                                          f"prontuário {current_grupo.prontuario_grupo_numero} "
                                                          f"foi transferido por {current_user_terapeuta} "
                                                          f"para {novo_terapeuta} em {data_transfer}."
                                                          f"\n Motivo: {entrada_text}")

        return True

    except Exception as e:
        print("Erro ao executar registro_prontuario_individual_transfer_grupo", str(e))
        return False  # se necessario: return pacientes_grupo
