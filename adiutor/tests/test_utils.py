import pytest
from accounts.utils import hide_email, generate_otp


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
