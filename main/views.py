from django.contrib.auth import login as user_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from .forms import (UserRegistrationForm, CadastroPacienteForm, EntradaProntuario,
                    CadastroProfissionaisForm, PacienteDesligamentoForm, PacienteTransferenciaForm)
from .models import CadastroPacientes, CadastroProfissionais, Prontuarios
# Create your views here.

# TODO:
# view de listagem de consultas/mes
# opção de impressão de prontuario
#


@login_required
def cadastrar_paciente(request):
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
    current_user_terapeuta = request.user.Terapeutas.get()
    current_terapeuta_pacientes = CadastroPacientes.objects.filter(terapeuta_id=current_user_terapeuta)
    context = {
        'current_user': current_user_terapeuta,
        'pacientes': current_terapeuta_pacientes,
    }
    return render(request, 'index.html', context)


@login_required
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
                new_entry.autor = current_user_terapeuta
                new_entry.save()
    context = {
        'form': form,
        'sucesso': sucesso,
    }
    return render(request, 'cadastramento_pac.html', context)


@login_required()
@permission_required('deslig_pac', raise_exception=True)
def desligar_paciente(request, prontuario_numero):
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

    return render(request, 'PLACEHOLDER-TEMPLATE', context)


@login_required()
@permission_required('transfer_pac', raise_exception=True)
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
    return render(request, 'PLACEHOLDER-TEMPLATE', context)


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
            new_user.groups.add(terapeutas_group)
            terapeuta = terapeuta_form.save(commit=False)
            terapeuta.usuario_codigo_id = new_user.id
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
    form = CadastroProfissionaisForm
    sucesso = False
    if request.method == 'POST':
        form = CadastroProfissionaisForm(request.POST)
        if form.is_valid():
            sucesso = True
            new_terapeuta = form.save(commit=False)
            new_terapeuta.usuario_codigo_id = current_user_id
            new_terapeuta.save()
    context = {
        'form': CadastroProfissionaisForm,
        'sucesso': sucesso,
    }
    return render(request, 'user_perfil.html', context)


def usuario_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user_login(request, form.get_user())
            return redirect('/main/index/')
    else:
        form = AuthenticationForm()

    context = {
        'form': form
    }
    return render(request, 'login.html', context)
