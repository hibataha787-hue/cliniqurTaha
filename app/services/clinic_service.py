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
            if data.objective is not None: profile.objective = data.objective
            if data.age is not None: profile.age = data.age
            if data.gender is not None: profile.gender = data.gender
            if data.current_weight is not None: profile.current_weight = data.current_weight
            if data.target_weight is not None: profile.target_weight = data.target_weight
            if data.height is not None: profile.height = data.height
            if data.activity_level is not None: profile.activity_level = data.activity_level
            if data.profession is not None: profile.profession = data.profession
            if data.ville is not None: profile.ville = data.ville
            if data.mode_de_vie is not None: profile.mode_de_vie = data.mode_de_vie
            if data.preference is not None: profile.preference = data.preference
            if data.liked_recipes is not None: profile.liked_recipes = data.liked_recipes
            if data.disliked_recipes is not None: profile.disliked_recipes = data.disliked_recipes
            if data.meals_per_day is not None: profile.meals_per_day = data.meals_per_day
            if data.waist_size is not None: profile.waist_size = data.waist_size
            if data.allergies is not None: profile.allergies = data.allergies
            if data.remarks is not None: profile.remarks = data.remarks
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
