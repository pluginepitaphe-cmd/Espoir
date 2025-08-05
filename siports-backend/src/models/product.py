from src.models.user import db  # Utiliser la même instance de db
from datetime import datetime
import json

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='EUR')
    availability = db.Column(db.String(50), default='available')  # available, out_of_stock, discontinued
    
    # Relations avec l'utilisateur (exposant/partenaire)
    user_id = db.Column(db.Integer, nullable=False)  # ID de l'exposant/partenaire
    
    # Spécifications techniques (stockées en JSON)
    specifications = db.Column(db.Text)  # JSON string
    
    # Images et documents
    images = db.Column(db.Text)  # JSON array of image URLs
    documents = db.Column(db.Text)  # JSON array of document URLs
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'currency': self.currency,
            'availability': self.availability,
            'user_id': self.user_id,
            'specifications': json.loads(self.specifications) if self.specifications else {},
            'images': json.loads(self.images) if self.images else [],
            'documents': json.loads(self.documents) if self.documents else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def from_dict(data):
        product = Product()
        product.name = data.get('name')
        product.description = data.get('description')
        product.category = data.get('category')
        product.price = data.get('price')
        product.currency = data.get('currency', 'EUR')
        product.availability = data.get('availability', 'available')
        product.user_id = data.get('user_id')
        
        # Convertir les spécifications en JSON
        if 'specifications' in data:
            product.specifications = json.dumps(data['specifications'])
        
        # Convertir les images en JSON
        if 'images' in data:
            product.images = json.dumps(data['images'])
            
        # Convertir les documents en JSON
        if 'documents' in data:
            product.documents = json.dumps(data['documents'])
            
        return product
    
    def update_from_dict(self, data):
        if 'name' in data:
            self.name = data['name']
        if 'description' in data:
            self.description = data['description']
        if 'category' in data:
            self.category = data['category']
        if 'price' in data:
            self.price = data['price']
        if 'currency' in data:
            self.currency = data['currency']
        if 'availability' in data:
            self.availability = data['availability']
        if 'specifications' in data:
            self.specifications = json.dumps(data['specifications'])
        if 'images' in data:
            self.images = json.dumps(data['images'])
        if 'documents' in data:
            self.documents = json.dumps(data['documents'])
        
        self.updated_at = datetime.utcnow()

