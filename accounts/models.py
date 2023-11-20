from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
import re


def validate_numbers(value):
    if not re.match("^[0-9]+$", str(value)):
        raise ValidationError("Este campo pode conter apenas números")


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    # Incluido para possibilidade de 2SA por SMS
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='Telefone', validators=[
        validate_numbers, MinLengthValidator(limit_value=11), MaxLengthValidator(limit_value=11)
    ])
    otp = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.username
