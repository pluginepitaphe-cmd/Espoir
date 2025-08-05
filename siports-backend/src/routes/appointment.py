from flask import Blueprint, request, jsonify
from src.models.appointment import Appointment, Availability, db
from datetime import datetime

appointment_bp = Blueprint("appointment", __name__)

@appointment_bp.route("/appointments", methods=["GET"])
def get_appointments():
    """Récupérer tous les rendez-vous ou filtrer par exposant/visiteur"""
    try:
        exhibitor_id = request.args.get("exhibitor_id")
        visitor_id = request.args.get("visitor_id")

        query = Appointment.query

        if exhibitor_id:
            query = query.filter_by(exhibitor_id=exhibitor_id)
        if visitor_id:
            query = query.filter_by(visitor_id=visitor_id)

        appointments = query.all()
        return jsonify([app.to_dict() for app in appointments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/appointments", methods=["POST"])
def create_appointment():
    """Créer un nouveau rendez-vous"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ["exhibitor_id", "visitor_id", "start_time", "end_time"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        appointment = Appointment(
            exhibitor_id=data["exhibitor_id"],
            visitor_id=data["visitor_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]),
            notes=data.get("notes"),
            status=data.get("status", "pending")
        )
        db.session.add(appointment)
        db.session.commit()

        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    """Mettre à jour un rendez-vous"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()

        if "start_time" in data:
            appointment.start_time = datetime.fromisoformat(data["start_time"])
        if "end_time" in data:
            appointment.end_time = datetime.fromisoformat(data["end_time"])
        if "status" in data:
            appointment.status = data["status"]
        if "notes" in data:
            appointment.notes = data["notes"]

        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    """Supprimer un rendez-vous"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({"message": "Rendez-vous supprimé avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/availabilities", methods=["GET"])
def get_availabilities():
    """Récupérer les disponibilités d'un utilisateur"""
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "L'ID utilisateur est requis"}), 400

        availabilities = Availability.query.filter_by(user_id=user_id).all()
        return jsonify([avail.to_dict() for avail in availabilities]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/availabilities", methods=["POST"])
def add_availability():
    """Ajouter une nouvelle disponibilité"""
    try:
        data = request.get_json()
        required_fields = ["user_id", "start_time", "end_time"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        availability = Availability(
            user_id=data["user_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"])
        )
        db.session.add(availability)
        db.session.commit()
        return jsonify(availability.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/availabilities/<int:availability_id>", methods=["DELETE"])
def delete_availability(availability_id):
    """Supprimer une disponibilité"""
    try:
        availability = Availability.query.get_or_404(availability_id)
        db.session.delete(availability)
        db.session.commit()
        return jsonify({"message": "Disponibilité supprimée avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@appointment_bp.route("/global-calendar", methods=["GET"])
def get_global_calendar():
    """Récupérer tous les rendez-vous confirmés pour le calendrier global"""
    try:
        # On ne récupère que les rendez-vous confirmés pour le calendrier public
        appointments = Appointment.query.filter_by(status="confirmed").all()
        return jsonify([app.to_dict() for app in appointments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


