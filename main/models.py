from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from accounts.models import CustomUser
from datetime import date
import re
import regex


def validate_letters(value):
    if not re.match(r"^[^\d]+$", str(value)):
        raise ValidationError("Este campo pode conter apenas letras")


def validate_numbers(value):
    if not re.match("^[0-9]+$", str(value)):
        raise ValidationError("Este campo pode conter apenas números")


def validate_date_past(value):
    if value and isinstance(value, date):
        if value > timezone.now().date():
            raise ValidationError("A data não pode estar no futuro!")

    else:
        pass


class CadastroPacientes(models.Model):
    nome = models.CharField(verbose_name='Nome do Paciente', max_length=100,
                            validators=[validate_letters, MinLengthValidator(limit_value=5)])
    prontuario_numero = models.CharField(verbose_name='Nº de Prontuario', max_length=7,
                                         unique=True, validators=[validate_numbers, MinLengthValidator(limit_value=7)]
                                         )
    nascimento = models.DateField(verbose_name='Data de Nascimento', help_text='dd/mm/aaaa',
                                  validators=[validate_date_past])
    responsavel_legal = models.CharField(verbose_name='Responsável Legal', max_length=100,
                                         null=True, blank=True, validators=[validate_letters,
                                                                            MinLengthValidator(limit_value=5)])

    data_inicio = models.DateField(verbose_name='Data de Inicio', help_text='dd/mm/aaaa')
    data_final = models.DateField(verbose_name='Data do Desligamento', help_text='dd/mm/aaaa', blank=True, null=True,
                                  validators=[validate_date_past])

    desligado = models.BooleanField(verbose_name='Desligado', help_text='Paciente desligado', default=False)
    cpf_numero = models.CharField(verbose_name='CPF', max_length=11, unique=True,
                                  validators=[validate_numbers, MinLengthValidator(limit_value=11)])

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
                                            max_length=50, blank=True, null=True,
                                            validators=[validate_numbers, MinLengthValidator(limit_value=7)])
    terapeuta = models.ForeignKey(
        'CadastroProfissionais',
        related_name='pacientes',
        on_delete=models.PROTECT
    )
    endereco_rua = models.CharField(verbose_name='Endereço', max_length=100,
                                    validators=[MinLengthValidator(limit_value=10)])
    endereco_bairro = models.CharField(verbose_name='Bairro', max_length=50,
                                       validators=[MinLengthValidator(limit_value=3)])
    endereco_numero = models.CharField(verbose_name='Número', max_length=7, validators=[validate_numbers])
    endereco_complemento = models.CharField(verbose_name='Complemento', max_length=100,
                                            validators=[MinLengthValidator(limit_value=4)])
    telefone_numero = models.CharField(verbose_name='Telefone', max_length=11,
                                       validators=[validate_numbers, MinLengthValidator(limit_value=11)])
    cidade = models.CharField(verbose_name='Cidade', max_length=100, validators=[validate_letters,
                                                                                 MinLengthValidator(limit_value=3)])
    cep_numero = models.CharField(verbose_name='CEP', max_length=8, validators=[validate_numbers,
                                                                                MinLengthValidator(limit_value=8)])
    email = models.EmailField(verbose_name='E-mail')
    observacoes = models.TextField(verbose_name='Observações', blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.nome}, prontuário: {self.prontuario_numero}, terapeuta: {self.terapeuta}'

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ["nome"]
        permissions = [
            ('transfer_pac', 'Transferir Paciente (Terapeutas)'),
            ('deslig_pac', 'Desligar Paciente (Terapeutas)'),
            ('add_pac_group', 'Adicionar Paciente a Grupo (Terapeutas')
        ]


class ConveniosAceitos(models.Model):
    nome = models.CharField(verbose_name='Convênio', max_length=50, validators=[MinLengthValidator(limit_value=3)])
    cnpj_numero = models.CharField(verbose_name='CNPJ', max_length=14, validators=[validate_numbers,
                                                                                   MinLengthValidator(limit_value=14)])
    endereco_rua = models.CharField(verbose_name='Endereço', max_length=100,
                                    validators=[MinLengthValidator(limit_value=10)])
    endereco_bairro = models.CharField(verbose_name='Bairro', max_length=50,
                                       validators=[MinLengthValidator(limit_value=3)])
    endereco_numero = models.CharField(verbose_name='Número', max_length=7, validators=[validate_numbers])
    endereco_complemento = models.CharField(verbose_name='Complemento', max_length=100,
                                            validators=[MinLengthValidator(limit_value=4)])
    cidade = models.CharField(verbose_name='Cidade', max_length=20, validators=[validate_letters,
                                                                                MinLengthValidator(limit_value=3)])
    cep_numero = models.CharField(verbose_name='CEP', max_length=8, validators=[validate_numbers,
                                                                                MinLengthValidator(limit_value=8)])
    responsavel_contato = models.CharField(verbose_name='Nome do Resposável', max_length=50,
                                           validators=[validate_letters, MinLengthValidator(limit_value=3)])
    telefone_numero = models.CharField(verbose_name='Telefone', max_length=11,
                                       validators=[validate_numbers, MinLengthValidator(limit_value=11)])
    email = models.EmailField(verbose_name='E-mail para Contato')
    observacoes = models.TextField(verbose_name='Observações', blank=True, null=True)
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
    nome = models.CharField(verbose_name='Nome', max_length=100,
                            unique=True, editable=True, validators=[validate_letters])
    conselho_codigo = models.CharField(verbose_name='CRP', max_length=5, unique=True,
                                       editable=True, validators=[validate_numbers])
    STATUS_POS_CHOICES = (
        (0, 'Nível 1 - Incompleto'),
        (1, 'Nível 1 - Completo'),
        (2, 'Nível 2 - Incompleto'),
        (3, 'Nível 2 - Completo'),
        (4, 'Nível 3 - Incompleto'),
        (5, 'Nível 3 - Completo'),
    )
    pos_grad_status = models.IntegerField(verbose_name='Status Pós', choices=STATUS_POS_CHOICES, default=0)
    unimed_codigo = models.CharField(verbose_name='Número cadastro Unimed', max_length=6,
                                     unique=True, editable=True, validators=[validate_numbers])
    email = models.EmailField(verbose_name='Email', editable=True)
    telefone_numero = models.CharField(verbose_name='Telefone', max_length=11,
                                       editable=True, validators=[validate_numbers])
    endereco_rua = models.CharField(verbose_name='Endereço', max_length=100)
    endereco_bairro = models.CharField(verbose_name='Bairro', max_length=50)
    endereco_numero = models.CharField(verbose_name='Número', max_length=7, validators=[validate_numbers])
    endereco_complemento = models.CharField(verbose_name='Complemento', max_length=100)
    cidade = models.CharField(verbose_name='Cidade', max_length=20, validators=[validate_letters,
                                                                                MinLengthValidator(limit_value=3)])
    cep_numero = models.CharField(verbose_name='CEP', max_length=8, validators=[validate_numbers,
                                                                                MinLengthValidator(limit_value=8)])
    nascimento_data = models.DateField(verbose_name='Data de Nascimento', help_text='dd/mm/aaaa',
                                       validators=[validate_date_past])
    cpf_numero = models.CharField(verbose_name='CPF', unique=True, validators=[validate_numbers], max_length=11)
    rg_numero = models.CharField(verbose_name='Número RG', max_length=12,
                                 validators=[MinLengthValidator(limit_value=6)])
    rg_emissor = models.CharField(verbose_name='Orgão Emissor RG', max_length=50)
    usuario_codigo = models.ForeignKey(
        CustomUser,
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
    label = models.CharField(verbose_name='Nome', max_length=100, validators=[MinLengthValidator(limit_value=4)])
    prontuario_grupo_numero = models.CharField(verbose_name='Nº Prontuário do Grupo', max_length=5,
                                               unique=True, validators=[validate_numbers,
                                                                        MinLengthValidator(limit_value=4)])
    terapeuta_responsavel = models.ForeignKey(
        'CadastroProfissionais',
        related_name='grupos',
        on_delete=models.PROTECT,
        verbose_name='Terapeuta Responsável'
    )

    terapeuta_auxiliar1 = models.ManyToManyField(CadastroProfissionais,
                                                 verbose_name='Terapeuta Auxiliar', blank=True)
    desligado = models.BooleanField(verbose_name='Desativado', help_text='Grupo encerrado', default=False)
    data_inicio = models.DateField(verbose_name='Data de Inicio', help_text='dd/mm/aaaa')
    data_final = models.DateField(verbose_name='Data do Desligamento', help_text='dd/mm/aaaa', blank=True, null=True,
                                  validators=[validate_date_past])
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
    data_consulta = models.DateField(verbose_name='Data da Consulta', validators=[validate_date_past])
    entrada = models.TextField(verbose_name='Parecer', validators=[MinLengthValidator(limit_value=10)])
    objects = models.Manager()

    def __str__(self):
        return f'Prontuário Grupo {self.numero}'

    class Meta:
        verbose_name = 'Prontuário Grupo'
        verbose_name_plural = 'Prontuários Grupos'
        permissions = [
            ('add_entry_group', 'Adicionar entradas em prontuários de Grupo (Terapeutas)')
        ]


class PresencasGrupo(models.Model):
    consulta = models.ForeignKey('ProntuariosGrupos',
                                 on_delete=models.PROTECT,
                                 related_name='Consulta',
                                 verbose_name='Consulta'
                                 )
    grupo_prontuario = models.ForeignKey('CadastroGrupos',
                                         to_field='prontuario_grupo_numero',
                                         on_delete=models.PROTECT,
                                         verbose_name='Grupo nº')

    data = models.DateField(verbose_name='Data', blank=False, null=False, validators=[validate_date_past])
    pacientes = models.ManyToManyField(CadastroPacientes)

    def __str__(self):
        return f'Presenças Grupo {self.grupo_prontuario}'

    class Meta:
        verbose_name = 'Presença'
        verbose_name_plural = 'Presenças'


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
    data_consulta = models.DateField(verbose_name='Data da Consulta', validators=[validate_date_past])
    entrada = models.TextField(verbose_name='Parecer', validators=[MinLengthValidator(limit_value=10)])
    objects = models.Manager()

    def __str__(self):
        return f'Prontuário {self.numero}'

    class Meta:
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'
        permissions = [
            ('add_entry', 'Adicionar entradas em prontuários (Terapeutas)')
        ]


class HistoricoAcademico(models.Model):
    profissonal = models.ForeignKey('CadastroProfissionais',
                                    on_delete=models.PROTECT,
                                    verbose_name='Terapeuta')
    curso = models.CharField(verbose_name='Curso', max_length=30, validators=[validate_letters])
    instituicao = models.CharField(verbose_name='Instituição', max_length=50, validators=[validate_letters])
    ano_conclusao = models.CharField(verbose_name='Ano de Conclusão', max_length=4,
                                     validators=[validate_numbers, MinLengthValidator(limit_value=4)])
    objects = models.Manager()

    def __str__(self):
        return f'{self.curso} - {self.instituicao}'

    class Meta:
        verbose_name = 'Histórico Acadêmico'
        verbose_name_plural = 'Históricos Acadêmicos'
