#!/usr/bin/env python3
"""
Simple Database Module - PostgreSQL/SQLite
"""

import os
import sqlite3
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///test.db')

# Fix PostgreSQL URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def is_postgresql():
    """Check if using PostgreSQL"""
    return DATABASE_URL.startswith("postgresql://")

def get_engine():
    """Get SQLAlchemy engine"""
    return create_engine(DATABASE_URL)

def test_connection():
    """Test database connection"""
    try:
        if is_postgresql():
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        else:
            conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
            conn.execute("SELECT 1")
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def init_database():
    """Initialize database"""
    try:
        if is_postgresql():
            logger.info("Initializing PostgreSQL database...")
            engine = get_engine()
            
            with engine.connect() as conn:
                # Create simple test table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Insert test data
                conn.execute(text("""
                    INSERT INTO test_table (name) 
                    VALUES ('SIPORTS Test') 
                    ON CONFLICT DO NOTHING
                """))
                
                conn.commit()
                logger.info("✅ PostgreSQL database initialized")
                
        else:
            logger.info("Initializing SQLite database...")
            conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                INSERT OR IGNORE INTO test_table (name) VALUES ('SIPORTS Test')
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ SQLite database initialized")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise