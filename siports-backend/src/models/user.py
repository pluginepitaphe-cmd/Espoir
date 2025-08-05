from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserType(Enum):
    EXPOSANT = "exposant"
    PARTENAIRE = "partenaire"
    VISITEUR = "visiteur"

class UserStatus(Enum):
    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    REJETE = "rejete"
    DESACTIVE = "desactive"

class RejectionReason(Enum):
    EMAIL_INVALIDE = "Email invalide"
    PROFIL_INCOMPLET = "Profil incomplet"
    DOCUMENT_MANQUANT = "Document manquant"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    societe = db.Column(db.String(200), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    type_utilisateur = db.Column(db.Enum(UserType), nullable=False)
    statut = db.Column(db.Enum(UserStatus), default=UserStatus.EN_ATTENTE, nullable=False)
    
    # Champs pour le profil
    taux_completion_profil = db.Column(db.Integer, default=0)  # Pourcentage de 0 à 100
    documents_joints = db.Column(db.Text, nullable=True)  # JSON string des documents
    
    # Dates importantes
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    date_validation = db.Column(db.DateTime, nullable=True)
    date_derniere_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Champs pour le rejet
    raison_rejet = db.Column(db.Enum(RejectionReason), nullable=True)
    commentaire_rejet = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'nom': self.nom,
            'prenom': self.prenom,
            'societe': self.societe,
            'telephone': self.telephone,
            'type_utilisateur': self.type_utilisateur.value if self.type_utilisateur else None,
            'statut': self.statut.value if self.statut else None,
            'taux_completion_profil': self.taux_completion_profil,
            'documents_joints': self.documents_joints,
            'date_inscription': self.date_inscription.isoformat() if self.date_inscription else None,
            'date_validation': self.date_validation.isoformat() if self.date_validation else None,
            'date_derniere_modification': self.date_derniere_modification.isoformat() if self.date_derniere_modification else None,
            'raison_rejet': self.raison_rejet.value if self.raison_rejet else None,
            'commentaire_rejet': self.commentaire_rejet
        }

class ValidationAction(db.Model):
    __tablename__ = 'validation_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'valide', 'rejete', 'relance'
    date_action = db.Column(db.DateTime, default=datetime.utcnow)
    admin_email = db.Column(db.String(120), nullable=True)  # Email de l'admin qui a fait l'action
    commentaire = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', backref=db.backref('actions', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'date_action': self.date_action.isoformat() if self.date_action else None,
            'admin_email': self.admin_email,
            'commentaire': self.commentaire
        }

class Signalement(db.Model):
    __tablename__ = 'signalements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_signale_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_signaleur_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    raison = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_signalement = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='en_attente')  # 'en_attente', 'traite', 'ignore'
    action_prise = db.Column(db.String(200), nullable=True)
    
    user_signale = db.relationship('User', foreign_keys=[user_signale_id], backref='signalements_recus')
    user_signaleur = db.relationship('User', foreign_keys=[user_signaleur_id], backref='signalements_faits')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_signale_id': self.user_signale_id,
            'user_signaleur_id': self.user_signaleur_id,
            'raison': self.raison,
            'description': self.description,
            'date_signalement': self.date_signalement.isoformat() if self.date_signalement else None,
            'statut': self.statut,
            'action_prise': self.action_prise,
            'user_signale': self.user_signale.to_dict() if self.user_signale else None
        }

