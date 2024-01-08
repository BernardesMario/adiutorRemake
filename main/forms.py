from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from datetime import date
import re
from .models import (CadastroGrupos, CadastroProfissionais, CadastroPacientes, PresencasGrupo,
                     ConveniosAceitos, Prontuarios, ProntuariosGrupos, validate_numbers, validate_letters)
from accounts.models import CustomUser


class TerapeutaRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(validators=[
        validate_numbers, MinLengthValidator(limit_value=11), MaxLengthValidator(limit_value=11)])
    username = forms.CharField(validators=[validate_letters])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']

        def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()
                terapeutas_group = Group.objects.get(name='Terapeutas')
                user.groups.add(terapeutas_group)
            return user


class CadastroProfissionaisForm(forms.ModelForm):

    nome = forms.CharField(validators=[validate_letters])
    endereco_rua = forms.CharField(validators=[validate_letters])
    endereco_bairro = forms.CharField(validators=[validate_letters])
    cidade = forms.CharField(validators=[validate_letters])
    unimed_codigo = forms.CharField(validators=[validate_numbers])
    conselho_codigo = forms.CharField(validators=[validate_numbers])
    rg_numero = forms.CharField(validators=[validate_numbers])
    cpf_numero = forms.CharField(validators=[validate_numbers])
    endereco_numero = forms.CharField(validators=[validate_numbers])
    cep_numero = forms.CharField(validators=[validate_numbers])

    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento_data')
        hoje = date.today()
        if hoje < nascimento:
            raise forms.ValidationError('Idade Inválida')
        return nascimento

    class Meta:
        model = CadastroProfissionais
        fields = ['nome', 'nascimento_data', 'conselho_codigo', 'pos_grad_status', 'unimed_codigo', 'cpf_numero',
                  'rg_numero', 'rg_emissor', 'endereco_rua', 'endereco_bairro', 'endereco_complemento',
                  'endereco_numero', 'cidade', 'cep_numero']
        widgets = {
            'nascimento_data': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
        }


class CadastroPacienteForm(forms.ModelForm):
    # Função Clean para verificar se a idade não está no futuro
    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento')
        hoje = date.today()
        if hoje < nascimento:
            raise forms.ValidationError('Idade Inválida')
        return nascimento

    # Função Clean para garantir que um menor de idade possua responsável legal
    def clean(self):
        cleaned_data = super().clean()
        nascimento = cleaned_data.get('nascimento')
        responsavel_legal = cleaned_data.get('responsavel_legal')

        if nascimento:
            hoje = date.today()
            idade_paciente = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

            if idade_paciente < 18 and not responsavel_legal:
                raise forms.ValidationError("Pacientes menores de idade devem ter um responsável legal")

    def clean_responsavel(self):
        cleaned_data = super().clean()
        responsavel = cleaned_data.get('responsavel_legal')

        def validate_name(value):
            if not re.match(r"^[^\d]+$", str(value)):
                raise ValidationError("Este campo pode conter apenas letras")

        if responsavel:
            validate_name(responsavel)
        else:
            pass

    nome = forms.CharField(validators=[validate_letters])
    cpf_numero = forms.CharField(validators=[validate_numbers])
    carteirinha_convenio = forms.CharField(validators=[validate_numbers])
    telefone_numero = forms.CharField(validators=[validate_numbers])
    endereco_numero = forms.CharField(validators=[validate_numbers])
    endereco_rua = forms.CharField(validators=[validate_letters])
    endereco_bairro = forms.CharField(validators=[validate_letters])
    cidade = forms.CharField(validators=[validate_letters])
    cep_numero = forms.CharField(validators=[validate_numbers])

    class Meta:
        model = CadastroPacientes
        fields = '__all__'
        widgets = {
            'nascimento': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
            'data_inicio': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
            'data_final': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }


class CadastroPacienteNovoForm(forms.ModelForm):
    # Função Clean para verificar se a idade não está no futuro
    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento')
        hoje = date.today()
        if hoje < nascimento:
            raise forms.ValidationError('Idade Inválida')
        return nascimento

    # Função Clean para garantir que um menor de idade possua responsável legal
    def clean(self):
        cleaned_data = super().clean()
        nascimento = cleaned_data.get('nascimento')
        responsavel_legal = cleaned_data.get('responsavel_legal')

        if nascimento:
            hoje = date.today()
            idade_paciente = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

            if idade_paciente < 18 and not responsavel_legal:
                raise forms.ValidationError("Pacientes menores de idade devem ter um responsável legal")

    nome = forms.CharField(validators=[validate_letters])
    responsavel_legal = forms.CharField(validators=[validate_letters])
    cpf_numero = forms.CharField(validators=[validate_numbers])
    carteirinha_convenio = forms.CharField(validators=[validate_numbers])
    telefone_numero = forms.CharField(validators=[validate_numbers])

    class Meta:
        model = CadastroPacientes
        fields = ['nome', 'prontuario_numero', 'responsavel_legal',
                  'data_inicio', 'carteirinha_convenio', 'telefone_numero',
                  'convenio', 'terapeuta', 'cpf_numero',
                  'modalidade_atendimento', 'grupo', 'email', 'observacoes']

        widgets = {
            'nascimento': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )}


class CadastroGrupoForm(forms.ModelForm):

    prontuario_grupo_numero = forms.CharField(validators=[validate_numbers])

    class Meta:
        model = CadastroGrupos
        fields = ['label', 'prontuario_grupo_numero',
                  'terapeuta_responsavel', 'data_inicio']
        widgets = {'data_inicio': forms.DateInput(
            attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa',
                   'class': 'form-control'}
        )
        }
    # Checar funcionalidade do widget


class AdicionarPacGrupoForm(forms.ModelForm):

    class Meta:
        model = CadastroPacientes
        fields = ['grupo']


class CadastrarConvenios(forms.ModelForm):
    cnpj_numero = forms.CharField(validators=[validate_numbers])
    endereco_numero = forms.CharField(validators=[validate_numbers])
    cep_numero = forms.CharField(validators=[validate_numbers])
    telefone_numero = forms.CharField(validators=[validate_numbers])
    endereco_rua = forms.CharField(validators=[validate_letters])
    endereco_bairro = forms.CharField(validators=[validate_letters])
    cidade = forms.CharField(validators=[validate_letters])
    responsavel_contato = forms.CharField(validators=[validate_letters])

    class Meta:
        model = ConveniosAceitos
        fields = '__all__'


class EntradaProntuario(forms.ModelForm):
    def clean_data_consulta(self):
        data_consulta = self.cleaned_data.get('data_consulta')
        hoje = date.today()
        if hoje < data_consulta:
            raise forms.ValidationError('Idade Inválida')
        return data_consulta

    class Meta:
        model = Prontuarios
        fields = ['data_consulta', 'entrada']
        widgets = {
            'data_consulta': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
        }


class EntradaProntuarioGrupoForm(forms.ModelForm):
    def clean_data_consulta(self):
        data_consulta = self.cleaned_data.get('data_consulta')
        hoje = date.today()
        if hoje < data_consulta:
            raise forms.ValidationError('Idade Inválida')
        return data_consulta

    class Meta:
        model = ProntuariosGrupos
        fields = ['data_consulta', 'entrada']
        widgets = {
            'data_consulta': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }


class PacienteDesligamentoForm(forms.ModelForm):
    class Meta:
        model = CadastroPacientes
        fields = ['desligado', 'data_final']
        widgets = {
            'data_final': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }

    entrada_text = forms.CharField(
        label='Motivo',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )


class GrupoDesligamentoForm(forms.ModelForm):
    class Meta:
        model = CadastroGrupos
        fields = ['desligado', 'data_final']
        widgets = {
            'data_final': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }

    entrada_text = forms.CharField(
        label='Motivo',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )


class PacienteTransferenciaForm(forms.ModelForm):

    novo_terapeuta = forms.ModelChoiceField(
        queryset=CadastroProfissionais.objects.all(),
        label='Novo Terapeuta',
        required=True
    )

    entrada_text = forms.CharField(
        label='Motivo',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )

    class Meta:
        model = CadastroPacientes
        fields = ['novo_terapeuta']


class GrupoTrasferenciaForm(forms.ModelForm):

    novo_terapeuta = forms.ModelChoiceField(
        queryset=CadastroProfissionais.objects.all(),
        label='Novo Terapeuta',
        required=True
    )

    entrada_text = forms.CharField(
        label='Motivo',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True
    )

    class Meta:
        model = CadastroGrupos
        fields = ['novo_terapeuta']


class ReligarPacienteForm(forms.ModelForm):

    novo_terapeuta = forms.ModelChoiceField(
        queryset=CadastroProfissionais.objects.all(),
        label='Novo Terapeuta',
        required=True
    )
    data_retorno = forms.DateField(
        label='Data Retorno',
        widget=forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
        required=True
    )

    class Meta:
        model = CadastroPacientes
        fields = ['novo_terapeuta', 'data_retorno']
        widgets = {
            'data_retorno': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }


class UpdatePacienteForm(forms.ModelForm):
    carteirinha_convenio = forms.CharField(validators=[validate_numbers])
    telefone_numero = forms.CharField(validators=[validate_numbers])
    endereco_numero = forms.CharField(validators=[validate_numbers])
    cep_numero = forms.CharField(validators=[validate_numbers])

    class Meta:
        model = CadastroPacientes
        fields = ('convenio', 'carteirinha_convenio', 'enderco_rua', 'endereco_bairro', 'endereco_bairro',
                  'endereco_numero', 'endereco_complemento', 'telefone_numero', 'cidade', 'cep_numero', 'email')
