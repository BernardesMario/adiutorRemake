# Generated by Django 4.2.5 on 2023-09-07 18:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CadastroPacientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do Paciente')),
                ('prontuario_numero', models.CharField(max_length=7, unique=True, verbose_name='Nº de Prontuario')),
                ('nascimento', models.DateField(help_text='dd/mm/aaaa', verbose_name='Data de Nascimento')),
                ('responsavel_legal', models.CharField(blank=True, max_length=100, null=True, verbose_name='Responsável Legal')),
                ('data_inicio', models.DateField(help_text='dd/mm/aaaa', verbose_name='Data de Inicio')),
                ('data_final', models.DateField(blank=True, help_text='dd/mm/aaaa', null=True, verbose_name='Data do Desligamento')),
                ('cpf', models.CharField(max_length=11, unique=True, verbose_name='CPF')),
                ('carteirinha_convenio', models.CharField(blank=True, max_length=50, null=True, verbose_name='Número do Convênio')),
                ('telefone_numero', models.CharField(max_length=11, verbose_name='Telefone')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
            },
        ),
        migrations.CreateModel(
            name='CadastroProfissionais',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('conselho_codigo', models.CharField(max_length=5, unique=True, verbose_name='CRP')),
                ('unimed_codigo', models.CharField(max_length=6, unique=True, verbose_name='Número cadastro Unimed')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('telefone_numero', models.CharField(max_length=11, verbose_name='Telefone')),
                ('usuario_codigo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Terapeutas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Terapeuta',
                'verbose_name_plural': 'Terapeutas',
            },
        ),
        migrations.CreateModel(
            name='ConveniosAceitos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, verbose_name='Convênio')),
            ],
            options={
                'verbose_name': 'Convênio',
                'verbose_name_plural': 'Convênios',
            },
        ),
        migrations.CreateModel(
            name='Prontuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_entrada', models.DateField(auto_now_add=True, verbose_name='Data da Entrada')),
                ('data_consulta', models.DateField(verbose_name='Data da Consulta')),
                ('entrada', models.TextField(verbose_name='Parecer')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prontuarios', to='main.cadastroprofissionais', to_field='nome', verbose_name='Terapeuta')),
                ('numero', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paciente', to='main.cadastropacientes', to_field='prontuario_numero', verbose_name='Nº de Prontuário')),
            ],
            options={
                'verbose_name': 'Prontuário',
                'verbose_name_plural': 'Prontuários',
                'permissions': [('add_entry', 'Adicionar entradas em prontuários')],
            },
        ),
        migrations.AddField(
            model_name='cadastropacientes',
            name='convenio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pacientes', to='main.conveniosaceitos'),
        ),
        migrations.AddField(
            model_name='cadastropacientes',
            name='terapeuta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pacientes', to='main.cadastroprofissionais'),
        ),
    ]
