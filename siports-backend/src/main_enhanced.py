import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Import des modèles existants
from src.models.user import db, User
from src.models.product import Product
from src.models.appointment import Appointment, Availability
from src.models.networking import Connection, Message, Discussion, DiscussionPost
from src.models.chatbot import ChatConversation, ChatMessage
from src.models.blog import BlogPost, BlogCategory, BlogTag, BlogComment

# Import des nouveaux modèles
from src.models.analytics import AnalyticsEvent, UserProfile, UserInteraction, AIRecommendation, DailyMetrics
from src.models.products import ProductEnhanced, ProductView, ProductInterest, ProductCategory

# Import des routes existantes
from src.routes.user import user_bp
from src.routes.product import product_bp
from src.routes.appointment import appointment_bp
from src.routes.networking import networking_bp
from src.routes.chatbot import chatbot_bp
from src.routes.blog import blog_bp
from src.routes.contact import contact_bp

# Import des nouvelles routes
from src.routes.analytics import analytics_bp
from src.routes.products import products_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration améliorée
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialisation des extensions
CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
db.init_app(app)

# Enregistrement des blueprints existants
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(appointment_bp, url_prefix='/api')
app.register_blueprint(networking_bp, url_prefix='/api')
app.register_blueprint(chatbot_bp, url_prefix='/api')
app.register_blueprint(blog_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')

# Enregistrement des nouveaux blueprints
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(products_bp, url_prefix='/api/products-enhanced')

# Route d'information sur les nouvelles fonctionnalités
@app.route('/api/features', methods=['GET'])
def get_features():
    """Obtenir la liste des nouvelles fonctionnalités disponibles"""
    features = {
        'analytics': {
            'description': 'Analytics avancés avec IA',
            'endpoints': [
                '/api/analytics/track',
                '/api/analytics/profile/completion',
                '/api/analytics/recommendations/users',
                '/api/analytics/compatibility/<user_id>',
                '/api/analytics/engagement',
                '/api/analytics/dashboard/admin'
            ]
        },
        'ai_recommendations': {
            'description': 'Système de recommandations IA',
            'features': [
                'Matching algorithmique entre utilisateurs',
                'Calcul de compatibilité business',
                'Recommandations de produits',
                'Optimisation des profils'
            ]
        },
        'enhanced_products': {
            'description': 'Gestion avancée des produits',
            'endpoints': [
                '/api/products-enhanced/',
                '/api/products-enhanced/my-products',
                '/api/products-enhanced/my-interests',
                '/api/products-enhanced/categories'
            ]
        },
        'user_profiles': {
            'description': 'Profils utilisateur enrichis',
            'features': [
                'Score de complétion automatique',
                'Données sectorielles',
                'Analytics d\'engagement',
                'Insights IA'
            ]
        }
    }
    
    return jsonify({
        'version': '2.0',
        'features': features,
        'status': 'active'
    })

# Création des tables
with app.app_context():
    db.create_all()

def create_enhanced_demo_data():
    """Créer des données de démonstration enrichies"""
    try:
        # Créer les catégories de produits si elles n'existent pas
        categories = [
            {'name': 'Équipements Portuaires', 'slug': 'port_equipment', 'icon': 'crane', 'color': '#2563eb'},
            {'name': 'Technologies Maritimes', 'slug': 'maritime_tech', 'icon': 'chip', 'color': '#059669'},
            {'name': 'Services Logistiques', 'slug': 'logistics', 'icon': 'truck', 'color': '#dc2626'},
            {'name': 'Solutions Digitales', 'slug': 'digital', 'icon': 'computer', 'color': '#7c3aed'},
            {'name': 'Environnement & Durabilité', 'slug': 'sustainability', 'icon': 'leaf', 'color': '#16a34a'}
        ]
        
        for cat_data in categories:
            existing_cat = ProductCategory.query.filter_by(slug=cat_data['slug']).first()
            if not existing_cat:
                category = ProductCategory(**cat_data)
                db.session.add(category)
        
        # Enrichir les utilisateurs existants avec des profils
        users = User.query.all()
        for user in users:
            existing_profile = UserProfile.query.filter_by(user_id=user.id).first()
            if not existing_profile:
                profile_data = {
                    'exhibitor': {
                        'industry_sector': 'maritime_transport',
                        'company_size': 'medium',
                        'annual_revenue': 5000000,
                        'description': 'Entreprise spécialisée dans les solutions de transport maritime',
                        'interests': '["innovation", "sustainability", "automation"]',
                        'completion_score': 85
                    },
                    'visitor': {
                        'industry_sector': 'port_services',
                        'company_size': 'large',
                        'annual_revenue': 50000000,
                        'description': 'Autorité portuaire en charge du développement',
                        'interests': '["infrastructure", "technology", "logistics"]',
                        'completion_score': 75
                    },
                    'partner': {
                        'industry_sector': 'consulting',
                        'company_size': 'small',
                        'annual_revenue': 1000000,
                        'description': 'Cabinet de conseil en stratégie maritime',
                        'interests': '["strategy", "innovation", "partnerships"]',
                        'completion_score': 90
                    },
                    'admin': {
                        'industry_sector': 'events',
                        'company_size': 'medium',
                        'description': 'Organisation d\'événements maritimes',
                        'interests': '["networking", "innovation", "industry"]',
                        'completion_score': 100
                    }
                }
                
                data = profile_data.get(user.user_type, {})
                if data:
                    profile = UserProfile(
                        user_id=user.id,
                        industry_sector=data.get('industry_sector'),
                        company_size=data.get('company_size'),
                        annual_revenue=data.get('annual_revenue'),
                        description=data.get('description'),
                        interests=data.get('interests'),
                        completion_score=data.get('completion_score', 50),
                        engagement_score=75.0
                    )
                    db.session.add(profile)
        
        db.session.commit()
        print("✅ Données de démonstration enrichies créées avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données enrichies: {str(e)}")
        db.session.rollback()

# Initialiser les données après la création des tables
with app.app_context():
    create_enhanced_demo_data()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    print("🚀 Démarrage de SIPORTS avec fonctionnalités avancées...")
    print("📊 Analytics IA disponibles sur /api/analytics")
    print("🤖 Recommandations IA disponibles sur /api/analytics/recommendations")
    print("📦 Produits enrichis disponibles sur /api/products-enhanced")
    print("ℹ️  Informations sur les fonctionnalités: /api/features")
    app.run(host='0.0.0.0', port=5000, debug=True)

