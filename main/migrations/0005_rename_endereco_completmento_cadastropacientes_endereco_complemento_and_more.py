# Generated by Django 4.2.6 on 2023-12-04 16:09

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_cadastroprofissionais_endereco_numero'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cadastropacientes',
            old_name='endereco_completmento',
            new_name='endereco_complemento',
        ),
        migrations.AddField(
            model_name='cadastropacientes',
            name='cep_numero',
            field=models.CharField(default='88000111', max_length=8, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=8)], verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='cadastropacientes',
            name='cidade',
            field=models.CharField(default='florianopolis', max_length=100, validators=[main.models.validate_letters, django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='cadastroprofissionais',
            name='cep_numero',
            field=models.CharField(default='88000111', max_length=8, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=8)], verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='cadastroprofissionais',
            name='cidade',
            field=models.CharField(default='florianopolis', max_length=20, validators=[main.models.validate_letters, django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='cadastroprofissionais',
            name='nascimento_data',
            field=models.DateField(default=django.utils.timezone.now, help_text='dd/mm/aaaa', validators=[main.models.validate_date_past], verbose_name='Data de Nascimento'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='cep_numero',
            field=models.CharField(default='88000111', max_length=8, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=8)], verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='cidade',
            field=models.CharField(default='florianopolis', max_length=20, validators=[main.models.validate_letters, django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='cnpj_numero',
            field=models.CharField(default=72722222000155, max_length=14, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=14)], verbose_name='CNPJ'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='endereco_bairro',
            field=models.CharField(default='centro', max_length=50, validators=[django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Bairro'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='endereco_complemento',
            field=models.CharField(default='apt 500', max_length=100, validators=[django.core.validators.MinLengthValidator(limit_value=4)], verbose_name='Complemento'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='endereco_numero',
            field=models.CharField(default='123', max_length=7, validators=[main.models.validate_numbers], verbose_name='Número'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='endereco_rua',
            field=models.CharField(default='rua do centro', max_length=100, validators=[django.core.validators.MinLengthValidator(limit_value=10)], verbose_name='Endereço'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='observacoes',
            field=models.TextField(blank=True, null=True, verbose_name='Observações'),
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='responsavel_contato',
            field=models.CharField(default='jorge', max_length=50, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Contato do Resposável'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conveniosaceitos',
            name='telefone_numero',
            field=models.CharField(default=48990003232, max_length=11, validators=[main.models.validate_numbers, django.core.validators.MinLengthValidator(limit_value=11)], verbose_name='Telefone'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cadastrogrupos',
            name='data_final',
            field=models.DateField(blank=True, help_text='dd/mm/aaaa', null=True, validators=[main.models.validate_date_past], verbose_name='Data do Desligamento'),
        ),
        migrations.AlterField(
            model_name='cadastropacientes',
            name='data_final',
            field=models.DateField(blank=True, help_text='dd/mm/aaaa', null=True, validators=[main.models.validate_date_past], verbose_name='Data do Desligamento'),
        ),
        migrations.AlterField(
            model_name='cadastropacientes',
            name='endereco_bairro',
            field=models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(limit_value=3)], verbose_name='Bairro'),
        ),
        migrations.AlterField(
            model_name='cadastropacientes',
            name='endereco_numero',
            field=models.CharField(max_length=7, validators=[main.models.validate_numbers], verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='cadastropacientes',
            name='nascimento',
            field=models.DateField(help_text='dd/mm/aaaa', validators=[main.models.validate_date_past], verbose_name='Data de Nascimento'),
        ),
        migrations.AlterField(
            model_name='presencasgrupo',
            name='data',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data'),
        ),
        migrations.AlterField(
            model_name='prontuarios',
            name='data_consulta',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data da Consulta'),
        ),
        migrations.AlterField(
            model_name='prontuariosgrupos',
            name='data_consulta',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data da Consulta'),
        ),
    ]
