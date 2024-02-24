from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Union
from django.http import HttpRequest


def get_selected_items(request: HttpRequest) -> List[Union[int, str]]:
    """Retorna uma lista com dados obtidos de um POST
    """
    selected_items = request.POST.getlist('selected_items')

    return selected_items


def calculate_age(data_nascimento: date) -> int:
    """ Calcula idade através de uma data fornecida
    """
    today = date.today()
    age = relativedelta(today, data_nascimento)

    return age.years
