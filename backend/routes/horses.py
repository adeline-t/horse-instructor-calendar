"""
Horses blueprint (formerly equides)
All CRUD operations for horses
"""
from flask import Blueprint, request, jsonify
from models import db, Horse
from sqlalchemy import or_

horses_bp = Blueprint('horses', __name__)

@horses_bp.route('/horses', methods=['GET'])
def get_horses():
    """Get all active horses"""
    horses = Horse.query.filter_by(active=True).order_by(Horse.name).all()
    return jsonify([h.to_dict() for h in horses])

@horses_bp.route('/horses/<int:id>', methods=['GET'])
def get_horse(id):
    """Get a specific horse"""
    horse = Horse.query.get_or_404(id)
    return jsonify(horse.to_dict())

@horses_bp.route('/horses', methods=['POST'])
def create_horse():
    """Create a new horse"""
    data = request.json

    if not data.get('name'):
        return jsonify({'error': 'Horse name is required'}), 400

    horse = Horse(
        name=data['name'],
        type=data.get('type'),
        owner_id=data.get('owner_id'),
        notes=data.get('notes')
    )

    db.session.add(horse)
    db.session.commit()

    return jsonify(horse.to_dict()), 201

@horses_bp.route('/horses/<int:id>', methods=['PUT'])
def update_horse(id):
    """Update an existing horse"""
    horse = Horse.query.get_or_404(id)
    data = request.json

    horse.name = data.get('name', horse.name)
    horse.type = data.get('type', horse.type)
    horse.owner_id = data.get('owner_id', horse.owner_id)
    horse.active = data.get('active', horse.active)
    horse.notes = data.get('notes', horse.notes)

    db.session.commit()
    return jsonify(horse.to_dict())

@horses_bp.route('/horses/<int:id>', methods=['DELETE'])
def delete_horse(id):
    """Soft delete a horse"""
    horse = Horse.query.get_or_404(id)
    horse.active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Horse deleted successfully'})

@horses_bp.route('/horses/search', methods=['GET'])
def search_horses():
    """Search horses"""
    query = request.args.get('q', '')
    horses = Horse.query.filter(
        Horse.active == True,
        or_(
            Horse.name.ilike(f'%{query}%'),
            Horse.type.ilike(f'%{query}%')
        )
    ).order_by(Horse.name).all()
    return jsonify([h.to_dict() for h in horses])
