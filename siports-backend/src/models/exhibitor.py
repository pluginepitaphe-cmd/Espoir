from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Exhibitor(db.Model):
    __tablename__ = 'exhibitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    country = db.Column(db.String(50))
    category = db.Column(db.String(50))
    size = db.Column(db.String(20))
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    website = db.Column(db.String(200))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    specialties = db.Column(db.Text)  # JSON string
    products = db.Column(db.Text)     # JSON string
    certifications = db.Column(db.Text)  # JSON string
    is_partner = db.Column(db.Boolean, default=False)
    partner_level = db.Column(db.String(20))  # platine, or, argent, bronze
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    appointments = db.relationship('Appointment', backref='exhibitor', lazy=True)
    messages = db.relationship('Message', backref='exhibitor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'country': self.country,
            'category': self.category,
            'size': self.size,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'website': self.website,
            'email': self.email,
            'phone': self.phone,
            'specialties': self.specialties,
            'products': self.products,
            'certifications': self.certifications,
            'is_partner': self.is_partner,
            'partner_level': self.partner_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey('exhibitors.id'), nullable=False)
    visitor_name = db.Column(db.String(100), nullable=False)
    visitor_email = db.Column(db.String(100), nullable=False)
    visitor_company = db.Column(db.String(100))
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50))  # presentation, demo, reunion, etc.
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, proposed
    message = db.Column(db.Text)
    proposed_date = db.Column(db.DateTime)  # Si l'exposant propose une autre date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'exhibitor_id': self.exhibitor_id,
            'visitor_name': self.visitor_name,
            'visitor_email': self.visitor_email,
            'visitor_company': self.visitor_company,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'message': self.message,
            'proposed_date': self.proposed_date.isoformat() if self.proposed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey('exhibitors.id'), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(100), nullable=False)
    sender_company = db.Column(db.String(100))
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'exhibitor_id': self.exhibitor_id,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'sender_company': self.sender_company,
            'subject': self.subject,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

