from django import forms
from django.contrib.auth.forms import UserCreationForm, User
from django.contrib.auth.models import Group
from datetime import date
from .models import CadastroProfissionais, CadastroPacientes, ConveniosAceitos, Prontuarios


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

    class Meta:
        model = CadastroPacientes
        fields = '__all__'


class CadastrarConvenios(forms.ModelForm):
    class Meta:
        model = ConveniosAceitos
        fields = '__all__'


class EntradaProntuario(forms.ModelForm):
    class Meta:
        model = Prontuarios
        fields = ['data_consulta', 'entrada']


class CadastroProfissionaisForm(forms.ModelForm):
    class Meta:
        model = CadastroProfissionais
        fields = ['nome', 'conselho_codigo', 'unimed_codigo', 'telefone_numero']


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

        def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()
                terapeutas_group = Group.objects.get(name='Terapeutas')
                user.groups.add(terapeutas_group)
            return user


class PacienteDesligamentoForm(forms.ModelForm):
    model = CadastroPacientes
    fields = ['desligado', 'data_final']


class PacienteTransferenciaForm(forms.ModelForm):
    model = CadastroPacientes
    fields = ['terapeuta_id']
