from flask_mail import Message
from main import mail

BASE_URL = "http://localhost:5000"

def enviar_email_recuperacao(user, token):
    link = f"{BASE_URL}/reset-password?token={token}"

    msg = Message(
        subject="Recuperação de Password",
        sender="noreply.safedeposit@gmail.com",
        recipients=[user.email]
    )

    msg.body = f"""
Hello {user.username},

Click the link below to reset your password:

{link}

This link expires in 15 minutes.

If you did not request this action, ignore this email.
"""

    mail.send(msg)

def enviar_email_apagar_cofre(user, vault_id, token):
    link = f"{BASE_URL}/delete-vault-confirm?vault_id={vault_id}&token={token}"

    msg = Message(
        subject="Confirm Vault Deletion",
        sender="noreply.safedeposit@gmail.com",
        recipients=[user.email]
    )

    msg.body = f"""
Hello {user.username},

Click the link below to confirm the deletion of your vault:

{link}

This link expires in 15 minutes.

If you did not request this action, ignore this email.
"""

    mail.send(msg)