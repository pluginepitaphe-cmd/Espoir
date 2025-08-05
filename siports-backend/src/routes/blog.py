from flask import Blueprint, request, jsonify
from src.models.blog import BlogPost, BlogCategory, BlogTag, BlogComment
from src.models.user import db
from datetime import datetime
import markdown
from sqlalchemy import or_, desc

blog_bp = Blueprint('blog', __name__, url_prefix='/api/blog')

# Routes pour les articles
@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """Récupérer tous les articles avec pagination et filtres"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_slug = request.args.get('category')
        tag_slug = request.args.get('tag')
        search = request.args.get('search')
        status = request.args.get('status', 'published')
        featured_only = request.args.get('featured', False, type=bool)
        
        # Construction de la requête
        query = BlogPost.query
        
        # Filtres
        if status:
            query = query.filter(BlogPost.status == status)
        
        if category_slug:
            query = query.join(BlogCategory).filter(BlogCategory.slug == category_slug)
        
        if tag_slug:
            query = query.join(BlogPost.tags).filter(BlogTag.slug == tag_slug)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BlogPost.title.ilike(search_term),
                    BlogPost.content.ilike(search_term),
                    BlogPost.excerpt.ilike(search_term)
                )
            )
        
        if featured_only:
            query = query.filter(BlogPost.is_featured == True)
        
        # Tri
        if request.args.get('sort') == 'views':
            query = query.order_by(desc(BlogPost.view_count))
        elif request.args.get('sort') == 'likes':
            query = query.order_by(desc(BlogPost.like_count))
        else:
            # Tri par défaut : articles épinglés en premier, puis par date de publication
            query = query.order_by(desc(BlogPost.is_sticky), desc(BlogPost.published_at))
        
        # Pagination
        posts = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/posts/<slug>', methods=['GET'])
def get_post_by_slug(slug):
    """Récupérer un article par son slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug).first()
        
        if not post:
            return jsonify({'success': False, 'error': 'Article non trouvé'}), 404
        
        # Incrémenter le compteur de vues
        post.increment_view_count()
        
        return jsonify({
            'success': True,
            'post': post.to_dict(include_content=True)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/posts', methods=['POST'])
def create_post():
    """Créer un nouvel article"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['title', 'content', 'category_id', 'author_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Champ requis manquant: {field}'}), 400
        
        # Vérifier que la catégorie existe
        category = BlogCategory.query.get(data['category_id'])
        if not category:
            return jsonify({'success': False, 'error': 'Catégorie non trouvée'}), 404
        
        # Créer l'article
        post = BlogPost(
            title=data['title'],
            content=data['content'],
            excerpt=data.get('excerpt'),
            category_id=data['category_id'],
            author_id=data['author_id'],
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description'),
            meta_keywords=data.get('meta_keywords'),
            featured_image=data.get('featured_image'),
            featured_image_alt=data.get('featured_image_alt'),
            status=data.get('status', 'draft'),
            is_featured=data.get('is_featured', False),
            allow_comments=data.get('allow_comments', True),
            is_sticky=data.get('is_sticky', False)
        )
        
        # Convertir le contenu Markdown en HTML
        if post.content:
            post.content_html = markdown.markdown(post.content, extensions=['codehilite', 'fenced_code'])
        
        # Gérer la publication
        if data.get('status') == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
        elif data.get('scheduled_at'):
            post.scheduled_at = datetime.fromisoformat(data['scheduled_at'])
        
        db.session.add(post)
        db.session.flush()  # Pour obtenir l'ID
        
        # Ajouter les tags
        if 'tag_ids' in data:
            tags = BlogTag.query.filter(BlogTag.id.in_(data['tag_ids'])).all()
            post.tags = tags
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article créé avec succès',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Mettre à jour un article"""
    try:
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({'success': False, 'error': 'Article non trouvé'}), 404
        
        data = request.get_json()
        
        # Mettre à jour les champs
        updatable_fields = [
            'title', 'content', 'excerpt', 'category_id', 'meta_title', 
            'meta_description', 'meta_keywords', 'featured_image', 
            'featured_image_alt', 'status', 'is_featured', 'allow_comments', 
            'is_sticky'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(post, field, data[field])
        
        # Reconvertir le contenu Markdown en HTML si modifié
        if 'content' in data:
            post.content_html = markdown.markdown(post.content, extensions=['codehilite', 'fenced_code'])
        
        # Gérer la publication
        if data.get('status') == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
        elif data.get('scheduled_at'):
            post.scheduled_at = datetime.fromisoformat(data['scheduled_at'])
        
        # Mettre à jour les tags
        if 'tag_ids' in data:
            tags = BlogTag.query.filter(BlogTag.id.in_(data['tag_ids'])).all()
            post.tags = tags
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article mis à jour avec succès',
            'post': post.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Supprimer un article"""
    try:
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({'success': False, 'error': 'Article non trouvé'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article supprimé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes pour les catégories
@blog_bp.route('/categories', methods=['GET'])
def get_categories():
    """Récupérer toutes les catégories"""
    try:
        categories = BlogCategory.query.filter_by(is_active=True).order_by(BlogCategory.sort_order, BlogCategory.name).all()
        
        return jsonify({
            'success': True,
            'categories': [category.to_dict() for category in categories]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/categories', methods=['POST'])
def create_category():
    """Créer une nouvelle catégorie"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'success': False, 'error': 'Nom de catégorie requis'}), 400
        
        category = BlogCategory(
            name=data['name'],
            description=data.get('description'),
            color=data.get('color', '#3B82F6'),
            icon=data.get('icon'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Catégorie créée avec succès',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes pour les tags
@blog_bp.route('/tags', methods=['GET'])
def get_tags():
    """Récupérer tous les tags"""
    try:
        tags = BlogTag.query.order_by(BlogTag.name).all()
        
        return jsonify({
            'success': True,
            'tags': [tag.to_dict() for tag in tags]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@blog_bp.route('/tags', methods=['POST'])
def create_tag():
    """Créer un nouveau tag"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'success': False, 'error': 'Nom de tag requis'}), 400
        
        tag = BlogTag(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tag créé avec succès',
            'tag': tag.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Routes pour les statistiques
@blog_bp.route('/stats', methods=['GET'])
def get_blog_stats():
    """Récupérer les statistiques du blog"""
    try:
        total_posts = BlogPost.query.count()
        published_posts = BlogPost.query.filter_by(status='published').count()
        draft_posts = BlogPost.query.filter_by(status='draft').count()
        total_categories = BlogCategory.query.filter_by(is_active=True).count()
        total_tags = BlogTag.query.count()
        
        # Articles les plus vus
        popular_posts = BlogPost.query.filter_by(status='published').order_by(desc(BlogPost.view_count)).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_posts': total_posts,
                'published_posts': published_posts,
                'draft_posts': draft_posts,
                'total_categories': total_categories,
                'total_tags': total_tags,
                'popular_posts': [post.to_dict() for post in popular_posts]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

