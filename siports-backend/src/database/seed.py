from src.models.exhibitor import db, Exhibitor, Appointment, Message
from src.models.user import User
from datetime import datetime, timedelta
import json

def seed_database():
    """Initialiser la base de données avec des données de test"""
    
    # Vérifier si des données existent déjà
    if Exhibitor.query.first():
        return  # Données déjà présentes
    
    # Créer les exposants
    exhibitors_data = [
        {
            'name': 'Atlantic Logistics',
            'description': 'Spécialiste en logistique maritime et transport de marchandises. Solutions complètes pour l\'import-export.',
            'location': 'Casablanca',
            'country': 'Maroc',
            'category': 'Logistique',
            'size': 'Grande',
            'rating': 4.8,
            'reviews_count': 156,
            'website': 'https://atlantic-logistics.ma',
            'email': 'contact@atlantic-logistics.ma',
            'phone': '+212 522 123 456',
            'specialties': json.dumps(['Transport maritime', 'Logistique portuaire', 'Dédouanement']),
            'products': json.dumps(['Services de transport', 'Entreposage', 'Conseil logistique']),
            'certifications': json.dumps(['ISO 9001', 'ISO 14001', 'ISPS Code']),
            'is_partner': False
        },
        {
            'name': 'Mediterranean Shipping Co',
            'description': 'Compagnie maritime internationale offrant des services de transport de conteneurs.',
            'location': 'Tanger',
            'country': 'Maroc',
            'category': 'Transport Maritime',
            'size': 'Très Grande',
            'rating': 4.6,
            'reviews_count': 289,
            'website': 'https://msc.com',
            'email': 'info@msc-morocco.com',
            'phone': '+212 539 987 654',
            'specialties': json.dumps(['Transport de conteneurs', 'Lignes régulières', 'Services porte-à-porte']),
            'products': json.dumps(['Transport maritime', 'Services logistiques', 'Solutions intermodales']),
            'certifications': json.dumps(['ISO 9001', 'SOLAS', 'MARPOL']),
            'is_partner': False
        },
        {
            'name': 'Port Equipment Solutions',
            'description': 'Fournisseur d\'équipements portuaires et solutions technologiques pour les ports.',
            'location': 'Agadir',
            'country': 'Maroc',
            'category': 'Équipements',
            'size': 'Moyenne',
            'rating': 4.4,
            'reviews_count': 78,
            'website': 'https://port-equipment.ma',
            'email': 'sales@port-equipment.ma',
            'phone': '+212 528 456 789',
            'specialties': json.dumps(['Grues portuaires', 'Systèmes de manutention', 'Maintenance']),
            'products': json.dumps(['Grues', 'Équipements de levage', 'Systèmes automatisés']),
            'certifications': json.dumps(['CE', 'ISO 9001', 'OHSAS 18001']),
            'is_partner': False
        },
        {
            'name': 'Marine Insurance Group',
            'description': 'Assurance maritime et protection des marchandises en transit.',
            'location': 'Rabat',
            'country': 'Maroc',
            'category': 'Assurance',
            'size': 'Grande',
            'rating': 4.7,
            'reviews_count': 134,
            'website': 'https://marine-insurance.ma',
            'email': 'contact@marine-insurance.ma',
            'phone': '+212 537 654 321',
            'specialties': json.dumps(['Assurance maritime', 'Assurance cargo', 'Gestion des risques']),
            'products': json.dumps(['Polices d\'assurance', 'Évaluation des risques', 'Gestion des sinistres']),
            'certifications': json.dumps(['ACAPS', 'ISO 27001', 'Solvabilité II']),
            'is_partner': False
        },
        {
            'name': 'Digital Port Technologies',
            'description': 'Solutions digitales pour la modernisation des ports et la digitalisation des processus.',
            'location': 'Casablanca',
            'country': 'Maroc',
            'category': 'Technologie',
            'size': 'Moyenne',
            'rating': 4.9,
            'reviews_count': 92,
            'website': 'https://digitalport.tech',
            'email': 'info@digitalport.tech',
            'phone': '+212 522 789 123',
            'specialties': json.dumps(['IoT portuaire', 'Intelligence artificielle', 'Blockchain']),
            'products': json.dumps(['Plateformes digitales', 'Capteurs IoT', 'Solutions IA']),
            'certifications': json.dumps(['ISO 27001', 'GDPR', 'SOC 2']),
            'is_partner': False
        },
        {
            'name': 'Sustainable Shipping Alliance',
            'description': 'Promotion du transport maritime durable et des technologies vertes.',
            'location': 'Mohammedia',
            'country': 'Maroc',
            'category': 'Environnement',
            'size': 'Moyenne',
            'rating': 4.5,
            'reviews_count': 67,
            'website': 'https://sustainable-shipping.org',
            'email': 'contact@sustainable-shipping.org',
            'phone': '+212 523 345 678',
            'specialties': json.dumps(['Technologies vertes', 'Réduction des émissions', 'Carburants alternatifs']),
            'products': json.dumps(['Conseil environnemental', 'Audit carbone', 'Solutions durables']),
            'certifications': json.dumps(['ISO 14001', 'Green Marine', 'Carbon Trust']),
            'is_partner': False
        }
    ]
    
    # Créer les partenaires
    partners_data = [
        {
            'name': 'Maersk Morocco',
            'description': 'Leader mondial du transport maritime et de la logistique intégrée.',
            'location': 'Casablanca',
            'country': 'Maroc',
            'category': 'Transport Maritime',
            'size': 'Très Grande',
            'rating': 4.9,
            'reviews_count': 456,
            'website': 'https://maersk.com/ma',
            'email': 'morocco@maersk.com',
            'phone': '+212 522 111 222',
            'specialties': json.dumps(['Transport de conteneurs', 'Logistique intégrée', 'Solutions digitales']),
            'products': json.dumps(['Services maritimes', 'Logistique terrestre', 'Solutions end-to-end']),
            'certifications': json.dumps(['ISO 9001', 'ISO 14001', 'OHSAS 18001']),
            'is_partner': True,
            'partner_level': 'platine'
        },
        {
            'name': 'CMA CGM Maroc',
            'description': 'Groupe français leader mondial du transport maritime de conteneurs.',
            'location': 'Tanger',
            'country': 'Maroc',
            'category': 'Transport Maritime',
            'size': 'Très Grande',
            'rating': 4.7,
            'reviews_count': 324,
            'website': 'https://cmacgm.ma',
            'email': 'maroc@cmacgm.com',
            'phone': '+212 539 333 444',
            'specialties': json.dumps(['Lignes régulières', 'Transport spécialisé', 'Logistique']),
            'products': json.dumps(['Transport maritime', 'Services logistiques', 'Solutions intermodales']),
            'certifications': json.dumps(['ISO 9001', 'ISO 14001', 'ISPS']),
            'is_partner': True,
            'partner_level': 'or'
        },
        {
            'name': 'Hapag-Lloyd Morocco',
            'description': 'Compagnie maritime allemande spécialisée dans le transport de conteneurs.',
            'location': 'Casablanca',
            'country': 'Maroc',
            'category': 'Transport Maritime',
            'size': 'Grande',
            'rating': 4.6,
            'reviews_count': 198,
            'website': 'https://hapag-lloyd.ma',
            'email': 'morocco@hapag-lloyd.com',
            'phone': '+212 522 555 666',
            'specialties': json.dumps(['Transport de conteneurs', 'Services reefer', 'Cargo spécialisé']),
            'products': json.dumps(['Transport maritime', 'Services de conteneurs', 'Logistique']),
            'certifications': json.dumps(['ISO 9001', 'ISO 14001', 'AEO']),
            'is_partner': True,
            'partner_level': 'argent'
        },
        {
            'name': 'COSCO Shipping Morocco',
            'description': 'Compagnie maritime chinoise offrant des services de transport global.',
            'location': 'Tanger',
            'country': 'Maroc',
            'category': 'Transport Maritime',
            'size': 'Très Grande',
            'rating': 4.4,
            'reviews_count': 167,
            'website': 'https://cosco-morocco.com',
            'email': 'morocco@cosco.com',
            'phone': '+212 539 777 888',
            'specialties': json.dumps(['Transport de conteneurs', 'Bulk carriers', 'Services portuaires']),
            'products': json.dumps(['Transport maritime', 'Services portuaires', 'Logistique']),
            'certifications': json.dumps(['ISO 9001', 'SOLAS', 'MARPOL']),
            'is_partner': True,
            'partner_level': 'bronze'
        }
    ]
    
    # Insérer les exposants
    for exhibitor_data in exhibitors_data:
        exhibitor = Exhibitor(**exhibitor_data)
        db.session.add(exhibitor)
    
    # Insérer les partenaires
    for partner_data in partners_data:
        partner = Exhibitor(**partner_data)
        db.session.add(partner)
    
    # Commit les exposants et partenaires
    db.session.commit()
    
    # Créer quelques rendez-vous de test
    exhibitors = Exhibitor.query.all()
    if exhibitors:
        sample_appointments = [
            {
                'exhibitor_id': exhibitors[0].id,
                'visitor_name': 'Ahmed Benali',
                'visitor_email': 'ahmed.benali@example.com',
                'visitor_company': 'Import Export Maroc',
                'appointment_date': datetime.now() + timedelta(days=2, hours=10),
                'appointment_type': 'presentation',
                'status': 'pending',
                'message': 'Intéressé par vos services de logistique maritime.'
            },
            {
                'exhibitor_id': exhibitors[1].id,
                'visitor_name': 'Fatima Alaoui',
                'visitor_email': 'fatima.alaoui@example.com',
                'visitor_company': 'Textile Export SA',
                'appointment_date': datetime.now() + timedelta(days=3, hours=14),
                'appointment_type': 'demo',
                'status': 'accepted',
                'message': 'Souhaitons discuter de partenariat pour l\'export textile.'
            }
        ]
        
        for apt_data in sample_appointments:
            appointment = Appointment(**apt_data)
            db.session.add(appointment)
    
    # Créer quelques messages de test
    if exhibitors:
        sample_messages = [
            {
                'exhibitor_id': exhibitors[0].id,
                'sender_name': 'Mohamed Tazi',
                'sender_email': 'mohamed.tazi@example.com',
                'sender_company': 'Logistics Pro',
                'subject': 'Demande de devis',
                'content': 'Bonjour, nous aimerions obtenir un devis pour le transport de 50 conteneurs vers l\'Europe.',
                'is_read': False
            },
            {
                'exhibitor_id': exhibitors[2].id,
                'sender_name': 'Aicha Bennani',
                'sender_email': 'aicha.bennani@example.com',
                'sender_company': 'Port Services',
                'subject': 'Équipements portuaires',
                'content': 'Nous recherchons des équipements de manutention pour notre nouveau terminal.',
                'is_read': False
            }
        ]
        
        for msg_data in sample_messages:
            message = Message(**msg_data)
            db.session.add(message)
    
    # Commit final
    db.session.commit()
    print("Base de données initialisée avec succès avec des données de test.")

