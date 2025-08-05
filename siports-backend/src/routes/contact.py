from flask import Blueprint, jsonify, request
from src.services.email_service import email_service
from datetime import datetime

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact", methods=["POST"])
def send_contact_message():
    """Envoyer un message via le formulaire de contact"""
    try:
        data = request.json
        
        # Validation des données requises
        required_fields = ["name", "email", "subject", "message"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Le champ {field} est requis"}), 400
        
        # Préparer les données pour l'e-mail
        form_data = {
            "name": data["name"],
            "email": data["email"],
            "subject": data["subject"],
            "message": data["message"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Envoyer la notification e-mail
        success = email_service.send_contact_form_notification(form_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Votre message a été envoyé avec succès. Nous vous répondrons sous 48h."
            }), 200
        else:
            return jsonify({
                "error": "Erreur lors de l'envoi du message. Veuillez réessayer."
            }), 500
        
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

@contact_bp.route("/contact/test", methods=["POST"])
def test_email_service():
    """Route de test pour vérifier le service d'e-mail"""
    try:
        test_data = {
            "test_type": "Service Test",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Test du service d'envoi d'e-mails"
        }
        
        success = email_service.send_notification_email(
            "Test du service d'e-mail",
            "Ceci est un test du service d'envoi d'e-mails de SIPORTS",
            test_data,
            "test"
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "E-mail de test envoyé avec succès"
            }), 200
        else:
            return jsonify({
                "error": "Erreur lors de l'envoi de l'e-mail de test"
            }), 500
            
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500

