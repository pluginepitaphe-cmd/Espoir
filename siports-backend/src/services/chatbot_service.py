import openai
import os
import json
from typing import List, Dict, Optional
from src.models.chatbot import ChatConversation, ChatMessage, ChatbotKnowledge
from src.models.user import db
from src.models.product import Product
from datetime import datetime

class ChatbotService:
    """Service pour gérer les interactions avec le chatbot IA"""
    
    def __init__(self):
        # Configuration OpenAI (les variables d'environnement sont déjà définies)
        self.client = openai.OpenAI()
        self.model = "gpt-4.1-mini"
        
        # Contexte système pour le chatbot SIPORTS
        self.system_context = """
        Tu es l'assistant virtuel de SIPORTS 2026, le Salon International des Ports et de leur Écosystème.
        
        INFORMATIONS SUR L'ÉVÉNEMENT :
        - Dates : Du 5 au 7 février 2026
        - Lieu : Parc d'Exposition Mohammed VI, El Jadida, Maroc
        - Organisé sous l'égide du Ministère de l'Équipement et de l'Eau
        - Thèmes : infrastructures portuaires, connectivité, innovation durable, exploitation, logistique portuaire, digitalisation et formation
        
        STATISTIQUES ATTENDUES :
        - +6000 visiteurs attendus
        - +300 exposants
        - +30 conférences
        - +50 pays représentés
        
        PAVILLONS D'EXPOSITION :
        - Institutionnel
        - Industrie portuaire
        - Exploitation & Gestion des ports
        - Académique & Formation
        
        TON RÔLE :
        - Aide les visiteurs à naviguer sur la plateforme
        - Réponds aux questions sur l'événement, les exposants et leurs produits
        - Guide les utilisateurs dans leurs démarches (inscription, prise de rendez-vous, réseautage)
        - Sois professionnel, courtois et informatif
        - Réponds en français principalement, mais adapte-toi à la langue de l'utilisateur
        
        Si tu ne connais pas une information spécifique, oriente l'utilisateur vers les bonnes sections de la plateforme ou suggère de contacter l'organisation.
        """
    
    def get_or_create_conversation(self, session_id: str, user_id: Optional[int] = None) -> ChatConversation:
        """Récupère ou crée une conversation pour une session donnée"""
        conversation = ChatConversation.query.filter_by(session_id=session_id).first()
        
        if not conversation:
            conversation = ChatConversation(
                session_id=session_id,
                user_id=user_id
            )
            db.session.add(conversation)
            db.session.commit()
        
        return conversation
    
    def add_message(self, conversation: ChatConversation, message_type: str, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Ajoute un message à la conversation"""
        message = ChatMessage(
            conversation_id=conversation.id,
            message_type=message_type,
            content=content,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return message
    
    def get_conversation_history(self, conversation: ChatConversation, limit: int = 10) -> List[Dict]:
        """Récupère l'historique récent de la conversation pour le contexte"""
        messages = ChatMessage.query.filter_by(conversation_id=conversation.id)\
                                  .order_by(ChatMessage.created_at.desc())\
                                  .limit(limit)\
                                  .all()
        
        # Inverser l'ordre pour avoir les messages du plus ancien au plus récent
        messages.reverse()
        
        history = []
        for message in messages:
            role = "user" if message.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": message.content
            })
        
        return history
    
    def search_knowledge_base(self, query: str) -> Optional[str]:
        """Recherche dans la base de connaissances locale"""
        # Recherche par mots-clés dans la base de connaissances
        knowledge_items = ChatbotKnowledge.query.filter(
            ChatbotKnowledge.is_active == True,
            db.or_(
                ChatbotKnowledge.question.contains(query),
                ChatbotKnowledge.keywords.contains(query),
                ChatbotKnowledge.answer.contains(query)
            )
        ).order_by(ChatbotKnowledge.priority).all()
        
        if knowledge_items:
            return knowledge_items[0].answer
        
        return None
    
    def get_relevant_context(self, query: str) -> str:
        """Récupère le contexte pertinent basé sur la requête de l'utilisateur"""
        context_parts = []
        
        # Recherche dans la base de connaissances
        kb_answer = self.search_knowledge_base(query)
        if kb_answer:
            context_parts.append(f"Information de la base de connaissances : {kb_answer}")
        
        # Recherche d'exposants/produits pertinents si la requête semble liée
        if any(keyword in query.lower() for keyword in ['produit', 'exposant', 'entreprise', 'solution', 'service']):
            products = Product.query.filter(
                db.or_(
                    Product.name.contains(query),
                    Product.description.contains(query),
                    Product.category.contains(query)
                )
            ).limit(3).all()
            
            if products:
                product_info = "Produits/services pertinents : "
                for product in products:
                    product_info += f"{product.name} ({product.category}) - {product.description[:100]}... "
                context_parts.append(product_info)
        
        return " ".join(context_parts) if context_parts else ""
    
    def generate_response(self, session_id: str, user_message: str, user_id: Optional[int] = None) -> Dict:
        """Génère une réponse du chatbot"""
        try:
            # Récupérer ou créer la conversation
            conversation = self.get_or_create_conversation(session_id, user_id)
            
            # Ajouter le message de l'utilisateur
            self.add_message(conversation, "user", user_message)
            
            # Récupérer l'historique de la conversation
            history = self.get_conversation_history(conversation)
            
            # Récupérer le contexte pertinent
            relevant_context = self.get_relevant_context(user_message)
            
            # Préparer les messages pour OpenAI
            messages = [{"role": "system", "content": self.system_context}]
            
            if relevant_context:
                messages.append({
                    "role": "system", 
                    "content": f"Contexte supplémentaire pour cette requête : {relevant_context}"
                })
            
            messages.extend(history)
            messages.append({"role": "user", "content": user_message})
            
            # Appel à l'API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content
            
            # Ajouter la réponse du bot à la conversation
            self.add_message(conversation, "bot", bot_response, {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else None
            })
            
            return {
                "success": True,
                "response": bot_response,
                "conversation_id": conversation.id,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants."
            }
    
    def get_conversation_messages(self, session_id: str) -> List[Dict]:
        """Récupère tous les messages d'une conversation"""
        conversation = ChatConversation.query.filter_by(session_id=session_id).first()
        
        if not conversation:
            return []
        
        messages = ChatMessage.query.filter_by(conversation_id=conversation.id)\
                                  .order_by(ChatMessage.created_at)\
                                  .all()
        
        return [message.to_dict() for message in messages]
    
    def initialize_knowledge_base(self):
        """Initialise la base de connaissances avec des données de base"""
        knowledge_items = [
            {
                "category": "event",
                "question": "Quand a lieu SIPORTS 2026 ?",
                "answer": "SIPORTS 2026 se déroule du 5 au 7 février 2026 au Parc d'Exposition Mohammed VI à El Jadida, Maroc.",
                "keywords": "date,quand,février,2026,el jadida,maroc"
            },
            {
                "category": "event",
                "question": "Où se déroule SIPORTS 2026 ?",
                "answer": "SIPORTS 2026 se déroule au Parc d'Exposition Mohammed VI à El Jadida, Maroc.",
                "keywords": "lieu,où,el jadida,maroc,parc exposition"
            },
            {
                "category": "event",
                "question": "Qu'est-ce que SIPORTS ?",
                "answer": "SIPORTS est le Salon International des Ports et de leur Écosystème, organisé sous l'égide du Ministère de l'Équipement et de l'Eau. C'est le rendez-vous international dédié à l'univers portuaire : infrastructures, connectivité, innovation durable, exploitation, logistique portuaire, digitalisation et formation.",
                "keywords": "siports,salon,ports,écosystème,maritime"
            },
            {
                "category": "general",
                "question": "Comment prendre un rendez-vous ?",
                "answer": "Pour prendre un rendez-vous avec un exposant, rendez-vous dans la section 'Calendrier' de la plateforme ou consultez le mini-site de l'exposant qui vous intéresse. Vous pourrez voir ses disponibilités et réserver un créneau.",
                "keywords": "rendez-vous,réserver,calendrier,exposant"
            },
            {
                "category": "general",
                "question": "Comment contacter un exposant ?",
                "answer": "Vous pouvez contacter un exposant via la section 'Réseautage' pour envoyer une demande de connexion, ou directement via son mini-site où vous trouverez ses informations de contact.",
                "keywords": "contact,exposant,réseautage,connexion"
            }
        ]
        
        for item in knowledge_items:
            existing = ChatbotKnowledge.query.filter_by(question=item["question"]).first()
            if not existing:
                kb_item = ChatbotKnowledge(**item)
                db.session.add(kb_item)
        
        db.session.commit()

