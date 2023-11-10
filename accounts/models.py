from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_numer = models.CharField(max_length=11, unique=True, verbose_name='Telefone')
    # Incluido para possibilidade de 2SA por SMS
    otp = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.username
