"""
Availability blueprint (formerly disponibilites)
All CRUD operations for availability slots
"""
from flask import Blueprint, request, jsonify
from models import db, Availability

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/availability', methods=['GET'])
def get_availability():
    """Get availability slots grouped by day"""
    slots = Availability.query.all()

    # Group by day
    result = {}
    for slot in slots:
        if slot.day not in result:
            result[slot.day] = []
        result[slot.day].append(slot.to_dict())

    return jsonify(result)

@availability_bp.route('/availability/<string:day>', methods=['GET'])
def get_day_availability(day):
    """Get availability for a specific day"""
    slots = Availability.query.filter_by(day=day).all()
    return jsonify([s.to_dict() for s in slots])

@availability_bp.route('/availability/<string:day>', methods=['PUT'])
def update_day_availability(day):
    """Update availability for a specific day"""
    # Delete existing slots for this day
    Availability.query.filter_by(day=day).delete()

    # Add new slots
    data = request.json
    slots = data.get('slots', [])

    for slot_data in slots:
        slot = Availability(
            day=day,
            start_time=slot_data['start'],
            end_time=slot_data['end'],
            occupied=slot_data.get('occupied', False)
        )
        db.session.add(slot)

    db.session.commit()
    return jsonify({'success': True, 'message': f'Availability updated for {day}'})

@availability_bp.route('/availability', methods=['POST'])
def create_availability_slot():
    """Create a new availability slot"""
    data = request.json

    slot = Availability(
        day=data['day'],
        start_time=data['start'],
        end_time=data['end'],
        occupied=data.get('occupied', False)
    )

    db.session.add(slot)
    db.session.commit()

    return jsonify(slot.to_dict()), 201
