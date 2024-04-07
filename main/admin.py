from django.contrib import admin
from .models import (CadastroProfissionais, CadastroGrupos, CadastroPacientes, ConveniosAceitos, ProntuariosGrupos,
                     ProntuariosIndividuais, HistoricoAcademico, PacientesMedia, ProfissionaisMedia)


@admin.register(CadastroPacientes)
class CadastroPacientesAdmin(admin.ModelAdmin):
    list_display = ['nome', 'prontuario_numero', 'data_inicio', 'terapeuta']
    search_fields = ['nome', 'prontuario_numero', 'data_inicio', 'terapeuta']
    list_filter = ['terapeuta', 'desligado']


class ProntuarioIndividuaisAdmin(admin.ModelAdmin):
    list_display = ['numero', 'autor', 'data_consulta', 'data_entrada']
    search_fields = ['numero', 'autor', 'data_consulta', 'data_entrada']
    list_filter = ['numero', 'autor']


@admin.register(CadastroProfissionais)
class CadastroProfissionaisAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(CadastroGrupos)
class CadastroGruposAdmin(admin.ModelAdmin):
    list_display = ['label', 'terapeuta_responsavel', 'prontuario_grupo_numero']
    search_fields = ['label', 'terapeuta_responsavel', 'terapeuta_auxiliar', 'prontuario_grupo_numero']
    list_filter = ['terapeuta_responsavel', 'terapeuta_auxiliar','desligado']


@admin.register(ProntuariosGrupos)
class ProntuarioGruposAdmin(admin.ModelAdmin):
    list_display = ['numero', 'autor', 'data_consulta', 'data_entrada']
    search_fields = ['numero', 'autor', 'data_consulta', 'data_entrada']
    list_filter = ['numero', 'autor']


@admin.register(ConveniosAceitos)
class ConvenioAceitosAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj_numero']
    search_fields = ['nome', 'cnpj_numero']


@admin.register(HistoricoAcademico)
class HistoricoAcademicoAdmin(admin.ModelAdmin):
    list_display = ['terapeuta', 'curso']
    search_fields = ['terapeuta']
    list_filter = ['terapeuta']


@admin.register(PacientesMedia)
class PacienteMediaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'description']
    search_fields = ['paciente', 'description']
    list_filter = ['paciente']


@admin.register(ProfissionaisMedia)
class ProfissionaisMediaAdmin(admin.ModelAdmin):
    list_display = ['terapeuta', 'description']
    search_fields = ['terapeuta', 'description']
    list_filter = ['terapeuta']

