from flask import Blueprint, request, jsonify
from src.models.exhibitor import db, Exhibitor, Appointment, Message
from datetime import datetime
import json

exhibitor_bp = Blueprint('exhibitor', __name__)

@exhibitor_bp.route('/exhibitors', methods=['GET'])
def get_exhibitors():
    """Récupérer la liste des exposants avec filtres optionnels"""
    try:
        # Paramètres de filtrage
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        country = request.args.get('country', '')
        is_partner = request.args.get('is_partner', '')
        
        # Construction de la requête
        query = Exhibitor.query
        
        if search:
            query = query.filter(
                db.or_(
                    Exhibitor.name.ilike(f'%{search}%'),
                    Exhibitor.description.ilike(f'%{search}%'),
                    Exhibitor.specialties.ilike(f'%{search}%')
                )
            )
        
        if category:
            query = query.filter(Exhibitor.category == category)
            
        if country:
            query = query.filter(Exhibitor.country == country)
            
        if is_partner:
            query = query.filter(Exhibitor.is_partner == (is_partner.lower() == 'true'))
        
        exhibitors = query.all()
        return jsonify([exhibitor.to_dict() for exhibitor in exhibitors])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/exhibitors/<int:exhibitor_id>', methods=['GET'])
def get_exhibitor(exhibitor_id):
    """Récupérer les détails d'un exposant spécifique"""
    try:
        exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
        return jsonify(exhibitor.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/exhibitors/<string:exhibitor_name>', methods=['GET'])
def get_exhibitor_by_name(exhibitor_name):
    """Récupérer les détails d'un exposant par nom (pour mini-sites)"""
    try:
        # Convertir le nom formaté en nom original
        name = exhibitor_name.replace('-', ' ').title()
        exhibitor = Exhibitor.query.filter(Exhibitor.name.ilike(f'%{name}%')).first()
        
        if not exhibitor:
            return jsonify({'error': 'Exposant non trouvé'}), 404
            
        return jsonify(exhibitor.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/exhibitors/<int:exhibitor_id>/appointments', methods=['POST'])
def create_appointment(exhibitor_id):
    """Créer une demande de rendez-vous"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['visitor_name', 'visitor_email', 'appointment_date', 'appointment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Vérifier que l'exposant existe
        exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
        
        # Créer le rendez-vous
        appointment = Appointment(
            exhibitor_id=exhibitor_id,
            visitor_name=data['visitor_name'],
            visitor_email=data['visitor_email'],
            visitor_company=data.get('visitor_company', ''),
            appointment_date=datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00')),
            appointment_type=data['appointment_type'],
            message=data.get('message', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Demande de rendez-vous envoyée avec succès',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/exhibitors/<int:exhibitor_id>/messages', methods=['POST'])
def send_message(exhibitor_id):
    """Envoyer un message à un exposant"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['sender_name', 'sender_email', 'subject', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ requis manquant: {field}'}), 400
        
        # Vérifier que l'exposant existe
        exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
        
        # Créer le message
        message = Message(
            exhibitor_id=exhibitor_id,
            sender_name=data['sender_name'],
            sender_email=data['sender_email'],
            sender_company=data.get('sender_company', ''),
            subject=data['subject'],
            content=data['content']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message envoyé avec succès',
            'message_data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
def update_appointment_status(appointment_id):
    """Mettre à jour le statut d'un rendez-vous (pour les exposants)"""
    try:
        data = request.get_json()
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if 'status' in data:
            appointment.status = data['status']
            
        if 'proposed_date' in data and data['proposed_date']:
            appointment.proposed_date = datetime.fromisoformat(data['proposed_date'].replace('Z', '+00:00'))
            
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Statut du rendez-vous mis à jour',
            'appointment': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupérer la liste des catégories d'exposants"""
    try:
        categories = db.session.query(Exhibitor.category).distinct().all()
        return jsonify([cat[0] for cat in categories if cat[0]])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/countries', methods=['GET'])
def get_countries():
    """Récupérer la liste des pays d'exposants"""
    try:
        countries = db.session.query(Exhibitor.country).distinct().all()
        return jsonify([country[0] for country in countries if country[0]])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exhibitor_bp.route('/partners', methods=['GET'])
def get_partners():
    """Récupérer la liste des partenaires"""
    try:
        partners = Exhibitor.query.filter(Exhibitor.is_partner == True).all()
        return jsonify([partner.to_dict() for partner in partners])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

