from flask import Blueprint, request, jsonify
from src.models.networking import Connection, Message, Discussion, DiscussionPost, db
from datetime import datetime

networking_bp = Blueprint("networking", __name__)

# Routes pour les connexions
@networking_bp.route("/connections", methods=["GET"])
def get_connections():
    """Récupérer les connexions d'un utilisateur"""
    try:
        user_id = request.args.get("user_id")
        status = request.args.get("status")  # pending, accepted, rejected
        
        if not user_id:
            return jsonify({"error": "L'ID utilisateur est requis"}), 400

        query = Connection.query.filter(
            (Connection.requester_id == user_id) | (Connection.receiver_id == user_id)
        )
        
        if status:
            query = query.filter_by(status=status)

        connections = query.all()
        return jsonify([conn.to_dict() for conn in connections]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/connections", methods=["POST"])
def send_connection_request():
    """Envoyer une demande de connexion"""
    try:
        data = request.get_json()
        required_fields = ["requester_id", "receiver_id"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        # Vérifier qu'une connexion n'existe pas déjà
        existing = Connection.query.filter(
            ((Connection.requester_id == data["requester_id"]) & 
             (Connection.receiver_id == data["receiver_id"])) |
            ((Connection.requester_id == data["receiver_id"]) & 
             (Connection.receiver_id == data["requester_id"]))
        ).first()

        if existing:
            return jsonify({"error": "Une connexion existe déjà entre ces utilisateurs"}), 400

        connection = Connection(
            requester_id=data["requester_id"],
            receiver_id=data["receiver_id"],
            message=data.get("message", "")
        )
        db.session.add(connection)
        db.session.commit()

        return jsonify(connection.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/connections/<int:connection_id>", methods=["PUT"])
def update_connection_status(connection_id):
    """Accepter ou rejeter une demande de connexion"""
    try:
        connection = Connection.query.get_or_404(connection_id)
        data = request.get_json()

        if "status" in data and data["status"] in ["accepted", "rejected"]:
            connection.status = data["status"]
            db.session.commit()
            return jsonify(connection.to_dict()), 200
        else:
            return jsonify({"error": "Statut invalide"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Routes pour les messages
@networking_bp.route("/messages", methods=["GET"])
def get_messages():
    """Récupérer les messages entre deux utilisateurs"""
    try:
        user1_id = request.args.get("user1_id")
        user2_id = request.args.get("user2_id")
        
        if not user1_id or not user2_id:
            return jsonify({"error": "Les IDs des deux utilisateurs sont requis"}), 400

        messages = Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.created_at).all()

        return jsonify([msg.to_dict() for msg in messages]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/messages", methods=["POST"])
def send_message():
    """Envoyer un message"""
    try:
        data = request.get_json()
        required_fields = ["sender_id", "receiver_id", "content"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        message = Message(
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            content=data["content"]
        )
        db.session.add(message)
        db.session.commit()

        return jsonify(message.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/messages/<int:message_id>/read", methods=["PUT"])
def mark_message_as_read(message_id):
    """Marquer un message comme lu"""
    try:
        message = Message.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        return jsonify(message.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/conversations", methods=["GET"])
def get_conversations():
    """Récupérer toutes les conversations d'un utilisateur"""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "L'ID utilisateur est requis"}), 400

        # Récupérer les derniers messages de chaque conversation
        conversations = db.session.query(Message).filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).order_by(Message.created_at.desc()).all()

        # Grouper par conversation (paire d'utilisateurs)
        conversation_dict = {}
        for msg in conversations:
            other_user_id = msg.receiver_id if msg.sender_id == int(user_id) else msg.sender_id
            if other_user_id not in conversation_dict:
                conversation_dict[other_user_id] = msg

        return jsonify([msg.to_dict() for msg in conversation_dict.values()]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes pour les discussions/forums
@networking_bp.route("/discussions", methods=["GET"])
def get_discussions():
    """Récupérer toutes les discussions publiques"""
    try:
        category = request.args.get("category")
        query = Discussion.query.filter_by(is_public=True)
        
        if category:
            query = query.filter_by(category=category)

        discussions = query.order_by(Discussion.created_at.desc()).all()
        return jsonify([disc.to_dict() for disc in discussions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/discussions", methods=["POST"])
def create_discussion():
    """Créer une nouvelle discussion"""
    try:
        data = request.get_json()
        required_fields = ["title", "creator_id"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        discussion = Discussion(
            title=data["title"],
            description=data.get("description", ""),
            creator_id=data["creator_id"],
            category=data.get("category", ""),
            is_public=data.get("is_public", True)
        )
        db.session.add(discussion)
        db.session.commit()

        return jsonify(discussion.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/discussions/<int:discussion_id>/posts", methods=["GET"])
def get_discussion_posts(discussion_id):
    """Récupérer tous les posts d'une discussion"""
    try:
        posts = DiscussionPost.query.filter_by(discussion_id=discussion_id).order_by(DiscussionPost.created_at).all()
        return jsonify([post.to_dict() for post in posts]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@networking_bp.route("/discussions/<int:discussion_id>/posts", methods=["POST"])
def add_discussion_post(discussion_id):
    """Ajouter un post à une discussion"""
    try:
        data = request.get_json()
        required_fields = ["author_id", "content"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        post = DiscussionPost(
            discussion_id=discussion_id,
            author_id=data["author_id"],
            content=data["content"]
        )
        db.session.add(post)
        db.session.commit()

        return jsonify(post.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

