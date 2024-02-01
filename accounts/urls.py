from django.urls import path
from .views import validate_otp

urlpatterns = [
    path('login-with-otp/', validate_otp, name='login-with-otp'),
    path('validate-otp/', validate_otp, name='validate-otp'),
]
