from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from main.forms import validate_letters, validate_numbers
from django.core.validators import MinLengthValidator, MaxLengthValidator


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(validators=[
        validate_numbers, MinLengthValidator(limit_value=11), MaxLengthValidator(limit_value=11)])
    username = forms.CharField(validators=[validate_letters])

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")


class LoginWithOTPForm(forms.Form):
    # Unbound Form para validação the OTP
    otp = forms.CharField(validators=[MinLengthValidator(limit_value=6), MaxLengthValidator(limit_value=6)])
