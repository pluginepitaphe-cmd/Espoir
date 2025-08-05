from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserStatus, UserType, RejectionReason, ValidationAction, Signalement
from src.utils.email import email_service
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Récupère les statistiques pour le tableau de bord"""
    try:
        # Compter les utilisateurs par statut
        valides = User.query.filter_by(statut=UserStatus.VALIDE).count()
        en_attente = User.query.filter_by(statut=UserStatus.EN_ATTENTE).count()
        rejetes = User.query.filter_by(statut=UserStatus.REJETE).count()
        
        # Inscrits dans les dernières 24h
        hier = datetime.utcnow() - timedelta(days=1)
        inscrits_24h = User.query.filter(User.date_inscription >= hier).count()
        
        # Modifications récentes (dernières 24h)
        modifs_recentes = User.query.filter(User.date_derniere_modification >= hier).count()
        
        # Données pour le graphique des 7 derniers jours
        graphique_data = []
        for i in range(7):
            date_debut = datetime.utcnow() - timedelta(days=i+1)
            date_fin = datetime.utcnow() - timedelta(days=i)
            
            validations = ValidationAction.query.filter(
                and_(
                    ValidationAction.date_action >= date_debut,
                    ValidationAction.date_action < date_fin,
                    ValidationAction.action == 'valide'
                )
            ).count()
            
            rejets = ValidationAction.query.filter(
                and_(
                    ValidationAction.date_action >= date_debut,
                    ValidationAction.date_action < date_fin,
                    ValidationAction.action == 'rejete'
                )
            ).count()
            
            graphique_data.append({
                'date': date_debut.strftime('%Y-%m-%d'),
                'validations': validations,
                'rejets': rejets
            })
        
        graphique_data.reverse()  # Ordre chronologique
        
        return jsonify({
            'success': True,
            'data': {
                'valides': valides,
                'en_attente': en_attente,
                'rejetes': rejetes,
                'inscrits_24h': inscrits_24h,
                'modifs_recentes': modifs_recentes,
                'graphique_7_jours': graphique_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/pending', methods=['GET'])
def get_pending_users():
    """Récupère la liste des utilisateurs en attente de validation"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.filter_by(statut=UserStatus.EN_ATTENTE)\
                         .order_by(User.date_inscription.asc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'users': [user.to_dict() for user in users.items],
                'total': users.total,
                'pages': users.pages,
                'current_page': page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/validate', methods=['POST'])
def validate_user(user_id):
    """Valide un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.statut != UserStatus.EN_ATTENTE:
            return jsonify({'success': False, 'error': 'Utilisateur déjà traité'}), 400
        
        user.statut = UserStatus.VALIDE
        user.date_validation = datetime.utcnow()
        
        # Enregistrer l'action
        action = ValidationAction(
            user_id=user_id,
            action='valide',
            admin_email=request.json.get('admin_email', 'admin@example.com')
        )
        
        db.session.add(action)
        db.session.commit()
        
        # Envoyer email de validation
        email_service.send_validation_email(
            user.email, 
            f"{user.prenom} {user.nom}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur validé avec succès',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
def reject_user(user_id):
    """Rejette un utilisateur"""
    try:
        data = request.get_json()
        raison = data.get('raison')
        commentaire = data.get('commentaire', '')
        
        if not raison:
            return jsonify({'success': False, 'error': 'Raison de rejet requise'}), 400
        
        user = User.query.get_or_404(user_id)
        
        if user.statut != UserStatus.EN_ATTENTE:
            return jsonify({'success': False, 'error': 'Utilisateur déjà traité'}), 400
        
        user.statut = UserStatus.REJETE
        user.raison_rejet = RejectionReason(raison)
        user.commentaire_rejet = commentaire
        
        # Enregistrer l'action
        action = ValidationAction(
            user_id=user_id,
            action='rejete',
            admin_email=data.get('admin_email', 'admin@example.com'),
            commentaire=f"Raison: {raison}. {commentaire}"
        )
        
        db.session.add(action)
        db.session.commit()
        
        # Envoyer email de rejet
        email_service.send_rejection_email(
            user.email,
            f"{user.prenom} {user.nom}",
            raison,
            commentaire
        )
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur rejeté avec succès',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Récupère la liste des utilisateurs avec filtres"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        type_filter = request.args.get('type')
        status_filter = request.args.get('status')
        search = request.args.get('search', '')
        
        query = User.query
        
        # Filtres
        if type_filter:
            query = query.filter(User.type_utilisateur == UserType(type_filter))
        
        if status_filter:
            query = query.filter(User.statut == UserStatus(status_filter))
        
        if search:
            query = query.filter(
                or_(
                    User.email.contains(search),
                    User.nom.contains(search),
                    User.prenom.contains(search),
                    User.societe.contains(search)
                )
            )
        
        users = query.order_by(User.date_inscription.desc())\
                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'users': [user.to_dict() for user in users.items],
                'total': users.total,
                'pages': users.pages,
                'current_page': page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/remind', methods=['POST'])
def remind_user(user_id):
    """Envoie un rappel à un utilisateur pour compléter son profil"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Enregistrer l'action
        action = ValidationAction(
            user_id=user_id,
            action='relance',
            admin_email=request.json.get('admin_email', 'admin@example.com')
        )
        
        db.session.add(action)
        db.session.commit()
        
        # Envoyer email de rappel
        email_service.send_reminder_email(
            user.email,
            f"{user.prenom} {user.nom}",
            user.taux_completion_profil
        )
        
        return jsonify({
            'success': True,
            'message': 'Rappel envoyé avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
def deactivate_user(user_id):
    """Désactive un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        user.statut = UserStatus.DESACTIVE
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur désactivé avec succès',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/export', methods=['GET'])
def export_users():
    """Exporte la liste des utilisateurs en CSV"""
    try:
        type_filter = request.args.get('type')
        status_filter = request.args.get('status')
        
        query = User.query
        
        if type_filter:
            query = query.filter(User.type_utilisateur == UserType(type_filter))
        
        if status_filter:
            query = query.filter(User.statut == UserStatus(status_filter))
        
        users = query.all()
        
        # Créer le CSV
        csv_data = "ID,Email,Nom,Prénom,Société,Type,Statut,Date inscription,Taux completion\n"
        for user in users:
            csv_data += f"{user.id},{user.email},{user.nom},{user.prenom},{user.societe or ''},"
            csv_data += f"{user.type_utilisateur.value},{user.statut.value},"
            csv_data += f"{user.date_inscription.strftime('%Y-%m-%d') if user.date_inscription else ''},"
            csv_data += f"{user.taux_completion_profil}%\n"
        
        return jsonify({
            'success': True,
            'data': {
                'csv_content': csv_data,
                'filename': f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/reports', methods=['GET'])
def get_reports():
    """Récupère la liste des signalements"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reports = Signalement.query.filter_by(statut='en_attente')\
                                 .order_by(Signalement.date_signalement.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'reports': [report.to_dict() for report in reports.items],
                'total': reports.total,
                'pages': reports.pages,
                'current_page': page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/reports/<int:report_id>/action', methods=['POST'])
def handle_report(report_id):
    """Traite un signalement"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'supprimer_contenu', 'avertir_utilisateur', 'ignorer'
        
        report = Signalement.query.get_or_404(report_id)
        report.statut = 'traite'
        report.action_prise = action
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Signalement traité avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

