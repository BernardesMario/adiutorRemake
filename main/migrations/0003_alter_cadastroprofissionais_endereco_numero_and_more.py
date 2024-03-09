# Generated by Django 4.2.6 on 2023-11-13 14:00

import django.core.validators
from django.db import migrations, models
import main.models
import main.utils


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_endereco_completmento_cadastroprofissionais_endereco_complemento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastroprofissionais',
            name='endereco_numero',
            field=models.CharField(max_length=7, validators=[main.models.validate_letters], verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='cadastroprofissionais',
            name='rg_numero',
            field=models.CharField(max_length=12, validators=[django.core.validators.MinLengthValidator(limit_value=6)], verbose_name='Número RG'),
        ),
    ]
