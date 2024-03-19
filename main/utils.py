from django.db.models.fields.files import File, ImageFile
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Union
from django.http import HttpRequest


def get_selected_items(request: HttpRequest) -> List[Union[int, str]]:
    """Retorna uma lista com dados obtidos de um POST
    """
    if request.method != 'POST':
        pass

    selected_items = request.POST.getlist('selected_items')

    return selected_items


def calculate_age(data_nascimento: date) -> int:
    """ Calcula idade através de uma data fornecida
    """
    today = date.today()
    age = relativedelta(today, data_nascimento)

    return age.years


def is_date_not_future(data_field: date) -> bool:
    """ Validação de campos de data para assegurar
    que data não está no futuro
    """

    hoje = date.today()
    is_valid = hoje >= data_field

    return is_valid


def certificado_year_validator(input_year: int) -> bool:
    """ Validação para o campo 'ano_conclusao' da model HistoricoAcademico
    """

    min_value = 1924
    entry_value = input_year

    is_valid = entry_value > min_value

    return is_valid


def media_form_ensure_file(text_file: File, image_file: ImageFile) -> bool:

    if not text_file and not image_file:
        return False

    return True


def is_image_file_extension_valid(file: ImageFile) -> bool:

    if file.name.split('.')[-1] not in ['jpg', 'jpeg', 'png', 'gif']:
        return False

    return True
