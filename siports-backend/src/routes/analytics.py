from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

from ..models.user import User, db
from ..models.analytics import AnalyticsEvent, UserProfile, UserInteraction, AIRecommendation, DailyMetrics
from ..services.ai_service import AIService

analytics_bp = Blueprint('analytics', __name__)
ai_service = AIService()

@analytics_bp.route('/track', methods=['POST'])
@jwt_required()
def track_event():
    """Enregistrer un événement analytics"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Créer l'événement analytics
        event = AnalyticsEvent(
            user_id=current_user_id,
            session_id=data.get('session_id'),
            event_type=data.get('event_type'),
            event_data=json.dumps(data.get('event_data', {})),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            geolocation=data.get('geolocation')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Événement enregistré'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'enregistrement de l'événement: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/profile/completion', methods=['GET'])
@jwt_required()
def get_profile_completion():
    """Obtenir le score de complétion du profil"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Obtenir ou créer le profil enrichi
        profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            profile = UserProfile(user_id=current_user_id)
            db.session.add(profile)
        
        # Préparer les données utilisateur pour l'IA
        user_data = user.to_dict()
        if profile:
            user_data.update(profile.to_dict())
        
        # Calculer le score de complétion
        completion_score = ai_service.calculate_profile_completion_score(user_data)
        
        # Obtenir les recommandations
        recommendations = ai_service.get_profile_recommendations(user_data)
        
        # Mettre à jour le score dans la base
        profile.completion_score = completion_score
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'completion_score': completion_score,
            'recommendations': recommendations,
            'profile_data': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du calcul de complétion: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/recommendations/users', methods=['GET'])
@jwt_required()
def get_user_recommendations():
    """Obtenir des recommandations d'utilisateurs"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Obtenir le profil enrichi
        profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        user_data = user.to_dict()
        if profile:
            user_data.update(profile.to_dict())
        
        # Obtenir tous les autres utilisateurs actifs
        other_users = User.query.filter(
            User.id != current_user_id,
            User.is_active == True,
            User.approval_status == 'approved'
        ).all()
        
        other_users_data = []
        for other_user in other_users:
            other_profile = UserProfile.query.filter_by(user_id=other_user.id).first()
            other_data = other_user.to_dict()
            if other_profile:
                other_data.update(other_profile.to_dict())
            other_users_data.append(other_data)
        
        # Générer les recommandations
        recommendations = ai_service.get_user_recommendations(
            current_user_id, user_data, other_users_data
        )
        
        # Sauvegarder les recommandations en base
        for rec in recommendations[:5]:  # Top 5 seulement
            ai_rec = AIRecommendation(
                user_id=current_user_id,
                recommendation_type='user_match',
                target_id=rec['user_id'],
                target_type='user',
                confidence_score=rec['compatibility_score'],
                reasoning=rec['reasoning'],
                recommendation_data=json.dumps({
                    'success_probability': rec['success_probability'],
                    'recommended_topics': rec['recommended_topics']
                }),
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(ai_rec)
        
        db.session.commit()
        
        return jsonify({
            'recommendations': recommendations,
            'total_count': len(recommendations)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération de recommandations: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/compatibility/<int:target_user_id>', methods=['GET'])
@jwt_required()
def calculate_compatibility(target_user_id):
    """Calculer la compatibilité avec un utilisateur spécifique"""
    try:
        current_user_id = get_jwt_identity()
        
        if current_user_id == target_user_id:
            return jsonify({'error': 'Impossible de calculer la compatibilité avec soi-même'}), 400
        
        # Obtenir les deux utilisateurs
        user1 = User.query.get(current_user_id)
        user2 = User.query.get(target_user_id)
        
        if not user1 or not user2:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Obtenir les profils enrichis
        profile1 = UserProfile.query.filter_by(user_id=current_user_id).first()
        profile2 = UserProfile.query.filter_by(user_id=target_user_id).first()
        
        user1_data = user1.to_dict()
        user2_data = user2.to_dict()
        
        if profile1:
            user1_data.update(profile1.to_dict())
        if profile2:
            user2_data.update(profile2.to_dict())
        
        # Calculer la compatibilité
        compatibility = ai_service.calculate_user_compatibility(user1_data, user2_data)
        
        # Prédire le meilleur moment pour un rendez-vous
        meeting_prediction = ai_service.predict_optimal_meeting_time(current_user_id, target_user_id)
        
        # Enregistrer l'interaction
        interaction = UserInteraction(
            initiator_id=current_user_id,
            target_id=target_user_id,
            interaction_type='compatibility_check',
            compatibility_score=compatibility['compatibility_score'],
            success_probability=compatibility['success_probability'],
            interaction_data=json.dumps({
                'factors': compatibility['factors'],
                'recommended_topics': compatibility['recommended_topics']
            })
        )
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'compatibility': compatibility,
            'meeting_suggestions': meeting_prediction,
            'interaction_id': interaction.id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du calcul de compatibilité: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/engagement', methods=['GET'])
@jwt_required()
def get_engagement_analysis():
    """Analyser l'engagement de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        
        # Obtenir les événements analytics des 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        events = AnalyticsEvent.query.filter(
            AnalyticsEvent.user_id == current_user_id,
            AnalyticsEvent.timestamp >= thirty_days_ago
        ).all()
        
        # Convertir en format pour l'IA
        events_data = [event.to_dict() for event in events]
        
        # Analyser l'engagement
        engagement_analysis = ai_service.analyze_user_engagement(current_user_id, events_data)
        
        # Mettre à jour le score d'engagement dans le profil
        profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        if not profile:
            profile = UserProfile(user_id=current_user_id)
            db.session.add(profile)
        
        profile.engagement_score = engagement_analysis['engagement_score']
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(engagement_analysis), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'analyse d'engagement: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Dashboard analytics pour les administrateurs"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'admin':
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Statistiques générales
        total_users = User.query.filter_by(is_active=True).count()
        pending_approvals = User.query.filter_by(approval_status='pending').count()
        
        # Répartition par type d'utilisateur
        user_types = db.session.query(
            User.user_type,
            db.func.count(User.id).label('count')
        ).filter_by(is_active=True).group_by(User.user_type).all()
        
        # Événements des 7 derniers jours
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = AnalyticsEvent.query.filter(
            AnalyticsEvent.timestamp >= seven_days_ago
        ).count()
        
        # Utilisateurs actifs (avec événements récents)
        active_users = db.session.query(AnalyticsEvent.user_id).filter(
            AnalyticsEvent.timestamp >= seven_days_ago
        ).distinct().count()
        
        # Métriques d'engagement par type d'utilisateur
        engagement_by_type = {}
        for user_type, _ in user_types:
            avg_engagement = db.session.query(
                db.func.avg(UserProfile.engagement_score)
            ).join(User).filter(User.user_type == user_type).scalar()
            
            engagement_by_type[user_type] = round(avg_engagement or 0, 1)
        
        return jsonify({
            'overview': {
                'total_users': total_users,
                'pending_approvals': pending_approvals,
                'recent_events': recent_events,
                'active_users': active_users
            },
            'user_distribution': {ut[0]: ut[1] for ut in user_types},
            'engagement_by_type': engagement_by_type,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du dashboard admin: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/interactions', methods=['GET'])
@jwt_required()
def get_user_interactions():
    """Obtenir les interactions de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        
        # Interactions initiées par l'utilisateur
        initiated = UserInteraction.query.filter_by(initiator_id=current_user_id).all()
        
        # Interactions reçues par l'utilisateur
        received = UserInteraction.query.filter_by(target_id=current_user_id).all()
        
        return jsonify({
            'initiated': [interaction.to_dict() for interaction in initiated],
            'received': [interaction.to_dict() for interaction in received],
            'total_initiated': len(initiated),
            'total_received': len(received)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des interactions: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@analytics_bp.route('/feedback/recommendation/<int:recommendation_id>', methods=['POST'])
@jwt_required()
def provide_recommendation_feedback(recommendation_id):
    """Fournir un feedback sur une recommandation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recommendation = AIRecommendation.query.filter_by(
            id=recommendation_id,
            user_id=current_user_id
        ).first()
        
        if not recommendation:
            return jsonify({'error': 'Recommandation non trouvée'}), 404
        
        # Mettre à jour le feedback
        recommendation.user_feedback = data.get('feedback')  # accepted, rejected, ignored
        recommendation.feedback_timestamp = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback enregistré'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

