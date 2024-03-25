from django import template

register = template.Library()


@register.filter
def format_phone_number(phone_number: str) -> str:

    if not phone_number or len(phone_number) !=11:

        return phone_number

    formatted_number = f"({phone_number[0:2]}) {phone_number[2:7]} - {phone_number[7:]}"

    return formatted_number


@register.filter
def format_cpf(cpf_number: str) -> str:

    if not cpf_number or len(cpf_number) != 11:

        return cpf_number

    formatted_cpf = f"{cpf_number[:3]}.{cpf_number[3:6]}.{cpf_number[6:9]}.{cpf_number[9:]}"

    return formatted_cpf
