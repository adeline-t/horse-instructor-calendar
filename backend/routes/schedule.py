"""
Schedule API Routes
Handles scheduled sessions (actual bookings)
"""
from flask import Blueprint, request, jsonify
from models import db, Schedule
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """Get schedule with optional date filtering"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        sessions = query.order_by(Schedule.start_time).all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/schedule/<int:session_id>', methods=['GET'])
def get_schedule_item(session_id):
    """Get single schedule session by ID"""
    try:
        session = Schedule.query.get_or_404(session_id)
        return jsonify(session.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 404


@schedule_bp.route('/schedule', methods=['POST'])
def create_schedule_item():
    """Create new scheduled session"""
    try:
        data = request.get_json()

        # Validate required fields
        required = ['start_time', 'end_time']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Parse ISO datetime strings
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))

        session = Schedule(
            rider_id=data.get('rider_id'),
            horse_id=data.get('horse_id'),
            lesson_id=data.get('lesson_id'),
            start_time=start_time,
            end_time=end_time,
            notes=data.get('notes'),
            status=data.get('status', 'scheduled')
        )

        db.session.add(session)
        db.session.commit()

        return jsonify(session.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/schedule/<int:session_id>', methods=['PUT'])
def update_schedule_item(session_id):
    """Update existing scheduled session"""
    try:
        session = Schedule.query.get_or_404(session_id)
        data = request.get_json()

        # Update fields
        if 'rider_id' in data:
            session.rider_id = data['rider_id']
        if 'horse_id' in data:
            session.horse_id = data['horse_id']
        if 'lesson_id' in data:
            session.lesson_id = data['lesson_id']
        if 'start_time' in data:
            session.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            session.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        if 'notes' in data:
            session.notes = data['notes']
        if 'status' in data:
            session.status = data['status']

        db.session.commit()
        return jsonify(session.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/schedule/<int:session_id>', methods=['DELETE'])
def delete_schedule_item(session_id):
    """Delete scheduled session"""
    try:
        session = Schedule.query.get_or_404(session_id)
        db.session.delete(session)
        db.session.commit()

        return jsonify({'message': 'Schedule session deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/schedule/rider', methods=['GET'])
def get_rider_schedule():
    """Get schedule for a specific rider"""
    try:
        rider_id = request.args.get('rider_id', type=int)
        if not rider_id:
            return jsonify({'error': 'rider_id is required'}), 400

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query.filter_by(rider_id=rider_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        sessions = query.order_by(Schedule.start_time).all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@schedule_bp.route('/schedule/horse', methods=['GET'])
def get_horse_schedule():
    """Get schedule for a specific horse"""
    try:
        horse_id = request.args.get('horse_id', type=int)
        if not horse_id:
            return jsonify({'error': 'horse_id is required'}), 400

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query.filter_by(horse_id=horse_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        sessions = query.order_by(Schedule.start_time).all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
