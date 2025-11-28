"""
Availability API Routes
Manages weekly availability slots
"""
from flask import Blueprint, request, jsonify
from models import db, Availability
from sqlalchemy.exc import SQLAlchemyError

availability_bp = Blueprint('availability', __name__)

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


@availability_bp.route('/availability', methods=['GET'])
def get_availability():
    """Get all availability slots grouped by day"""
    try:
        slots = Availability.query.order_by(Availability.day, Availability.start_time).all()

        # Group by day
        result = {day: [] for day in DAYS}
        for slot in slots:
            result[slot.day].append(slot.to_dict())

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@availability_bp.route('/availability/<string:day>', methods=['GET'])
def get_availability_by_day(day):
    """Get availability slots for a specific day"""
    try:
        if day.lower() not in DAYS:
            return jsonify({'error': 'Invalid day'}), 400

        slots = Availability.query.filter_by(day=day.lower()).order_by(Availability.start_time).all()
        return jsonify([s.to_dict() for s in slots]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@availability_bp.route('/availability/<string:day>', methods=['PUT'])
def update_availability_by_day(day):
    """Replace all availability slots for a specific day"""
    try:
        if day.lower() not in DAYS:
            return jsonify({'error': 'Invalid day'}), 400

        data = request.get_json()
        slots = data.get('slots', [])

        # Delete existing slots for this day
        Availability.query.filter_by(day=day.lower()).delete()

        # Add new slots
        for slot_data in slots:
            slot = Availability(
                day=day.lower(),
                start_time=slot_data['start'],
                end_time=slot_data['end']
            )
            db.session.add(slot)

        db.session.commit()

        # Return updated slots
        updated_slots = Availability.query.filter_by(day=day.lower()).order_by(Availability.start_time).all()
        return jsonify([s.to_dict() for s in updated_slots]), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@availability_bp.route('/availability', methods=['POST'])
def create_availability_slot():
    """Create a single availability slot"""
    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ['day', 'start_time', 'end_time']):
            return jsonify({'error': 'day, start_time, and end_time are required'}), 400

        if data['day'].lower() not in DAYS:
            return jsonify({'error': 'Invalid day'}), 400

        slot = Availability(
            day=data['day'].lower(),
            start_time=data['start_time'],
            end_time=data['end_time']
        )

        db.session.add(slot)
        db.session.commit()

        return jsonify(slot.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@availability_bp.route('/availability/<int:slot_id>', methods=['DELETE'])
def delete_availability_slot(slot_id):
    """Delete a specific availability slot"""
    try:
        slot = Availability.query.get_or_404(slot_id)
        db.session.delete(slot)
        db.session.commit()

        return jsonify({'message': 'Availability slot deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
