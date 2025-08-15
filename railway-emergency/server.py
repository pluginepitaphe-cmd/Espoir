#!/usr/bin/env python3
"""
SIPORTS Emergency - Ultra Simple Version
Debug mode for Railway deployment
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple FastAPI app
app = FastAPI(title="SIPORTS Emergency API", version="1.0.0")

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment info
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'emergency')
DATABASE_URL = os.environ.get('DATABASE_URL', 'not_configured')

@app.get("/")
async def root():
    """Emergency API Status"""
    logger.info("Root endpoint called")
    return {
        "message": "SIPORTS Emergency API",
        "status": "running",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "database_configured": "postgresql" in DATABASE_URL if DATABASE_URL else False
    }

@app.get("/health")
async def health_check():
    """Simple health check - NO DATABASE"""
    logger.info("Health check called")
    
    health_status = {
        "status": "healthy",
        "service": "siports-emergency",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "checks": {
            "api": "healthy",
            "database": "skipped"  # Skip DB check for now
        }
    }
    
    logger.info(f"Health check response: {health_status}")
    return health_status

@app.get("/debug")
async def debug_info():
    """Debug information"""
    logger.info("Debug endpoint called")
    
    return {
        "environment_vars": {
            "PORT": os.environ.get('PORT', 'not_set'),
            "ENVIRONMENT": os.environ.get('ENVIRONMENT', 'not_set'),
            "DATABASE_URL": "configured" if os.environ.get('DATABASE_URL') else "not_set"
        },
        "python_version": "3.x",
        "working_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    logger.info("Test endpoint called")
    return {
        "message": "Test successful",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Minimal startup"""
    logger.info("🚨 SIPORTS Emergency API starting...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {os.environ.get('PORT', 'not_set')}")
    logger.info(f"Database URL configured: {'Yes' if DATABASE_URL != 'not_configured' else 'No'}")
    logger.info("✅ Emergency API ready - No database connection attempted")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")