"""
Recurring Lessons API Routes
Handles CRUD operations for recurring lessons
"""
from flask import Blueprint, request, jsonify
from models import db, RecurringLesson
from sqlalchemy.exc import SQLAlchemyError

recurring_lessons_bp = Blueprint('recurring_lessons', __name__)


@recurring_lessons_bp.route('/recurring-lessons', methods=['GET'])
def get_recurring_lessons():
    """Get all recurring lessons"""
    try:
        lessons = RecurringLesson.query.all()
        return jsonify([l.to_dict() for l in lessons]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@recurring_lessons_bp.route('/recurring-lessons/<int:lesson_id>', methods=['GET'])
def get_recurring_lesson(lesson_id):
    """Get single recurring lesson by ID"""
    try:
        lesson = RecurringLesson.query.get_or_404(lesson_id)
        return jsonify(lesson.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 404


@recurring_lessons_bp.route('/recurring-lessons', methods=['POST'])
def create_recurring_lesson():
    """Create new recurring lesson"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['name', 'day', 'time', 'duration']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        lesson = RecurringLesson(
            name=data['name'],
            day=data['day'],
            time=data['time'],
            duration=data['duration'],
            max_riders=data.get('max_riders'),
            level=data.get('level'),
            notes=data.get('notes'),
            active=data.get('active', True)
        )

        db.session.add(lesson)
        db.session.commit()

        return jsonify(lesson.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@recurring_lessons_bp.route('/recurring-lessons/<int:lesson_id>', methods=['PUT'])
def update_recurring_lesson(lesson_id):
    """Update existing recurring lesson"""
    try:
        lesson = RecurringLesson.query.get_or_404(lesson_id)
        data = request.get_json()

        # Update fields
        if 'name' in data:
            lesson.name = data['name']
        if 'day' in data:
            lesson.day = data['day']
        if 'time' in data:
            lesson.time = data['time']
        if 'duration' in data:
            lesson.duration = data['duration']
        if 'max_riders' in data:
            lesson.max_riders = data['max_riders']
        if 'level' in data:
            lesson.level = data['level']
        if 'notes' in data:
            lesson.notes = data['notes']
        if 'active' in data:
            lesson.active = data['active']

        db.session.commit()
        return jsonify(lesson.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@recurring_lessons_bp.route('/recurring-lessons/<int:lesson_id>', methods=['DELETE'])
def delete_recurring_lesson(lesson_id):
    """Delete recurring lesson (soft delete)"""
    try:
        lesson = RecurringLesson.query.get_or_404(lesson_id)

        # Soft delete
        lesson.active = False
        db.session.commit()

        return jsonify({'message': 'Recurring lesson deactivated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
