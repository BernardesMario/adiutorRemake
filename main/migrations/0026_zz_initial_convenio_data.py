# Generated by Django 4.2.6 on 2024-05-13 18:55

from django.db import migrations, models


def create_initial_convenio(apps, schema_editor):
    ConveniosAceitos = apps.get_model('main', 'ConveniosAceitos')
    convenio = ConveniosAceitos.objects.create(
        nome="Particular",
        cnpj_numero="11111111111114",
        endereco_rua="",
        endereco_bairro="",
        endereco_numero="",
        endereco_complemento="",
        cidade="",
        cep_numero="",
        responsavel_contato="",
        telefone_numero="",
        email="",
        observacoes="",
    )
    return convenio


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_alter_cadastrogrupos_terapeuta_auxiliar_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_convenio),
    ]
