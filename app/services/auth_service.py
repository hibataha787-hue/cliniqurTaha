from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from app.models import db, User, PatientProfile
from app.utils.mail import send_otp_email, send_login_notification
from app.utils.security import log_audit_event
from datetime import datetime

class AuthService:
    @staticmethod
    def login_challenge(username, password, mail):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.is_2fa_enabled or user.role == 'doctor':
                if send_otp_email(user, mail):
                    return {"status": "2fa_required", "user_id": user.id}
                return {"status": "error", "message": "Erreur d'envoie de l'email"}
            
            login_user(user)
            log_audit_event(user.id, "Login Success")
            send_login_notification(user, mail)
            return {"status": "success", "role": user.role}
        
        log_audit_event(None, "Login Failed", f"Username: {username}")
        return {"status": "invalid"}

    @staticmethod
    def verify_2fa(user_id, code, mail):
        user = User.query.get(user_id)
        if user and user.otp_code == code and datetime.utcnow() < user.otp_expiry:
            user.otp_code = None
            db.session.commit()
            login_user(user)
            log_audit_event(user.id, "2FA Success")
            send_login_notification(user, mail)
            return {"status": "success", "role": user.role}
        return {"status": "invalid"}

    @staticmethod
    def register_patient(data):
        if User.query.filter_by(username=data.username).first() or \
           User.query.filter_by(email=data.email).first():
            return {"status": "exists"}
        
        new_user = User(
            username=data.username,
            email=data.email,
            password=generate_password_hash(data.password, method='scrypt'),
            role='patient',
            full_name=data.full_name
        )
        db.session.add(new_user)
        db.session.commit()
        
        profile = PatientProfile(user_id=new_user.id)
        db.session.add(profile)
        db.session.commit()
        
        login_user(new_user)
        return {"status": "success"}
