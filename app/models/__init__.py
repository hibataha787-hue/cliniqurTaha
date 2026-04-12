from flask import Flask
from flask_login import UserMixin
from datetime import datetime
from app.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'patient' or 'doctor'
    full_name = db.Column(db.String(100))
    profile = db.relationship('PatientProfile', backref='user', lazy=True)
    received_messages = db.relationship('Message', backref='receiver', primaryjoin='User.id==Message.receiver_id', lazy=True)
    otp_code = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    is_2fa_enabled = db.Column(db.Boolean, default=False)

class PatientProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    age = db.Column(db.Integer)
    current_weight = db.Column(db.Float)
    target_weight = db.Column(db.Float)
    height = db.Column(db.Float)
    gender = db.Column(db.String(10))
    objective = db.Column(db.String(50)) # 'Perte de Poids', 'Prise de Masse', 'Manger Sainement'
    activity_level = db.Column(db.String(50))
    health_metrics = db.Column(db.Text) # JSON string

class MealLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.String(50)) # Breakfast, Lunch, etc.
    content = db.Column(db.Text)
    calories = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class NutritionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class AssignedMeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.String(20)) # Lundi, Mardi, etc.
    meal_type = db.Column(db.String(50)) # Petit-déjeuner, Déjeuner, Dîner, Collation
    title = db.Column(db.String(200))
    ingredients = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    calories = db.Column(db.Integer)
    proteins = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
