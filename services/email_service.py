from flask_mail import Message
from main import mail

def enviar_email_recuperacao(user, token):
    link = f"http://localhost:5000/reset-password?token={token}"

    msg = Message(
        subject="Recuperação de Password",
        sender="noreply.safedeposit@gmail.com",
        recipients=[user.email]
    )

    msg.body = f"""
Olá {user.username},

Clique no link para redefinir a sua password:

{link}

Este link expira em 15 minutos.

Se não fez este pedido, ignore este email.
"""

    mail.send(msg)