from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def get_selected_items(request):
    selected_items = request.POST.getlist('selected_items')

    return selected_items


def calculate_age(data_nascimento):
    today = date.today()
    age = relativedelta(today, data_nascimento)
    return age.years
