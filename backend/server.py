#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIPORTS - Plateforme de Gestion d'Événements Salon Maritime
Adapté pour l'environnement Kubernetes avec FastAPI
Intégration WordPress complète
"""

import os
import sys
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
import jwt
import secrets
import json
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Import chatbot service
from chatbot_service import siports_ai_service, ChatRequest, ChatResponse

# Configure logging
logger = logging.getLogger(__name__)

# Import WordPress integration
try:
    from wordpress_extensions import init_wordpress_integration
    WORDPRESS_ENABLED = True
    print("✅ WordPress integration loaded successfully")
except ImportError as e:
    WORDPRESS_ENABLED = False
    print(f"⚠️  WordPress integration not available: {e}")
except Exception as e:
    WORDPRESS_ENABLED = False
    print(f"❌ WordPress integration error: {e}")

# Configuration
ROOT_DIR = Path(__file__).parent
DATABASE_PATH = ROOT_DIR / "siports.db"

# FastAPI app
app = FastAPI(title="SIPORTS API", version="2.0.0")

# Initialize WordPress integration if available
if WORDPRESS_ENABLED:
    try:
        init_wordpress_integration(app)
        print("🎉 WordPress integration initialized successfully")
    except Exception as e:
        print(f"❌ WordPress integration failed: {e}")
        WORDPRESS_ENABLED = False

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
JWT_SECRET = secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    user_type: str = "visitor"
    company: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    user_type: str
    company: Optional[str] = None
    profile_completion: int = 0

class AnalyticsEvent(BaseModel):
    session_id: str
    event_type: str
    event_data: dict = {}

class PackageUpdate(BaseModel):
    package_id: str
    
class PartnershipUpdate(BaseModel):
    package_id: str
    
class MatchingFilters(BaseModel):
    match_type: str = "all"
    sector: str = "all"
    compatibility: int = 70
    location: str = "all"
    package_level: str = "all"

class UserInteraction(BaseModel):
    to_user_id: int
    interaction_type: str
    metadata: dict = {}

# Database functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with tables and demo data"""
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            user_type TEXT DEFAULT 'visitor',
            visitor_package TEXT DEFAULT 'free',
            partnership_package TEXT,
            exhibition_package TEXT,
            package_expires_at TIMESTAMP,
            b2b_meetings_allowed INTEGER DEFAULT 0,
            b2b_meetings_used INTEGER DEFAULT 0,
            company TEXT,
            position TEXT,
            phone TEXT,
            sector TEXT,
            interests TEXT,
            looking_for TEXT,
            budget_range TEXT,
            languages TEXT,
            certifications TEXT,
            profile_completion INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS partnership_packages (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            features TEXT, -- JSON string
            benefits TEXT, -- JSON string
            visibility_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            compatibility_score INTEGER NOT NULL,
            match_type TEXT, -- automatic, manual
            status TEXT DEFAULT 'pending', -- pending, accepted, declined
            mutual_interests TEXT,
            business_potential TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user1_id) REFERENCES users (id),
            FOREIGN KEY (user2_id) REFERENCES users (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL, -- view, message, meeting_request, connect
            metadata TEXT, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (id),
            FOREIGN KEY (to_user_id) REFERENCES users (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_id TEXT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products_enhanced (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            sector TEXT,
            price REAL,
            currency TEXT DEFAULT 'EUR',
            specifications TEXT,
            images TEXT,
            tags TEXT,
            status TEXT DEFAULT 'draft',
            views_count INTEGER DEFAULT 0,
            engagement_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create demo users if they don't exist
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        demo_users = [
            {
                'email': 'admin@siportevent.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'SIPORTS',
                'user_type': 'admin',
                'company': 'SIPORTS',
                'position': 'Administrateur',
                'sector': 'Événementiel',
                'profile_completion': 100
            },
            {
                'email': 'exposant@example.com',
                'password': 'expo123',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'user_type': 'exhibitor',
                'company': 'Maritime Solutions',
                'position': 'Directeur Commercial',
                'sector': 'Maritime',
                'interests': 'Équipements portuaires, IoT, Automatisation',
                'profile_completion': 85
            },
            {
                'email': 'visiteur@example.com',
                'password': 'visit123',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'user_type': 'visitor',
                'company': 'Port de Marseille',
                'position': 'Responsable Achats',
                'sector': 'Portuaire',
                'interests': 'Grues, Logistique, Sécurité',
                'profile_completion': 70
            },
            {
                'email': 'partenaire@example.com',
                'password': 'part123',
                'first_name': 'Pierre',
                'last_name': 'Durand',
                'user_type': 'partner',
                'company': 'Logistique Plus',
                'position': 'Directeur Partenariats',
                'sector': 'Logistique',
                'interests': 'Transport, Manutention, Entreposage',
                'profile_completion': 90
            }
        ]
        
        for user_data in demo_users:
            password = user_data.pop('password')
            password_hash = generate_password_hash(password)
            
            placeholders = ', '.join(['?' for _ in user_data.keys()])
            columns = ', '.join(user_data.keys())
            
            conn.execute(f'''
                INSERT INTO users (password_hash, {columns})
                VALUES (?, {placeholders})
            ''', [password_hash] + list(user_data.values()))
    
    conn.commit()
    conn.close()

# JWT functions
def create_access_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.get("/api/partnership-packages")
async def get_partnership_packages():
    packages = [
        {
            "id": "platinum",
            "name": "Partenaire Platinum",
            "price": 25000,  # Optimisé de 98000$ à 25000$
            "original_price": 35000,
            "currency": "USD",
            "discount": "29%",
            "features": [
                "Logo 1ère ligne sur tous supports",
                "Mini-site SIPORTS Premium dédié", 
                "4 flags entrée + vidéos LED",
                "Prise de parole inauguration",
                "10.000 invitations personnalisées",
                "1 atelier dédié (3h)",
                "Branding conférence de presse"
            ],
            "benefits": ["ROI: 300-500%", "50.000+ professionnels", "500+ leads qualifiés"],
            "visibility_level": 5
        },
        {
            "id": "gold", 
            "name": "Partenaire Gold",
            "price": 15000,  # Optimisé de 68000$ à 15000$
            "original_price": 22000,
            "currency": "USD",
            "discount": "32%",
            "features": [
                "Logo 2ème ligne supports",
                "Bannière web rotative",
                "2 flags entrée + écrans LED",
                "5.000 invitations",
                "1 atelier dédié (2h)",
                "Espace Musée des ports"
            ],
            "benefits": ["ROI: 200-400%", "30.000+ professionnels", "300+ leads"],
            "visibility_level": 4
        },
        {
            "id": "silver",
            "name": "Partenaire Silver", 
            "price": 8000,   # Optimisé de 48000$ à 8000$
            "original_price": 12000,
            "currency": "USD",
            "discount": "33%",
            "features": [
                "Logo 3ème ligne supports",
                "Présence newsletter",
                "1 flag entrée",
                "2.000 invitations",
                "Catalogue officiel"
            ],
            "benefits": ["ROI: 150-250%", "20.000+ professionnels", "200+ leads"],
            "visibility_level": 3
        },
        {
            "id": "startup",
            "name": "Pack Startup", 
            "price": 2500,   # Nouveau forfait accessible
            "original_price": 4000,
            "currency": "USD", 
            "discount": "38%",
            "features": [
                "Logo espace startup",
                "Stand 9m² inclus",
                "Mentorat inclus",
                "50 invitations",
                "Package jeune entreprise"
            ],
            "benefits": ["ROI: 100-200%", "10.000+ professionnels", "Réseau startup"],
            "visibility_level": 2
        }
    ]
    return {"packages": packages}

@app.get("/api/exhibition-packages")
async def get_exhibition_packages():
    packages = [
        {
            "id": "premium_booth",
            "name": "Stand Premium",
            "price": 8000,    # Optimisé de 15000$ à 8000$
            "original_price": 12000,
            "size": "54 m²",
            "features": [
                "Emplacement premium",
                "Design personnalisé inclus",
                "Équipement audiovisuel complet",
                "Service hostessing 3 jours",
                "100 invitations VIP",
                "Catalogue exposants premium"
            ]
        },
        {
            "id": "standard_booth", 
            "name": "Stand Standard",
            "price": 3500,    # Optimisé de 8000$ à 3500$
            "original_price": 5000,
            "size": "18 m²",
            "features": [
                "Emplacement standard",
                "Équipement de base inclus",
                "50 invitations",
                "Catalogue exposants",
                "Support technique"
            ]
        },
        {
            "id": "startup_booth",
            "name": "Stand Startup",
            "price": 1200,    # Optimisé de 3000$ à 1200$
            "original_price": 2000,
            "size": "9 m²", 
            "features": [
                "Espace dédié startups",
                "Package jeune entreprise",
                "25 invitations",
                "Mentorat inclus",
                "Réseau entrepreneurs"
            ]
        },
        {
            "id": "virtual_booth",
            "name": "Stand Virtuel",
            "price": 500,     # Nouveau forfait très accessible
            "size": "Digital",
            "features": [
                "Présence 100% digitale",
                "Showroom virtuel 3D",
                "Visioconférences illimitées", 
                "Chat en temps réel",
                "Analytics détaillés"
            ]
        }
    ]
    return {"packages": packages}

@app.post("/api/update-partnership")
async def update_partnership(partnership_data: PartnershipUpdate, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Mettre à jour le forfait partenariat
    cursor.execute('''
        UPDATE users 
        SET partnership_package = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (partnership_data.package_id, current_user))
    
    conn.commit()
    conn.close()
    
    return {"message": "Forfait partenariat mis à jour", "package": partnership_data.package_id}

@app.post("/api/matching/generate")
async def generate_matches(filters: MatchingFilters, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer le profil utilisateur
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Simuler l'algorithme de matching (en production, utiliser ML/IA)
    matches = [
        {
            "id": 1,
            "name": "Maritime Solutions International",
            "type": "partner",
            "level": "platinum", 
            "sector": "Équipements portuaires",
            "location": "Maroc",
            "compatibility": 95,
            "mutual_interests": ["Automatisation", "IoT", "Ports intelligents"],
            "business_potential": "Très élevé",
            "description": "Leader mondial en automatisation portuaire",
            "languages": ["Français", "Anglais", "Arabe"]
        },
        {
            "id": 2,
            "name": "Port Authority Morocco",
            "type": "visitor",
            "level": "vip",
            "sector": "Gestion portuaire", 
            "location": "Maroc",
            "compatibility": 92,
            "mutual_interests": ["Digitalisation", "Modernisation"],
            "business_potential": "Très élevé",
            "description": "Autorité portuaire nationale",
            "languages": ["Français", "Arabe", "Anglais"]
        }
    ]
    
    # Filtrer selon les critères
    filtered_matches = []
    for match in matches:
        if filters.match_type != "all" and match["type"] != filters.match_type:
            continue
        if filters.sector != "all" and match["sector"] != filters.sector:
            continue
        if match["compatibility"] < filters.compatibility:
            continue
        filtered_matches.append(match)
    
    conn.close()
    return {"matches": filtered_matches}

@app.post("/api/user-interaction")
async def record_interaction(interaction: UserInteraction, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_interactions (from_user_id, to_user_id, interaction_type, metadata)
        VALUES (?, ?, ?, ?)
    ''', (current_user, interaction.to_user_id, interaction.interaction_type, json.dumps(interaction.metadata)))
    
    conn.commit()
    conn.close()
    
    return {"message": "Interaction enregistrée"}

@app.get("/api/matching/analytics")
async def get_matching_analytics(current_user: int = Depends(get_current_user)):
    return {
        "compatibility_avg": 87,
        "quality_matches": 92,
        "response_rate": 78,
        "total_matches": 24,
        "successful_connections": 18,
        "insights": [
            {
                "type": "recommendation",
                "title": "Optimisez votre profil",
                "message": "Ajoutez vos projets d'innovation pour attirer +40% de partenaires tech"
            },
            {
                "type": "trend", 
                "title": "IA en hausse",
                "message": "Les discussions sur l'IA sont en hausse de +45% parmi vos matches"
            },
            {
                "type": "opportunity",
                "title": "Nouveaux partenaires",
                "message": "3 partenaires Platinum recherchent des solutions dans votre secteur"
            }
        ]
    }

# Admin endpoints
@app.get("/api/admin/dashboard/stats")
async def get_admin_dashboard_stats(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier que c'est un admin
    cursor.execute("SELECT user_type FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    if not user or user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    # Stats globales
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'visitor'")
    total_visitors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'exhibitor'")
    total_exhibitors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'partner'")
    total_partners = cursor.fetchone()[0]
    
    # Comptes en attente (simulé - tous les comptes non-admin sont considérés comme validés par défaut)
    pending_accounts = 0
    validated_accounts = total_users - 1  # Exclure l'admin
    
    conn.close()
    
    return {
        "total_users": total_users,
        "total_visitors": total_visitors,
        "total_exhibitors": total_exhibitors,
        "total_partners": total_partners,
        "pending_accounts": pending_accounts,
        "validated_accounts": validated_accounts,
        "recent_signups": 8,  # Simulé
        "active_sessions": 12  # Simulé
    }

@app.get("/api/admin/users/pending")
async def get_pending_users(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier que c'est un admin
    cursor.execute("SELECT user_type FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    if not user or user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    # Pour la démonstration, retourner quelques utilisateurs "en attente"
    cursor.execute('''
        SELECT id, email, first_name, last_name, user_type, company, created_at
        FROM users 
        WHERE user_type != 'admin' 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    
    users = []
    for row in cursor.fetchall():
        users.append({
            "id": row['id'],
            "email": row['email'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "user_type": row['user_type'],
            "company": row['company'],
            "created_at": row['created_at'],
            "status": "pending"  # Simulé
        })
    
    conn.close()
    return {"users": users}

@app.post("/api/admin/users/{user_id}/validate")
async def validate_user(user_id: int, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier que c'est un admin
    cursor.execute("SELECT user_type FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    if not user or user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    # Vérifier que l'utilisateur existe
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Simuler la validation (dans une vraie app, on ajouterait un champ is_validated)
    cursor.execute('''
        UPDATE users 
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "message": f"Utilisateur {target_user['first_name']} {target_user['last_name']} validé avec succès",
        "user_id": user_id,
        "action": "validated"
    }

@app.post("/api/admin/users/{user_id}/reject")
async def reject_user(user_id: int, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier que c'est un admin
    cursor.execute("SELECT user_type FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    if not user or user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    # Vérifier que l'utilisateur existe
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Simuler le rejet (dans une vraie app, on pourrait désactiver le compte)
    cursor.execute('''
        UPDATE users 
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "message": f"Utilisateur {target_user['first_name']} {target_user['last_name']} rejeté",
        "user_id": user_id,
        "action": "rejected"
    }

@app.get("/api/admin/users")
async def get_all_users(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier que c'est un admin
    cursor.execute("SELECT user_type FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    if not user or user['user_type'] != 'admin':
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    cursor.execute('''
        SELECT id, email, first_name, last_name, user_type, company, 
               visitor_package, partnership_package, created_at, updated_at
        FROM users 
        WHERE user_type != 'admin'
        ORDER BY created_at DESC
    ''')
    
    users = []
    for row in cursor.fetchall():
        users.append({
            "id": row['id'],
            "email": row['email'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "user_type": row['user_type'],
            "company": row['company'],
            "visitor_package": row['visitor_package'],
            "partnership_package": row['partnership_package'],
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        })
    
    conn.close()
    return {"users": users}

# Routes
@app.get("/api/")
async def root():
    return {"message": "SIPORTS API v2.0", "status": "running"}

@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    conn = get_db_connection()
    
    # Check if user exists
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Cet email est déjà enregistré")
    
    # Create user
    password_hash = generate_password_hash(user_data.password)
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, user_type, company, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_data.email, password_hash, user_data.first_name, user_data.last_name, 
          user_data.user_type, user_data.company, user_data.phone))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"message": "Inscription réussie", "user_id": user_id}

@app.get("/api/auth/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupérer les informations de l'utilisateur connecté"""
    try:
        # Décoder le token JWT
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Récupérer les informations utilisateur
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, first_name, last_name, user_type, company, phone,
                   visitor_package, partnership_package, profile_completion
            FROM users WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "user_type": user["user_type"],
            "company": user["company"],
            "phone": user["phone"],
            "visitor_package": user["visitor_package"],
            "partnership_package": user["partnership_package"],
            "profile_completion": user["profile_completion"]
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (login_data.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password_hash'], login_data.password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    access_token = create_access_token(user['id'])
    
    return {
        "access_token": access_token,
        "user": {
            "id": user['id'],
            "email": user['email'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "user_type": user['user_type'],
            "company": user['company'],
            "profile_completion": user['profile_completion']
        }
    }

@app.post("/api/auth/visitor-login")
async def visitor_login():
    # Create temporary visitor account
    visitor_email = f"visiteur_{secrets.token_hex(8)}@example.com"
    visitor_password = secrets.token_hex(8)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = generate_password_hash(visitor_password)
    cursor.execute('''
        INSERT INTO users (email, password_hash, first_name, last_name, user_type, profile_completion)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (visitor_email, password_hash, "Visiteur", "Temporaire", "visitor", 30))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    access_token = create_access_token(user_id)
    
    return {
        "access_token": access_token,
        "user": {
            "id": user_id,
            "email": visitor_email,
            "first_name": "Visiteur",
            "last_name": "Temporaire",
            "user_type": "visitor",
            "profile_completion": 30
        }
    }

@app.get("/api/analytics/profile/completion")
async def get_profile_completion(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Calculate completion score
    completion_score = 0
    total_fields = 10
    
    if user['first_name']: completion_score += 1
    if user['last_name']: completion_score += 1
    if user['email']: completion_score += 1
    if user['company']: completion_score += 1
    if user['position']: completion_score += 1
    if user['phone']: completion_score += 1
    if user['sector']: completion_score += 1
    if user['interests']: completion_score += 1
    if user['user_type'] != 'visitor': completion_score += 1
    
    completion_percentage = int((completion_score / total_fields) * 100)
    
    suggestions = []
    if not user['company']: suggestions.append("Ajoutez votre entreprise")
    if not user['position']: suggestions.append("Précisez votre poste")
    if not user['phone']: suggestions.append("Ajoutez votre numéro de téléphone")
    if not user['sector']: suggestions.append("Sélectionnez votre secteur d'activité")
    if not user['interests']: suggestions.append("Définissez vos centres d'intérêt")
    
    return {
        "completion_score": completion_percentage,
        "suggestions": suggestions,
        "profile_strength": "Excellent" if completion_percentage >= 80 else "Bon" if completion_percentage >= 60 else "À améliorer"
    }

@app.get("/api/analytics/engagement")
async def get_engagement_analytics(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analytics_events WHERE user_id = ?", (current_user,))
    total_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_events WHERE user_id = ?", (current_user,))
    unique_sessions = cursor.fetchone()[0]
    
    conn.close()
    
    engagement_score = min(total_events * 10, 100)
    
    return {
        "engagement_score": engagement_score,
        "total_events": total_events,
        "unique_sessions": max(unique_sessions, 1),
        "insights": [
            "Votre activité a augmenté de 25% cette semaine",
            "Vous avez consulté 8 profils d'exposants",
            "3 nouveaux contacts vous ont ajouté"
        ],
        "recommendations": [
            "Complétez votre profil pour plus de visibilité",
            "Planifiez des rendez-vous avec vos contacts",
            "Explorez les nouveaux produits de votre secteur"
        ]
    }

@app.post("/api/analytics/track")
async def track_event(event_data: AnalyticsEvent, request: Request, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analytics_events (user_id, session_id, event_type, event_data, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (current_user, event_data.session_id, event_data.event_type, 
          json.dumps(event_data.event_data), request.client.host, request.headers.get("user-agent")))
    
    conn.commit()
    conn.close()
    
    return {"message": "Événement enregistré"}

@app.get("/api/features")
async def get_features():
    return {
        "features": [
            "Analytics avancés avec IA",
            "Recommandations personnalisées", 
            "Tracking d'engagement en temps réel",
            "Profils enrichis avec scoring",
            "Gestion de produits avancée",
            "Sessions visiteur temporaires",
            "Interface moderne et responsive",
            "Synchronisation WordPress"
        ],
        "version": "2.0.0",
        "status": "Production Ready"
    }

@app.get("/api/visitor-packages")
async def get_visitor_packages():
    packages = [
        {
            "id": "free",
            "name": "Free Pass",
            "price": "Gratuit",
            "features": [
                "Accès à l'espace exposition",
                "Conférences publiques",
                "Documentation générale",
                "Application mobile du salon",
                "Événements de réseautage"
            ],
            "b2b_meetings": 0,
            "duration_days": 1
        },
        {
            "id": "basic",
            "name": "Basic Pass",
            "price": "150€",
            "features": [
                "Accès aux expositions",
                "Conférences principales",
                "Documentation exposition",
                "Pause café réseautage",
                "2 réunions B2B garanties"
            ],
            "b2b_meetings": 2,
            "duration_days": 1
        },
        {
            "id": "premium",
            "name": "Premium Pass",
            "price": "350€",
            "features": [
                "Tous les avantages Basic",
                "Ateliers spécialisés",
                "Déjeuners de réseautage",
                "5 réunions B2B garanties",
                "Accès salon VIP"
            ],
            "b2b_meetings": 5,
            "duration_days": 2
        },
        {
            "id": "vip",
            "name": "VIP Pass",
            "price": "750€",
            "features": [
                "Tous les avantages Premium",
                "Soirée de gala",
                "Accès aux conférences exclusives",
                "Service de conciergerie dédié",
                "Transferts aéroport inclus",
                "RDV B2B illimités"
            ],
            "b2b_meetings": -1,  # -1 = illimité
            "duration_days": 3
        }
    ]
    return {"packages": packages}

@app.post("/api/update-package")
async def update_user_package(package_data: PackageUpdate, current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Récupérer les informations du forfait
    packages_info = {
        "free": {"meetings": 0, "days": 1},
        "basic": {"meetings": 2, "days": 1},
        "premium": {"meetings": 5, "days": 2},
        "vip": {"meetings": -1, "days": 3}  # -1 = illimité
    }
    
    package_info = packages_info.get(package_data.package_id)
    if not package_info:
        raise HTTPException(status_code=400, detail="Forfait invalide")
    
    # Calculer la date d'expiration (pour démonstration, on ajoute les jours à partir d'aujourd'hui)
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=package_info["days"])
    
    # Mettre à jour l'utilisateur
    cursor.execute('''
        UPDATE users 
        SET visitor_package = ?, 
            package_expires_at = ?,
            b2b_meetings_allowed = ?,
            b2b_meetings_used = 0
        WHERE id = ?
    ''', (package_data.package_id, expires_at, package_info["meetings"], current_user))
    
    conn.commit()
    conn.close()
    
    return {"message": "Forfait mis à jour avec succès", "package": package_data.package_id}

@app.get("/api/user-package-status")
async def get_user_package_status(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT visitor_package, package_expires_at, b2b_meetings_allowed, b2b_meetings_used 
        FROM users WHERE id = ?
    ''', (current_user,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    package_id, expires_at, meetings_allowed, meetings_used = result
    
    # Vérifier si le forfait est expiré
    from datetime import datetime
    is_expired = False
    if expires_at:
        expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00') if expires_at.endswith('Z') else expires_at)
        is_expired = expiry_date < datetime.utcnow()
    
    return {
        "package_id": package_id or "free",
        "expires_at": expires_at,
        "is_expired": is_expired,
        "b2b_meetings": {
            "allowed": meetings_allowed or 0,
            "used": meetings_used or 0,
            "remaining": max(0, (meetings_allowed or 0) - (meetings_used or 0)) if meetings_allowed != -1 else -1
        }
    }

@app.post("/api/book-b2b-meeting")
async def book_b2b_meeting(current_user: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Vérifier le statut du forfait
    cursor.execute('''
        SELECT visitor_package, b2b_meetings_allowed, b2b_meetings_used 
        FROM users WHERE id = ?
    ''', (current_user,))
    
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    package_id, meetings_allowed, meetings_used = result
    
    # Vérifier si l'utilisateur peut réserver un RDV
    if meetings_allowed == 0:
        raise HTTPException(status_code=403, detail="Votre forfait ne permet pas de réserver des RDV B2B")
    
    if meetings_allowed != -1 and meetings_used >= meetings_allowed:
        raise HTTPException(status_code=403, detail="Vous avez atteint la limite de RDV B2B pour votre forfait")
    
    # Incrémenter le compteur de RDV utilisés
    cursor.execute('''
        UPDATE users SET b2b_meetings_used = b2b_meetings_used + 1 WHERE id = ?
    ''', (current_user,))
    
    conn.commit()
    conn.close()
    
    return {"message": "RDV B2B réservé avec succès"}

# =============================================================================
# SIPORTS v2.0 - AI CHATBOT ENDPOINTS
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint principal du chatbot IA SIPORTS v2.0
    Assistance intelligente pour événements maritimes
    """
    try:
        response = await siports_ai_service.generate_response(request)
        logger.info(f"Chatbot response generated successfully for context: {request.context_type}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur endpoint chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du chatbot")

@app.post("/api/chat/exhibitor", response_model=ChatResponse)
async def exhibitor_chat_endpoint(request: ChatRequest):
    """
    Endpoint spécialisé pour recommandations exposants
    """
    request.context_type = "exhibitor"
    return await chat_endpoint(request)

@app.post("/api/chat/package", response_model=ChatResponse) 
async def package_chat_endpoint(request: ChatRequest):
    """
    Endpoint spécialisé pour suggestions de forfaits
    """
    request.context_type = "package"
    return await chat_endpoint(request)

@app.post("/api/chat/event", response_model=ChatResponse)
async def event_chat_endpoint(request: ChatRequest):
    """
    Endpoint spécialisé pour informations événements
    """
    request.context_type = "event"
    return await chat_endpoint(request)

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Récupère l'historique d'une session de chat
    """
    try:
        history = siports_ai_service.get_conversation_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Erreur récupération historique: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur récupération historique")

@app.delete("/api/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Efface l'historique d'une session de chat
    """
    try:
        success = siports_ai_service.clear_conversation_history(session_id)
        if success:
            return {"message": "Historique effacé avec succès"}
        else:
            return {"message": "Session non trouvée"}
    except Exception as e:
        logger.error(f"Erreur effacement historique: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur effacement historique")

@app.post("/api/chat/stream")
async def streaming_chat_endpoint(request: ChatRequest):
    """
    Endpoint streaming pour réponses temps réel
    """
    async def generate_stream():
        try:
            # Générer la réponse normale
            response = await siports_ai_service.generate_response(request)
            
            # Simuler le streaming en envoyant la réponse par chunks
            words = response.response.split()
            for i, word in enumerate(words):
                chunk_data = {
                    "chunk": word + " ",
                    "session_id": response.session_id,
                    "is_final": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Petite pause pour simuler le streaming
                import asyncio
                await asyncio.sleep(0.05)
                
        except Exception as e:
            error_chunk = {"error": str(e), "is_final": True}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/api/chatbot/health")
async def chatbot_health_check():
    """
    Vérification de santé du service chatbot
    """
    try:
        # Test simple du service
        test_request = ChatRequest(message="test health", context_type="general")
        response = await siports_ai_service.generate_response(test_request)
        
        return {
            "status": "healthy",
            "service": "siports-ai-chatbot",
            "version": "2.0.0",
            "mock_mode": siports_ai_service.mock_mode,
            "model": siports_ai_service.model_name,
            "test_response_length": len(response.response),
            "active_sessions": len(siports_ai_service.conversation_history)
        }
    except Exception as e:
        logger.error(f"Health check chatbot failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "siports-ai-chatbot"
        }

@app.get("/api/chatbot/stats")
async def chatbot_statistics():
    """
    Statistiques du chatbot
    """
    try:
        active_sessions = len(siports_ai_service.conversation_history)
        total_messages = sum(len(history) for history in siports_ai_service.conversation_history.values())
        
        return {
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "service_mode": "mock" if siports_ai_service.mock_mode else "ollama",
            "model_name": siports_ai_service.model_name,
            "uptime": "Service active"
        }
    except Exception as e:
        logger.error(f"Erreur statistiques chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur récupération statistiques")

# =============================================================================
# END AI CHATBOT ENDPOINTS  
# =============================================================================

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    logging.info("🚀 SIPORTS API Server Started")
    logging.info("📊 Database initialized with demo data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)