import secrets
from datetime import datetime, timedelta

def gerar_token_recuperacao(user):
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expira = datetime.now() + timedelta(minutes=15)
    return token


def validar_token(user, token):
    if user.reset_token != token:
        return False
    
    if datetime.now() > user.reset_token_expira:
        return False

    return True


def reset_password(user, token, nova_password):
    if not validar_token(user, token):
        raise Exception("Token inválido ou expirado")

    user.palavrapass = nova_password

    user.reset_token = None
    user.reset_token_expira = None

def gerar_delete_token():
    token = secrets.token_urlsafe(32)
    expiration = datetime.now() + timedelta(minutes=15)

    return token, expiration

