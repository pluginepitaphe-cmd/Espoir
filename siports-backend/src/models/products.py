from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from .user import db

class ProductEnhanced(db.Model):
    """Modèle pour les produits/services des exposants (version enrichie)"""
    __tablename__ = 'products_enhanced'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations de base
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    
    # Détails commerciaux
    price_range = db.Column(db.String(50))  # budget, standard, premium, enterprise
    currency = db.Column(db.String(3), default='EUR')
    availability = db.Column(db.String(50))  # available, limited, pre_order, discontinued
    
    # Médias
    images = db.Column(db.Text)  # JSON array of image URLs
    videos = db.Column(db.Text)  # JSON array of video URLs
    documents = db.Column(db.Text)  # JSON array of document URLs
    
    # Spécifications techniques
    specifications = db.Column(db.Text)  # JSON object
    features = db.Column(db.Text)  # JSON array
    tags = db.Column(db.Text)  # JSON array for search
    
    # Statut et modération
    status = db.Column(db.String(20), default='draft')  # draft, pending, approved, rejected
    moderation_notes = db.Column(db.Text)
    
    # Analytics
    views_count = db.Column(db.Integer, default=0)
    interest_count = db.Column(db.Integer, default=0)  # bookmarks, likes
    contact_requests = db.Column(db.Integer, default=0)
    
    # SEO et recherche
    seo_keywords = db.Column(db.Text)  # JSON array
    search_vector = db.Column(db.Text)  # For full-text search
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relations
    user = db.relationship('User', backref='products')
    
    def to_dict(self, include_analytics=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'price_range': self.price_range,
            'currency': self.currency,
            'availability': self.availability,
            'images': json.loads(self.images) if self.images else [],
            'videos': json.loads(self.videos) if self.videos else [],
            'documents': json.loads(self.documents) if self.documents else [],
            'specifications': json.loads(self.specifications) if self.specifications else {},
            'features': json.loads(self.features) if self.features else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'status': self.status,
            'seo_keywords': json.loads(self.seo_keywords) if self.seo_keywords else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_analytics:
            data.update({
                'views_count': self.views_count,
                'interest_count': self.interest_count,
                'contact_requests': self.contact_requests
            })
            
        return data

class ProductView(db.Model):
    """Tracking des vues de produits"""
    __tablename__ = 'product_views'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products_enhanced.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100))
    
    # Données de la vue
    view_duration = db.Column(db.Integer)  # en secondes
    interaction_data = db.Column(db.Text)  # JSON: scroll, clicks, etc.
    referrer = db.Column(db.String(255))
    
    # Géolocalisation et device
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    device_type = db.Column(db.String(20))  # mobile, tablet, desktop
    
    # Métadonnées
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    product = db.relationship('ProductEnhanced', backref='views')
    viewer = db.relationship('User', backref='product_views')

class ProductInterest(db.Model):
    """Intérêts/bookmarks des utilisateurs pour les produits"""
    __tablename__ = 'product_interests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products_enhanced.id'), nullable=False)
    
    # Type d'intérêt
    interest_type = db.Column(db.String(20), default='bookmark')  # bookmark, like, want_info
    notes = db.Column(db.Text)  # Notes privées de l'utilisateur
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Statut de suivi
    follow_up_status = db.Column(db.String(20), default='pending')  # pending, contacted, meeting_scheduled, closed
    follow_up_notes = db.Column(db.Text)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', backref='product_interests')
    product = db.relationship('ProductEnhanced', backref='interests')
    
    # Contrainte d'unicité
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_interest'),)

class ProductCategory(db.Model):
    """Catégories de produits avec hiérarchie"""
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Hiérarchie
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    level = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    
    # Métadonnées
    icon = db.Column(db.String(100))  # CSS class or icon name
    color = db.Column(db.String(7))  # Hex color
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    parent = db.relationship('ProductCategory', remote_side=[id], backref='children')
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'icon': self.icon,
            'color': self.color,
            'is_active': self.is_active
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children if child.is_active]
            
        return data

