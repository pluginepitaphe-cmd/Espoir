from src.models.user import db
from datetime import datetime
import os

class Document(db.Model):
    """Modèle pour stocker les documents et plaquettes téléchargés"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Taille en bytes
    mime_type = db.Column(db.String(100), nullable=False)
    file_extension = db.Column(db.String(10), nullable=False)
    
    # Métadonnées
    category = db.Column(db.String(100), nullable=False)  # 'brochure', 'catalog', 'technical_sheet', 'event_program'
    document_type = db.Column(db.String(50), nullable=False)  # 'exhibitor', 'event', 'product'
    
    # Relations
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    related_entity_id = db.Column(db.Integer)  # ID de l'entité liée (produit, exposant, etc.)
    related_entity_type = db.Column(db.String(50))  # 'product', 'exhibitor', 'event'
    
    # Contrôle d'accès
    is_public = db.Column(db.Boolean, default=True)  # Accessible aux visiteurs non connectés
    requires_login = db.Column(db.Boolean, default=False)  # Nécessite une connexion
    allowed_user_types = db.Column(db.String(200))  # Types d'utilisateurs autorisés (JSON)
    
    # Statistiques
    download_count = db.Column(db.Integer, default=0)
    last_downloaded = db.Column(db.DateTime)
    
    # Métadonnées temporelles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # Document mis en avant
    
    def to_dict(self, include_file_path=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_size_formatted': self.format_file_size(),
            'mime_type': self.mime_type,
            'file_extension': self.file_extension,
            'category': self.category,
            'document_type': self.document_type,
            'uploaded_by': self.uploaded_by,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type,
            'is_public': self.is_public,
            'requires_login': self.requires_login,
            'download_count': self.download_count,
            'last_downloaded': self.last_downloaded.isoformat() if self.last_downloaded else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'is_featured': self.is_featured
        }
        
        if include_file_path:
            data['file_path'] = self.file_path
            data['stored_filename'] = self.stored_filename
        
        return data
    
    def format_file_size(self):
        """Formate la taille du fichier en unités lisibles"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_download_url(self):
        """Génère l'URL de téléchargement du document"""
        return f"/api/documents/{self.id}/download"
    
    def increment_download_count(self):
        """Incrémente le compteur de téléchargements"""
        self.download_count += 1
        self.last_downloaded = datetime.utcnow()
        db.session.commit()

class DocumentCategory(db.Model):
    """Modèle pour les catégories de documents"""
    __tablename__ = 'document_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Nom de l'icône (ex: 'FileText', 'Download')
    color = db.Column(db.String(20))  # Couleur hexadécimale
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class DocumentDownload(db.Model):
    """Modèle pour tracer les téléchargements de documents"""
    __tablename__ = 'document_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null pour les visiteurs anonymes
    ip_address = db.Column(db.String(45))  # Support IPv4 et IPv6
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.String(500))
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    document = db.relationship('Document', backref='downloads')
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'downloaded_at': self.downloaded_at.isoformat()
        }

