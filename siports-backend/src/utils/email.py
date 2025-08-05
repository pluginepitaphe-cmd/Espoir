"""
Module pour l'envoi d'emails aux utilisateurs
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

class EmailService:
    """Service d'envoi d'emails"""
    
    def __init__(self):
        # Configuration SMTP (à adapter selon le fournisseur)
        self.smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'admin@salon-maritime.fr')
        
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """
        Envoie un email
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            body: Corps du message en texte brut
            html_body: Corps du message en HTML (optionnel)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Ajouter le corps en texte brut
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Ajouter le corps en HTML si fourni
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # En mode développement, on simule l'envoi
            if os.getenv('FLASK_ENV') == 'development' or not self.smtp_username:
                print(f"📧 [SIMULATION] Email envoyé à {to_email}")
                print(f"   Sujet: {subject}")
                print(f"   Corps: {body[:100]}...")
                return True
            
            # Envoyer l'email via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            print(f"✅ Email envoyé avec succès à {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email à {to_email}: {str(e)}")
            return False
    
    def send_validation_email(self, user_email: str, user_name: str) -> bool:
        """Envoie un email de validation de compte"""
        subject = "🎉 Votre compte a été validé - Salon Maritime"
        
        body = f"""Bonjour {user_name},

Excellente nouvelle ! Votre compte pour le Salon Maritime a été validé avec succès.

Vous pouvez maintenant accéder à toutes les fonctionnalités de la plateforme :
• Consulter les exposants et partenaires
• Participer aux événements de réseautage
• Accéder aux ressources exclusives

Connectez-vous dès maintenant sur notre plateforme pour commencer votre expérience.

Cordialement,
L'équipe du Salon Maritime

---
Cet email a été envoyé automatiquement, merci de ne pas y répondre.
"""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">🎉 Compte validé avec succès !</h2>
                
                <p>Bonjour <strong>{user_name}</strong>,</p>
                
                <p>Excellente nouvelle ! Votre compte pour le <strong>Salon Maritime</strong> a été validé avec succès.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c5aa0; margin-top: 0;">Vous pouvez maintenant :</h3>
                    <ul style="margin: 0;">
                        <li>Consulter les exposants et partenaires</li>
                        <li>Participer aux événements de réseautage</li>
                        <li>Accéder aux ressources exclusives</li>
                    </ul>
                </div>
                
                <p>Connectez-vous dès maintenant sur notre plateforme pour commencer votre expérience.</p>
                
                <p style="margin-top: 30px;">
                    Cordialement,<br>
                    <strong>L'équipe du Salon Maritime</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_rejection_email(self, user_email: str, user_name: str, reason: str, comment: str = "") -> bool:
        """Envoie un email de rejet de compte"""
        subject = "❌ Votre demande de compte - Salon Maritime"
        
        body = f"""Bonjour {user_name},

Nous avons examiné votre demande de compte pour le Salon Maritime.

Malheureusement, nous ne pouvons pas valider votre compte pour la raison suivante :
{reason}

{comment if comment else ''}

Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez corriger les informations manquantes, n'hésitez pas à nous contacter ou à créer un nouveau compte avec les informations correctes.

Cordialement,
L'équipe du Salon Maritime

---
Cet email a été envoyé automatiquement, merci de ne pas y répondre.
"""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #dc3545;">❌ Demande de compte non validée</h2>
                
                <p>Bonjour <strong>{user_name}</strong>,</p>
                
                <p>Nous avons examiné votre demande de compte pour le <strong>Salon Maritime</strong>.</p>
                
                <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                    <p style="margin: 0;"><strong>Raison du rejet :</strong> {reason}</p>
                    {f'<p style="margin: 10px 0 0 0;">{comment}</p>' if comment else ''}
                </div>
                
                <p>Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez corriger les informations manquantes, n'hésitez pas à nous contacter ou à créer un nouveau compte avec les informations correctes.</p>
                
                <p style="margin-top: 30px;">
                    Cordialement,<br>
                    <strong>L'équipe du Salon Maritime</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_reminder_email(self, user_email: str, user_name: str, completion_rate: int) -> bool:
        """Envoie un email de rappel pour compléter le profil"""
        subject = "📝 Complétez votre profil - Salon Maritime"
        
        body = f"""Bonjour {user_name},

Votre compte pour le Salon Maritime est en cours de validation.

Nous avons remarqué que votre profil n'est complété qu'à {completion_rate}%. Pour accélérer le processus de validation, nous vous invitons à compléter les informations manquantes :

• Informations personnelles complètes
• Documents justificatifs (si requis)
• Description de votre activité/société

Un profil complet nous permet de valider votre compte plus rapidement et vous donne accès à toutes les fonctionnalités de la plateforme.

Connectez-vous sur votre compte pour compléter votre profil.

Cordialement,
L'équipe du Salon Maritime

---
Cet email a été envoyé automatiquement, merci de ne pas y répondre.
"""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ffc107;">📝 Complétez votre profil</h2>
                
                <p>Bonjour <strong>{user_name}</strong>,</p>
                
                <p>Votre compte pour le <strong>Salon Maritime</strong> est en cours de validation.</p>
                
                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p style="margin: 0;"><strong>Profil complété à {completion_rate}%</strong></p>
                    <div style="background-color: #e9ecef; height: 10px; border-radius: 5px; margin: 10px 0;">
                        <div style="background-color: #ffc107; height: 10px; border-radius: 5px; width: {completion_rate}%;"></div>
                    </div>
                </div>
                
                <p>Pour accélérer le processus de validation, nous vous invitons à compléter les informations manquantes :</p>
                
                <ul>
                    <li>Informations personnelles complètes</li>
                    <li>Documents justificatifs (si requis)</li>
                    <li>Description de votre activité/société</li>
                </ul>
                
                <p>Un profil complet nous permet de valider votre compte plus rapidement et vous donne accès à toutes les fonctionnalités de la plateforme.</p>
                
                <p style="margin-top: 30px;">
                    Cordialement,<br>
                    <strong>L'équipe du Salon Maritime</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)

# Instance globale du service email
email_service = EmailService()

