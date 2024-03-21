from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.core.validators import MinLengthValidator, MaxLengthValidator, FileExtensionValidator
from datetime import date
import re
from .models import (CadastroGrupos, CadastroProfissionais, CadastroPacientes,
                     ConveniosAceitos, ProntuariosIndividuais, ProntuariosGrupos, validate_numbers, validate_letters,
                     HistoricoAcademico, ProfissionaisMedia, PacientesMedia)
from accounts.models import CustomUser
from .services.pacientes_services import (is_data_nova_consulta_group_valid)
from .services.pacientes_forms_services import (is_paciente_menor_acompanhado,
                                                cpf_responsavel_required_when_responsavel,
                                                is_data_nova_consulta_individual_valid,
                                                ensure_paciente_convenio_carteirinha)
from .utils import (is_date_not_future, certificado_year_validator, calculate_age, is_image_file_extension_valid,
                    media_form_ensure_file)


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
                user.requires_otp_login = True
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

    def _raise_if_nascimento_is_invalid(self):
        nascimento_data = self.cleaned_data.get('nascimento_data')

        if nascimento_data is None or not is_date_not_future(nascimento_data):
            raise forms.ValidationError('Data de Nascimento Inválida')


class CadastroPacienteForm(forms.ModelForm):

    def clean_responsavel(self):
        """Função clean para validação de caracteres do campo responsavel_legal
        """
        cleaned_data = super().clean()
        responsavel = cleaned_data.get('responsavel_legal')

        def validate_name(value: str):
            if not re.match(r"^[^\d]+$", str(value)):
                raise forms.ValidationError("Este campo pode conter apenas letras")

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
    cpf_responsavel_legal = forms.CharField(validators=[validate_numbers])

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

    def _raise_if_nascimento_is_invalid(self):
        nascimento_data = self.cleaned_data.get('nascimento')

        if nascimento_data is None or not is_date_not_future(nascimento_data):
            raise forms.ValidationError('Data de Nascimento inválida!')

    def _raise_if_paciente_menor_idade_minina(self):
        nascimento_data = self.cleaned_data.get('nascimento')
        paciente_idade = calculate_age(nascimento_data)
        idade_minima = 3

        if paciente_idade < idade_minima:
            raise forms.ValidationError('Paciente possui idade inferior a 3 anos completos!')

    def _raise_if_inicio_is_invalid(self):
        data_inicio = self.cleaned_data.get('data_inicio')

        if data_inicio is None or not is_date_not_future(data_inicio):
            raise forms.ValidationError('Data de Inicio inválida')

    def _raise_if_menor_desacompanhado(self):
        nascimento = self.cleaned_data.get('nascimento')
        responsavel_legal = self.cleaned_data.get('responsavel_legal')

        if not is_paciente_menor_acompanhado(nascimento, responsavel_legal):
            raise forms.ValidationError('Pacientes menores de idade devem estar acompanhados por responsável legal!')

    def _raise_if_acompanhante_sem_cpf(self):
        responsavel_legal = self.cleaned_data.get('responsavel_legal')
        cpf_responsavel_legal = self.cleaned_data.get('cpf_responsavel_legal')

        if not cpf_responsavel_required_when_responsavel(responsavel_legal, cpf_responsavel_legal):
            raise forms.ValidationError('CPF do responsável não pode estar em branco!')

    def _raise_if_paciente_convenio_sem_carteirinha(self):
        convenio = self.cleaned_data.get('convenio')
        carteirinha_convenio = self.cleaned_data.get('carteirinha_convenio')

        if not ensure_paciente_convenio_carteirinha(convenio, carteirinha_convenio):
            raise forms.ValidationError('Campo "Carteirinha Conveio" Obrigatório para pacientes de Planos de Saude!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_menor_desacompanhado()
        self._raise_if_nascimento_is_invalid()
        self._raise_if_inicio_is_invalid()
        self._raise_if_acompanhante_sem_cpf()
        self._raise_if_paciente_menor_idade_minina()
        self._raise_if_paciente_convenio_sem_carteirinha()
        return cleaned_data


class CadastroPacienteNovoForm(forms.ModelForm):

    def clean_nascimento(self):
        nascimento = self.cleaned_data.get('nascimento')
        hoje = date.today()
        if hoje < nascimento:
            raise forms.ValidationError('Idade Inválida')
        return nascimento

    def clean(self):
        cleaned_data = super().clean()
        nascimento = cleaned_data.get('nascimento')
        responsavel_legal = cleaned_data.get('responsavel_legal')

        if nascimento:
            idade_paciente = calculate_age(nascimento)

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
            )
        }


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


class AdicionarPacGrupoForm(forms.ModelForm):
    class Meta:
        model = CadastroPacientes
        fields = ['grupo']


class CadastrarConveniosForm(forms.ModelForm):
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


class EntradaProntuarioForm(forms.ModelForm):
    class Meta:
        model = ProntuariosIndividuais
        fields = ['data_consulta', 'entrada']
        widgets = {
            'data_consulta': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            ),
        }

    def _raise_if_data_is_invalid(self):
        data_consulta = self.cleaned_data.get('data_consulta')

        if data_consulta is None or not is_date_not_future(data_consulta):
            raise forms.ValidationError('Data da Consulta Inválida!')

    def _raise_if_data_consulta_not_valid(self):
        data_consulta = self.cleaned_data.get('data_consulta')

        if not is_data_nova_consulta_individual_valid(self.initial['numero'], data_consulta):
            raise forms.ValidationError('Paciente possui consultas posteriores a data informada!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_data_is_invalid()
        self._raise_if_data_consulta_not_valid()
        return cleaned_data


class EntradaProntuarioGrupoForm(forms.ModelForm):
    class Meta:
        model = ProntuariosGrupos
        fields = ['data_consulta', 'entrada']
        widgets = {
            'data_consulta': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'dd/mm/aaaa', 'class': 'form-control'}
            )
        }

    def _raise_if_data_is_invalid(self):
        data_consulta = self.cleaned_data.get('data_consulta')

        if data_consulta is None or not is_date_not_future(data_consulta):
            raise forms.ValidationError('Data da Consulta Inválida!')

    def _raise_if_data_consulta_is_invalid(self):
        data_nova_entrada = self.cleaned_data.get('data_consulta')

        if not is_data_nova_consulta_group_valid(self.initial['numero'], data_nova_entrada):
            raise forms.ValidationError('O grupo possui consultas posteriores a data informada!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_data_is_invalid()
        self._raise_if_data_consulta_is_invalid()
        return cleaned_data


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

    def _raise_if_data_is_invalid(self):
        data_final = self.cleaned_data.get('data_final')

        if data_final is None or not is_date_not_future(data_final):
            raise forms.ValidationError('Data Final Inválida!')

    def _raise_if_data_final_is_invalid(self):
        data_nova_entrada = self.cleaned_data.get('data_final')

        if not is_data_nova_consulta_individual_valid(self.initial['numero'], data_nova_entrada):
            raise forms.ValidationError('O paciente possui consultas posteriores a data informada!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_data_is_invalid()
        self._raise_if_data_final_is_invalid()
        return cleaned_data


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

    def _raise_if_data_is_invalid(self):
        data_final = self.cleaned_data.get('data_final')

        if data_final is None or not is_date_not_future(data_final):
            raise forms.ValidationError('Data Final Inválida!')

    def _raise_if_data_final_not_valid(self):
        data_final = self.cleaned_data.get('data_final')

        if not is_data_nova_consulta_group_valid(self.initial['prontuario_grupo_numero'], data_final):
            raise forms.ValidationError('Grupo possui consultas posteriores a data informada!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_data_is_invalid()
        self._raise_if_data_final_not_valid()
        return cleaned_data


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
        fields = ('convenio', 'carteirinha_convenio', 'endereco_rua', 'endereco_bairro', 'endereco_bairro',
                  'endereco_numero', 'endereco_complemento', 'telefone_numero', 'cidade', 'cep_numero', 'email')


class GenerateProducaoForm(forms.Form):
    terapeuta = forms.ModelChoiceField(
        queryset=CadastroProfissionais.objects.all(),
        label='Novo Terapeuta',
        required=True
    )

    data_inicial = forms.DateField(label='Data Inicial',
                                   widget=forms.DateInput(attrs={'type': 'date',
                                                                 'placeholder': 'dd/mm/aaaa',
                                                                 'class': 'form-control'}),
                                   required=True)

    data_final = forms.DateField(label='Data Final',
                                 widget=forms.DateInput(attrs={'type': 'date',
                                                               'placeholder': 'dd/mm/aaaa',
                                                               'class': 'form-control'}),
                                 required=False)

    def _raise_if_data_inicial_is_invalid(self):
        data_inicial = self.cleaned_data.get('data_inicial')

        if data_inicial is None or not is_date_not_future(data_inicial):
            raise forms.ValidationError('Data Inicial Inválida!')

    def _raise_if_data_final_is_invalid(self):
        data_final = self.cleaned_data.get('data_final')

        if data_final is None:
            data_final = date.today()

        if not is_date_not_future(data_final):
            raise forms.ValidationError('Data Final Inválida!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_data_inicial_is_invalid()
        self._raise_if_data_final_is_invalid()

        return cleaned_data


class HistoricoAcademicoForm(forms.ModelForm):
    curso = forms.CharField(label='Curso', validators=[validate_letters])

    instituicao = forms.CharField(label='Instituição', validators=[validate_letters])

    certificado_conclusao = forms.FileField(label='Certificado', validators=[FileExtensionValidator(['pdf'])],
                                            widget=forms.ClearableFileInput(attrs={'multiple': False,
                                                                                   'accept': 'application/pdf'})
                                            )
    ano_conclusao = forms.IntegerField(label='Ano de Conclusão', validators=[validate_numbers])

    class Meta:
        model = HistoricoAcademico
        fields = ('curso', 'instituicao', 'ano_conclusao', 'certificado_conclusao')

    def _raise_if_conclusao_over_100_years(self):
        ano_conclusao = self.cleaned_data.get('ano_conclusao')

        if not certificado_year_validator(ano_conclusao):
            raise forms.ValidationError('Ano de Conclusão Inválido!')

    def _raise_if_concluso_in_future(self):
        ano_conclusao = self.cleaned_data.get('ano_conclusao')
        ano_atual = int(date.today().year)

        if ano_conclusao > ano_atual:
            raise forms.ValidationError('Ano de Conclusão não pode estar no futuro!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_conclusao_over_100_years()
        self._raise_if_concluso_in_future()

        return cleaned_data


class TerapeutaMediaUploadForm(forms.ModelForm):
    pdf_file = forms.FileField(label='PDF', widget=forms.ClearableFileInput(attrs={'multiple': False,
                                                                                   'accept': 'application/pdf'}),
                               validators=[FileExtensionValidator(['pdf'])], required=False)

    image_file = forms.ImageField(label='Imagens', widget=forms.ClearableFileInput({'multiple': False}), required=False)

    description = forms.CharField(label='Descrição', max_length=255)

    class Meta:
        model = ProfissionaisMedia
        fields = ('pdf_file', 'image_file', 'description')

    def _raise_if_no_files_upload(self):
        text_file = self.cleaned_data.get('pdf_file')
        image_file = self.cleaned_data.get('image_file')

        if not media_form_ensure_file(text_file, image_file):
            raise forms.ValidationError('Nenhum arquivo selecionado!')

    def _raise_if_image_file_not_supported(self):
        image_file = self.cleaned_data.get('image_file')

        if image_file and not is_image_file_extension_valid(image_file):
            raise forms.ValidationError('Arquivo de imagem não suportado!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_no_files_upload()
        self._raise_if_image_file_not_supported()

        return cleaned_data


class PacienteMediaUploadForm(forms.ModelForm):
    pdf_file = forms.FileField(label='PDF', widget=forms.ClearableFileInput(attrs={'multiple': False,
                                                                                   'accept': 'application/pdf'}),
                               validators=[FileExtensionValidator(['pdf'])], required=False)

    image_file = forms.ImageField(label='Imagens', widget=forms.ClearableFileInput({'multiple': False}), required=False)

    description = forms.CharField(label='Descrição', max_length=255)

    class Meta:
        model = PacientesMedia
        fields = ('pdf_file', 'image_file', 'description')

    def _raise_if_no_files_upload(self):
        text_file = self.cleaned_data.get('pdf_file')
        image_file = self.cleaned_data.get('image_file')

        if not media_form_ensure_file(text_file, image_file):
            raise forms.ValidationError('Nenhum arquivo selecionado!')

    def _raise_if_image_file_not_supported(self):
        image_file = self.cleaned_data.get('image_file')

        if image_file and not is_image_file_extension_valid(image_file):
            raise forms.ValidationError('Arquivo de imagem não suportado!')

    def clean(self):
        cleaned_data = super().clean()
        self._raise_if_no_files_upload()
        self._raise_if_image_file_not_supported()

        return cleaned_data
