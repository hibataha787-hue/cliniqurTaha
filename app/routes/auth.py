from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, logout_user
from app.services.auth_service import AuthService
from app.dtos.schemas import UserLogin, UserCreate, OTPVerify
from pydantic import ValidationError
from app.extensions import limiter, mail

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        return redirect(url_for('patient.dashboard'))
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        try:
            data = UserLogin(
                username=request.form.get('username'),
                password=request.form.get('password')
            )
            result = AuthService.login_challenge(data.username, data.password, mail)
            
            if result['status'] == '2fa_required':
                session['temp_user_id'] = result['user_id']
                flash('Un code de vérification a été envoyé à votre email.')
                return redirect(url_for('patient.dashboard'))
            
            if result['status'] == 'success':
                if result['role'] == 'doctor':
                    return redirect(url_for('doctor.dashboard'))
                return redirect(url_for('patient.dashboard'))
            
            if result['status'] == 'error':
                flash(f"Erreur : {result.get('message')}")
            else:
                flash('Nom d\'utilisateur ou mot de passe invalide')
        except ValidationError:
            flash("Données de connexion invalides")
            
    return redirect(url_for('auth.index'))

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('temp_user_id')
    if not user_id:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        try:
            data = OTPVerify(otp_code=request.form.get('otp_code'))
            result = AuthService.verify_2fa(user_id, data.otp_code, mail)
            
            if result['status'] == 'success':
                session.pop('temp_user_id')
                if result['role'] == 'doctor':
                    return redirect(url_for('doctor.dashboard'))
                return redirect(url_for('patient.dashboard'))
            flash("Code invalide ou expiré.")
        except ValidationError:
            flash("Format de code invalide (6 chiffres)")
            
    return render_template('doctor.dashboard')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = UserCreate(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password'),
            full_name=request.form.get('full_name')
        )
        result = AuthService.register_patient(data)
        if result['status'] == 'success':
            return redirect(url_for('patient.onboarding'))
        flash('Utilisateur ou Email déjà existant')
    except ValidationError:
        flash("Données d'inscription invalides")
    return redirect(url_for('auth.index'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))
