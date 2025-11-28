"""
Schedule blueprint (formerly planning)
All CRUD operations for schedule/sessions
"""
from flask import Blueprint, request, jsonify
from models import db, Schedule
from datetime import datetime

schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """Get schedule with optional date filtering"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Schedule.query

    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    sessions = query.order_by(Schedule.start_time).all()
    return jsonify([s.to_dict() for s in sessions])

@schedule_bp.route('/schedule/<int:id>', methods=['GET'])
def get_schedule_item(id):
    """Get a specific schedule item"""
    session = Schedule.query.get_or_404(id)
    return jsonify(session.to_dict())

@schedule_bp.route('/schedule', methods=['POST'])
def create_schedule():
    """Create a new schedule item"""
    data = request.json

    if not data.get('start_time') or not data.get('end_time'):
        return jsonify({'error': 'Start time and end time are required'}), 400

    session = Schedule(
        rider_id=data.get('rider_id'),
        horse_id=data.get('horse_id'),
        lesson_type=data.get('lesson_type'),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        notes=data.get('notes'),
        status=data.get('status', 'scheduled')
    )

    db.session.add(session)
    db.session.commit()

    return jsonify(session.to_dict()), 201

@schedule_bp.route('/schedule/<int:id>', methods=['PUT'])
def update_schedule(id):
    """Update an existing schedule item"""
    session = Schedule.query.get_or_404(id)
    data = request.json

    session.rider_id = data.get('rider_id', session.rider_id)
    session.horse_id = data.get('horse_id', session.horse_id)
    session.lesson_type = data.get('lesson_type', session.lesson_type)
    session.status = data.get('status', session.status)
    session.notes = data.get('notes', session.notes)

    if data.get('start_time'):
        session.start_time = datetime.fromisoformat(data['start_time'])
    if data.get('end_time'):
        session.end_time = datetime.fromisoformat(data['end_time'])

    db.session.commit()
    return jsonify(session.to_dict())

@schedule_bp.route('/schedule/<int:id>', methods=['DELETE'])
def delete_schedule(id):
    """Delete a schedule item"""
    session = Schedule.query.get_or_404(id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Schedule deleted successfully'})

@schedule_bp.route('/schedule/rider', methods=['GET'])
def get_rider_schedule():
    """Get schedule for a specific rider"""
    rider_id = request.args.get('rider_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not rider_id:
        return jsonify({'error': 'rider_id is required'}), 400

    query = Schedule.query.filter_by(rider_id=rider_id)

    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    sessions = query.order_by(Schedule.start_time).all()
    return jsonify([s.to_dict() for s in sessions])

@schedule_bp.route('/schedule/horse', methods=['GET'])
def get_horse_schedule():
    """Get schedule for a specific horse"""
    horse_id = request.args.get('horse_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not horse_id:
        return jsonify({'error': 'horse_id is required'}), 400

    query = Schedule.query.filter_by(horse_id=horse_id)

    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    sessions = query.order_by(Schedule.start_time).all()
    return jsonify([s.to_dict() for s in sessions])
