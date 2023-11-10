from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from main.forms import validate_letters, validate_numbers


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(validators=[validate_numbers])
    username = forms.CharField(validators=[validate_letters])

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")
