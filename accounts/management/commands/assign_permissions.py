import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adiutor.settings')
django.setup()


class Command(BaseCommand):
    """Delega permissões para os Grupos de Usuários
    Terapeutas e Administrativos
    """

    def assign_permissions_to_group(self, group, permissions):
        for permission in permissions:
            group.permissions.add(permission)
            self.stdout.write(self.style.SUCCESS(f"Permissão '{permission}' delegada ao grupo:"
                                                 f" '{group.name}' com sucesso!"))

    def handle(self, *args, **options):
        permission_data = [
            {
                'content_type_name': 'main',
                'model_name': 'prontuariosindividuais',
                'permission_codename': 'add_entry',
                'permission_name': 'Adicionar entradas em prontuários (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastroprofissionais',
                'permission_codename': 'add_terapeuta',
                'permission_name': 'Adicionar novos Usuários (Administrativos)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastropacientes',
                'permission_codename': 'deslig_pac',
                'permission_name': 'Desligar Paciente (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastropacientes',
                'permission_codename': 'transfer_pac',
                'permission_name': 'Transferir Paciente (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastropacientes',
                'permission_codename': 'add_pac_group',
                'permission_name': 'Adicionar Paciente a Grupo (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'conveniosaceitos',
                'permission_codename': 'add_convenio',
                'permission_name': 'Adicionar Novo Convenio (Administrativos)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'prontuariosgrupos',
                'permission_codename': 'add_entry_group',
                'permission_name': 'Adicionar entradas em prontuários de Grupo (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastrogrupos',
                'permission_codename': 'transfer_group',
                'permission_name': 'Transferir Grupo (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastrogrupos',
                'permission_codename': 'deslig_group',
                'permission_name': 'Desligar Grupo (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastropacientes',
                'permission_codename': 'remove_pac_from_group',
                'permission_name': 'Remover Paciente de um Grupo (Terapeutas)',
            },
            {
                'content_type_name': 'main',
                'model_name': 'cadastrogrupos',
                'permission_codename': 'create_group',
                'permission_name': 'Cadastrar Grupo (Terapeutas)',
            },
            # Adicione aqui novas permissões
            '''
            {
                'content_type_name': 'APP',
                'model_name': 'MODEL',
                'permission_codename': 'CODENAME',
                'permission_name': 'NAME',
            },
            '''
        ]

        try:
            terapeutas_group = Group.objects.get(name='Terapeutas')
            administrativo_group = Group.objects.get(name='Administrativo')

            for data in permission_data:
                try:
                    content_type = ContentType.objects.get(
                        app_label=data['content_type_name'],
                        model=data['model_name']
                    )
                except ContentType.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Content type '{data['content_type_name']}'"
                                                       f"for '{data['model_name']}'"
                                                       f" não existe. Pulando..."))
                    continue

                permission, created = Permission.objects.get_or_create(
                    content_type=content_type,
                    codename=data['permission_codename'],
                    defaults={'name': data['permission_name']}
                )

                if 'Terapeutas' in data['permission_name']:
                    self.assign_permissions_to_group(terapeutas_group, [permission])
                elif 'Administrativos' in data['permission_name']:
                    self.assign_permissions_to_group(administrativo_group, [permission])

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ocorreu um erro: {e}'))


if __name__ == "__main__":
    Command().handle()
