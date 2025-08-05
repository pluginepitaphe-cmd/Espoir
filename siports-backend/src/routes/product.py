from flask import Blueprint, request, jsonify
from src.models.product import Product, db
import os
from werkzeug.utils import secure_filename

product_bp = Blueprint('product', __name__)

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Récupérer tous les produits ou filtrer par utilisateur"""
    try:
        user_id = request.args.get('user_id')
        category = request.args.get('category')
        
        query = Product.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)
            
        products = query.all()
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Récupérer un produit spécifique"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products', methods=['POST'])
def create_product():
    """Créer un nouveau produit"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if not data.get('name') or not data.get('user_id'):
            return jsonify({'error': 'Le nom du produit et l\'ID utilisateur sont requis'}), 400
        
        product = Product.from_dict(data)
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Mettre à jour un produit existant"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        product.update_from_dict(data)
        db.session.commit()
        
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Supprimer un produit"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Produit supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/<int:product_id>/upload', methods=['POST'])
def upload_file(product_id):
    """Upload de fichiers (images ou documents) pour un produit"""
    try:
        product = Product.query.get_or_404(product_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'image')  # 'image' ou 'document'
        
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Créer un nom de fichier unique
            filename = f"{product_id}_{file_type}_{filename}"
            
            # Créer le dossier s'il n'existe pas
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # URL relative pour accéder au fichier
            file_url = f"/static/uploads/{filename}"
            
            # Mettre à jour le produit avec la nouvelle URL
            if file_type == 'image':
                current_images = product.to_dict()['images']
                current_images.append(file_url)
                product.images = str(current_images).replace("'", '"')
            else:
                current_documents = product.to_dict()['documents']
                current_documents.append({
                    'name': file.filename,
                    'url': file_url
                })
                product.documents = str(current_documents).replace("'", '"')
            
            db.session.commit()
            
            return jsonify({
                'message': 'Fichier uploadé avec succès',
                'file_url': file_url,
                'product': product.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/categories', methods=['GET'])
def get_categories():
    """Récupérer toutes les catégories de produits"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        return jsonify(category_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@product_bp.route('/products/search', methods=['GET'])
def search_products():
    """Rechercher des produits par nom ou description"""
    try:
        query_text = request.args.get('q', '')
        category = request.args.get('category')
        
        query = Product.query
        
        if query_text:
            query = query.filter(
                db.or_(
                    Product.name.contains(query_text),
                    Product.description.contains(query_text)
                )
            )
        
        if category:
            query = query.filter_by(category=category)
        
        products = query.all()
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

