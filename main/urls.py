from django.urls import path
from django.contrib.auth.decorators import permission_required
from .views import (cadastrar_paciente, add_entrada, index, list_entradas,
                    cadastro_user, usuario_login, informacoes_terapeuta)


app_name = 'main'

urlpatterns = [
    path('novo/', cadastrar_paciente, name='novo'),
    path('add_entrada/<str:prontuario_numero>/',
         permission_required('main.add_entry')(add_entrada),
         name='add_entrada'
         ),
    path('prontuario/<str:prontuario_numero>/', list_entradas, name='prontuario'),
    path('index/', index, name='index'),
    path('usuario/', cadastro_user, name='usuario'),
    path('perfil/', informacoes_terapeuta, name='perfil'),
    path('login', usuario_login, name='login')
]
