"""
Riders blueprint (formerly cavaliers)
All CRUD operations for riders
"""
from flask import Blueprint, request, jsonify
from models import db, Rider
from sqlalchemy import or_

riders_bp = Blueprint('riders', __name__)

@riders_bp.route('/riders', methods=['GET'])
def get_riders():
    """Get all active riders"""
    riders = Rider.query.filter_by(active=True).order_by(Rider.name).all()
    return jsonify([r.to_dict() for r in riders])

@riders_bp.route('/riders/<int:id>', methods=['GET'])
def get_rider(id):
    """Get a specific rider"""
    rider = Rider.query.get_or_404(id)
    return jsonify(rider.to_dict())

@riders_bp.route('/riders', methods=['POST'])
def create_rider():
    """Create a new rider"""
    data = request.json

    if not data.get('name'):
        return jsonify({'error': 'Rider name is required'}), 400

    rider = Rider(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone'),
        notes=data.get('notes')
    )

    db.session.add(rider)
    db.session.commit()

    return jsonify(rider.to_dict()), 201

@riders_bp.route('/riders/<int:id>', methods=['PUT'])
def update_rider(id):
    """Update an existing rider"""
    rider = Rider.query.get_or_404(id)
    data = request.json

    rider.name = data.get('name', rider.name)
    rider.email = data.get('email', rider.email)
    rider.phone = data.get('phone', rider.phone)
    rider.active = data.get('active', rider.active)
    rider.notes = data.get('notes', rider.notes)

    db.session.commit()
    return jsonify(rider.to_dict())

@riders_bp.route('/riders/<int:id>', methods=['DELETE'])
def delete_rider(id):
    """Soft delete a rider"""
    rider = Rider.query.get_or_404(id)
    rider.active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Rider deleted successfully'})

@riders_bp.route('/riders/search', methods=['GET'])
def search_riders():
    """Search riders"""
    query = request.args.get('q', '')
    riders = Rider.query.filter(
        Rider.active == True,
        or_(
            Rider.name.ilike(f'%{query}%'),
            Rider.email.ilike(f'%{query}%')
        )
    ).order_by(Rider.name).all()
    return jsonify([r.to_dict() for r in riders])
