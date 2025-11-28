"""
Database models for Equestrian Management System
Replaces JSON file storage with MySQL
All French terms translated to English:
- cavaliers → riders
- equides → horses
- cours_recurrents → recurring_lessons
- disponibilites → availability
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Rider(db.Model):
    """Rider model (formerly cavaliers)"""
    __tablename__ = 'riders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'active': self.active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Horse(db.Model):
    """Horse model (formerly equides)"""
    __tablename__ = 'horses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # Type of horse (breed, discipline, etc.)
    owner_id = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'owner_id': self.owner_id,
            'active': self.active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RecurringLesson(db.Model):
    """Recurring lesson model (formerly cours_recurrents)"""
    __tablename__ = 'recurring_lessons'

    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'))
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'), nullable=True)
    day = db.Column(db.String(20))  # Day of week (Monday, Tuesday, etc.)
    time = db.Column(db.String(10))  # Time (HH:MM format)
    duration = db.Column(db.Integer)  # Duration in minutes
    lesson_type = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(7))  # Hex color for calendar display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rider = db.relationship('Rider', backref='recurring_lessons')
    horse = db.relationship('Horse', backref='recurring_lessons')

    def to_dict(self):
        return {
            'id': self.id,
            'rider_id': self.rider_id,
            'rider_name': self.rider.name if self.rider else None,
            'horse_id': self.horse_id,
            'horse_name': self.horse.name if self.horse else None,
            'day': self.day,
            'time': self.time,
            'duration': self.duration,
            'lesson_type': self.lesson_type,
            'active': self.active,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Schedule(db.Model):
    """Schedule model (formerly planning)"""
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('riders.id'))
    horse_id = db.Column(db.Integer, db.ForeignKey('horses.id'))
    lesson_type = db.Column(db.String(50))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rider = db.relationship('Rider', backref='sessions')
    horse = db.relationship('Horse', backref='sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'rider_id': self.rider_id,
            'rider_name': self.rider.name if self.rider else None,
            'horse_id': self.horse_id,
            'horse_name': self.horse.name if self.horse else None,
            'lesson_type': self.lesson_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Availability(db.Model):
    """Availability model (formerly disponibilites)"""
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)  # Day of week
    start_time = db.Column(db.String(10), nullable=False)  # HH:MM format
    end_time = db.Column(db.String(10), nullable=False)  # HH:MM format
    occupied = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'start': self.start_time,
            'end': self.end_time,
            'occupied': self.occupied
        }
