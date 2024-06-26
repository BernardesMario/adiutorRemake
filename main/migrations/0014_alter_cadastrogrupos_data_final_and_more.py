# Generated by Django 4.2.6 on 2024-02-27 18:05

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_cadastrogrupos_data_final_and_more'),
    ]

    operations = [
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
            name='nascimento',
            field=models.DateField(help_text='dd/mm/aaaa', validators=[main.models.validate_date_past], verbose_name='Data de Nascimento'),
        ),
        migrations.AlterField(
            model_name='cadastroprofissionais',
            name='nascimento_data',
            field=models.DateField(help_text='dd/mm/aaaa', validators=[main.models.validate_date_past], verbose_name='Data de Nascimento'),
        ),
        migrations.AlterField(
            model_name='presencasgrupo',
            name='data',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data'),
        ),
        migrations.AlterField(
            model_name='prontuariosgrupos',
            name='data_consulta',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data da Consulta'),
        ),
        migrations.AlterField(
            model_name='prontuariosindividuais',
            name='data_consulta',
            field=models.DateField(validators=[main.models.validate_date_past], verbose_name='Data da Consulta'),
        ),
    ]
