from django.urls import path
from .views import LoginWithOTP

# from .views import validate_otp


app_name = 'account'

urlpatterns = [
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    # path('login-with-otp/', validate_otp, name='login-with-otp'),
    # path('validate-otp/', validate_otp, name='validate-otp'),
]
