# Generated by Django 4.2.6 on 2024-02-21 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_rename_terapeuta_auxiliar1_cadastrogrupos_terapeuta_auxiliar'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Prontuarios',
            new_name='ProntuariosIndividuais',
        ),
    ]
