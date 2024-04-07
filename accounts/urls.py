from django.urls import path
from .views import LoginWithOTP, logout_view, usuario_login

app_name = 'accounts'

urlpatterns = [
    path('login', usuario_login, name='login'),
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    path('logout/', logout_view, name='logout')
]
