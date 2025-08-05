from flask import Blueprint, request, jsonify
from src.services.chatbot_service import ChatbotService
from src.models.chatbot import ChatbotKnowledge
from src.models.user import db
import uuid

chatbot_bp = Blueprint('chatbot', __name__)
chatbot_service = ChatbotService()

@chatbot_bp.route('/api/chatbot/chat', methods=['POST'])
def chat():
    """Endpoint pour envoyer un message au chatbot"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message requis'}), 400
        
        message = data['message'].strip()
        if not message:
            return jsonify({'error': 'Message ne peut pas être vide'}), 400
        
        # Récupérer ou générer un session_id
        session_id = data.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Récupérer l'ID utilisateur si fourni (pour les utilisateurs connectés)
        user_id = data.get('user_id')
        
        # Générer la réponse
        result = chatbot_service.generate_response(session_id, message, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants.'
        }), 500

@chatbot_bp.route('/api/chatbot/conversation/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Récupère l'historique d'une conversation"""
    try:
        messages = chatbot_service.get_conversation_messages(session_id)
        return jsonify({
            'success': True,
            'messages': messages,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/new-session', methods=['POST'])
def new_session():
    """Crée une nouvelle session de chat"""
    try:
        session_id = str(uuid.uuid4())
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/knowledge', methods=['GET'])
def get_knowledge_base():
    """Récupère la base de connaissances (pour l'administration)"""
    try:
        knowledge_items = ChatbotKnowledge.query.filter_by(is_active=True)\
                                               .order_by(ChatbotKnowledge.category, ChatbotKnowledge.priority)\
                                               .all()
        
        return jsonify({
            'success': True,
            'knowledge_items': [item.to_dict() for item in knowledge_items]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/knowledge', methods=['POST'])
def add_knowledge():
    """Ajoute un élément à la base de connaissances"""
    try:
        data = request.get_json()
        
        required_fields = ['category', 'question', 'answer']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} requis'}), 400
        
        knowledge_item = ChatbotKnowledge(
            category=data['category'],
            question=data['question'],
            answer=data['answer'],
            keywords=data.get('keywords', ''),
            priority=data.get('priority', 1)
        )
        
        db.session.add(knowledge_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Élément ajouté à la base de connaissances',
            'knowledge_item': knowledge_item.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/knowledge/<int:knowledge_id>', methods=['PUT'])
def update_knowledge(knowledge_id):
    """Met à jour un élément de la base de connaissances"""
    try:
        knowledge_item = ChatbotKnowledge.query.get_or_404(knowledge_id)
        data = request.get_json()
        
        # Mettre à jour les champs fournis
        if 'category' in data:
            knowledge_item.category = data['category']
        if 'question' in data:
            knowledge_item.question = data['question']
        if 'answer' in data:
            knowledge_item.answer = data['answer']
        if 'keywords' in data:
            knowledge_item.keywords = data['keywords']
        if 'priority' in data:
            knowledge_item.priority = data['priority']
        if 'is_active' in data:
            knowledge_item.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Élément mis à jour',
            'knowledge_item': knowledge_item.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/knowledge/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge(knowledge_id):
    """Supprime un élément de la base de connaissances"""
    try:
        knowledge_item = ChatbotKnowledge.query.get_or_404(knowledge_id)
        
        db.session.delete(knowledge_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Élément supprimé de la base de connaissances'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/initialize', methods=['POST'])
def initialize_chatbot():
    """Initialise la base de connaissances du chatbot"""
    try:
        chatbot_service.initialize_knowledge_base()
        
        return jsonify({
            'success': True,
            'message': 'Base de connaissances initialisée avec succès'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chatbot_bp.route('/api/chatbot/suggestions', methods=['GET'])
def get_suggestions():
    """Récupère des suggestions de questions pour le chatbot"""
    try:
        suggestions = [
            "Quand a lieu SIPORTS 2026 ?",
            "Où se déroule l'événement ?",
            "Comment prendre un rendez-vous avec un exposant ?",
            "Quels sont les thèmes du salon ?",
            "Comment contacter un exposant ?",
            "Combien d'exposants sont attendus ?",
            "Comment s'inscrire à l'événement ?",
            "Quels sont les pavillons d'exposition ?"
        ]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

