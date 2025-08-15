#!/usr/bin/env python3
"""
SIPORTS v2 - With PostgreSQL Test
Version progressive avec base de données
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

# Configure minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple FastAPI app
app = FastAPI(title="SIPORTS v2 PostgreSQL", version="2.0.0")

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment info
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
DATABASE_URL = os.environ.get('DATABASE_URL', 'not_configured')

# Database functions
def is_postgresql():
    """Check if using PostgreSQL"""
    return DATABASE_URL.startswith("postgresql://")

def test_database_connection():
    """Test database connection"""
    if not DATABASE_URL or DATABASE_URL == 'not_configured':
        return False, "DATABASE_URL not configured"
    
    try:
        # Fix postgres:// to postgresql://
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, "PostgreSQL connection successful"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"

def init_simple_database():
    """Initialize simple test table"""
    if not DATABASE_URL or DATABASE_URL == 'not_configured':
        return False, "No database configured"
    
    try:
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Create simple test table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS siports_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            conn.execute(text("""
                INSERT INTO siports_test (name) 
                VALUES ('SIPORTS Backend Test') 
                ON CONFLICT DO NOTHING
            """))
            
            conn.commit()
            logger.info("✅ Database initialized with test table")
            return True, "Database initialized successfully"
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False, f"Database init failed: {str(e)}"

@app.get("/")
async def root():
    """API Status with database info"""
    logger.info("Root endpoint called")
    
    db_connected, db_message = test_database_connection()
    
    return {
        "message": "SIPORTS v2.0 with PostgreSQL",
        "status": "running",
        "version": "2.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "database": {
            "configured": DATABASE_URL != 'not_configured',
            "type": "postgresql" if is_postgresql() else "unknown",
            "connection": "success" if db_connected else "failed",
            "message": db_message
        }
    }

@app.get("/health")
async def health_check():
    """Health check with database test"""
    logger.info("Health check called")
    
    health_status = {
        "status": "healthy",
        "service": "siports-v2-postgresql",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "checks": {
            "api": "healthy"
        }
    }
    
    # Test database if configured
    if DATABASE_URL and DATABASE_URL != 'not_configured':
        db_connected, db_message = test_database_connection()
        health_status["checks"]["database"] = "healthy" if db_connected else "unhealthy"
        health_status["database_message"] = db_message
        
        if not db_connected:
            health_status["status"] = "degraded"
    else:
        health_status["checks"]["database"] = "not_configured"
    
    logger.info(f"Health check response: {health_status}")
    return health_status

@app.get("/database/test")
async def test_database():
    """Test database connection and operations"""
    logger.info("Database test endpoint called")
    
    if not DATABASE_URL or DATABASE_URL == 'not_configured':
        return {
            "status": "error",
            "message": "DATABASE_URL not configured",
            "timestamp": datetime.now().isoformat()
        }
    
    # Test connection
    db_connected, connection_message = test_database_connection()
    
    if not db_connected:
        return {
            "status": "error",
            "connection": "failed",
            "message": connection_message,
            "timestamp": datetime.now().isoformat()
        }
    
    # Test initialization
    init_success, init_message = init_simple_database()
    
    return {
        "status": "success" if init_success else "error",
        "connection": "success",
        "connection_message": connection_message,
        "initialization": "success" if init_success else "failed",
        "init_message": init_message,
        "database_url_configured": True,
        "database_type": "postgresql",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug")
async def debug_info():
    """Debug information with database details"""
    logger.info("Debug endpoint called")
    
    return {
        "environment_vars": {
            "PORT": os.environ.get('PORT', 'not_set'),
            "ENVIRONMENT": os.environ.get('ENVIRONMENT', 'not_set'),
            "DATABASE_URL": "configured" if os.environ.get('DATABASE_URL') else "not_set",
            "DATABASE_TYPE": "postgresql" if is_postgresql() else "unknown"
        },
        "database": {
            "url_configured": DATABASE_URL != 'not_configured',
            "is_postgresql": is_postgresql(),
            "connection_test": test_database_connection()[0] if DATABASE_URL != 'not_configured' else False
        },
        "python_version": "3.x",
        "working_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup with database initialization"""
    logger.info("🚀 SIPORTS v2.0 with PostgreSQL starting...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {os.environ.get('PORT', 'not_set')}")
    logger.info(f"Database URL configured: {'Yes' if DATABASE_URL != 'not_configured' else 'No'}")
    
    if DATABASE_URL and DATABASE_URL != 'not_configured':
        logger.info(f"Database type: {'PostgreSQL' if is_postgresql() else 'Unknown'}")
        
        # Test database connection
        db_connected, db_message = test_database_connection()
        if db_connected:
            logger.info("✅ Database connection successful")
            
            # Initialize database
            init_success, init_message = init_simple_database()
            if init_success:
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning(f"⚠️ Database initialization failed: {init_message}")
        else:
            logger.warning(f"⚠️ Database connection failed: {db_message}")
    else:
        logger.info("⚠️ No database configured")
    
    logger.info("✅ SIPORTS v2.0 ready!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")