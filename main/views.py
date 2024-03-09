from datetime import date
from typing import Callable

from django.contrib.auth import login as user_login
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from verify_email.email_handler import send_verification_email

from .forms import (TerapeutaRegistrationForm, CadastroPacienteForm, EntradaProntuarioForm, CadastrarConveniosForm,
                    CadastroProfissionaisForm, PacienteDesligamentoForm, PacienteTransferenciaForm, UpdatePacienteForm,
                    CadastroGrupoForm, EntradaProntuarioGrupoForm, ReligarPacienteForm,
                    AdicionarPacGrupoForm, GrupoTrasferenciaForm, GrupoDesligamentoForm)
from .models import (CadastroPacientes, ProntuariosIndividuais, CadastroGrupos,
                     ProntuariosGrupos, PresencasGrupo, CadastroProfissionais)
from .services.file_service import render_to_pdf
from .services.pacientes_services import (filter_inactive_pacientes_by_terapeuta, filter_active_pacientes_by_terapeuta,
                                          filter_active_groups_by_terapeuta, filter_inactive_groups_by_terapeuta,
                                          get_current_paciente, get_current_grupo_prontuario_numero,
                                          get_current_paciente_prontuario, when_add_pacientes_to_group_get_info_and_act,
                                          get_current_group, get_pacientes_sem_grupo, filter_active_pacientes,
                                          get_current_group_prontuario, get_pacientes_in_group,
                                          get_selected_pacientes, register_presencas_consulta_grupo,
                                          save_new_entrada_prontuario_grupo_in_individual_prontuario,
                                          desligamento_paciente_registro_prontuario_individual,
                                          save_desligamento_paciente_individual, save_desligamento_group,
                                          registro_desligamento_grupos, transfer_paciente_individual,
                                          registro_prontuario_transferencia_paciente, save_and_register_grupo_transfer,
                                          registro_prontuario_individual_transfer_grupo, religamento_pacientes,
                                          registro_prontuario_religamento_paciente, filter_inactive_pacientes)

from .services.terapeutas_services import get_terapeutas_group, get_administrativo_group, get_current_user_terapeuta, \
    associate_new_user_to_cadastro_profissional
from .services.users_service import redirect_logged_user_to_home
from .utils import get_selected_items, calculate_age


def render_cadastro_paciente_form(request: HttpRequest, cadastro_form=None):
    if not cadastro_form:
        cadastro_form = CadastroPacienteForm()

    context = {
        'form': cadastro_form
    }
    return render(request, 'cadastramento_pac.html', context)


@login_required(login_url="/main/login")
def cadastrar_paciente(request: HttpRequest):
    """View para cadastramento de pacientes
    """
    if request.method != 'POST':
        return render_cadastro_paciente_form(request)

    cadastro_form = CadastroPacienteForm(request.POST)

    if not cadastro_form.is_valid():
        return render_cadastro_paciente_form(request, cadastro_form)

    sucesso = True
    cadastro_form.save()

    context = {
        'form': cadastro_form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_pac.html', context)


def render_cadastro_grupo_form(request: HttpRequest, grupo_form=None):
    current_user_terapeuta = get_current_user_terapeuta(request)

    if not grupo_form:
        grupo_form = CadastroGrupoForm(initial={'terapeuta_responsavel': current_user_terapeuta})

    context = {
        'form': grupo_form
    }

    return render(request, 'cadastramento_grupo.html', context)


@login_required(login_url="/main/login")
def cadastrar_grupo(request: HttpRequest):
    """View para criar Grupos
    """
    if request.method != 'POST':
        return render_cadastro_grupo_form(request)

    grupo_form = CadastroGrupoForm(request.POST)

    if not grupo_form.is_valid():
        return render_cadastro_grupo_form(request, grupo_form)

    new_grupo = grupo_form.save()

    redirect_url = reverse('main:add-pac-grupo', args=[str(new_grupo.id)])
    return redirect(redirect_url)


def render_add_pacientes_group_form(request: HttpRequest, pacs_form=None):
    pacientes = get_pacientes_sem_grupo()
    if not pacs_form:
        pacs_form = AdicionarPacGrupoForm()

    context = {
        'form': pacs_form,
        'pacientes': pacientes,

    }

    return render(request, 'add_pac_grupo.html', context)


@login_required(login_url="/main/login")
def add_pacs_grupo(request: HttpRequest, grupo_id):
    """ View para adicionar pacientes sem grupo em um Grupo recem criado
    """
    grupo_id = int(grupo_id)
    sucesso = False
    if request.method != 'POST':
        return render_add_pacientes_group_form(request)

    pacs_form = AdicionarPacGrupoForm(request.POST)

    if not pacs_form.is_valid():
        return render_add_pacientes_group_form(request, pacs_form)

    prontuario_grupo_numero = get_current_grupo_prontuario_numero(grupo_id)
    sucess_result = when_add_pacientes_to_group_get_info_and_act(request, prontuario_grupo_numero)

    if sucess_result:
        sucesso = True

    context = {
        'form': pacs_form,
        'sucesso': sucesso
    }

    return render(request, 'add_pac_grupo.html', context)


@login_required(login_url="/main/login")
def index(request: HttpRequest):
    """ View para a página principal de Usuarios do Grupo Terapeuta
    lista todos os pacientes e grupos, divididos por ativos e inativos
    """
    current_user_terapeuta = get_current_user_terapeuta(request)

    active_pacientes = filter_active_pacientes_by_terapeuta(current_user_terapeuta)
    inactive_pacientes = filter_inactive_pacientes_by_terapeuta(current_user_terapeuta)

    active_grupos = filter_active_groups_by_terapeuta(current_user_terapeuta)
    inactive_grupos = filter_inactive_groups_by_terapeuta(current_user_terapeuta)

    context = {
        'current_user': current_user_terapeuta,
        'active_pacientes': active_pacientes,
        'inactive_pacientes': inactive_pacientes,
        'active_grupos': active_grupos,
        'inactive_grupos': inactive_grupos,
    }
    return render(request, 'index.html', context)


@login_required(login_url="/main/login")
# TODO criar permissão para visualização de prontuario
def list_entradas(request: HttpRequest, prontuario_numero: str, as_pdf=False):
    """View para exibir o prontuario de um paciente individual
    """
    current_user_terapeuta = get_current_user_terapeuta(request)
    current_paciente = get_current_paciente(prontuario_numero)
    current_paciente_prontuario = get_current_paciente_prontuario(prontuario_numero)

    context = {
        'prontuario_numero': prontuario_numero,
        'current_user': current_user_terapeuta,
        'paciente': current_paciente,
        'prontuarios': current_paciente_prontuario,
    }

    if request.GET.get('as_pdf'):
        template = 'prontuario_for_pdf.html'
        return render_to_pdf(template, context)

    template = 'prontuario_pac.html'
    return render(request, template, context)


@login_required(login_url="/main/login")
# TODO Criar permissão para ver prontuarios
def list_entradas_grupo(request: HttpRequest, prontuario_grupo_numero: str):
    """View para exibir o prontuario de um grupo
    """
    current_user_terapeuta = get_current_user_terapeuta(request)
    current_grupo = get_current_group(prontuario_grupo_numero)
    current_grupo_prontuario = get_current_group_prontuario(prontuario_grupo_numero)

    context = {
        'current_user': current_user_terapeuta,
        'grupo': current_grupo,
        'prontuarios': current_grupo_prontuario,

    }
    return render(request, 'prontuario_grupo.html', context)


def render_add_entrada_prontuario_individual(request, prontuario_numero: str, entrada_form=None):
    """Renderiza o Form de nova entrada em Prontuarios individuais
    """
    if not entrada_form:
        entrada_form = EntradaProntuarioForm(initial={'numero': prontuario_numero})

    context = {
        'form': entrada_form,
    }

    return render(request, 'nova_entrada.html', context)


@login_required(login_url="/main/login")
@permission_required('main.add_entry', raise_exception=True)
def add_entrada(request: HttpRequest, prontuario_numero: str):
    """View para adicionar entradas no
    prontuarios de pacientes individuais
    """

    if request.method != 'POST':
        return render_add_entrada_prontuario_individual(request, prontuario_numero)

    entrada_form = EntradaProntuarioForm(initial={'numero': prontuario_numero}, data=request.POST)

    if not entrada_form.is_valid():
        return render_add_entrada_prontuario_individual(request, prontuario_numero, entrada_form)

    paciente = get_current_paciente(prontuario_numero)

    current_user_terapeuta = get_current_user_terapeuta(request)

    new_entry = entrada_form.save(commit=False)
    new_entry.numero = paciente
    new_entry.autor = current_user_terapeuta
    new_entry.save()
    sucesso = True

    context = {
        'form': entrada_form,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada.html', context)


def render_add_entrada_prontuario_grupo(request: HttpRequest, prontuario_grupo_numero: str, entrada_form=None):
    pacientes_grupo = get_pacientes_in_group(prontuario_grupo_numero)
    if not entrada_form:

        entrada_form = EntradaProntuarioGrupoForm(initial={'numero': prontuario_grupo_numero})

    context = {'form': entrada_form,
               'pacientes_grupo': pacientes_grupo
               }

    return render(request, 'nova_entrada_grupo.html', context)


@login_required(login_url="/main/login")
@permission_required('main.add_entry_group', raise_exception=True)
def add_entrada_sessao_grupo(request: HttpRequest, prontuario_grupo_numero: str):
    """ View para adicionar novas entradas em prontuario de Grupo
    """
    sucesso = False
    pacientes_grupo = get_pacientes_in_group(prontuario_grupo_numero)

    if request.method != 'POST':
        return render_add_entrada_prontuario_grupo(request, prontuario_grupo_numero)

    entrada_form = EntradaProntuarioGrupoForm(initial={'numero': prontuario_grupo_numero}, data=request.POST)

    if not entrada_form.is_valid():
        return render_add_entrada_prontuario_grupo(request, prontuario_grupo_numero, entrada_form)

    current_user_terapeuta = get_current_user_terapeuta(request)
    selected_items = get_selected_items(request)

    new_entry = entrada_form.save(commit=False)
    new_entry.numero_id = prontuario_grupo_numero
    new_entry.autor = current_user_terapeuta
    new_entry.save()

    pacs_presentes = get_selected_pacientes(selected_items)

    register_presencas_success = register_presencas_consulta_grupo(new_entry, pacs_presentes, prontuario_grupo_numero)
    register_prontuarios_individuais_success = save_new_entrada_prontuario_grupo_in_individual_prontuario(new_entry, current_user_terapeuta, pacs_presentes)

    if register_prontuarios_individuais_success and register_presencas_success:
        sucesso = True

    context = {
        'form': entrada_form,
        'pacientes_grupo': pacientes_grupo,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada_grupo.html', context)


def render_desligamento_form(request: HttpRequest, prontuario_numero: str, desligamento_form=None):
    if not desligamento_form:
        desligamento_form = PacienteDesligamentoForm(initial={'numero': prontuario_numero})

    context = {
        'form': desligamento_form,
    }

    return render(request, 'deslig_pac.html', context)


@login_required(login_url="/main/login")
@permission_required('main.deslig_pac', raise_exception=True)
def desligar_paciente(request: HttpRequest, prontuario_numero: str):
    """ View para desligar um paciente
    """
    sucesso = False
    current_paciente = get_current_paciente(prontuario_numero)

    if request.method != 'POST':
        return render_desligamento_form(request, prontuario_numero)

    desligamento_form = PacienteDesligamentoForm(request.POST, initial={'numero': prontuario_numero})

    if not desligamento_form.is_valid():
        return render_desligamento_form(request, prontuario_numero, desligamento_form)

    current_user_terapeuta = get_current_user_terapeuta(request)

    registro_desligamento = desligamento_paciente_registro_prontuario_individual(current_user_terapeuta,
                                                                                 current_paciente, desligamento_form)
    pac_desligado = save_desligamento_paciente_individual(current_paciente)

    if registro_desligamento and pac_desligado:
        sucesso = True

    context = {
        'form': desligamento_form,
        'sucesso': sucesso,
    }

    return render(request, 'deslig_pac.html', context)


def render_desligamento_grupo_form(request: HttpRequest, prontuario_grupo_numero: str, desligamento_form=None):
    if not desligamento_form:
        desligamento_form = GrupoDesligamentoForm(initial={'numero': prontuario_grupo_numero})

    context = {
        'form': desligamento_form,
    }

    return render(request, 'deslig_grupo.html', context)


@login_required(login_url="/main/login")
# definir permissão
def desligar_grupo(request: HttpRequest, prontuario_grupo_numero: str):
    """View para desligamento de grupos
    """
    sucesso = False

    if request.method != 'POST':
        return render_desligamento_grupo_form(request, prontuario_grupo_numero)

    desligamento_form = GrupoDesligamentoForm(initial={'prontuario_grupo_numero': prontuario_grupo_numero},
                                              data=request.POST)

    if not desligamento_form.is_valid():
        return render_desligamento_grupo_form(request, prontuario_grupo_numero, desligamento_form)

    current_grupo = get_current_group(prontuario_grupo_numero)
    pacientes_grupo = get_pacientes_in_group(prontuario_grupo_numero)
    current_user_terapeuta = get_current_user_terapeuta(request)

    registro_desligamento = registro_desligamento_grupos(pacientes_grupo, current_grupo, desligamento_form,
                                                         current_user_terapeuta)

    grupo_desligado = save_desligamento_group(current_grupo, desligamento_form)

    if registro_desligamento and grupo_desligado:
        sucesso = True

    context = {
        'form': desligamento_form,
        'sucesso': sucesso,
    }

    return render(request, 'deslig_grupo.html', context)


def render_transfer_paciente_form(request: HttpRequest, transfer_form=None):
    if not transfer_form:
        transfer_form = PacienteTransferenciaForm()

    context = {
        'form': transfer_form,
    }

    return render(request, 'transfer_pac.html', context)


@login_required(login_url="/main/login")
@permission_required('main.transfer_pac', raise_exception=True)
def transferir_paciente(request: HttpRequest, prontuario_numero: str) -> HttpResponse:
    """View para transferir pacientes individuais de
    um terapeuta para outro """

    sucesso = False
    if request.method != 'POST':
        return render_transfer_paciente_form(request)

    transfer_form = PacienteTransferenciaForm(request.POST)

    if not transfer_form.is_valid():
        return render_transfer_paciente_form(request, transfer_form)

    current_paciente = get_current_paciente(prontuario_numero)
    current_user_terapeuta = get_current_user_terapeuta(request)

    transferencia_sucess = transfer_paciente_individual(current_paciente, transfer_form)
    registro_transferencia_sucess = registro_prontuario_transferencia_paciente(current_paciente, transfer_form, current_user_terapeuta)

    if transferencia_sucess and registro_transferencia_sucess:
        sucesso = True

    context = {
        'form': transfer_form,
        'sucesso': sucesso,
    }

    return render(request, 'transfer_pac.html', context)


def render_transfer_grupo_form(request: HttpRequest, transfer_form=None):
    if not transfer_form:
        transfer_form = GrupoTrasferenciaForm()

    context = {
        'form': transfer_form,
    }

    return render(request, 'transfer_grupo.html', context)


@login_required(login_url="/main/login")
# adicionar permissão
def transferir_grupo(request: HttpRequest, prontuario_grupo_numero: str):
    """View para transferir grupo de um terapeuta para outro
    """
    sucesso = False

    if request.method != 'POST':
        return render_transfer_grupo_form(request)

    transfer_form = GrupoTrasferenciaForm(request.POST)

    if not transfer_form.is_valid():
        return render_transfer_grupo_form(request, transfer_form)

    current_grupo = get_current_group(prontuario_grupo_numero)
    current_user_terapeuta = get_current_user_terapeuta(request)

    transfer_sucess = save_and_register_grupo_transfer(transfer_form, current_user_terapeuta, current_grupo)

    transfer_registro_individual = registro_prontuario_individual_transfer_grupo(transfer_form, current_grupo,
                                                                                 current_user_terapeuta)

    if transfer_sucess and transfer_registro_individual:
        sucesso = True

    context = {
        'form': transfer_form,
        'sucesso': sucesso,
    }

    return render(request, 'transfer_grupo.html', context)


def render_cadastro_user_terapeuta_forms(request: HttpRequest, user_form=None, terapeuta_form=None):
    if not user_form:
        user_form = TerapeutaRegistrationForm()

    if not terapeuta_form:
        terapeuta_form = CadastroProfissionaisForm()

    context = {
        'user_form': user_form,
        'terapeuta_form': terapeuta_form,
    }

    return render(request, 'cadastramento_user.html', context)


@login_required(login_url="/main/login")
@permission_required('main.add_terapeuta', raise_exception=True)
def cadastro_user_terapeuta(request: HttpRequest):
    """ View para cadastrar novos Terapeutas e Usuários relacionado ao terapeuta
    """
    sucesso = False

    if request.method != 'POST':
        return render_cadastro_user_terapeuta_forms(request)

    user_form = TerapeutaRegistrationForm(request.POST)
    terapeuta_form = CadastroProfissionaisForm(request.POST)

    if not user_form.is_valid() or not terapeuta_form.is_valid():
        print(user_form.errors)
        print(terapeuta_form.errors)
        return render_cadastro_user_terapeuta_forms(request, user_form, terapeuta_form)

    new_user = user_form.save()

    valid_terapeuta_form = terapeuta_form if terapeuta_form.is_valid() else None

    associate_success = associate_new_user_to_cadastro_profissional(new_user, valid_terapeuta_form)

    if associate_success:
        inactive_user = send_verification_email(request, user_form)
        sucesso = True

    context = {
        'user_form': user_form,
        'terapeuta_form': terapeuta_form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_user.html', context)


@login_required(login_url="/main/login")
def index_perfil(request: HttpRequest):
    """ View para exibir todos os pacientes e terapeutas registrados
    para usuários administrativos (redirect para alterações cadastrais)
    """
    pacientes_ativos = filter_active_pacientes()
    pacientes_inativos = filter_inactive_pacientes()
    terapeutas = CadastroProfissionais.objects.all

    context = {
        'lis_pacientes_ativos': pacientes_ativos,
        'lis_pacientes_inativos': pacientes_inativos,
        'list_terapeutas': terapeutas
    }

    return render(request, 'list_perfils.html', context)


# ALTERAR PARA USER-ADMINs
@login_required(login_url="/main/login")
def informacoes_terapeuta(request: HttpRequest, id):
    current_user_id = request.user.id
    perfil_form = CadastroProfissionaisForm
    sucesso = False

    if request.method == 'POST':
        perfil_form = CadastroProfissionaisForm(request.POST)

        if perfil_form.is_valid():
            sucesso = True
            new_terapeuta = perfil_form.save(commit=False)

            # Garante que o usuário atual faça modificações em seu próprio cadastro
            new_terapeuta.usuario_codigo_id = current_user_id
            new_terapeuta.save()

    context = {
        'form': perfil_form,
        'sucesso': sucesso,
    }
    return render(request, 'user_perfil.html', context)


@login_required(login_url="/main/login")
def admin_interface(request: HttpRequest):
    """ View para a página inical de usuários do grupo 'Administrativos'.
    """
    return render(request, 'admin_main.html')


def render_login_form(request: HttpRequest, login_form=None):
    if not login_form:
        login_form = AuthenticationForm()

    context = {
        'form': login_form
    }
    return render(request, 'login.html', context)


def usuario_login(request: HttpRequest):
    if request.method != 'POST':
        return render_login_form(request)

    login_form = AuthenticationForm(request, request.POST)

    if not login_form.is_valid():
        return render_login_form(request, login_form)

    current_user = login_form.get_user()

    if current_user.require_otp_login:
        redirect_url = reverse('account:login-with-otp') + f'?email={current_user.email}'
        return redirect(redirect_url)

    user_login(request, current_user)

    terapeutas_group = get_terapeutas_group()
    administrativo_group = get_administrativo_group()

    return redirect_logged_user_to_home(current_user, terapeutas_group, administrativo_group)


def render_novo_convenio_form(request: HttpRequest, convenio_form=None):
    if not convenio_form:
        convenio_form = CadastrarConveniosForm()

    context = {
        'form': convenio_form,
    }

    return render(request, 'add_convenio.html', context)


@login_required(login_url="/main/login")
@permission_required('main.add_convenio', raise_exception=True)
def novo_convenio(request: HttpRequest):
    """ View para registrar novos convênios
    """
    if request.method != 'POST':
        return render_novo_convenio_form(request)

    convenio_form = CadastrarConveniosForm(request.POST)

    if not convenio_form.is_valid():
        return render_novo_convenio_form(request, convenio_form)

    convenio_form.save()
    sucesso = True

    context = {
        'form': convenio_form,
        'sucesso': sucesso
    }

    return render(request, 'add_convenio.html', context)


@login_required(login_url="/main/login")
def detalhes_paciente(request: HttpRequest, prontuario_numero: str):
    current_paciente = get_current_paciente(prontuario_numero)
    nascimento = current_paciente.nascimento
    idade_paciente = calculate_age(nascimento)

    context = {
        'paciente': current_paciente,
        'idade': idade_paciente
    }
    return render(request, 'paciente_details.html', context)


@login_required(login_url="/main/login")
def detalhes_grupo(request: HttpRequest, prontuario_grupo_numero: str):
    current_grupo = get_current_group(prontuario_grupo_numero)
    current_grupo_sessoes = get_current_group_prontuario(prontuario_grupo_numero)
    current_grupo_membros = get_pacientes_in_group(prontuario_grupo_numero)
    sessoes_count = len(current_grupo_sessoes)

    context = {
        'grupo': current_grupo,
        'sessoes': current_grupo_sessoes,
        'participantes': current_grupo_membros,
        'count': sessoes_count
    }

    return render(request, 'grupo_detalhes.html', context)


@login_required(login_url="/main/login")
def list_consultas(request):
    pass


def redirect_page(request):
    pass


def render_religar_paciente_form(request, relig_form=None):
    if not relig_form:
        relig_form = ReligarPacienteForm()

    context = {
        'form': relig_form
    }

    return render(request, 'relig_pac.html', context)


@login_required(login_url="/main/login")
def religar_paciente(request: HttpRequest, prontuario_numero: str):
    """ View para reativar um paciente previamente desligado
    """

    sucesso = False
    if request.method != 'POST':
        return render_religar_paciente_form(request)

    relig_form = ReligarPacienteForm(request.POST)

    if not relig_form.is_valid():
        return render_religar_paciente_form(request, relig_form)

    current_paciente = get_current_paciente(prontuario_numero)
    paciente_religado = religamento_pacientes(current_paciente, relig_form)
    registro_desligamento = registro_prontuario_religamento_paciente(current_paciente, relig_form)

    if paciente_religado and registro_desligamento:
        sucesso = True

    context = {
        'sucesso': sucesso,
        'form': relig_form
    }

    return render(request, 'relig_pac.html', context)


def handle_error(request):
    return render(request, 'error.html')
