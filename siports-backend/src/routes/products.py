from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

from ..models.user import User, db
from ..models.products import ProductEnhanced, ProductView, ProductInterest, ProductCategory
from ..models.analytics import AnalyticsEvent
from ..services.ai_service import AIService

products_bp = Blueprint('products', __name__)
ai_service = AIService()

@products_bp.route('/', methods=['GET'])
def get_products():
    """Obtenir la liste des produits avec filtres"""
    try:
        # Paramètres de filtrage
        category = request.args.get('category')
        user_type = request.args.get('user_type')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Construire la requête
        query = ProductEnhanced.query.filter_by(status='approved')
        
        if category:
            query = query.filter_by(category=category)
        
        if user_type:
            query = query.join(User).filter(User.user_type == user_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    ProductEnhanced.name.ilike(search_term),
                    ProductEnhanced.description.ilike(search_term),
                    ProductEnhanced.tags.ilike(search_term)
                )
            )
        
        # Pagination
        products = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Enrichir avec les données utilisateur
        result = []
        for product in products.items:
            product_data = product.to_dict(include_analytics=True)
            product_data['user'] = {
                'id': product.user.id,
                'company': product.user.company,
                'user_type': product.user.user_type,
                'profile_image': product.user.profile_image
            }
            result.append(product_data)
        
        return jsonify({
            'products': result,
            'pagination': {
                'page': products.page,
                'pages': products.pages,
                'per_page': products.per_page,
                'total': products.total,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des produits: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtenir un produit spécifique"""
    try:
        product = ProductEnhanced.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404
        
        if product.status != 'approved':
            return jsonify({'error': 'Produit non disponible'}), 403
        
        # Enregistrer la vue
        session_id = request.headers.get('X-Session-ID', 'anonymous')
        current_user_id = None
        
        try:
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except:
            pass
        
        # Créer l'événement de vue
        view = ProductView(
            product_id=product_id,
            viewer_id=current_user_id,
            session_id=session_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            device_type=_detect_device_type(request.headers.get('User-Agent', ''))
        )
        db.session.add(view)
        
        # Incrémenter le compteur de vues
        product.views_count += 1
        
        # Enregistrer l'événement analytics
        if current_user_id:
            analytics_event = AnalyticsEvent(
                user_id=current_user_id,
                session_id=session_id,
                event_type='product_view',
                event_data=json.dumps({
                    'product_id': product_id,
                    'product_name': product.name,
                    'product_category': product.category
                }),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(analytics_event)
        
        db.session.commit()
        
        # Préparer la réponse
        product_data = product.to_dict(include_analytics=True)
        product_data['user'] = {
            'id': product.user.id,
            'first_name': product.user.first_name,
            'last_name': product.user.last_name,
            'company': product.user.company,
            'position': product.user.position,
            'user_type': product.user.user_type,
            'profile_image': product.user.profile_image,
            'email': product.user.email if current_user_id else None
        }
        
        # Ajouter les produits similaires si utilisateur connecté
        if current_user_id:
            similar_products = _get_similar_products(product, limit=5)
            product_data['similar_products'] = similar_products
        
        return jsonify(product_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du produit: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """Créer un nouveau produit"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type not in ['exhibitor', 'partner']:
            return jsonify({'error': 'Seuls les exposants et partenaires peuvent créer des produits'}), 403
        
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'description', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Créer le produit
        product = ProductEnhanced(
            user_id=current_user_id,
            name=data['name'],
            description=data['description'],
            category=data['category'],
            subcategory=data.get('subcategory'),
            price_range=data.get('price_range'),
            currency=data.get('currency', 'EUR'),
            availability=data.get('availability', 'available'),
            images=json.dumps(data.get('images', [])),
            videos=json.dumps(data.get('videos', [])),
            documents=json.dumps(data.get('documents', [])),
            specifications=json.dumps(data.get('specifications', {})),
            features=json.dumps(data.get('features', [])),
            tags=json.dumps(data.get('tags', [])),
            seo_keywords=json.dumps(data.get('seo_keywords', [])),
            status='pending'  # Nécessite approbation
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Enregistrer l'événement analytics
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            session_id=request.headers.get('X-Session-ID', 'unknown'),
            event_type='product_created',
            event_data=json.dumps({
                'product_id': product.id,
                'product_name': product.name,
                'category': product.category
            }),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(analytics_event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Produit créé avec succès',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création du produit: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Mettre à jour un produit"""
    try:
        current_user_id = get_jwt_identity()
        product = ProductEnhanced.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404
        
        if product.user_id != current_user_id:
            return jsonify({'error': 'Non autorisé à modifier ce produit'}), 403
        
        data = request.get_json()
        
        # Mettre à jour les champs modifiables
        updatable_fields = [
            'name', 'description', 'category', 'subcategory', 'price_range',
            'currency', 'availability', 'images', 'videos', 'documents',
            'specifications', 'features', 'tags', 'seo_keywords'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['images', 'videos', 'documents', 'specifications', 'features', 'tags', 'seo_keywords']:
                    setattr(product, field, json.dumps(data[field]))
                else:
                    setattr(product, field, data[field])
        
        product.updated_at = datetime.utcnow()
        
        # Si modification majeure, remettre en attente d'approbation
        major_changes = ['name', 'description', 'category', 'price_range']
        if any(field in data for field in major_changes):
            product.status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Produit mis à jour avec succès',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la mise à jour du produit: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/<int:product_id>/interest', methods=['POST'])
@jwt_required()
def add_product_interest(product_id):
    """Ajouter un produit aux favoris/intérêts"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        product = ProductEnhanced.query.get(product_id)
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404
        
        # Vérifier si l'intérêt existe déjà
        existing_interest = ProductInterest.query.filter_by(
            user_id=current_user_id,
            product_id=product_id
        ).first()
        
        if existing_interest:
            # Mettre à jour l'intérêt existant
            existing_interest.interest_type = data.get('interest_type', 'bookmark')
            existing_interest.notes = data.get('notes', '')
            existing_interest.priority = data.get('priority', 'medium')
            existing_interest.updated_at = datetime.utcnow()
        else:
            # Créer un nouvel intérêt
            interest = ProductInterest(
                user_id=current_user_id,
                product_id=product_id,
                interest_type=data.get('interest_type', 'bookmark'),
                notes=data.get('notes', ''),
                priority=data.get('priority', 'medium')
            )
            db.session.add(interest)
            
            # Incrémenter le compteur d'intérêt du produit
            product.interest_count += 1
        
        # Enregistrer l'événement analytics
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            session_id=request.headers.get('X-Session-ID', 'unknown'),
            event_type='product_interest_added',
            event_data=json.dumps({
                'product_id': product_id,
                'product_name': product.name,
                'interest_type': data.get('interest_type', 'bookmark')
            }),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(analytics_event)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Intérêt ajouté avec succès'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'ajout d'intérêt: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/my-products', methods=['GET'])
@jwt_required()
def get_my_products():
    """Obtenir les produits de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        
        products = ProductEnhanced.query.filter_by(user_id=current_user_id).order_by(
            ProductEnhanced.created_at.desc()
        ).all()
        
        result = []
        for product in products:
            product_data = product.to_dict(include_analytics=True)
            
            # Ajouter les statistiques détaillées
            recent_views = ProductView.query.filter(
                ProductView.product_id == product.id,
                ProductView.timestamp >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            product_data['recent_views'] = recent_views
            result.append(product_data)
        
        return jsonify({
            'products': result,
            'total_count': len(result)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des produits utilisateur: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/my-interests', methods=['GET'])
@jwt_required()
def get_my_interests():
    """Obtenir les produits d'intérêt de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        
        interests = ProductInterest.query.filter_by(user_id=current_user_id).join(
            Product
        ).filter(ProductEnhanced.status == 'approved').order_by(
            ProductInterest.created_at.desc()
        ).all()
        
        result = []
        for interest in interests:
            interest_data = {
                'interest_id': interest.id,
                'interest_type': interest.interest_type,
                'notes': interest.notes,
                'priority': interest.priority,
                'follow_up_status': interest.follow_up_status,
                'created_at': interest.created_at.isoformat(),
                'product': interest.product.to_dict(),
                'user': {
                    'id': interest.product.user.id,
                    'company': interest.product.user.company,
                    'profile_image': interest.product.user.profile_image
                }
            }
            result.append(interest_data)
        
        return jsonify({
            'interests': result,
            'total_count': len(result)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des intérêts: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Obtenir la liste des catégories de produits"""
    try:
        categories = ProductCategory.query.filter_by(
            is_active=True,
            parent_id=None
        ).order_by(ProductCategory.sort_order).all()
        
        result = []
        for category in categories:
            category_data = category.to_dict(include_children=True)
            
            # Ajouter le nombre de produits dans cette catégorie
            product_count = ProductEnhanced.query.filter_by(
                category=category.slug,
                status='approved'
            ).count()
            category_data['product_count'] = product_count
            
            result.append(category_data)
        
        return jsonify({
            'categories': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des catégories: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

def _detect_device_type(user_agent):
    """Détecter le type d'appareil à partir du User-Agent"""
    user_agent = user_agent.lower()
    
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'tablet'
    else:
        return 'desktop'

def _get_similar_products(product, limit=5):
    """Obtenir des produits similaires"""
    # Recherche simple basée sur la catégorie et les tags
    similar = ProductEnhanced.query.filter(
        ProductEnhanced.id != product.id,
        ProductEnhanced.status == 'approved',
        db.or_(
            ProductEnhanced.category == product.category,
            ProductEnhanced.tags.ilike(f'%{product.category}%')
        )
    ).limit(limit).all()
    
    return [p.to_dict() for p in similar]

