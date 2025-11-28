"""
Recurring lessons blueprint (formerly cours_recurrents)
All CRUD operations for recurring lessons
"""
from flask import Blueprint, request, jsonify
from models import db, RecurringLesson

recurring_lessons_bp = Blueprint('recurring_lessons', __name__)

@recurring_lessons_bp.route('/recurring-lessons', methods=['GET'])
def get_recurring_lessons():
    """Get all active recurring lessons"""
    lessons = RecurringLesson.query.filter_by(active=True).all()
    return jsonify([l.to_dict() for l in lessons])

@recurring_lessons_bp.route('/recurring-lessons/<int:id>', methods=['GET'])
def get_recurring_lesson(id):
    """Get a specific recurring lesson"""
    lesson = RecurringLesson.query.get_or_404(id)
    return jsonify(lesson.to_dict())

@recurring_lessons_bp.route('/recurring-lessons', methods=['POST'])
def create_recurring_lesson():
    """Create a new recurring lesson"""
    data = request.json

    lesson = RecurringLesson(
        rider_id=data.get('rider_id'),
        horse_id=data.get('horse_id'),
        day=data.get('day'),
        time=data.get('time'),
        duration=data.get('duration
