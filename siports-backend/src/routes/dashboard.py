from flask import Blueprint, request, jsonify
from src.models.exhibitor import db, Exhibitor, Appointment, Message
from src.models.user import User
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/exhibitor/<int:exhibitor_id>', methods=['GET'])
def get_exhibitor_dashboard(exhibitor_id):
    """Récupérer les données du tableau de bord exposant"""
    try:
        exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
        
        # Statistiques des rendez-vous
        total_appointments = Appointment.query.filter_by(exhibitor_id=exhibitor_id).count()
        pending_appointments = Appointment.query.filter_by(
            exhibitor_id=exhibitor_id, 
            status='pending'
        ).count()
        accepted_appointments = Appointment.query.filter_by(
            exhibitor_id=exhibitor_id, 
            status='accepted'
        ).count()
        
        # Messages non lus
        unread_messages = Message.query.filter_by(
            exhibitor_id=exhibitor_id,
            is_read=False
        ).count()
        
        # Rendez-vous récents
        recent_appointments = Appointment.query.filter_by(
            exhibitor_id=exhibitor_id
        ).order_by(Appointment.created_at.desc()).limit(5).all()
        
        # Messages récents
        recent_messages = Message.query.filter_by(
            exhibitor_id=exhibitor_id
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        # Rendez-vous à venir
        upcoming_appointments = Appointment.query.filter(
            Appointment.exhibitor_id == exhibitor_id,
            Appointment.status == 'accepted',
            Appointment.appointment_date > datetime.utcnow()
        ).order_by(Appointment.appointment_date.asc()).limit(5).all()
        
        return jsonify({
            'exhibitor': exhibitor.to_dict(),
            'stats': {
                'total_appointments': total_appointments,
                'pending_appointments': pending_appointments,
                'accepted_appointments': accepted_appointments,
                'unread_messages': unread_messages
            },
            'recent_appointments': [apt.to_dict() for apt in recent_appointments],
            'recent_messages': [msg.to_dict() for msg in recent_messages],
            'upcoming_appointments': [apt.to_dict() for apt in upcoming_appointments]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/partner/<int:partner_id>', methods=['GET'])
def get_partner_dashboard(partner_id):
    """Récupérer les données du tableau de bord partenaire"""
    try:
        partner = Exhibitor.query.filter_by(id=partner_id, is_partner=True).first()
        if not partner:
            return jsonify({'error': 'Partenaire non trouvé'}), 404
        
        # Statistiques spécifiques aux partenaires
        total_collaborations = 0  # À implémenter selon les besoins
        active_projects = 0       # À implémenter selon les besoins
        
        # Utiliser les mêmes statistiques que les exposants pour l'instant
        total_appointments = Appointment.query.filter_by(exhibitor_id=partner_id).count()
        pending_appointments = Appointment.query.filter_by(
            exhibitor_id=partner_id, 
            status='pending'
        ).count()
        
        unread_messages = Message.query.filter_by(
            exhibitor_id=partner_id,
            is_read=False
        ).count()
        
        # Données récentes
        recent_appointments = Appointment.query.filter_by(
            exhibitor_id=partner_id
        ).order_by(Appointment.created_at.desc()).limit(5).all()
        
        recent_messages = Message.query.filter_by(
            exhibitor_id=partner_id
        ).order_by(Message.created_at.desc()).limit(5).all()
        
        return jsonify({
            'partner': partner.to_dict(),
            'stats': {
                'total_collaborations': total_collaborations,
                'active_projects': active_projects,
                'total_appointments': total_appointments,
                'pending_appointments': pending_appointments,
                'unread_messages': unread_messages
            },
            'recent_appointments': [apt.to_dict() for apt in recent_appointments],
            'recent_messages': [msg.to_dict() for msg in recent_messages]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/appointments/<int:exhibitor_id>', methods=['GET'])
def get_exhibitor_appointments(exhibitor_id):
    """Récupérer tous les rendez-vous d'un exposant/partenaire"""
    try:
        status_filter = request.args.get('status', '')
        
        query = Appointment.query.filter_by(exhibitor_id=exhibitor_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify([apt.to_dict() for apt in appointments])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/messages/<int:exhibitor_id>', methods=['GET'])
def get_exhibitor_messages(exhibitor_id):
    """Récupérer tous les messages d'un exposant/partenaire"""
    try:
        messages = Message.query.filter_by(
            exhibitor_id=exhibitor_id
        ).order_by(Message.created_at.desc()).all()
        
        return jsonify([msg.to_dict() for msg in messages])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_as_read(message_id):
    """Marquer un message comme lu"""
    try:
        message = Message.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Message marqué comme lu',
            'message_data': message.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/analytics/<int:exhibitor_id>', methods=['GET'])
def get_exhibitor_analytics(exhibitor_id):
    """Récupérer les analyses pour un exposant/partenaire"""
    try:
        # Analyses des rendez-vous par mois
        appointments_by_month = {}
        appointments = Appointment.query.filter_by(exhibitor_id=exhibitor_id).all()
        
        for apt in appointments:
            month_key = apt.created_at.strftime('%Y-%m')
            if month_key not in appointments_by_month:
                appointments_by_month[month_key] = 0
            appointments_by_month[month_key] += 1
        
        # Analyses des messages par mois
        messages_by_month = {}
        messages = Message.query.filter_by(exhibitor_id=exhibitor_id).all()
        
        for msg in messages:
            month_key = msg.created_at.strftime('%Y-%m')
            if month_key not in messages_by_month:
                messages_by_month[month_key] = 0
            messages_by_month[month_key] += 1
        
        # Types de rendez-vous
        appointment_types = {}
        for apt in appointments:
            if apt.appointment_type:
                if apt.appointment_type not in appointment_types:
                    appointment_types[apt.appointment_type] = 0
                appointment_types[apt.appointment_type] += 1
        
        return jsonify({
            'appointments_by_month': appointments_by_month,
            'messages_by_month': messages_by_month,
            'appointment_types': appointment_types,
            'total_interactions': len(appointments) + len(messages)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

