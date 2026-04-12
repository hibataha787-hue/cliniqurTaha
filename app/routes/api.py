from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.clinic_service import ClinicService
from app.dtos.schemas import MealAssign, MessageSend
from pydantic import ValidationError

api_bp = Blueprint('api', __name__)

@api_bp.route('/doctor/assign_meal', methods=['POST'])
@login_required
def assign_meal():
    if current_user.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        data = MealAssign(**request.json)
        ClinicService.assign_meal(current_user.id, data)
        return jsonify({'status': 'success'})
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400

@api_bp.route('/doctor/delete_assigned_meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_assigned_meal(meal_id):
    if current_user.role != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    if ClinicService.delete_assigned_meal(meal_id):
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Meal not found'}), 404

@api_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    try:
        data = MessageSend(**request.json)
        ClinicService.send_message(current_user.id, data)
        return jsonify({'status': 'success'})
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.errors()}), 400

@api_bp.route('/log_meal', methods=['POST'])
@login_required
def log_meal():
    from app.models import db, MealLog
    data = request.json
    new_meal = MealLog(
        user_id=current_user.id,
        meal_type=data.get('meal_type'),
        content=data.get('content'),
        calories=data.get('calories', 0)
    )
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({'status': 'success'})
