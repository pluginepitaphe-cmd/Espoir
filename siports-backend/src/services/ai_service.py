import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AIService:
    """Service d'Intelligence Artificielle pour recommandations et matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.user_vectors = {}
        self.product_vectors = {}
        
    def calculate_profile_completion_score(self, user_data: Dict) -> int:
        """Calcule le score de complétion du profil utilisateur"""
        required_fields = {
            'basic_info': ['first_name', 'last_name', 'email'],
            'company_info': ['company', 'position'],
            'contact_info': ['phone'],
            'profile_details': ['bio', 'profile_image'],
            'preferences': ['interests']
        }
        
        weights = {
            'basic_info': 30,
            'company_info': 25,
            'contact_info': 15,
            'profile_details': 20,
            'preferences': 10
        }
        
        total_score = 0
        
        for category, fields in required_fields.items():
            category_score = 0
            for field in fields:
                if field in user_data and user_data[field]:
                    if field == 'interests' and isinstance(user_data[field], list):
                        category_score += 1 if len(user_data[field]) > 0 else 0
                    else:
                        category_score += 1
            
            # Pourcentage de complétion pour cette catégorie
            category_percentage = (category_score / len(fields)) * weights[category]
            total_score += category_percentage
        
        return min(100, int(total_score))
    
    def get_profile_recommendations(self, user_data: Dict) -> List[Dict]:
        """Génère des recommandations pour améliorer le profil"""
        recommendations = []
        
        # Vérifier les champs manquants
        if not user_data.get('bio'):
            recommendations.append({
                'type': 'profile_completion',
                'priority': 'high',
                'title': 'Ajoutez une biographie',
                'description': 'Une biographie attrayante augmente vos chances de connexion de 60%',
                'action': 'add_bio'
            })
        
        if not user_data.get('profile_image'):
            recommendations.append({
                'type': 'profile_completion',
                'priority': 'high',
                'title': 'Ajoutez une photo de profil',
                'description': 'Les profils avec photo reçoivent 3x plus de vues',
                'action': 'add_profile_image'
            })
        
        if not user_data.get('company'):
            recommendations.append({
                'type': 'profile_completion',
                'priority': 'medium',
                'title': 'Renseignez votre entreprise',
                'description': 'Aide les autres participants à mieux vous identifier',
                'action': 'add_company'
            })
        
        # Recommandations basées sur le type d'utilisateur
        if user_data.get('user_type') == 'exhibitor':
            if not user_data.get('products') or len(user_data.get('products', [])) == 0:
                recommendations.append({
                    'type': 'content',
                    'priority': 'high',
                    'title': 'Ajoutez vos premiers produits',
                    'description': 'Présentez votre catalogue pour attirer des visiteurs',
                    'action': 'add_products'
                })
        
        return recommendations
    
    def calculate_user_compatibility(self, user1_data: Dict, user2_data: Dict) -> Dict:
        """Calcule la compatibilité entre deux utilisateurs"""
        compatibility_factors = {}
        total_score = 0
        
        # Compatibilité sectorielle (30%)
        if user1_data.get('industry_sector') and user2_data.get('industry_sector'):
            if user1_data['industry_sector'] == user2_data['industry_sector']:
                compatibility_factors['industry'] = 0.9
            else:
                # Secteurs complémentaires
                complementary_sectors = {
                    'maritime_transport': ['port_services', 'logistics'],
                    'port_services': ['maritime_transport', 'equipment'],
                    'equipment': ['port_services', 'technology'],
                    'technology': ['equipment', 'services']
                }
                user1_sector = user1_data['industry_sector']
                if user2_data['industry_sector'] in complementary_sectors.get(user1_sector, []):
                    compatibility_factors['industry'] = 0.7
                else:
                    compatibility_factors['industry'] = 0.3
        else:
            compatibility_factors['industry'] = 0.5
        
        # Compatibilité de taille d'entreprise (20%)
        size_compatibility = {
            ('startup', 'startup'): 0.9,
            ('startup', 'small'): 0.8,
            ('small', 'medium'): 0.9,
            ('medium', 'large'): 0.8,
            ('large', 'enterprise'): 0.9
        }
        
        user1_size = user1_data.get('company_size', 'unknown')
        user2_size = user2_data.get('company_size', 'unknown')
        compatibility_factors['company_size'] = size_compatibility.get((user1_size, user2_size), 0.5)
        
        # Compatibilité géographique (15%)
        # Simulé pour l'exemple
        compatibility_factors['geography'] = random.uniform(0.6, 0.9)
        
        # Compatibilité d'intérêts (25%)
        user1_interests = set(user1_data.get('interests', []))
        user2_interests = set(user2_data.get('interests', []))
        
        if user1_interests and user2_interests:
            common_interests = len(user1_interests.intersection(user2_interests))
            total_interests = len(user1_interests.union(user2_interests))
            compatibility_factors['interests'] = common_interests / total_interests if total_interests > 0 else 0
        else:
            compatibility_factors['interests'] = 0.5
        
        # Historique d'interactions (10%)
        compatibility_factors['interaction_history'] = random.uniform(0.4, 0.8)
        
        # Calcul du score final
        weights = {
            'industry': 0.30,
            'company_size': 0.20,
            'geography': 0.15,
            'interests': 0.25,
            'interaction_history': 0.10
        }
        
        total_score = sum(compatibility_factors[factor] * weights[factor] 
                         for factor in compatibility_factors)
        
        return {
            'compatibility_score': round(total_score, 2),
            'factors': compatibility_factors,
            'success_probability': min(0.95, total_score * 1.1),
            'recommended_topics': self._generate_conversation_topics(user1_data, user2_data)
        }
    
    def _generate_conversation_topics(self, user1_data: Dict, user2_data: Dict) -> List[str]:
        """Génère des sujets de conversation recommandés"""
        topics = []
        
        # Sujets basés sur les secteurs
        sector_topics = {
            'maritime_transport': ['Optimisation des routes maritimes', 'Carburants verts', 'Digitalisation du transport'],
            'port_services': ['Automatisation portuaire', 'Gestion des flux', 'Services aux navires'],
            'equipment': ['Innovation technologique', 'Maintenance prédictive', 'Équipements durables'],
            'technology': ['IoT maritime', 'Intelligence artificielle', 'Cybersécurité maritime']
        }
        
        user1_sector = user1_data.get('industry_sector')
        user2_sector = user2_data.get('industry_sector')
        
        if user1_sector in sector_topics:
            topics.extend(sector_topics[user1_sector][:2])
        if user2_sector in sector_topics and user2_sector != user1_sector:
            topics.extend(sector_topics[user2_sector][:1])
        
        # Sujets généraux
        general_topics = [
            'Tendances du marché maritime',
            'Développement durable',
            'Partenariats stratégiques',
            'Innovation et R&D'
        ]
        
        topics.extend(random.sample(general_topics, min(2, len(general_topics))))
        
        return list(set(topics))[:5]  # Maximum 5 sujets uniques
    
    def get_user_recommendations(self, user_id: int, user_data: Dict, all_users: List[Dict]) -> List[Dict]:
        """Génère des recommandations d'utilisateurs à contacter"""
        recommendations = []
        
        for other_user in all_users:
            if other_user['id'] == user_id:
                continue
                
            # Calculer la compatibilité
            compatibility = self.calculate_user_compatibility(user_data, other_user)
            
            # Filtrer par score minimum
            if compatibility['compatibility_score'] >= 0.6:
                recommendation = {
                    'user_id': other_user['id'],
                    'user_data': {
                        'name': f"{other_user.get('first_name', '')} {other_user.get('last_name', '')}",
                        'company': other_user.get('company'),
                        'position': other_user.get('position'),
                        'user_type': other_user.get('user_type'),
                        'profile_image': other_user.get('profile_image')
                    },
                    'compatibility_score': compatibility['compatibility_score'],
                    'success_probability': compatibility['success_probability'],
                    'recommended_topics': compatibility['recommended_topics'],
                    'reasoning': self._generate_recommendation_reasoning(compatibility)
                }
                recommendations.append(recommendation)
        
        # Trier par score de compatibilité
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return recommendations[:10]  # Top 10 recommandations
    
    def _generate_recommendation_reasoning(self, compatibility: Dict) -> str:
        """Génère une explication de la recommandation"""
        score = compatibility['compatibility_score']
        factors = compatibility['factors']
        
        if score >= 0.8:
            return "Excellente compatibilité - secteurs complémentaires et intérêts communs"
        elif score >= 0.7:
            return "Bonne compatibilité - potentiel de collaboration intéressant"
        elif score >= 0.6:
            return "Compatibilité correcte - échange d'expériences possible"
        else:
            return "Compatibilité limitée - contact exploratoire"
    
    def predict_optimal_meeting_time(self, user1_id: int, user2_id: int) -> Dict:
        """Prédit le meilleur moment pour un rendez-vous"""
        # Simulation basée sur des patterns typiques
        now = datetime.now()
        
        # Créneaux préférés (simulation)
        preferred_slots = [
            {'day': 'tuesday', 'hour': 10, 'score': 0.9},
            {'day': 'wednesday', 'hour': 14, 'score': 0.85},
            {'day': 'thursday', 'hour': 11, 'score': 0.8},
            {'day': 'tuesday', 'hour': 15, 'score': 0.75},
            {'day': 'friday', 'hour': 10, 'score': 0.7}
        ]
        
        # Calculer les prochaines dates disponibles
        suggestions = []
        for slot in preferred_slots[:3]:
            # Trouver le prochain jour correspondant
            days_ahead = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4}
            target_day = days_ahead[slot['day']]
            current_day = now.weekday()
            
            days_to_add = (target_day - current_day) % 7
            if days_to_add == 0 and now.hour >= slot['hour']:
                days_to_add = 7  # Semaine suivante
            
            suggested_date = now + timedelta(days=days_to_add)
            suggested_datetime = suggested_date.replace(hour=slot['hour'], minute=0, second=0, microsecond=0)
            
            suggestions.append({
                'datetime': suggested_datetime.isoformat(),
                'confidence': slot['score'],
                'reasoning': f"Créneau optimal basé sur les patterns d'activité"
            })
        
        return {
            'suggestions': suggestions,
            'best_suggestion': suggestions[0] if suggestions else None
        }
    
    def analyze_user_engagement(self, user_id: int, analytics_data: List[Dict]) -> Dict:
        """Analyse l'engagement d'un utilisateur"""
        if not analytics_data:
            return {'engagement_score': 0, 'insights': []}
        
        # Calculer les métriques d'engagement
        total_events = len(analytics_data)
        unique_sessions = len(set(event.get('session_id') for event in analytics_data))
        
        # Types d'événements et leurs poids
        event_weights = {
            'profile_view': 1,
            'product_view': 2,
            'contact_request': 5,
            'meeting_scheduled': 10,
            'message_sent': 3,
            'document_download': 4
        }
        
        weighted_score = sum(event_weights.get(event.get('event_type'), 1) for event in analytics_data)
        
        # Normaliser le score (0-100)
        engagement_score = min(100, (weighted_score / max(1, total_events)) * 10)
        
        # Générer des insights
        insights = []
        
        if engagement_score >= 80:
            insights.append("Utilisateur très actif - excellent engagement")
        elif engagement_score >= 60:
            insights.append("Bon niveau d'engagement - utilisateur régulier")
        elif engagement_score >= 40:
            insights.append("Engagement modéré - potentiel d'amélioration")
        else:
            insights.append("Faible engagement - nécessite des actions d'activation")
        
        # Analyser les patterns temporels
        recent_events = [e for e in analytics_data 
                        if datetime.fromisoformat(e.get('timestamp', '2024-01-01')) > datetime.now() - timedelta(days=7)]
        
        if len(recent_events) > len(analytics_data) * 0.5:
            insights.append("Activité récente élevée - utilisateur engagé")
        
        return {
            'engagement_score': round(engagement_score, 1),
            'total_events': total_events,
            'unique_sessions': unique_sessions,
            'insights': insights,
            'recommendations': self._generate_engagement_recommendations(engagement_score)
        }
    
    def _generate_engagement_recommendations(self, engagement_score: float) -> List[str]:
        """Génère des recommandations pour améliorer l'engagement"""
        recommendations = []
        
        if engagement_score < 40:
            recommendations.extend([
                "Complétez votre profil pour augmenter votre visibilité",
                "Explorez les profils d'autres participants",
                "Participez aux événements de networking"
            ])
        elif engagement_score < 70:
            recommendations.extend([
                "Initiez plus de contacts avec d'autres participants",
                "Partagez du contenu pour augmenter votre visibilité",
                "Planifiez des rendez-vous avec vos contacts"
            ])
        else:
            recommendations.extend([
                "Continuez votre excellent engagement",
                "Partagez votre expérience avec d'autres participants",
                "Explorez de nouveaux secteurs d'activité"
            ])
        
        return recommendations

