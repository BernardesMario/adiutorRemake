import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Union
from django.core.exceptions import ValidationError
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
    """ Validação de campos de data
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
