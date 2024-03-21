from django.urls import path
from .views import LoginWithOTP, logout_view

app_name = 'account'

urlpatterns = [
    path('login-with-otp/', LoginWithOTP.as_view(), name='login-with-otp'),
    path('logout/', logout_view, name='logout')
]
