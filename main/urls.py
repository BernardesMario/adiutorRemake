from django.urls import path
from django.contrib.auth.decorators import permission_required
from .views import (cadastrar_paciente, add_entrada, index, list_entradas,
                    cadastro_user, usuario_login, informacoes_terapeuta,
                    desligar_paciente, transferir_paciente, admin_interface,
                    novo_convenio, detalhes_paciente, cadastrar_grupo,
                    add_entrada_sessao_grupo, )


app_name = 'main'

urlpatterns = [
    path('novo/', cadastrar_paciente, name='novo'),
    path('add_entrada/<str:prontuario_numero>/',
         permission_required('main.add_entry')(add_entrada),
         name='add_entrada'
         ),
    path('desligamento/<str:prontuario_numero>/',
         permission_required('main.deslig_pac')(desligar_paciente),
         name='desligamento'),
    path('transfer/<str:prontuario_numero>/',
         permission_required('main.transfer_pac')(transferir_paciente),
         name='transferencia'),
    path('prontuario/<str:prontuario_numero>/',
         list_entradas, name='prontuario'),
    path('index/', index, name='index'),
    path('usuario/',
         permission_required('main.add_terapeuta')(cadastro_user),
         name='usuario'),
    path('administrativo/', admin_interface, name='administrativo'),
    path('convenio/',
         permission_required('main.add_convenio')(novo_convenio),
         name='convenio'),
    path('perfil/', informacoes_terapeuta, name='perfil'),
    path('dadospac/<str:prontuario_numero>/',
         detalhes_paciente, name='dadospac'),
    path('login', usuario_login, name='login'),
    path('add-entrada-grupo/<str:prontuario_grupo_numero>/',
         permission_required('main.add_entry_group')(add_entrada_sessao_grupo),
         name='add-entrada-grupo'
         ),
]
