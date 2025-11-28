"""
Riders API Routes
Handles CRUD operations for riders
"""
from flask import Blueprint, request, jsonify
from models import db, Rider
from sqlalchemy.exc import SQLAlchemyError

riders_bp = Blueprint('riders', __name__)


@riders_bp.route('/riders', methods=['GET'])
def get_riders():
    """Get all riders"""
    try:
        riders = Rider.query.all()
        return jsonify([r.to_dict() for r in riders]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@riders_bp.route('/riders/<int:rider_id>', methods=['GET'])
def get_rider(rider_id):
    """Get single rider by ID"""
    try:
        rider = Rider.query.get_or_404(rider_id)
        return jsonify(rider.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 404


@riders_bp.route('/riders', methods=['POST'])
def create_rider():
    """Create new rider"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        rider = Rider(
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            level=data.get('level'),
            notes=data.get('notes'),
            active=data.get('active', True)
        )

        db.session.add(rider)
        db.session.commit()

        return jsonify(rider.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@riders_bp.route('/riders/<int:rider_id>', methods=['PUT'])
def update_rider(rider_id):
    """Update existing rider"""
    try:
        rider = Rider.query.get_or_404(rider_id)
        data = request.get_json()

        # Update fields
        if 'name' in data:
            rider.name = data['name']
        if 'email' in data:
            rider.email = data['email']
        if 'phone' in data:
            rider.phone = data['phone']
        if 'level' in data:
            rider.level = data['level']
        if 'notes' in data:
            rider.notes = data['notes']
        if 'active' in data:
            rider.active = data['active']

        db.session.commit()
        return jsonify(rider.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@riders_bp.route('/riders/<int:rider_id>', methods=['DELETE'])
def delete_rider(rider_id):
    """Delete rider (soft delete by setting active=False)"""
    try:
        rider = Rider.query.get_or_404(rider_id)

        # Soft delete
        rider.active = False
        db.session.commit()

        return jsonify({'message': 'Rider deactivated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@riders_bp.route('/riders/search', methods=['GET'])
def search_riders():
    """Search riders by name or email"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify([]), 200

        riders = Rider.query.filter(
            (Rider.name.ilike(f'%{query}%')) |
            (Rider.email.ilike(f'%{query}%'))
        ).all()

        return jsonify([r.to_dict() for r in riders]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
