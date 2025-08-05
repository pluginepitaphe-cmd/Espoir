from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from .user import db

class AnalyticsEvent(db.Model):
    """Modèle pour tracker les événements utilisateur"""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    geolocation = db.Column(db.String(100))  # "lat,lng"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='analytics_events')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'event_type': self.event_type,
            'event_data': json.loads(self.event_data) if self.event_data else {},
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'geolocation': self.geolocation,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class UserProfile(db.Model):
    """Profil utilisateur enrichi avec données IA"""
    __tablename__ = 'user_profiles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Informations entreprise enrichies
    industry_sector = db.Column(db.String(100))
    company_size = db.Column(db.String(20))  # startup, small, medium, large, enterprise
    annual_revenue = db.Column(db.BigInteger)
    linkedin_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    banner_url = db.Column(db.String(255))
    
    # Données de contact enrichies
    contact_info = db.Column(db.Text)  # JSON: phone, email, address, etc.
    
    # Préférences et intérêts
    interests = db.Column(db.Text)  # JSON array
    preferences = db.Column(db.Text)  # JSON object
    
    # Données IA et analytics
    ai_insights = db.Column(db.Text)  # JSON: recommendations, scores, etc.
    completion_score = db.Column(db.Integer, default=0)  # 0-100
    engagement_score = db.Column(db.Float, default=0.0)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='profile')
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'industry_sector': self.industry_sector,
            'company_size': self.company_size,
            'annual_revenue': self.annual_revenue,
            'linkedin_url': self.linkedin_url,
            'description': self.description,
            'logo_url': self.logo_url,
            'banner_url': self.banner_url,
            'contact_info': json.loads(self.contact_info) if self.contact_info else {},
            'interests': json.loads(self.interests) if self.interests else [],
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'ai_insights': json.loads(self.ai_insights) if self.ai_insights else {},
            'completion_score': self.completion_score,
            'engagement_score': self.engagement_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserInteraction(db.Model):
    """Modèle pour tracker les interactions entre utilisateurs"""
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # view, contact, meeting, etc.
    interaction_data = db.Column(db.Text)  # JSON with additional data
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    
    # Scoring IA
    compatibility_score = db.Column(db.Float)
    success_probability = db.Column(db.Float)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    initiator = db.relationship('User', foreign_keys=[initiator_id], backref='initiated_interactions')
    target = db.relationship('User', foreign_keys=[target_id], backref='received_interactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'initiator_id': self.initiator_id,
            'target_id': self.target_id,
            'interaction_type': self.interaction_type,
            'interaction_data': json.loads(self.interaction_data) if self.interaction_data else {},
            'status': self.status,
            'compatibility_score': self.compatibility_score,
            'success_probability': self.success_probability,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DailyMetrics(db.Model):
    """Métriques agrégées par jour"""
    __tablename__ = 'daily_metrics'
    
    date = db.Column(db.Date, primary_key=True)
    user_type = db.Column(db.String(20), primary_key=True)
    metric_name = db.Column(db.String(100), primary_key=True)
    metric_value = db.Column(db.Float, nullable=False)
    meta_data = db.Column(db.Text)  # JSON with additional context
    
    def to_dict(self):
        return {
            'date': self.date.isoformat() if self.date else None,
            'user_type': self.user_type,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'meta_data': json.loads(self.meta_data) if self.meta_data else {}
        }

class AIRecommendation(db.Model):
    """Recommandations générées par IA"""
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)  # user_match, product, event, etc.
    target_id = db.Column(db.Integer)  # ID de l'objet recommandé
    target_type = db.Column(db.String(50))  # user, product, event, etc.
    
    # Scoring et métadonnées IA
    confidence_score = db.Column(db.Float, nullable=False)
    reasoning = db.Column(db.Text)  # Explication de la recommandation
    recommendation_data = db.Column(db.Text)  # JSON avec données supplémentaires
    
    # Feedback utilisateur
    user_feedback = db.Column(db.String(20))  # accepted, rejected, ignored
    feedback_timestamp = db.Column(db.DateTime)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    user = db.relationship('User', backref='ai_recommendations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recommendation_type': self.recommendation_type,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'confidence_score': self.confidence_score,
            'reasoning': self.reasoning,
            'recommendation_data': json.loads(self.recommendation_data) if self.recommendation_data else {},
            'user_feedback': self.user_feedback,
            'feedback_timestamp': self.feedback_timestamp.isoformat() if self.feedback_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

