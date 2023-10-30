from django.db import models
from django.contrib.auth.models import User


class CadastroPacientes(models.Model):
    nome = models.CharField(verbose_name='Nome do Paciente', max_length=100)
    prontuario_numero = models.CharField(verbose_name='Nº de Prontuario', max_length=7, unique=True)
    nascimento = models.DateField(verbose_name='Data de Nascimento', help_text='dd/mm/aaaa')
    responsavel_legal = models.CharField(verbose_name='Responsável Legal', max_length=100, null=True, blank=True)

    data_inicio = models.DateField(verbose_name='Data de Inicio', help_text='dd/mm/aaaa')
    data_final = models.DateField(verbose_name='Data do Desligamento', help_text='dd/mm/aaaa', blank=True, null=True)

    desligado = models.BooleanField(verbose_name='Desligado', help_text='Paciente desligado', default=False)
    cpf_numero = models.CharField(verbose_name='CPF', max_length=11, unique=True)

    MOD_CHOICES = (
        (0, 'Individual'),
        (1, 'Grupo'),
        (2, 'Casal'),
    )
    modalidade_atendimento = models.IntegerField(verbose_name='Modalidade', choices=MOD_CHOICES)
    grupo = models.ForeignKey(
        'CadastroGrupos',
        related_name='membros',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    convenio = models.ForeignKey(
        'ConveniosAceitos',
        related_name='pacientes',
        on_delete=models.PROTECT
    )
    carteirinha_convenio = models.CharField(verbose_name='Número do Convênio',
                                            max_length=50, blank=True, null=True)
    terapeuta = models.ForeignKey(
        'CadastroProfissionais',
        related_name='pacientes',
        on_delete=models.PROTECT
    )
    telefone_numero = models.CharField(verbose_name='Telefone', max_length=11)
    email = models.EmailField(verbose_name='E-mail', null=True, blank=True)
    observacoes = models.TextField(verbose_name='Observações', blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.nome}, prontuário: {self.prontuario_numero}, terapeuta: {self.terapeuta}'

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        permissions = [
            ('transfer_pac', 'Transferir Paciente (Terapeutas)'),
            ('deslig_pac', 'Desligar Paciente (Terapeutas)'),
            ('add_pac_group', 'Adicionar Paciente a Grupo (Terapeutas')
        ]


class ConveniosAceitos(models.Model):
    nome = models.CharField(verbose_name='Convênio', max_length=50)
    objects = models.Manager()

    def __str__(self):
        return f'{self.nome}'

    class Meta:
        verbose_name = 'Convênio'
        verbose_name_plural = 'Convênios'
        permissions = [
            ('add_convenio', 'Adicionar Novo Convenio (Administrativos)')
        ]


class CadastroProfissionais(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=100, unique=True, editable=True)
    conselho_codigo = models.CharField(verbose_name='CRP', max_length=5, unique=True, editable=True)
    unimed_codigo = models.CharField(verbose_name='Número cadastro Unimed', max_length=6, unique=True, editable=True)
    email = models.EmailField(verbose_name='Email', editable=True)
    telefone_numero = models.CharField(verbose_name='Telefone', max_length=11, editable=True)
    usuario_codigo = models.ForeignKey(
        User,
        related_name='Terapeutas',
        on_delete=models.PROTECT
    )
    objects = models.Manager()

    def __str__(self):
        return f'{self.nome}'

    class Meta:
        verbose_name = 'Terapeuta'
        verbose_name_plural = 'Terapeutas'
        permissions = [
            ('add_terapeuta', 'Adicionar novos Usuários (Administrativos)')
        ]


class CadastroGrupos(models.Model):
    label = models.CharField(verbose_name='Nome', max_length=100)
    prontuario_grupo_numero = models.CharField(verbose_name='Nº Prontuário do Grupo', max_length=5, unique=True)
    terapeuta_responsavel = models.ForeignKey(
        'CadastroProfissionais',
        related_name='grupos',
        on_delete=models.PROTECT
    )
    desligado = models.BooleanField(verbose_name='Desativado', help_text='Grupo encerrado', default=False)
    data_inicio = models.DateField(verbose_name='Data de Inicio', help_text='dd/mm/aaaa')
    data_final = models.DateField(verbose_name='Data do Desligamento', help_text='dd/mm/aaaa', blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.label} - {self.terapeuta_responsavel}'

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        permissions = [
            ('transfer_group', 'Transferir Grupo (Terapeutas)'),
            ('deslig_group', 'Desligar Grupo (Terapeutas)')
        ]


class ProntuariosGrupos(models.Model):
    numero = models.ForeignKey(
        'CadastroGrupos',
        on_delete=models.PROTECT,
        to_field='prontuario_grupo_numero',
        related_name='grupo',
        verbose_name='Nº Prontuário do Grupo'
    )
    autor = models.ForeignKey(
        'CadastroProfissionais',
        on_delete=models.PROTECT,
        to_field='nome',
        related_name='prontuario_grupo',
        verbose_name='Terapeuta Responsável'
    )
    data_entrada = models.DateField(auto_now_add=True, editable=False, verbose_name='Data da Entrada')
    data_consulta = models.DateField(verbose_name='Data da Consulta')
    entrada = models.TextField(verbose_name='Parecer')
    objects = models.Manager()

    def __str__(self):
        return f'Prontuário Grupo {self.numero}'

    class Meta:
        verbose_name = 'Prontuário Grupo'
        verbose_name_plural = 'Prontuários Grupos'
        permissions = [
            ('add_entry_group', 'Adicionar entradas em prontuários de Grupo (Terapeutas)')
        ]


class Prontuarios(models.Model):
    numero = models.ForeignKey(
        'CadastroPacientes',
        on_delete=models.PROTECT,
        to_field='prontuario_numero',
        related_name='paciente',
        verbose_name='Nº de Prontuário'
    )
    autor = models.ForeignKey(
        'CadastroProfissionais',
        on_delete=models.PROTECT,
        to_field='nome',
        related_name='prontuarios',
        verbose_name='Terapeuta'
    )
    data_entrada = models.DateField(auto_now_add=True, editable=False, verbose_name='Data da Entrada')
    data_consulta = models.DateField(verbose_name='Data da Consulta')
    entrada = models.TextField(verbose_name='Parecer')
    objects = models.Manager()

    def __str__(self):
        return f'Prontuário {self.numero}'

    class Meta:
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
        permissions = [
            ('add_entry', 'Adicionar entradas em prontuários (Terapeutas)')
        ]
