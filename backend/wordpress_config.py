#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration WordPress pour SIPORTS
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class WordPressConfig(BaseSettings):
    # Configuration base de données WordPress
    wp_db_host: str = os.getenv("WP_DB_HOST", "localhost")
    wp_db_name: str = os.getenv("WP_DB_NAME", "siportevent_db")
    wp_db_user: str = os.getenv("WP_DB_USER", "siportevent_user")
    wp_db_password: str = os.getenv("WP_DB_PASSWORD", "")
    wp_table_prefix: str = os.getenv("WP_TABLE_PREFIX", "wp_")
    wp_db_port: int = int(os.getenv("WP_DB_PORT", "3306"))
    
    # Configuration JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "siports-wordpress-integration-secret-2024")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Configuration SIPORTS
    wordpress_url: str = os.getenv("WORDPRESS_URL", "https://siportevent.com")
    siports_api_url: str = os.getenv("SIPORTS_API_URL", "https://ec48b228-5fe8-445c-98da-33775eea8a9d.preview.emergentagent.com")
    
    # Configuration CORS
    cors_origins: List[str] = [
        "https://siportevent.com",
        "https://www.siportevent.com",
        "https://ec48b228-5fe8-445c-98da-33775eea8a9d.preview.emergentagent.com",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields like DATABASE_URL

# Instance globale de configuration
wp_config = WordPressConfig()

# Configuration des mappings de données
SIPORTS_TO_WP_USER_MAPPING = {
    "id": "siports_user_id",
    "email": "user_email",
    "first_name": "first_name", 
    "last_name": "last_name",
    "user_type": "siports_user_type",
    "visitor_package": "siports_visitor_package",
    "partnership_package": "siports_partnership_package",
    "company": "siports_company",
    "phone": "siports_phone",
    "created_at": "siports_created_at"
}

ERROR_MESSAGES = {
    "auth_failed": "Authentification échouée",
    "token_expired": "Token expiré", 
    "token_invalid": "Token invalide",
    "permission_denied": "Permission refusée",
    "sync_failed": "Synchronisation échouée",
    "db_connection_failed": "Connexion base de données échouée"
}

def get_database_config():
    """Retourne la configuration de base de données WordPress"""
    return {
        "host": wp_config.wp_db_host,
        "port": wp_config.wp_db_port,
        "database": wp_config.wp_db_name,
        "user": wp_config.wp_db_user,
        "password": wp_config.wp_db_password,
        "charset": "utf8mb4",
        "autocommit": True
    }

def get_table_name(base_table: str) -> str:
    """Retourne le nom complet d'une table WordPress avec préfixe"""
    return f"{wp_config.wp_table_prefix}{base_table}"