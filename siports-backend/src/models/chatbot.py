from src.models.user import db
from datetime import datetime
import json

class ChatConversation(db.Model):
    """Modèle pour stocker les conversations du chatbot"""
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)  # ID de session pour les utilisateurs non connectés
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Optionnel pour les utilisateurs connectés
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec les messages
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [message.to_dict() for message in self.messages]
        }

class ChatMessage(db.Model):
    """Modèle pour stocker les messages individuels du chatbot"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' ou 'bot'
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.Text)  # JSON pour stocker des métadonnées supplémentaires
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'message_type': self.message_type,
            'content': self.content,
            'metadata': json.loads(self.message_metadata) if self.message_metadata else None,
            'created_at': self.created_at.isoformat()
        }

class ChatbotKnowledge(db.Model):
    """Modèle pour stocker la base de connaissances du chatbot"""
    __tablename__ = 'chatbot_knowledge'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # 'event', 'exhibitor', 'product', 'general'
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text)  # Mots-clés pour la recherche
    priority = db.Column(db.Integer, default=1)  # Priorité de la réponse (1 = haute, 5 = basse)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'question': self.question,
            'answer': self.answer,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

