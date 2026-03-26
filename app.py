import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, PatientProfile, MealLog, NutritionPlan, Message, AssignedMeal

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nutrition-clinic-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            return redirect(url_for('patient_dashboard'))
        
        flash('Invalid username or password')
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    
    if User.query.filter_by(username=username).first() or \
       User.query.filter_by(email=email).first():
        flash('Username or Email already exists')
        return redirect(url_for('index'))
    
    new_user = User(
        username=username, 
        email=email,
        phone=phone,
        password=generate_password_hash(password, method='scrypt'),
        role='patient',
        full_name=full_name
    )
    db.session.add(new_user)
    db.session.commit()
    
    profile = PatientProfile(user_id=new_user.id)
    db.session.add(profile)
    db.session.commit()
    
    login_user(new_user)
    return redirect(url_for('onboarding'))

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.role != 'patient':
        return redirect(url_for('index'))
        
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        profile.objective = request.form.get('objective')
        profile.age = request.form.get('age')
        profile.gender = request.form.get('gender')
        profile.current_weight = request.form.get('current_weight')
        profile.target_weight = request.form.get('target_weight')
        profile.height = request.form.get('height')
        profile.activity_level = request.form.get('activity_level')
        db.session.commit()
        return redirect(url_for('patient_dashboard'))
        
    return render_template('onboarding.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('index'))
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    assigned_meals = AssignedMeal.query.filter_by(patient_id=current_user.id).all()
    plan = NutritionPlan.query.filter_by(patient_id=current_user.id).first()
    
    # Calculate today's localized day string
    days_map = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
    from datetime import datetime
    today_str = days_map[datetime.now().weekday()]
    
    return render_template('patient_dashboard.html', profile=profile, assigned_meals=assigned_meals, plan=plan, today_str=today_str)

@app.route('/patient/program')
@login_required
def patient_program():
    if current_user.role != 'patient':
        return redirect(url_for('index'))
    plan = NutritionPlan.query.filter_by(patient_id=current_user.id).first()
    return render_template('program.html', plan=plan)

@app.route('/patient/meals')
@login_required
def patient_meals():
    if current_user.role != 'patient':
        return redirect(url_for('index'))
    logged_meals = MealLog.query.filter_by(user_id=current_user.id).order_by(MealLog.timestamp.desc()).all()
    assigned_meals = AssignedMeal.query.filter_by(patient_id=current_user.id).all()
    plan = NutritionPlan.query.filter_by(patient_id=current_user.id).first()
    return render_template('meals.html', logged_meals=logged_meals, assigned_meals=assigned_meals, plan=plan)

@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
def patient_profile():
    if current_user.role != 'patient':
        return redirect(url_for('index'))
    profile = PatientProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        profile.objective = request.form.get('objective')
        profile.age = request.form.get('age')
        profile.gender = request.form.get('gender')
        profile.current_weight = request.form.get('current_weight')
        profile.target_weight = request.form.get('target_weight')
        profile.height = request.form.get('height')
        profile.activity_level = request.form.get('activity_level')
        db.session.commit()
        flash('Profil mis à jour avec succès !')
        return redirect(url_for('patient_profile'))
        
    edit_mode = request.args.get('edit', False)
    if edit_mode:
        return render_template('onboarding.html', profile=profile, edit_mode=True)
    return render_template('profile_view.html', profile=profile)

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('index'))
    patients = User.query.filter_by(role='patient').all()
    return render_template('doctor_dashboard.html', patients=patients)

@app.route('/doctor/patient/<int:patient_id>')
@login_required
def patient_details(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('index'))
    patient = User.query.get_or_404(patient_id)
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    assigned_meals = AssignedMeal.query.filter_by(patient_id=patient_id).all()
    plan = NutritionPlan.query.filter_by(patient_id=patient_id).first()
    return render_template('patient_details.html', patient=patient, profile=profile, assigned_meals=assigned_meals, plan=plan)

@app.route('/doctor/patient/<int:patient_id>/program_builder')
@login_required
def program_builder(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('index'))
    patient = User.query.get_or_404(patient_id)
    assigned_meals = AssignedMeal.query.filter_by(patient_id=patient_id).all()
    return render_template('doctor_program_builder.html', patient=patient, assigned_meals=assigned_meals)

@app.route('/api/doctor/assign_meal', methods=['POST'])
@login_required
def assign_meal():
    if current_user.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    new_meal = AssignedMeal(
        patient_id=data.get('patient_id'),
        doctor_id=current_user.id,
        day_of_week=data.get('day_of_week'),
        meal_type=data.get('meal_type'),
        title=data.get('title'),
        ingredients=data.get('ingredients'),
        photo_url=data.get('photo_url', ''),
        calories=int(data.get('calories', 0) or 0),
        proteins=int(data.get('proteins', 0) or 0),
        carbs=int(data.get('carbs', 0) or 0),
        fats=int(data.get('fats', 0) or 0)
    )
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/doctor/delete_assigned_meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_assigned_meal(meal_id):
    if current_user.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    meal = AssignedMeal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/doctor/save_plan', methods=['POST'])
@login_required
def save_plan():
    if current_user.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    patient_id = data.get('patient_id')
    program_details = data.get('program_details')
    
    plan = NutritionPlan.query.filter_by(patient_id=patient_id).first()
    if not plan:
        plan = NutritionPlan(patient_id=patient_id, doctor_id=current_user.id)
        db.session.add(plan)
    
    plan.program_details = program_details
    db.session.commit()
    return redirect(url_for('patient_details', patient_id=patient_id))

@app.route('/api/log_meal', methods=['POST'])
@login_required
def log_meal():
    data = request.json
    new_meal = MealLog(
        user_id=current_user.id,
        meal_type=data.get('meal_type'),
        content=data.get('content'),
        calories=data.get('calories')
    )
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/messages')
@login_required
def messages():
    if current_user.role == 'patient':
        doctor = User.query.filter_by(role='doctor').first()
        contacts = [doctor] if doctor else []
        contact_id = doctor.id if doctor else None
    else:
        contacts = User.query.filter_by(role='patient').all()
        contact_id = request.args.get('contact_id', type=int)
        if not contact_id and contacts:
            contact_id = contacts[0].id

    contact = User.query.get(contact_id) if contact_id else None
    all_msgs = []
    
    if contact:
        received = Message.query.filter_by(receiver_id=current_user.id, sender_id=contact.id).all()
        sent = Message.query.filter_by(sender_id=current_user.id, receiver_id=contact.id).all()
        all_msgs = sorted(received + sent, key=lambda x: x.timestamp)
        # Mark received as read
        for m in received:
            m.is_read = True
        db.session.commit()

    return render_template('messages.html', messages=all_msgs, contact=contact, contacts=contacts)

@app.route('/api/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.json
    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=data.get('receiver_id'),
        content=data.get('content')
    )
    db.session.add(new_msg)
    db.session.commit()
    return jsonify({'status': 'success'})

with app.app_context():
    db.create_all()
    # Seed fixed doctor account
    if not User.query.filter_by(username='taha').first():
        doctor = User(
            username='taha',
            email='doctor@clinique.com',
            password=generate_password_hash('taha123', method='scrypt'),
            role='doctor',
            full_name='Dr. Taha'
        )
        db.session.add(doctor)
        db.session.commit()
        print("Doctor account seeded: taha / taha123")

if __name__ == '__main__':
    app.run(debug=True)
