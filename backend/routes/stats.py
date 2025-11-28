"""
Statistics API Routes
Provides aggregated statistics and reports
"""
from flask import Blueprint, request, jsonify
from models import db, Schedule, Rider, Horse, RecurringLesson
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get general statistics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Base counts
        total_riders = Rider.query.filter_by(active=True).count()
        total_horses = Horse.query.filter_by(active=True).count()
        total_lessons = RecurringLesson.query.filter_by(active=True).count()

        # Schedule query
        schedule_query = Schedule.query

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            schedule_query = schedule_query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            schedule_query = schedule_query.filter(Schedule.start_time <= end_dt)

        total_sessions = schedule_query.count()

        # Session status breakdown
        status_breakdown = db.session.query(
            Schedule.status,
            func.count(Schedule.id)
        ).group_by(Schedule.status).all()

        return jsonify({
            'total_riders': total_riders,
            'total_horses': total_horses,
            'total_lessons': total_lessons,
            'total_sessions': total_sessions,
            'status_breakdown': {status: count for status, count in status_breakdown}
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/statistics/riders/<int:rider_id>', methods=['GET'])
def get_rider_statistics(rider_id):
    """Get statistics for a specific rider"""
    try:
        rider = Rider.query.get_or_404(rider_id)

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query.filter_by(rider_id=rider_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        total_sessions = query.count()
        completed_sessions = query.filter_by(status='completed').count()

        return jsonify({
            'rider': rider.to_dict(),
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/statistics/horses/<int:horse_id>', methods=['GET'])
def get_horse_statistics(horse_id):
    """Get statistics for a specific horse"""
    try:
        horse = Horse.query.get_or_404(horse_id)

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query.filter_by(horse_id=horse_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        total_sessions = query.count()
        unique_riders = query.with_entities(Schedule.rider_id).distinct().count()

        return jsonify({
            'horse': horse.to_dict(),
            'total_sessions': total_sessions,
            'unique_riders': unique_riders
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/statistics/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson_statistics(lesson_id):
    """Get statistics for a specific recurring lesson"""
    try:
        lesson = RecurringLesson.query.get_or_404(lesson_id)

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Schedule.query.filter_by(lesson_id=lesson_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Schedule.start_time >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date + 'T23:59:59')
            query = query.filter(Schedule.start_time <= end_dt)

        total_sessions = query.count()
        unique_riders = query.with_entities(Schedule.rider_id).distinct().count()

        return jsonify({
            'lesson': lesson.to_dict(),
            'total_sessions': total_sessions,
            'unique_riders': unique_riders
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@stats_bp.route('/reports/<string:report_type>', methods=['GET'])
def get_report(report_type):
    """Generate specific report type"""
    try:
        if report_type == 'utilization':
            return get_utilization_report()
        elif report_type == 'attendance':
            return get_attendance_report()
        else:
            return jsonify({'error': 'Unknown report type'}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


def get_utilization_report():
    """Horse and rider utilization report"""
    horse_utilization = db.session.query(
        Horse.name,
        func.count(Schedule.id).label('session_count')
    ).outerjoin(Schedule).group_by(Horse.id).all()

    rider_utilization = db.session.query(
        Rider.name,
        func.count(Schedule.id).label('session_count')
    ).outerjoin(Schedule).group_by(Rider.id).all()

    return jsonify({
        'horses': [{'name': name, 'sessions': count} for name, count in horse_utilization],
        'riders': [{'name': name, 'sessions': count} for name, count in rider_utilization]
    }), 200


def get_attendance_report():
    """Attendance report by status"""
    attendance = db.session.query(
        Schedule.status,
        func.count(Schedule.id).label('count')
    ).group_by(Schedule.status).all()

    return jsonify({
        'attendance': [{'status': status, 'count': count} for status, count in attendance]
    }), 200


@stats_bp.route('/export/<string:data_type>', methods=['GET'])
def export_data(data_type):
    """Export data in specified format"""
    try:
        format_type = request.args.get('format', 'json')

        if data_type == 'riders':
            data = Rider.query.all()
            result = [r.to_dict() for r in data]
        elif data_type == 'horses':
            data = Horse.query.all()
            result = [h.to_dict() for h in data]
        elif data_type == 'schedule':
            data = Schedule.query.all()
            result = [s.to_dict() for s in data]
        elif data_type == 'lessons':
            data = RecurringLesson.query.all()
            result = [l.to_dict() for l in data]
        else:
            return jsonify({'error': 'Unknown data type'}), 400

        # For now, only JSON export is implemented
        # CSV/Excel export can be added later
        if format_type == 'json':
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Format not supported yet'}), 400

    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

