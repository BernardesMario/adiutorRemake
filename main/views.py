from django.contrib.auth import login as user_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string
from datetime import date
from verify_email.email_handler import send_verification_email
from .forms import (TerapeutaRegistrationForm, CadastroPacienteForm, EntradaProntuario, CadastrarConvenios,
                    CadastroProfissionaisForm, PacienteDesligamentoForm, PacienteTransferenciaForm, UpdatePacienteForm,
                    CadastroGrupoForm, CadastroPacienteNovoForm, EntradaProntuarioGrupoForm, ReligarPacienteForm,
                    AdicionarPacGrupoForm, GrupoTrasferenciaForm, GrupoDesligamentoForm)
from .models import (CadastroPacientes, Prontuarios, CadastroGrupos,
                     ProntuariosGrupos, PresencasGrupo, CadastroProfissionais)


@login_required(login_url="/main/login")
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


@login_required(login_url="/main/login")
def cadastrar_grupo(request):
    grupo_form = CadastroGrupoForm(request.POST or None)

    if grupo_form.is_valid():
        new_group = grupo_form.save()

        redirect_url = reverse('main:add-pac-grupo', args=[str(new_group.id)])
        return redirect(redirect_url)

    context = {
        'form': grupo_form,
    }

    return render(request, 'cadastramento_grupo.html', context)


@login_required(login_url="/main/login")
def add_pacs_grupo(request, grupo_id):
    current_user_terapeuta = request.user.Terapeutas.get()
    current_group = CadastroGrupos.objects.get(id=grupo_id)
    sucesso = False
    pacientes = CadastroPacientes.objects.filter(grupo__isnull=True)
    pacs_form = AdicionarPacGrupoForm
    data_grupo = date.today()
    grupo_id = grupo_id

    if request.method == "POST":
        grupo = grupo_id
        selected_items = request.POST.getlist('selected_items')

        if pacs_form.is_valid:
            CadastroPacientes.objects.filter(id__in=selected_items).update(grupo_id=grupo, modalidade_atendimento=1,
                                                                           terapeuta=current_user_terapeuta)

            def save_pac_grp(selected_items, current_group, commit=True):
                pacs_add = CadastroPacientes.objects.filter(id__in=selected_items)
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

            save_pac_grp(selected_items, current_group)

            sucesso = True

    context = {
        'form': pacs_form,
        'pacientes': pacientes,
        'sucesso': sucesso
    }

    return render(request, 'add_pac_grupo.html', context)


@login_required(login_url="/main/login")
def index(request):
    current_user_terapeuta = request.user.Terapeutas.get()
    current_terapeuta_pacientes = CadastroPacientes.objects.filter(terapeuta_id=current_user_terapeuta)
    current_terapeuta_grupos = CadastroGrupos.objects.filter(terapeuta_responsavel_id=current_user_terapeuta)

    active_pacientes = current_terapeuta_pacientes.filter(desligado=False)
    inactive_pacientes = current_terapeuta_pacientes.filter(desligado=True)

    active_grupos = current_terapeuta_grupos.filter(desligado=False)
    inactive_grupos = current_terapeuta_grupos.filter(desligado=True)

    context = {
        'current_user': current_user_terapeuta,
        'pacientes': current_terapeuta_pacientes,
        'grupos': current_terapeuta_grupos,
        'active_pacientes': active_pacientes,
        'inactive_pacientes': inactive_pacientes,
        'active_grupos': active_grupos,
        'inactive_grupos': inactive_grupos,
    }
    return render(request, 'index.html', context)


@login_required(login_url="/main/login")
# criar permissão para visualização de prontuario
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


@login_required(login_url="/main/login")
# Criar permissão para ver prontuarios
def list_entradas_grupo(request, prontuario_grupo_numero):
    current_user_terapeuta = request.user.Terapeutas.get()
    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    current_grupo_prontuario = ProntuariosGrupos.objects.filter(numero_id=prontuario_grupo_numero)

    context = {
        'current_user': current_user_terapeuta,
        'grupo': current_grupo,
        'prontuarios': current_grupo_prontuario,

    }
    return render(request, 'prontuario_grupo.html', context)


@login_required(login_url="/main/login")
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


@login_required(login_url="/main/login")
@permission_required('main.add_entry_group', raise_exception=True)
def add_entrada_sessao_grupo(request, prontuario_grupo_numero):
    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
    pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=current_grupo.id)
    ultima_entrada = ProntuariosGrupos.objects.filter(
        numero=current_grupo.prontuario_grupo_numero
    ).order_by('-data_consulta').first()

    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None

    entrada_form = EntradaProntuarioGrupoForm(initial={'numero': prontuario_grupo_numero})
    sucesso = False

    if request.method == 'POST':
        entrada_form = EntradaProntuarioGrupoForm(request.POST)

        if entrada_form.is_valid():
            data_nova_entrada = entrada_form.cleaned_data['data_consulta']

            if ultima_entrada_data and data_nova_entrada < ultima_entrada_data:
                entrada_form.add_error('data_consulta', 'Data não pode ser anterior à da última consulta!')

            if not entrada_form.errors:
                sucesso = True

                new_entry = entrada_form.save(commit=False)
                new_entry.numero_id = current_grupo.prontuario_grupo_numero
                new_entry.autor = current_user_terapeuta
                new_entry.save()
                selected_items = request.POST.getlist('selected_items')
                pacs_presentes = CadastroPacientes.objects.filter(id__in=selected_items)

                for paciente in pacs_presentes:
                    entrada_prontuario_individual = Prontuarios(
                        numero=paciente,
                        autor=current_user_terapeuta,
                        data_consulta=new_entry.data_consulta,
                        entrada=new_entry.entrada
                    )
                    entrada_prontuario_individual.save()

                presencas_grupo_entry = PresencasGrupo(
                    consulta=new_entry,
                    grupo_prontuario=current_grupo,
                    data=new_entry.data_consulta,
                )
                presencas_grupo_entry.save()
                presencas_grupo_entry.pacientes.set(pacs_presentes)

    context = {
        'form': entrada_form,
        'pacientes': pacientes_grupo,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada_grupo.html', context)


@login_required(login_url="/main/login")
@permission_required('main.deslig_pac', raise_exception=True)
def desligar_paciente(request, prontuario_numero):
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
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
                                            'Paciente teve consultas posteriores a data informada!')

            if not desligamento_form.errors:
                entrada_text = desligamento_form.cleaned_data.get('entrada_text')
                data_ultima = desligamento_form.cleaned_data.get('data_final')

                def save_desligamento(commit=True):
                    ficha_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
                    ficha_paciente.desligado = True
                    ficha_paciente.save()

                    Prontuarios.objects.create(numero=paciente,
                                               autor=current_user_terapeuta,
                                               data_consulta=data_final,
                                               entrada=f"Paciente {ficha_paciente.nome} foi desligado por "
                                                       f"{current_user_terapeuta}"
                                                       f" em {data_ultima}. "
                                                       f"\n Motivo: {entrada_text}", )
                    return ficha_paciente

                save_desligamento()
                sucesso = True

    context = {
        'form': desligamento_form,
        'sucesso': sucesso,
    }

    return render(request, 'deslig_pac.html', context)


@login_required(login_url="/main/login")
# definir permissão
def desligar_grupo(request, prontuario_grupo_numero):
    grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
    desligamento_form = GrupoDesligamentoForm()

    ultima_entrada = ProntuariosGrupos.objects.filter(
        numero_id=prontuario_grupo_numero
    ).order_by('-data_consulta').first()
    ultima_entrada_data = ultima_entrada.data_consulta if ultima_entrada else None
    sucesso = False

    if request.method == 'POST':
        desligamento_form = GrupoDesligamentoForm(request.POST)

        if desligamento_form.is_valid():
            data_final = desligamento_form.cleaned_data['data_final']

            if not data_final or (ultima_entrada_data and data_final < ultima_entrada_data):
                desligamento_form.add_error('data_final',
                                            'Grupo teve consultas posteriores a data de desligamento informada!')

            if not desligamento_form.errors:
                entrada_text = desligamento_form.cleaned_data.get('entrada_text')

                def save_desligamento_grp(commit=True):
                    pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=grupo.id)
                    grupo.desligado = True
                    grupo.data_final = data_final
                    grupo.save()

                    for paciente in pacientes_grupo:
                        Prontuarios.objects.create(numero=paciente,
                                                   autor=current_user_terapeuta,
                                                   data_consulta=data_final,
                                                   entrada=f"Grupo {grupo.label} "
                                                           f"prontuário {grupo.prontuario_grupo_numero} "
                                                           f"foi desligado por {current_user_terapeuta} "
                                                           f"em {data_final}."
                                                           f"\n Motivo: {entrada_text}", )
                    return pacientes_grupo

                save_desligamento_grp()
                sucesso = True

    context = {
        'form': desligamento_form,
        'sucesso': sucesso,
    }

    return render(request, 'deslig_grupo.html', context)


@login_required(login_url="/main/login")
@permission_required('main.transfer_pac', raise_exception=True)
def transferir_paciente(request, prontuario_numero):
    paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    transfer_form = PacienteTransferenciaForm()
    current_user_terapeuta = request.user.Terapeutas.get()
    data_transfer = date.today()
    sucesso = False

    if request.method == 'POST':
        transfer_form = PacienteTransferenciaForm(request.POST)

        if transfer_form.is_valid():
            entrada_text = transfer_form.cleaned_data.get('entrada_text')
            novo_terapeuta = transfer_form.cleaned_data['novo_terapeuta']
            paciente.terapeuta = novo_terapeuta
            paciente.save()

            def save_transfer(commit=True):
                Prontuarios.objects.create(numero=paciente,
                                           autor=current_user_terapeuta,
                                           data_consulta=data_transfer,
                                           entrada=f"Paciente {paciente.nome} foi transferido por "
                                                   f"{current_user_terapeuta} para {novo_terapeuta} em {data_transfer}."
                                                   f"\n Motivo: {entrada_text}", )
                return paciente

            save_transfer()
            sucesso = True

    context = {
        'form': transfer_form,
        'sucesso': sucesso,
    }

    return render(request, 'transfer_pac.html', context)


@login_required(login_url="/main/login")
# adicionar permissão
def transferir_grupo(request, prontuario_grupo_numero):
    grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    current_user_terapeuta = request.user.Terapeutas.get()
    data_transfer = date.today()
    transfer_form = GrupoTrasferenciaForm()
    sucesso = False

    if request.method == 'POST':
        transfer_form = GrupoTrasferenciaForm(request.POST)

        if transfer_form.is_valid():
            entrada_text = transfer_form.cleaned_data.get('entrada_text')
            novo_terapeuta = transfer_form.cleaned_data['novo_terapeutas']
            grupo.terapeuta_responsavel = novo_terapeuta
            grupo.save()

            def save_transfer_grp(commit=True):
                pacientes_grupo = CadastroPacientes.objects.filter(grupo_id=grupo.id)
                for paciente in pacientes_grupo:
                    paciente.terapeuta = novo_terapeuta
                    paciente.save()
                    Prontuarios.objects.create(numero=paciente,
                                               autor=current_user_terapeuta,
                                               data_consulta=data_transfer,
                                               entrada=f"Grupo {grupo.label} "
                                                       f"prontuário {grupo.prontuario_grupo_numero} "
                                                       f"foi transferido por {current_user_terapeuta} "
                                                       f"para {novo_terapeuta} em {data_transfer}."
                                                       f"\n Motivo: {entrada_text}", )
                return pacientes_grupo

            save_transfer_grp()
            sucesso = True

    context = {
        'form': transfer_form,
        'sucesso': sucesso,
    }

    return render(request, 'transfer_grupo.html', context)


@login_required(login_url="/main/login")
@permission_required('main.add_terapeuta', raise_exception=True)
def cadastro_user_terapeuta(request):
    user_form = TerapeutaRegistrationForm()
    terapeuta_form = CadastroProfissionaisForm()
    terapeutas_group = Group.objects.get(name='Terapeutas')
    sucesso = False

    if request.method == 'POST':
        user_form = TerapeutaRegistrationForm(request.POST)
        terapeuta_form = CadastroProfissionaisForm(request.POST)

        if user_form.is_valid() and terapeuta_form.is_valid():
            sucesso = True
            new_user = user_form.save()
            new_user.save()
            new_user.groups.add(terapeutas_group)
            terapeuta = terapeuta_form.save(commit=False)
            terapeuta.usuario_codigo_id = new_user.id
            terapeuta.email = new_user.email
            terapeuta.telefone_numero = new_user.phone_number

            terapeuta.save()
            inactive_user = send_verification_email(request, user_form)
        else:
            print(terapeuta_form.errors)

    context = {
        'user_form': user_form,
        'terapeuta_form': terapeuta_form,
        'sucesso': sucesso,
    }

    return render(request, 'cadastramento_user.html', context)


@login_required(login_url="/main/login")
def index_perfil(request):
    pacientes_ativos = CadastroPacientes.objects.filter(desligado=False)
    pacientes_inativos = CadastroPacientes.objects.filter(desligado=True)
    terapeutas = CadastroProfissionais.objects.all

    context = {
        'lis_pacientes_ativos': pacientes_ativos,
        'lis_pacientes_inativos': pacientes_inativos,
        'list_terapeutas': terapeutas
    }

    return render(request, 'list_perfils.html', context)


'''
@login_required(login_url="/main/login")
def informacoes_pacientes(request,prontuario_numero):
    current_pac = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    perfil_form = PLACEHOLDER-FOR-FORM
    sucesso = False

    if request.method == 'POST':
        perfil_form = (request.POST)

        if perfil_form.is_valid():
    pass
'''


# ALTERAR PARA USER-ADMINs
@login_required(login_url="/main/login")
def informacoes_terapeuta(request, id):
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
            administrativo_group_id = 2  # conferir ID

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


@login_required(login_url="/main/login")
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


@login_required(login_url="/main/login")
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


@login_required(login_url="/main/login")
def detalhes_grupo(request, prontuario_grupo_numero):
    current_grupo = CadastroGrupos.objects.get(prontuario_grupo_numero=prontuario_grupo_numero)
    current_grupo_sessoes = ProntuariosGrupos.objects.filter(numero_id=prontuario_grupo_numero)
    current_grupo_membros = CadastroPacientes.objects.filter(grupo_id=current_grupo.id)
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


@login_required(login_url="/main/login")
def relig_pac(request, prontuario_numero):
    current_pac = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    relig_form = ReligarPacienteForm
    sucesso = False

    if request.method == 'POST':
        relig_form = ReligarPacienteForm(request.POST)

        if relig_form.is_valid():
            novo_terapeuta = relig_form.cleaned_data['novo_terapeuta']
            data_religamento = relig_form.cleaned_data['data_retorno']
            current_pac.terapeuta = novo_terapeuta
            current_pac.desligado = False
            current_pac.modalidade_atendimento = 0
            current_pac.save()

            def save_relig(commit=True):
                Prontuarios.objects.create(numero=current_pac,
                                           autor=novo_terapeuta,
                                           data_consulta=data_religamento,
                                           entrada=f"Paciente {current_pac.nome} reiniciou o processo no dia"
                                                   f"{data_religamento} com  {novo_terapeuta}."
                                           )
                return current_pac

            save_relig()
            sucesso = True

            # redirect_url = reverse('main:add-pac-grupo', args=[str(new_group.id)])
            # return redirect(redirect_url)

    context = {
        'sucesso': sucesso,
        'form': relig_form
    }

    return render(request, 'relig_pac.html', context)


@login_required(login_url="/main/login")
def update_pac(request, prontuario_numero):
    current_paciente = CadastroPacientes.objects.get(prontuario_numero=prontuario_numero)
    update_form = UpdatePacienteForm
    sucesso = False

    if request.method == 'POST':
        update_form = UpdatePacienteForm(request.POST)

        if update_form.is_valid():
            if 'convenio' in update_form.cleaned_data:
                current_paciente.convenio = update_form.cleaned_data.get('convenio')
                current_paciente.save()

            elif 'carteirinha_convenio' in update_form.cleaned_data:
                current_paciente.carteirinha_convenio = update_form.cleaned_data.get('carteirinha_convenio')
                current_paciente.save()

            elif 'endereco_rua' in update_form.cleaned_data:
                current_paciente.endereco_rua = update_form.cleaned_data.get('endereco_rua')
                current_paciente.save()

            elif 'endereco_bairro' in update_form.cleaned_data:
                current_paciente.endereco_bairro = update_form.cleaned_data.get('endereco_bairro')
                current_paciente.save()

            elif 'endereco_numero' in update_form.cleaned_data:
                current_paciente.endereco_numero = update_form.cleaned_data.get('endereco_numero')
                current_paciente.save()

            elif 'endereco_complemento' in update_form.cleaned_data:
                current_paciente.endereco_complemento = update_form.cleaned_data.get('endereco_complemento')
                current_paciente.save()

            elif 'telefone_numero' in update_form.cleaned_data:
                current_paciente.telefone_numero = update_form.cleaned_data.get('telefone_numero')
                current_paciente.save()

            elif 'cidade' in update_form.cleaned_data:
                current_paciente.cidade = update_form.cleaned_data.get('cidade')
                current_paciente.save()

            elif 'cep_numero' in update_form.cleaned_data:
                current_paciente.cep_numero = update_form.cleaned_data.get('cep_numero')
                current_paciente.save()

            elif 'email' in update_form.cleaned_data:
                current_paciente.email = update_form.cleaned_data.get('email')
                current_paciente.save()

            else:
                pass
            sucesso = True

    context = {
        'sucesso': sucesso,
        'paciente': current_paciente,
        'form': update_form
    }

    return render(request, 'update_pac.html', context)
