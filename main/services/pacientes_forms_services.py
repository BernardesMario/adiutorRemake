import re
from datetime import date
from typing import Union
from main.models import ConveniosAceitos
from main.services.pacientes_services import get_ultima_entrada_prontuarios_paciente_individual
from main.utils import calculate_age


def is_paciente_menor_acompanhado(nascimento: date, responsavel_legal: Union[str, None]) -> bool:
    """ Validação para garantir que menores de idade
    estejam acompanhados por um responsável legal
    """
    idade_paciente = calculate_age(nascimento)

    if idade_paciente < 18 and not responsavel_legal:
        return False

    return True


def cpf_responsavel_required_when_responsavel(responsavel_legal: Union[str, None],
                                              cpf_responsavel_legal: Union[str, None]) -> bool:
    """ Validação para garantir que quando há responsável legal
    o campo CPF do responsável também esteja preenchido
    """
    if responsavel_legal and not cpf_responsavel_legal:
        return False

    return True


def is_data_nova_consulta_individual_valid(numero: str, data_nova_consulta: date) -> bool:
    """ Validação para garantir que a data de uma nova entrada em prontuário
    de Pacientes individuais não é anterior a data da última consulta registrada
    """

    ultima_entrada_data = get_ultima_entrada_prontuarios_paciente_individual(numero)

    if ultima_entrada_data is None:
        return True

    is_valid = ultima_entrada_data and data_nova_consulta > ultima_entrada_data

    return is_valid


def ensure_paciente_convenio_carteirinha(convenio: ConveniosAceitos, carteirinha_convenio: str) -> bool:
    """ Garante que pacientes de convênios possuam o campo de numero da Carteirinha preenchido
    """
    particular_str = 'Particular'
    convenio_nome_str = str(convenio.nome)

    if convenio_nome_str != particular_str and not carteirinha_convenio:
        return False

    return True


def validate_responsavel_nome_if_responsavel(responsavel_name: Union[str, None]):
    if responsavel_name and not re.match(r"^[A-Za-z\sáéíóúãõâêîôûàèìòùçÁÉÍÓÚÃÕÂÊÎÔÛÀÈÌÒÙÇ]+$", responsavel_name, re.U):
        return False

    return True
