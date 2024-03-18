from accounts.utils import hide_email, generate_otp
from main.utils import calculate_age
from datetime import date
from unittest.mock import patch
from model_bakery import baker
import pytest


def test_hide_email():
    # Arrange
    str_email = str('t**t@email.com')
    email_to_hide = str('test@email.com')

    # Act
    hidden_email = hide_email(email_to_hide)

    # Assert
    assert hidden_email == str_email


def test_otp_lenght():
    # Arrange

    # Act
    otp = generate_otp()

    # Assert
    assert not len(otp) != 6


def test_age_calculator():
    # Arrange
    idade_esperada = int(20)
    data_nascimento = date(2004, 2, 20)

    # Act
    idade_calculada = calculate_age(data_nascimento)

    # Assert
    assert idade_esperada == idade_calculada


@pytest.mark.django_db
def test_prontuario_numero_creator_all_zero():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2400001'
    ultimo_prontuario = '2400000'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado


@pytest.mark.django_db
def test_prontuario_numero_creator_zero_one():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2400002'
    ultimo_prontuario = '2400001'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado


@pytest.mark.django_db
def test_prontuario_numero_creator_zero_niner():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2400010'
    ultimo_prontuario = '2400009'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado


@pytest.mark.django_db
def test_prontuario_numero_creator_hundred():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2400101'
    ultimo_prontuario = '2400100'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado


@pytest.mark.django_db
def test_prontuario_numero_creator_nine_nine():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2400100'
    ultimo_prontuario = '2400099'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado


@pytest.mark.django_db
def test_prontuario_numero_creator_random():
    # Arrange
    from main.models import create_prontuario_numero
    from main.models import CadastroPacientes

    numero_esperado = '2411112'
    ultimo_prontuario = '2411111'
    mock_last_prontuario = baker.make(CadastroPacientes, prontuario_numero=ultimo_prontuario)

    # Act
    with patch('main.models.CadastroPacientes.objects') as mock_objects:
        mock_objects.order_by.return_value.first.return_value = mock_last_prontuario
        numero_gerado = create_prontuario_numero()

    # Assert
    assert numero_gerado == numero_esperado
