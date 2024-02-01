from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework import status

from main.services.terapeutas_service import get_terapeutas_group, get_administrativo_group
from main.services.users_service import redirect_logged_user_to_home
from .utils import generate_otp, send_otp_email
from .models import CustomUser


def validate_otp(request):
    if request.method == 'POST':
        return validate_otp_when_post(request)

    email = request.GET.get('email', '')
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Não há usuários cadastrados com este email!.'},
                        status=status.HTTP_404_NOT_FOUND)

    otp = generate_otp()
    user.otp = otp
    user.save()

    send_otp_email(email, otp)
    # send_otp_phone(phone_number, otp)

    # TODO criar template de otp
    return Response({'message': 'Seu código de uso único foi enviado ao email registrado!'},
                    status=status.HTTP_200_OK)


def validate_otp_when_post(request):
    email = request.data.get('email', '')
    otp = request.data.get('otp', '')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Não existe um usuário cadastrado com esse e-mail!'},
                        status=status.HTTP_404_NOT_FOUND)

    if user.otp == otp:
        user.otp = None  # Reset the OTP field after successful validation
        user.save()

        login(request, user)

        terapeutas_group = get_terapeutas_group()
        administrativo_group = get_administrativo_group()

        # TODO: implementar timeout de sessao
        # Authenticate the user and create or get an authentication token
        # token, _ = Token.objects.get_or_create(user=user)

        # return Response({'token': token.key}, status=status.HTTP_200_OK)
        return redirect_logged_user_to_home(user, terapeutas_group, administrativo_group)
    else:
        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
