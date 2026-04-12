from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.clinic_service import ClinicService
from app.utils.security import role_required
from app.models import db, PatientProfile, MealLog, User
from app.dtos.schemas import PatientProfileUpdate
from pydantic import ValidationError
from datetime import datetime

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/patient/dashboard')
@login_required
@role_required('patient')
def dashboard():
    profile, assigned_meals, plan = ClinicService.get_patient_data(current_user.id)
    days_map = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
    today_str = days_map[datetime.now().weekday()]
    return render_template('patient_dashboard.html', profile=profile, assigned_meals=assigned_meals, plan=plan, today_str=today_str)

@patient_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def onboarding():
    if request.method == 'POST':
        try:
            data = PatientProfileUpdate(
                age=request.form.get('age'),
                current_weight=request.form.get('current_weight'),
                target_weight=request.form.get('target_weight'),
                height=request.form.get('height'),
                gender=request.form.get('gender'),
                objective=request.form.get('objective'),
                activity_level=request.form.get('activity_level')
            )
            ClinicService.update_patient_profile(current_user.id, data)
            return redirect(url_for('patient.dashboard'))
        except ValidationError:
            flash("Données d'onboarding invalides")
            
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('onboarding.html', profile=profile)

@patient_bp.route('/patient/program')
@login_required
@role_required('patient')
def program():
    from app.models import NutritionPlan
    plan = NutritionPlan.query.filter_by(patient_id=current_user.id).first()
    return render_template('program.html', plan=plan)

@patient_bp.route('/patient/meals')
@login_required
@role_required('patient')
def meals():
    logged_meals = MealLog.query.filter_by(user_id=current_user.id).order_by(MealLog.timestamp.desc()).all()
    profile, assigned_meals, plan = ClinicService.get_patient_data(current_user.id)
    return render_template('meals.html', logged_meals=logged_meals, assigned_meals=assigned_meals, plan=plan)

@patient_bp.route('/patient/profile', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def profile():
    if request.method == 'POST':
        try:
            data = PatientProfileUpdate(
                objective=request.form.get('objective'),
                age=request.form.get('age'),
                gender=request.form.get('gender'),
                current_weight=request.form.get('current_weight'),
                target_weight=request.form.get('target_weight'),
                height=request.form.get('height'),
                activity_level=request.form.get('activity_level')
            )
            ClinicService.update_patient_profile(current_user.id, data)
            flash('Profil mis à jour avec succès !')
            return redirect(url_for('patient.profile'))
        except ValidationError:
            flash("Données de profil invalides")
            
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    edit_mode = request.args.get('edit', False)
    if edit_mode:
        return render_template('onboarding.html', profile=profile, edit_mode=True)
    return render_template('profile_view.html', profile=profile)

@patient_bp.route('/messages')
@login_required
def messages():
    from app.models import Message
    if current_user.role == 'patient':
        doctor = User.query.filter_by(role='doctor').first()
        contacts = [doctor] if doctor else []
        contact_id = doctor.id if doctor else None
    else:
        contacts = User.query.filter_by(role='patient').all()
        contact_id = request.args.get('contact_id', type=int)
        if not contact_id and contacts: contact_id = contacts[0].id

    contact = User.query.get(contact_id) if contact_id else None
    all_msgs = []
    if contact:
        received = Message.query.filter_by(receiver_id=current_user.id, sender_id=contact.id).all()
        sent = Message.query.filter_by(sender_id=current_user.id, receiver_id=contact.id).all()
        all_msgs = sorted(received + sent, key=lambda x: x.timestamp)
        for m in received: m.is_read = True
        db.session.commit()

    return render_template('messages.html', messages=all_msgs, contact=contact, contacts=contacts)
