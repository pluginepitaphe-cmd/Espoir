#!/usr/bin/env python3
"""
SIPORTS v2.0 - Minimal Backend for Railway
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Import database
from database import init_database, test_connection, is_postgresql

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="SIPORTS v2.0 API",
    description="API pour événements maritimes",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    message: str

# Routes
@app.get("/")
async def root():
    """API Status"""
    return {
        "message": "SIPORTS v2.0 API",
        "status": "active", 
        "version": "2.0.0",
        "database": "postgresql" if is_postgresql() else "sqlite"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    health_status = {
        "status": "healthy",
        "service": "siports-api",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "database_type": "postgresql" if is_postgresql() else "sqlite",
        "checks": {}
    }

    # Test database
    try:
        if test_connection():
            health_status["checks"]["database"] = "healthy"
        else:
            health_status["checks"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status

@app.post("/api/chatbot/chat")
async def chat(request: ChatRequest):
    """Simple chatbot"""
    responses = [
        "Bonjour ! Je suis l'assistant IA de SIPORTS.",
        "Comment puis-je vous aider avec SIPORTS ?",
        "SIPORTS est votre plateforme d'événements maritimes !"
    ]
    
    import random
    response = random.choice(responses)
    
    return {
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
async def test_api():
    """Test endpoint"""
    return {
        "message": "API Test successful",
        "database_connected": test_connection(),
        "database_type": "postgresql" if is_postgresql() else "sqlite"
    }

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 SIPORTS v2.0 API starting...")
    logger.info(f"Database type: {'PostgreSQL' if is_postgresql() else 'SQLite'}")
    
    try:
        init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    logger.info("🎉 SIPORTS API ready!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)