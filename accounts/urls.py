from django.urls import path
from .views import LoginWithOTP

app_name = 'account'

urlpatterns = [
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
]
