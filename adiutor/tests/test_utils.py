from accounts.utils import hide_email, generate_otp
from main.utils import calculate_age
from datetime import date
from main.models import CadastroPacientes
from model_bakery import baker


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
