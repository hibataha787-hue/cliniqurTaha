from flask_mail import Message as MailMessage
from flask import current_app
import random
from datetime import datetime, timedelta
from app.models import db

def send_otp_email(user, mail):
    if user.otp_code and user.otp_expiry and datetime.utcnow() < user.otp_expiry:
        otp = user.otp_code
    else:
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
    
    msg = MailMessage("Votre code de vérification - Clinique Taha",
                  recipients=[user.email])
    msg.body = f"Votre code de sécurité est : {otp}. Il expire dans 10 minutes."
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"\n[DEV MODE] Impossible d'envoyer l'email : {e}")
        print(f"[DEV MODE] CODE OTP POUR {user.username} : {otp}\n")
        return True # On retourne True pour permettre le test local avec l'OTP console

def send_login_notification(user, mail):
    msg = MailMessage("Nouvelle connexion détectée - Clinique Taha",
                  recipients=[user.email])
    msg.body = f"Bonjour {user.full_name}, une nouvelle connexion a été détectée sur votre compte le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    try:
        mail.send(msg)
    except:
        pass
