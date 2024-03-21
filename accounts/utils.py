import random
import string
from django.core.mail import send_mail
from django.conf import settings


# TODO: mover para camada services
def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp


def send_otp_email(email, otp):
    subject = 'Seu código para Login no Adiutor'
    message = f'Seu código de uso único é: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def hide_email(email):

    username, domain = email.split('@')

    hidden_username = username[0] + '*' * (len(username) - 2) + username[-1]

    hidden_email = hidden_username + '@' + domain

    return hidden_email
