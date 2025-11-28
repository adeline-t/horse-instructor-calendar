"""
Statistics blueprint (formerly stats)
All statistical queries and reports
"""
from flask import Blueprint, request, jsonify
from models import db, Horse, Rider, Schedule, Availability
from sqlalchemy import func

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get general statistics"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Build query for sessions
    query = Schedule.query
    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    total_sessions = query.count()
    active_horses = Horse.query.filter_by(active=True).count()
    active_riders = Rider.query.filter_by(active=True).count()

    # Count available slots
    all_slots = Availability.query.all()
    available_slots = sum(1 for s in all_slots if not s.occupied)

    return jsonify({
        'total_sessions': total_sessions,
        'active_horses': active_horses,
        'active_riders': active_riders,
        'available_slots': available_slots,
        'period': {
            'start': start_date,
            'end': end_date
        }
    })

@stats_bp.route('/statistics/riders/<int:rider_id>', methods=['GET'])
def get_rider_statistics(rider_id):
    """Get statistics for a specific rider"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Schedule.query.filter_by(rider_id=rider_id)
    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    total_sessions = query.count()

    # Get lesson type breakdown
    lesson_types = db.session.query(
        Schedule.lesson_type,
        func.count(Schedule.id).label('count')
    ).filter_by(rider_id=rider_id).group_by(Schedule.lesson_type).all()

    return jsonify({
        'rider_id': rider_id,
        'total_sessions': total_sessions,
        'lesson_types': {lt[0]: lt[1] for lt in lesson_types if lt[0]},
        'period': {'start': start_date, 'end': end_date}
    })

@stats_bp.route('/statistics/horses/<int:horse_id>', methods=['GET'])
def get_horse_statistics(horse_id):
    """Get statistics for a specific horse"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Schedule.query.filter_by(horse_id=horse_id)
    if start_date:
        query = query.filter(Schedule.start_time >= start_date)
    if end_date:
        query = query.filter(Schedule.end_time <= end_date)

    total_sessions = query.count()

    return jsonify({
        'horse_id': horse_id,
        'total_sessions': total_sessions,
        'period': {'start': start_date, 'end': end_date}
    })

@stats_bp
