from django.urls import path
from django.contrib.auth.decorators import permission_required
from .views import (cadastrar_paciente, add_entrada, index, list_entradas,
                    cadastro_user_terapeuta, usuario_login, informacoes_terapeuta,
                    desligar_paciente, transferir_paciente, admin_interface, detalhes_grupo,
                    novo_convenio, detalhes_paciente, cadastrar_grupo, transferir_grupo, index_perfil,
                    add_entrada_sessao_grupo, add_pacientes_to_grupo, list_entradas_grupo, desligar_grupo,
                    modificar_cadastro_profissionais, producao_mensal, handle_error, cadastro_historico_academico,
                    terapeuta_media_upload, paciente_media_upload, redirect_to_homepage, view_certificado_curso,
                    view_paciente_pdf, view_paciente_images, view_terapeuta_images, view_terapeutas_pdf,
                    remover_membro_grupo, religar_paciente)

app_name = 'main'

urlpatterns = [
    path('novo/',
         cadastrar_paciente,
         name='novo'),
    path('add_pac_grupo/<str:grupo_id>/',
         add_pacientes_to_grupo,
         name='add-pacs-grupo'),

    path('add_entrada/<str:prontuario_numero>/',
         permission_required('main.add_entry')(add_entrada),
         name='add_entrada'),

    path('desligamento/<str:prontuario_numero>/',
         permission_required('main.deslig_pac')(desligar_paciente),
         name='desligamento'),

    path('reativar/<str:prontuario_numero>/',
         religar_paciente, name='religamento'),

    path('transfer/<str:prontuario_numero>/',
         permission_required('main.transfer_pac')(transferir_paciente),
         name='transferencia'),

    path('prontuario/<str:prontuario_numero>/',
         list_entradas,
         name='prontuario'),

    path('index/',
         index,
         name='index'),

    path('indice_cadastros',
         index_perfil,
         name='index-perfil'),

    path('usuario/',
         permission_required('main.add_terapeuta')(cadastro_user_terapeuta),
         name='usuario'),

    path('administrativo/',
         admin_interface,
         name='administrativo'),

    path('convenio/',
         permission_required('main.add_convenio')(novo_convenio),
         name='convenio'),

    path('perfil/<str:terapeuta_codigo>',
         informacoes_terapeuta,
         name='perfil'),

    path('dadospac/<str:prontuario_numero>/',
         detalhes_paciente,
         name='dadospac'),

    path('login', usuario_login, name='login'),

    path('add-entrada-grupo/<str:prontuario_grupo_numero>/',
         permission_required('main.add_entry_group')(add_entrada_sessao_grupo),
         name='add-entrada-grupo'),

    path('add_grupo/',
         permission_required('main.create_group')(cadastrar_grupo),
         name='add-grupo'),

    path('add_pac_grp/<str:grupo_id>',
         add_pacientes_to_grupo, name='add-pac-grupo'),
    # path('add_pac_grp', add_pacientes_to_grupo, name='add-pac-grupo'),

    path('grupo_prontuario/<str:prontuario_grupo_numero>/',
         list_entradas_grupo,
         name='grupo-prontuario'),

    path('transfer_grupo/<str:prontuario_grupo_numero>/',
         permission_required('main.transfer_group')
         (transferir_grupo),
         name='transfer-grupo'),

    path('deslig_grupo/<str:prontuario_grupo_numero>',
         permission_required('main.deslig_group')(desligar_grupo),
         name='deslig-grupo'),

    path('dados_grupo/<str:prontuario_grupo_numero>/',
         detalhes_grupo,
         name='dados-grupo'),

    path('error',
         handle_error,
         name='handle-error'),

    path('cadastrar_formacao/<str:terapeuta_codigo>/',
         cadastro_historico_academico,
         name='cadastrar_formacao'),

    path('modificar/terapeuta/<str:terapeuta_codigo>/',
         # permission_required(CREATE-PERMISSION)(),
         modificar_cadastro_profissionais,
         name='modificar-terapeuta'),

    path('producao/gerar/',
         producao_mensal,
         name='gerar-producao'),

    path('enviar_arquivo_terapeuta/<str:terapeuta_codigo>/',
         terapeuta_media_upload,
         name='enviar_arquivo_terapeuta'),

    path('enviar_arquivo_paciente/<str:prontuario_numero>',
         paciente_media_upload,
         name='enviar_arquivo_paciente'),

    path('homepage',
         redirect_to_homepage,
         name='homepage'),

    path('view_certificado/<int:curso_id>/',
         view_certificado_curso,
         name='view_certificado'),

    path('view_paciente_files/pdf/<int:media_id>',
         view_paciente_pdf,
         name='paciente/pdf'),

    path('view_paciente_images/image/<int:media_id>',
         view_paciente_images,
         name='paciente/image'),

    path('view_terapeuta_files/image/<int:media_id>',
         view_terapeuta_images,
         name='terapeuta/image'),

    path('view_terapeuta_files/pdf/<int:media_id>',
         view_terapeutas_pdf,
         name='terapeuta/pdf'),

    path('remove_grupo_member/<str:prontuario_numero>/<str:prontuario_grupo_numero>',
         permission_required('main.remove_pac_from_group')(remover_membro_grupo),
         name='remove_paciente')
]
