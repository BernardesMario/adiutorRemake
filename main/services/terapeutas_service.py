from django.contrib.auth.models import Group


def get_terapeutas_group() -> Group:
    terapeutas_group_id = 1  # Conferir ID

    terapeutas_group = Group.objects.get(id=terapeutas_group_id)

    return terapeutas_group


def get_administrativo_group() -> Group:
    administrativo_group_id = 2  # conferir ID

    administrativo_group = Group.objects.get(id=administrativo_group_id)

    return administrativo_group
