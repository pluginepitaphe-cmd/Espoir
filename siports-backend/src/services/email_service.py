import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Configuration SMTP pour Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "noreply@siports.com"  # Email fictif pour l'envoi
        self.recipient_email = "epitaphemarket@gmail.com"
        
        # Note: En production, ces informations devraient être dans des variables d'environnement
        # Pour cette démo, nous utilisons une configuration basique
        
    def send_notification_email(self, subject, message, user_data=None, event_type="general"):
        """
        Envoie un e-mail de notification à epitaphemarket@gmail.com
        
        Args:
            subject (str): Sujet de l'e-mail
            message (str): Corps du message
            user_data (dict): Données de l'utilisateur (optionnel)
            event_type (str): Type d'événement (inscription, connexion, etc.)
        """
        try:
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"[SIPORTS] {subject}"
            
            # Corps du message avec informations détaillées
            body = self._create_email_body(message, user_data, event_type)
            msg.attach(MIMEText(body, 'html'))
            
            # Pour cette démo, nous simulons l'envoi d'e-mail
            # En production, vous devriez configurer un vrai serveur SMTP
            self._simulate_email_send(msg)
            
            logger.info(f"E-mail envoyé avec succès: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'e-mail: {str(e)}")
            return False
    
    def _create_email_body(self, message, user_data, event_type):
        """Crée le corps HTML de l'e-mail"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #0891b2; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .user-info {{ background-color: #f0f9ff; padding: 15px; border-left: 4px solid #0891b2; margin: 15px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .event-type {{ display: inline-block; background-color: #10b981; color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚢 SIPORTS - Notification Système</h1>
            </div>
            
            <div class="content">
                <div class="event-type">{event_type.upper()}</div>
                <h2>Nouvelle activité détectée</h2>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Message:</strong> {message}</p>
                
                {self._format_user_data(user_data) if user_data else ""}
            </div>
            
            <div class="footer">
                <p>Cet e-mail a été généré automatiquement par le système SIPORTS.</p>
                <p>Salon International des Ports et de leur Écosystème</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _format_user_data(self, user_data):
        """Formate les données utilisateur pour l'e-mail"""
        if not user_data:
            return ""
            
        user_info = "<div class='user-info'><h3>Informations utilisateur:</h3><ul>"
        
        for key, value in user_data.items():
            if key not in ['password', 'confirm_password']:  # Exclure les mots de passe
                user_info += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        user_info += "</ul></div>"
        return user_info
    
    def _simulate_email_send(self, msg):
        """
        Simule l'envoi d'e-mail en sauvegardant dans un fichier log
        En production, remplacez cette méthode par un vrai envoi SMTP
        """
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'email_notifications.log')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"FROM: {msg['From']}\n")
            f.write(f"TO: {msg['To']}\n")
            f.write(f"SUBJECT: {msg['Subject']}\n")
            f.write(f"BODY:\n{msg.get_payload()[0].get_payload()}\n")
            f.write(f"{'='*50}\n")
    
    def send_user_registration_notification(self, user_data):
        """Envoie une notification pour une nouvelle inscription"""
        subject = "Nouvelle inscription utilisateur"
        message = f"Un nouvel utilisateur s'est inscrit sur la plateforme SIPORTS."
        return self.send_notification_email(subject, message, user_data, "inscription")
    
    def send_user_login_notification(self, user_data):
        """Envoie une notification pour une connexion utilisateur"""
        subject = "Connexion utilisateur"
        message = f"Un utilisateur s'est connecté à la plateforme SIPORTS."
        return self.send_notification_email(subject, message, user_data, "connexion")
    
    def send_contact_form_notification(self, form_data):
        """Envoie une notification pour un formulaire de contact"""
        subject = "Nouveau message de contact"
        message = f"Un nouveau message a été envoyé via le formulaire de contact."
        return self.send_notification_email(subject, message, form_data, "contact")
    
    def send_appointment_notification(self, appointment_data):
        """Envoie une notification pour un nouveau rendez-vous"""
        subject = "Nouveau rendez-vous programmé"
        message = f"Un nouveau rendez-vous a été programmé sur la plateforme."
        return self.send_notification_email(subject, message, appointment_data, "rendez-vous")
    
    def send_connection_request_notification(self, connection_data):
        """Envoie une notification pour une demande de connexion"""
        subject = "Nouvelle demande de connexion"
        message = f"Une nouvelle demande de connexion a été envoyée."
        return self.send_notification_email(subject, message, connection_data, "reseautage")

# Instance globale du service
email_service = EmailService()

