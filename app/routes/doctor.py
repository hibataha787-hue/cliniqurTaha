from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.clinic_service import ClinicService
from app.utils.security import role_required
from app.models import User
from app.dtos.schemas import UserUpdate
from pydantic import ValidationError

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctor/dashboard')
@login_required
@role_required('doctor')
def dashboard():
    patients = User.query.filter_by(role='patient').all()
    return render_template('doctor_dashboard.html', patients=patients)

@doctor_bp.route('/doctor/profile', methods=['GET', 'POST'])
@login_required
@role_required('doctor')
def profile():
    if request.method == 'POST':
        try:
            data = UserUpdate(
                full_name=request.form.get('full_name'),
                email=request.form.get('email'),
                password=request.form.get('password') if request.form.get('password') else None
            )
            ClinicService.update_profile(current_user, data)
            flash('Profil mis à jour avec succès !')
            return redirect(url_for('doctor.profile'))
        except ValidationError:
            flash("Données de profil invalides")
            
    return render_template('doctor_profile.html', user=current_user)

@doctor_bp.route('/doctor/patient/<int:patient_id>')
@login_required
@role_required('doctor')
def patient_details(patient_id):
    patient = User.query.get_or_404(patient_id)
    profile, assigned_meals, plan = ClinicService.get_patient_data(patient_id)
    return render_template('patient_details.html', patient=patient, profile=profile, assigned_meals=assigned_meals, plan=plan)

@doctor_bp.route('/doctor/save_plan', methods=['POST'])
@login_required
@role_required('doctor')
def save_plan():
    patient_id = request.form.get('patient_id')
    program_details = request.form.get('program_details')
    
    from app.models import db, NutritionPlan
    plan = NutritionPlan.query.filter_by(patient_id=patient_id).first()
    if not plan:
        plan = NutritionPlan(patient_id=patient_id, doctor_id=current_user.id)
        db.session.add(plan)
    
    plan.program_details = program_details
    db.session.commit()
    return redirect(url_for('doctor.patient_details', patient_id=patient_id))
