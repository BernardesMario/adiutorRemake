from django.contrib.auth import login as user_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from datetime import date
from .forms import (UserRegistrationForm, CadastroPacienteForm, EntradaProntuario, CadastrarConvenios,
                    CadastroProfissionaisForm, PacienteDesligamentoForm, PacienteTransferenciaForm,
                    CadastroGrupoForm, CadastroPacienteNovoForm, EntradaProntuarioGrupoForm)
from .models import CadastroPacientes, CadastroProfissionais, Prontuarios, CadastroGrupos, ProntuariosGrupos
# Create your views here.

# TODO:
# view de listagem de consultas/mes
# opção de impressão de prontuario
# upload de imagens/arquivos - linkar com prontuário
# pagamentos
# prontuario grupo (uma entrada > varios membros)


@login_required
def cadastrar_paciente(request):
    sucesso = False
    cadastro_form = CadastroPacienteForm(request.POST or None)

    if cadastro_form.is_valid():
        sucesso = True
        cadastro_form.save()

    context = {
        'form': cadastro_form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_pac.html', context)


@login_required
def cadastrar_grupo(request):
    sucesso = False
    grupo_form = CadastroGrupoForm
    pacientes_form = CadastroGrupoForm

    if request.method == 'POST':
        grupo_form = CadastroGrupoForm(request.POST)


@login_required
def index(request):
    current_user_terapeuta = request.user.Terapeutas.get()
    current_terapeuta_pacientes = CadastroPacientes.objects.filter(terapeuta_id=current_user_terapeuta)
    current_terapeuta_grupos = CadastroGrupos.objects.filter(terapeuta_responsavel_id=current_user_terapeuta)

    context = {
        'current_user': current_user_terapeuta,
        'pacientes': current_terapeuta_pacientes,
        'grupos': current_terapeuta_grupos,
    }
    return render(request, 'index.html', context)


@login_required
#criar permissão para visualização de prontuario
def list_entradas(request, prontuario_numero):
    current_user_terapeuta = request.user.Terapeutas.get()
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    current_paciente_prontuario = Prontuarios.objects.filter(numero_id=prontuario_numero)

    context = {
        'current_user': current_user_terapeuta,
        'paciente': current_paciente,
        'prontuarios': current_paciente_prontuario,
    }

    return render(request, 'prontuario_pac.html', context)


@login_required
@permission_required('main.add_entry', raise_exception=True)
def add_entrada(request, prontuario_numero):
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    current_user_terapeuta = request.user.Terapeutas.get()

    # Data da última entrada feita no prontuário do paciente
    ultima_entrada = Prontuarios.objects.filter(numero=prontuario_numero).order_by('-data_consulta').first()
    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None

    entrada_form = EntradaProntuario(initial={'numero': prontuario_numero})
    sucesso = False

    if request.method == 'POST':
        entrada_form = EntradaProntuario(request.POST)

        if entrada_form.is_valid():
            data_nova_entrada = entrada_form.cleaned_data['data_consulta']

            if ultima_entrada_data and data_nova_entrada < ultima_entrada_data:
                entrada_form.add_error('data_consulta', 'Data não pode ser anterior à da última consulta!')

            if not entrada_form.errors:
                sucesso = True
                new_entry = entrada_form.save(commit=False)
                new_entry.numero = paciente

                new_entry.autor = current_user_terapeuta
                new_entry.save()

    context = {
        'form': entrada_form,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada.html', context)

@login_required()
@permission_required('main.add_entry_group', raise_exception=True)
def add_entrada_sessao_grupo(request, prontuario_grupo_numero):
    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    # current_grupo_prontuario = ProntuariosGrupos.objects.get(numero=current_grupo.prontuario_grupo_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
    pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=current_grupo.id)

    ultima_entrada = ProntuariosGrupos.objects.filter(numero=current_grupo.prontuario_grupo_numero).order_b y('-data_consulta').first()
    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None
    entrada_form = EntradaProntuarioGrupoForm(initial={'numero': prontuario_grupo_numero})

    sucesso = False

    if entrada_form.is_valid():
        data_nova_entrada = entrada_form.cleaned_data['data_consulta']

        if ultima_entrada_data and data_nova_entrada < ultima_entrada_data:
            entrada_form.add_error('data_consulta', 'Data não pode ser anterior à da última consulta!')

        if not entrada_form.errors:
            sucesso = True
            new_entry = entrada_form.save(commit=False)
            new_entry.numero = current_grupo
            new_entry.autor = current_user_terapeuta
            new_entry.save()

    '''if request.method == 'POST':
        sessao_grupo_form = EntradaProntuarioGrupoForm(request.POST)

        if sessao_grupo_form.is_valid():
            nova_entrada_grupo = sessao_grupo_form.save(commit=False)
            nova_entrada_grupo.autor = current_user_terapeuta

            nova_entrada_grupo.numero.add(*pacientes_grupo)
            sucesso = True
'''
    context = {
        'form': sessao_grupo_form,
        'sucesso': sucesso,
    }

    return render(request, 'TEMPLATEPLACEHOLDER', context)


@login_required()
@permission_required('main.deslig_pac', raise_exception=True)
def desligar_paciente(request, prontuario_numero):
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    desligamento_form = PacienteDesligamentoForm()

    ultima_entrada = Prontuarios.objects.filter(numero=prontuario_numero).order_by('-data_consulta').first()
    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None
    sucesso = False

    if request.method == 'POST':
        desligamento_form = PacienteDesligamentoForm(request.POST)

        if desligamento_form.is_valid():
            data_final = desligamento_form.cleaned_data['data_final']

            # Validando se não houveram consultas posteriores a data de desligamento
            if not data_final or (ultima_entrada_data and data_final < ultima_entrada_data):
                desligamento_form.add_error('data_final',
                                            'Paciente teve consultas posteriores a data de desligamento informada!')

            if not desligamento_form.errors:
                paciente.desligado = True
                paciente.data_final = data_final
                paciente.save()
                sucesso = True

    context = {
        'form': desligamento_form,
        'sucesso': sucesso,
    }

    return render(request, 'deslig_pac.html', context)


@login_required()
@permission_required('main.transfer_pac', raise_exception=True)
def transferir_paciente(request, prontuario_numero):
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    transfer_form = PacienteTransferenciaForm()
    sucesso = False

    if request.method == 'POST':
        transfer_form = PacienteTransferenciaForm(request.POST)

        if transfer_form.is_valid():
            novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']
            paciente.terapeuta = novo_terapeuta
            paciente.save()
            sucesso = True

    context = {
        'form': transfer_form,
        'sucesso': sucesso,
    }

    return render(request, 'transfer_pac.html', context)


def redirect_page(request):
    pass


@login_required()
@permission_required('main.add_terapeuta', raise_exception=True)
def cadastro_user(request):
    user_form = UserRegistrationForm()
    terapeuta_form = CadastroProfissionaisForm
    terapeutas_group = Group.objects.get(name='Terapeutas')
    sucesso = False

    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        terapeuta_form = CadastroProfissionaisForm(request.POST)

        if user_form.is_valid():
            sucesso = True
            new_user = user_form.save()
            new_user.save()

            # Adiciona o novo usuário ao grupo 'Terapeutas'
            new_user.groups.add(terapeutas_group)

            terapeuta = terapeuta_form.save(commit=False)
            # Relaciona as entradas entre os models 'User' e 'Terapeutas'
            terapeuta.usuario_codigo_id = new_user.id
            # Define o mesmo email para usuário e terapeuta, evitando duplicar campos
            terapeuta.email = new_user.email
            terapeuta.save()

    context = {
        'user_form': user_form,
        'terapeuta_form': terapeuta_form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_user.html', context)


@login_required
def informacoes_terapeuta(request):
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


@login_required()
def admin_interface(request):
    """
    View para a página inical de usuários do grupo 'Administrativos'.
    """
    return render(request, 'admin_main.html')


def usuario_login(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, request.POST)

        if login_form.is_valid():
            current_user = login_form.get_user()
            user_login(request, current_user)

            # Definindo os IDs dos grupos de Usuario(Administrativo/Terapeuta)
            terapeutas_group_id = 1  # Conferir ID
            administrativo_group_id = 3  # conferir ID

            # Obtendo os grupos através dos IDs definidos
            terapeutas_group = Group.objects.get(id=terapeutas_group_id)
            administrativo_group = Group.objects.get(id=administrativo_group_id)

            # Checar Grupo do Usuário e redirecionar conforme grupo
            if terapeutas_group in current_user.groups.all():
                return redirect('/main/index/')
            elif administrativo_group in current_user.groups.all():
                return redirect('/main/administrativo/')
            else:
                error_message = "Algo deu errado! Entre em contato com a administração!\nErro: Grupo Inválido"
                return HttpResponseForbidden(error_message)
    else:
        login_form = AuthenticationForm()

    context = {
        'form': login_form
    }
    return render(request, 'login.html', context)


@login_required()
@permission_required('main.add_convenio', raise_exception=True)
def novo_convenio(request):
    sucesso = False
    convenio_form = CadastrarConvenios

    if request.method == 'POST':
        convenio_form = CadastrarConvenios(request.POST)

        if convenio_form.is_valid():
            convenio_form.save()
            sucesso = True

    context = {
        'form': convenio_form,
        'sucesso': sucesso
    }

    return render(request, 'add_convenio.html', context)


@login_required()
def detalhes_paciente(request, prontuario_numero):
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    nascimento = current_paciente.nascimento
    hoje = date.today()
    idade_paciente = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

    context = {
        'paciente': current_paciente,
        'idade': idade_paciente
    }
    return render(request, 'paciente_details.html', context)


@login_required()
def list_consultas(request):
    pass
