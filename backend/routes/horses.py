"""
Horses API Routes
Handles CRUD operations for horses
"""
from flask import Blueprint, request, jsonify
from models import db, Horse
from sqlalchemy.exc import SQLAlchemyError

horses_bp = Blueprint('horses', __name__)


@horses_bp.route('/horses', methods=['GET'])
def get_horses():
    """Get all horses"""
    try:
        horses = Horse.query.all()
        return jsonify([h.to_dict() for h in horses]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500


@horses_bp.route('/horses/<int:horse_id>', methods=['GET'])
def get_horse(horse_id):
    """Get single horse by ID"""
    try:
        horse = Horse.query.get_or_404(horse_id)
        return jsonify(horse.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 404


@horses_bp.route('/horses', methods=['POST'])
def create_horse():
    """Create new horse"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        horse = Horse(
            name=data['name'],
            type=data.get('type'),
            owner_id=data.get('owner_id'),
            notes=data.get('notes'),
            active=data.get('active', True)
        )

        db.session.add(horse)
        db.session.commit()

        return jsonify(horse.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@horses_bp.route('/horses/<int:horse_id>', methods=['PUT'])
def update_horse(horse_id):
    """Update existing horse"""
    try:
        horse = Horse.query.get_or_404(horse_id)
        data = request.get_json()

        # Update fields
        if 'name' in data:
            horse.name = data['name']
        if 'type' in data:
            horse.type = data['type']
        if 'owner_id' in data:
            horse.owner_id = data['owner_id']
        if 'notes' in data:
            horse.notes = data['notes']
        if 'active' in data:
            horse.active = data['active']

        db.session.commit()
        return jsonify(horse.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@horses_bp.route('/horses/<int:horse_id>', methods=['DELETE'])
def delete_horse(horse_id):
    """Delete horse (soft delete by setting active=False)"""
    try:
        horse = Horse.query.get_or_404(horse_id)

        # Soft delete
        horse.active = False
        db.session.commit()

        return jsonify({'message': 'Horse deactivated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@horses_bp.route('/horses/search', methods=['GET'])
def search_horses():
    """Search horses by name or type"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify([]), 200

        horses = Horse.query.filter(
            (Horse.name.ilike(f'%{query}%')) |
            (Horse.type.ilike(f'%{query}%'))
        ).all()

        return jsonify([h.to_dict() for h in horses]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
