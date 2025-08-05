#!/usr/bin/env python3
"""
Script pour créer les utilisateurs de démonstration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.user import db, User

def create_demo_users():
    """Créer les utilisateurs de démonstration"""
    with app.app_context():
        # Supprimer les utilisateurs existants
        User.query.delete()
        
        # Utilisateurs de démonstration
        demo_users = [
            {
                'email': 'admin@siportevent.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'SIPORTS',
                'company': 'SIPORTS Organization',
                'position': 'Administrateur',
                'user_type': 'admin',
                'approval_status': 'approved',
                'is_active': True,
                'email_verified': True
            },
            {
                'email': 'exposant@example.com',
                'password': 'expo123',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'company': 'Maritime Solutions',
                'position': 'Directeur Commercial',
                'user_type': 'exhibitor',
                'approval_status': 'approved',
                'is_active': True,
                'email_verified': True,
                'bio': 'Expert en solutions maritimes avec 15 ans d\'expérience'
            },
            {
                'email': 'visiteur@example.com',
                'password': 'visit123',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'company': 'Port Authority',
                'position': 'Responsable Achats',
                'user_type': 'visitor',
                'approval_status': 'approved',
                'is_active': True,
                'email_verified': True
            },
            {
                'email': 'partenaire@example.com',
                'password': 'partner123',
                'first_name': 'Pierre',
                'last_name': 'Durand',
                'company': 'Ocean Tech',
                'position': 'CEO',
                'user_type': 'partner',
                'approval_status': 'approved',
                'is_active': True,
                'email_verified': True
            }
        ]
        
        for user_data in demo_users:
            user = User.from_dict(user_data)
            db.session.add(user)
            print(f"Utilisateur créé: {user.email} ({user.user_type})")
        
        db.session.commit()
        print(f"\n{len(demo_users)} utilisateurs de démonstration créés avec succès!")

if __name__ == '__main__':
    create_demo_users()

