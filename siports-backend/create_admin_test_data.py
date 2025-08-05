#!/usr/bin/env python3
"""
Script pour créer des données de test pour le tableau de bord administrateur
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User, UserType, UserStatus, RejectionReason, ValidationAction, Signalement
from src.main import app
from datetime import datetime, timedelta
import random

def create_test_data():
    """Crée des données de test pour le tableau de bord"""
    
    with app.app_context():
        # Supprimer toutes les données existantes
        db.drop_all()
        db.create_all()
        
        # Créer des utilisateurs de test
        users_data = [
            # Utilisateurs en attente
            {
                'email': 'jean.dupont@maritime.fr',
                'nom': 'Dupont',
                'prenom': 'Jean',
                'societe': 'Maritime Solutions',
                'telephone': '0123456789',
                'type_utilisateur': UserType.EXPOSANT,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 85,
                'documents_joints': '["cv.pdf", "portfolio.pdf"]',
                'date_inscription': datetime.utcnow() - timedelta(days=2)
            },
            {
                'email': 'marie.martin@ocean.com',
                'nom': 'Martin',
                'prenom': 'Marie',
                'societe': 'Ocean Tech',
                'telephone': '0987654321',
                'type_utilisateur': UserType.PARTENAIRE,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 70,
                'documents_joints': '["presentation.pdf"]',
                'date_inscription': datetime.utcnow() - timedelta(days=1)
            },
            {
                'email': 'pierre.bernard@visitor.fr',
                'nom': 'Bernard',
                'prenom': 'Pierre',
                'societe': None,
                'telephone': '0147258369',
                'type_utilisateur': UserType.VISITEUR,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 60,
                'documents_joints': None,
                'date_inscription': datetime.utcnow() - timedelta(hours=12)
            },
            {
                'email': 'sophie.leroy@naval.fr',
                'nom': 'Leroy',
                'prenom': 'Sophie',
                'societe': 'Naval Engineering',
                'telephone': '0156789432',
                'type_utilisateur': UserType.EXPOSANT,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 45,
                'documents_joints': None,
                'date_inscription': datetime.utcnow() - timedelta(hours=6)
            },
            
            # Utilisateurs validés
            {
                'email': 'paul.durand@shipyard.com',
                'nom': 'Durand',
                'prenom': 'Paul',
                'societe': 'Shipyard International',
                'telephone': '0198765432',
                'type_utilisateur': UserType.EXPOSANT,
                'statut': UserStatus.VALIDE,
                'taux_completion_profil': 100,
                'documents_joints': '["cv.pdf", "certifications.pdf", "portfolio.pdf"]',
                'date_inscription': datetime.utcnow() - timedelta(days=5),
                'date_validation': datetime.utcnow() - timedelta(days=3)
            },
            {
                'email': 'claire.moreau@port.fr',
                'nom': 'Moreau',
                'prenom': 'Claire',
                'societe': 'Port Authority',
                'telephone': '0134567890',
                'type_utilisateur': UserType.PARTENAIRE,
                'statut': UserStatus.VALIDE,
                'taux_completion_profil': 95,
                'documents_joints': '["agreement.pdf"]',
                'date_inscription': datetime.utcnow() - timedelta(days=7),
                'date_validation': datetime.utcnow() - timedelta(days=4)
            },
            
            # Utilisateurs rejetés
            {
                'email': 'fake@invalid.com',
                'nom': 'Fake',
                'prenom': 'User',
                'societe': 'Invalid Corp',
                'telephone': '0000000000',
                'type_utilisateur': UserType.VISITEUR,
                'statut': UserStatus.REJETE,
                'taux_completion_profil': 30,
                'documents_joints': None,
                'date_inscription': datetime.utcnow() - timedelta(days=6),
                'raison_rejet': RejectionReason.EMAIL_INVALIDE,
                'commentaire_rejet': 'Adresse email non valide'
            },
            
            # Utilisateurs récents (dernières 24h)
            {
                'email': 'nouveau@recent.fr',
                'nom': 'Nouveau',
                'prenom': 'Utilisateur',
                'societe': 'Recent Company',
                'telephone': '0123456789',
                'type_utilisateur': UserType.EXPOSANT,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 50,
                'documents_joints': None,
                'date_inscription': datetime.utcnow() - timedelta(hours=3)
            },
            {
                'email': 'autre@recent.fr',
                'nom': 'Autre',
                'prenom': 'Récent',
                'societe': 'Another Recent',
                'telephone': '0987654321',
                'type_utilisateur': UserType.VISITEUR,
                'statut': UserStatus.EN_ATTENTE,
                'taux_completion_profil': 40,
                'documents_joints': None,
                'date_inscription': datetime.utcnow() - timedelta(hours=8)
            }
        ]
        
        # Créer les utilisateurs
        created_users = []
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
            created_users.append(user)
        
        db.session.commit()
        
        # Créer des actions de validation pour l'historique
        validation_actions = [
            {
                'user_id': created_users[4].id,  # Paul Durand
                'action': 'valide',
                'date_action': datetime.utcnow() - timedelta(days=3),
                'admin_email': 'admin@salon-maritime.fr'
            },
            {
                'user_id': created_users[5].id,  # Claire Moreau
                'action': 'valide',
                'date_action': datetime.utcnow() - timedelta(days=4),
                'admin_email': 'admin@salon-maritime.fr'
            },
            {
                'user_id': created_users[6].id,  # Fake User
                'action': 'rejete',
                'date_action': datetime.utcnow() - timedelta(days=5),
                'admin_email': 'admin@salon-maritime.fr',
                'commentaire': 'Email invalide détecté'
            },
            # Actions récentes pour le graphique
            {
                'user_id': created_users[0].id,  # Jean Dupont
                'action': 'relance',
                'date_action': datetime.utcnow() - timedelta(days=1),
                'admin_email': 'admin@salon-maritime.fr'
            }
        ]
        
        for action_data in validation_actions:
            action = ValidationAction(**action_data)
            db.session.add(action)
        
        # Créer quelques signalements de test
        signalements = [
            {
                'user_signale_id': created_users[4].id,
                'user_signaleur_id': created_users[5].id,
                'raison': 'Contenu inapproprié',
                'description': 'Commentaire déplacé dans le forum',
                'date_signalement': datetime.utcnow() - timedelta(days=2),
                'statut': 'en_attente'
            },
            {
                'user_signale_id': created_users[0].id,
                'user_signaleur_id': created_users[1].id,
                'raison': 'Spam',
                'description': 'Envoi de messages publicitaires répétés',
                'date_signalement': datetime.utcnow() - timedelta(hours=12),
                'statut': 'en_attente'
            }
        ]
        
        for signalement_data in signalements:
            signalement = Signalement(**signalement_data)
            db.session.add(signalement)
        
        db.session.commit()
        
        print("✅ Données de test créées avec succès!")
        print(f"📊 {len(created_users)} utilisateurs créés")
        print(f"📋 {len(validation_actions)} actions de validation créées")
        print(f"🚨 {len(signalements)} signalements créés")
        
        # Afficher un résumé
        print("\n📈 Résumé des données:")
        print(f"   • En attente: {len([u for u in created_users if u.statut == UserStatus.EN_ATTENTE])}")
        print(f"   • Validés: {len([u for u in created_users if u.statut == UserStatus.VALIDE])}")
        print(f"   • Rejetés: {len([u for u in created_users if u.statut == UserStatus.REJETE])}")
        print(f"   • Inscrits 24h: {len([u for u in created_users if u.date_inscription > datetime.utcnow() - timedelta(days=1)])}")

if __name__ == '__main__':
    create_test_data()

