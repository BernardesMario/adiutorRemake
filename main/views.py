from django.contrib.auth import login as user_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from datetime import date
from .forms import (UserRegistrationForm, CadastroPacienteForm, EntradaProntuario, CadastrarConvenios,
                    CadastroProfissionaisForm, PacienteDesligamentoForm, PacienteTransferenciaForm)
from .models import CadastroPacientes, CadastroProfissionais, Prontuarios
# Create your views here.

# TODO:
# view de listagem de consultas/mes
# opção de impressão de prontuario
#


@login_required
def cadastrar_paciente(request):
    """
    View para cadastramento de novos pacientes.
    """
    sucesso = False
    form = CadastroPacienteForm(request.POST or None)

    if form.is_valid():
        sucesso = True
        form.save()

    context = {
        'form': form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_pac.html', context)


@login_required
def index(request):
    """
    View para a página inicial de profissionais terapeutas.
    Exibe os pacientes relacionados ao Terapeuta logado.
    """
    # Obtem o terapeuta através do relacionamento User-Terapeuta
    current_user_terapeuta = request.user.Terapeutas.get()
    # Obter todos os pacientes do usuario logado para exibição na página
    current_terapeuta_pacientes = CadastroPacientes.objects.filter(terapeuta_id=current_user_terapeuta)

    context = {
        'current_user': current_user_terapeuta,
        'pacientes': current_terapeuta_pacientes,
    }
    return render(request, 'index.html', context)


@login_required
def list_entradas(request, prontuario_numero):
    """
    View para exibição dos prontuários.
    Recebe o numero do prontuario através da URL.
    """
    # Identifica o terapeuta logado através do relacionamento User-Terapeuta
    current_user_terapeuta = request.user.Terapeutas.get()
    # Identifica o paciente selecionado e localiza seu prontuário
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
    """
    View para adicionar entradas a um prontuário.
    Recebe o número do prontuário através da URL.
    View exclusiva para usuários do grupo 'Terapeutas', que possui a
    autorização 'add_entry' para adicionar entradas.
    """
    # Definindo 'paciente' com o número recebido da URL
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
    # Data da última entrada feita no prontuário do paciente
    ultima_entrada = Prontuarios.objects.filter(numero=prontuario_numero).order_by('-data_consulta').first()
    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None
    form = EntradaProntuario(initial={'numero': prontuario_numero})
    sucesso = False

    if request.method == 'POST':
        form = EntradaProntuario(request.POST)

        if form.is_valid():
            data_nova_entrada = form.cleaned_data['data_consulta']
            # Validação que a data da consulta não é anterior a última registrada
            if ultima_entrada_data and data_nova_entrada < ultima_entrada_data:
                form.add_error('data_consulta', 'Data não pode ser anterior à da última consulta!')

            if not form.errors:
                sucesso = True
                new_entry = form.save(commit=False)
                new_entry.numero = paciente
                # Designar usuário atual como autor da entrada automaticamente
                new_entry.autor = current_user_terapeuta
                new_entry.save()

    context = {
        'form': form,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada.html', context)


@login_required()
@permission_required('main.deslig_pac', raise_exception=True)
def desligar_paciente(request, prontuario_numero):
    """
    View para registrar desligamento de pacientes [Mudança do valor booleano ´Desligado para True].
    Recebe o número do prontuário através da URL.
    View exclusiva para usuários do grupo 'Terapeutas', que possui a
    autorização 'deslig_pac' para desligar pacientes.
    """
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    desligamento_form = PacienteDesligamentoForm()
    # Data da última entrada feita no prontuário do paciente
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
    """
    View para transferencia de um paciente para outro terapeuta.
    Função recebe o número do prontuário através da URL.
    View exclusiva para usuários do grupo 'Terapeutas', que possui a
    autorização 'transfer_pac' para transferir pacientes.
    """
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
    """
    View para adicionar novos usuarios terapeutas.
    View exclusiva para usuarios do grupo 'Administrativos'
    que possui a permissão 'main.add_tarapeuta' para adicionar
    novos terapeutas.
    """
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
    """
    View para atualizar as informações pessoais
    de usuários do grupo 'Terapeutas'.
    """
    current_user_id = request.user.id
    form = CadastroProfissionaisForm
    sucesso = False

    if request.method == 'POST':
        form = CadastroProfissionaisForm(request.POST)

        if form.is_valid():
            sucesso = True
            new_terapeuta = form.save(commit=False)

            # Garante que o usuário atual faça modificações em seu próprio cadastro
            new_terapeuta.usuario_codigo_id = current_user_id
            new_terapeuta.save()

    context = {
        'form': CadastroProfissionaisForm,
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
    """
    View de login.
    Redireciona o usuário para a página devida
    através do grupo a qual pertence.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            current_user = form.get_user()
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
        form = AuthenticationForm()

    context = {
        'form': form
    }
    return render(request, 'login.html', context)


@login_required()
@permission_required('main.add_convenio', raise_exception=True)
def novo_convenio(request):
    """
    View para cadastramento de novos Conveios.
    Exclusiva para usuários do grupo 'Administrativos'
    que possui a autorização 'main.add_convenio' para
    adicionar convenios.
    """
    sucesso = False
    form = CadastrarConvenios

    if request.method == 'POST':
        form = CadastrarConvenios(request.POST)

        if form.is_valid():
            form.save()
            sucesso = True

    context = {
        'form': form,
        'sucesso': sucesso
    }

    return render(request, 'add_convenio.html', context)


def detalhes_paciente(request, prontuario_numero):
    """
    View para exibir detalhes de um paciente
    """
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    nascimento = current_paciente.nascimento
    hoje = date.today()
    idade_paciente = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

    context = {
        'paciente': current_paciente,
        'idade': idade_paciente
    }
    return render(request, 'paciente_details.html', context)
