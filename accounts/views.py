from django.shortcuts import render, redirect
from django.contrib.auth import login
from main.services.terapeutas_services import get_terapeutas_group, get_administrativo_group
from main.services.users_service import redirect_logged_user_to_home
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import generate_otp, send_otp_email, hide_email
from .models import CustomUser
from .forms import LoginWithOTPForm


class LoginWithOTP(APIView):
    def get(self, request):
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
        hidden_mail_sent_to = hide_email(email)
        mail_sent_message = str(f"Insira o código de uso único enviado ao email: {hidden_mail_sent_to} para continuar")
        otp_form = LoginWithOTPForm

        #return Response({'message': f'Seu código de uso único foi enviado ao email: {hidden_mail_sent_to}!'},
        #                status=status.HTTP_200_OK)

        context = {
            'email_sent_to': email,
            'mail_sent_message': mail_sent_message,
            'otp_form': otp_form,
        }

        return render(request, 'login_with_otp.html', context)

    def post(self, request):
        email = request.data.get('email', '')
        otp = request.data.get('otp', '')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Não existe um usuário cadastrado com esse e-mail!'},
                            status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            user.otp = None  # Reset OTP
            user.save()

            login(request, user)

            terapeutas_group = get_terapeutas_group()
            administrativo_group = get_administrativo_group()

            return redirect_logged_user_to_home(user, terapeutas_group, administrativo_group)

            # return Response({'success': 'Usuário autenticado com sucesso!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Código de uso único inválido.'}, status=status.HTTP_400_BAD_REQUEST)
