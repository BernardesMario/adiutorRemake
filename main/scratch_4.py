def render_entrada_prontuario_pacs_form(request, prontuario_numero, entrada_form=None):
    if not entrada_form:
        entrada_form = EntradaProntuario(initial={'numero': prontuario_numero})

    context = {
        'form': entrada_form
    }
    return render(request, 'nova_entrada.html', context)


def add_entrada(request, prontuario_numero):
    current_user_terapeuta = request.user.Terapeutas.get()
    sucesso = False

    if request.method != 'POST':
        return render_entrada_prontuario_pacs_form(request, prontuario_numero)

    entrada_form = EntradaProntuario(initial={'numero': prontuario_numero, 'autor': current_user_terapeuta}, data=request.POST)

    if not entrada_form.is_valid():
        return render_entrada_prontuario_pacs_form(request, prontuario_numero, entrada_form)

    date_validation_result = date_validator_pacs(prontuario_numero, entrada_form)

    if date_validation_result:
        sucesso = True
        new_entry = entrada_form.save(commit=False)
        new_entry.save()

    context = {
        'form': entrada_form,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada.html', context)


def render_pacs_add_grp_form(request, entrada_form):
    context = {
        'form': entrada_form
    }

    return render(request, 'nova_entrada_grupo.html', context)


def add_entrada_sessao_grupo(request, prontuario_grupo_numero):
    entrada_form = EntradaProntuarioGrupoForm(initial={'numero': prontuario_grupo_numero})

    if request.method != 'POST':
        return render_pacs_add_grp_form(request, entrada_form)

    #date_validator_entrada_prontuario_grupo(prontuario_grupo_numero, entrada_form)

    if not entrada_form.is_valid():
        return render_pacs_add_grp_form(request, entrada_form)

    current_user_terapeuta = get_current_user_terapeuta(request)
    selected_items = get_selected_items(request)
    selected_pacs = get_selected_pacientes(selected_items)

    current_grupo = get_current_group(prontuario_grupo_numero)
    pacientes_grupo = get_pacs_grp(current_grupo)
    sucesso = False

    register_presencas_consulta_grupo(entrada_form, selected_pacs, prontuario_grupo_numero)
    save_new_entrada_prontuario_grupo_pacs_individual(entrada_form, current_grupo, current_user_terapeuta,
                                                      selected_pacs)

    context = {
        'form': entrada_form,
        'pacientes': pacientes_grupo,
        'sucesso': sucesso,
    }

    return render(request, 'nova_entrada_grupo.html', context)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    # upload_path = "user_{0}/{1}".format(instance.user.id, filename)

    return "user_{0}/{1}".format(instance.terapeuta.conselho_codigo, filename)

