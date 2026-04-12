from app.models import db, User, PatientProfile, MealLog, NutritionPlan, Message, AssignedMeal
from werkzeug.security import generate_password_hash
from app.utils.security import log_audit_event

class ClinicService:
    @staticmethod
    def get_patient_data(user_id):
        profile = PatientProfile.query.filter_by(user_id=user_id).first()
        assigned_meals = AssignedMeal.query.filter_by(patient_id=user_id).all()
        plan = NutritionPlan.query.filter_by(patient_id=user_id).first()
        return profile, assigned_meals, plan

    @staticmethod
    def update_profile(user, data):
        user.full_name = data.full_name
        user.email = data.email
        if data.password:
            user.password = generate_password_hash(data.password, method='scrypt')
        db.session.commit()
        log_audit_event(user.id, f"{user.role.capitalize()} Profile Update")

    @staticmethod
    def update_patient_profile(user_id, data):
        profile = PatientProfile.query.filter_by(user_id=user_id).first()
        if profile:
            if data.objective: profile.objective = data.objective
            if data.age: profile.age = data.age
            if data.gender: profile.gender = data.gender
            if data.current_weight: profile.current_weight = data.current_weight
            if data.target_weight: profile.target_weight = data.target_weight
            if data.height: profile.height = data.height
            if data.activity_level: profile.activity_level = data.activity_level
            db.session.commit()

    @staticmethod
    def assign_meal(doctor_id, data):
        new_meal = AssignedMeal(
            patient_id=data.patient_id,
            doctor_id=doctor_id,
            day_of_week=data.day_of_week,
            meal_type=data.meal_type,
            title=data.title,
            ingredients=data.ingredients,
            photo_url=data.photo_url or '',
            calories=data.calories,
            proteins=data.proteins,
            carbs=data.carbs,
            fats=data.fats
        )
        db.session.add(new_meal)
        db.session.commit()
        return True

    @staticmethod
    def delete_assigned_meal(meal_id):
        meal = AssignedMeal.query.get(meal_id)
        if meal:
            db.session.delete(meal)
            db.session.commit()
            return True
        return False

    @staticmethod
    def send_message(sender_id, data):
        new_msg = Message(
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            content=data.content
        )
        db.session.add(new_msg)
        db.session.commit()
        return True
