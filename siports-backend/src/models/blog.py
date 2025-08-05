from src.models.user import db
from datetime import datetime
import re

class BlogCategory(db.Model):
    """Modèle pour les catégories d'articles de blog"""
    __tablename__ = 'blog_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')  # Couleur hexadécimale
    icon = db.Column(db.String(50))  # Nom de l'icône (ex: 'Ship', 'Anchor')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    posts = db.relationship('BlogPost', backref='category', lazy=True)
    
    def __init__(self, **kwargs):
        super(BlogCategory, self).__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = self.generate_slug(self.name)
    
    @staticmethod
    def generate_slug(text):
        """Génère un slug à partir du texte"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'post_count': len(self.posts)
        }

class BlogTag(db.Model):
    """Modèle pour les tags d'articles de blog"""
    __tablename__ = 'blog_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(BlogTag, self).__init__(**kwargs)
        if not self.slug and self.name:
            self.slug = BlogCategory.generate_slug(self.name)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

# Table d'association pour la relation many-to-many entre posts et tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('blog_tags.id'), primary_key=True)
)

class BlogPost(db.Model):
    """Modèle pour les articles de blog"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    excerpt = db.Column(db.Text)  # Résumé de l'article
    content = db.Column(db.Text, nullable=False)  # Contenu en Markdown
    content_html = db.Column(db.Text)  # Contenu converti en HTML
    
    # Métadonnées SEO
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.String(500))
    
    # Images
    featured_image = db.Column(db.String(500))  # URL de l'image de couverture
    featured_image_alt = db.Column(db.String(255))  # Texte alternatif
    
    # Relations
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'), nullable=False)
    
    # Tags (relation many-to-many)
    tags = db.relationship('BlogTag', secondary=post_tags, lazy='subquery',
                          backref=db.backref('posts', lazy=True))
    
    # Statut et publication
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)  # Article mis en avant
    published_at = db.Column(db.DateTime)
    scheduled_at = db.Column(db.DateTime)  # Pour la planification
    
    # Statistiques
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    
    # Métadonnées temporelles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration
    allow_comments = db.Column(db.Boolean, default=True)
    is_sticky = db.Column(db.Boolean, default=False)  # Article épinglé
    
    def __init__(self, **kwargs):
        super(BlogPost, self).__init__(**kwargs)
        if not self.slug and self.title:
            self.slug = self.generate_unique_slug(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.excerpt and self.content:
            self.excerpt = self.generate_excerpt()
    
    def generate_unique_slug(self, title):
        """Génère un slug unique pour l'article"""
        base_slug = BlogCategory.generate_slug(title)
        slug = base_slug
        counter = 1
        
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def generate_excerpt(self, length=200):
        """Génère un extrait à partir du contenu"""
        if not self.content:
            return ""
        
        # Supprimer le markdown basique
        text = re.sub(r'[#*`_\[\]()]', '', self.content)
        text = re.sub(r'\n+', ' ', text)
        
        if len(text) <= length:
            return text
        
        return text[:length].rsplit(' ', 1)[0] + '...'
    
    def increment_view_count(self):
        """Incrémente le compteur de vues"""
        self.view_count += 1
        db.session.commit()
    
    def get_reading_time(self):
        """Calcule le temps de lecture estimé en minutes"""
        if not self.content:
            return 0
        
        word_count = len(self.content.split())
        reading_time = max(1, round(word_count / 200))  # 200 mots par minute
        return reading_time
    
    def get_url(self):
        """Génère l'URL de l'article"""
        return f"/blog/{self.category.slug}/{self.slug}"
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'featured_image': self.featured_image,
            'featured_image_alt': self.featured_image_alt,
            'author_id': self.author_id,
            'category': self.category.to_dict() if self.category else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'status': self.status,
            'is_featured': self.is_featured,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'allow_comments': self.allow_comments,
            'is_sticky': self.is_sticky,
            'reading_time': self.get_reading_time(),
            'url': self.get_url()
        }
        
        if include_content:
            data['content'] = self.content
            data['content_html'] = self.content_html
        
        return data

class BlogComment(db.Model):
    """Modèle pour les commentaires d'articles (optionnel)"""
    __tablename__ = 'blog_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null pour les commentaires anonymes
    author_name = db.Column(db.String(100))  # Pour les commentaires anonymes
    author_email = db.Column(db.String(255))  # Pour les commentaires anonymes
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, spam
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    post = db.relationship('BlogPost', backref='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

