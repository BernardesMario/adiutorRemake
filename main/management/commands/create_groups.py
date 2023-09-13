import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adiutor.settings')
django.setup()


class Command(BaseCommand):
    def create_group(self, group_name):
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Grupo '{group_name}' criado com sucesso"))
        return group

    def create_permission(self, content_type, codename, name):
        permission, created = Permission.objects.get_or_create(
            content_type=content_type,
            codename=codename,
            defaults={'name': name}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Permissão '{name}' criada com sucesso"))
        return permission

    def assign_permissions_to_group(self, group, permissions):
        for permission in permissions:
            group.permissions.add(permission)
            self.stdout.write(self.style.SUCCESS(f"Permissão '{permission}' delegada ao grupo '{group.name}' com sucesso!"))

    def handle(self, *args, **options):
        permission_data = [
            {
                'content_type_name': 'main',
                'model_name': 'prontuarios',
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
                'model_name': 'conveniosaceitos',
                'permission_codename': 'add_convenio',
                'permission_name': 'Adicionar Novo Convenio (Administrativos)',
            },
            # Adiciona aqui novas permissões
        ]

        try:
            terapeutas_group = self.create_group('Terapeutas')
            administrativo_group = self.create_group('Administrativos')

            for data in permission_data:
                try:
                    content_type = ContentType.objects.get(
                        app_label=data['content_type_name'],
                        model=data['model_name']
                    )
                except ContentType.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Content type '{data['content_type_name']}' não existe. Pulando..."))
                    continue

                permission = self.create_permission(
                    content_type,
                    data['permission_codename'],
                    data['permission_name']
                )

                if 'Terapeutas' in data['permission_name']:
                    self.assign_permissions_to_group(terapeutas_group, [permission])
                elif 'Administrativos' in data['permission_name']:
                    self.assign_permissions_to_group(administrativo_group, [permission])

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ocorreu um erro: {e}'))


if __name__ == "__main__":
    Command().handle()
