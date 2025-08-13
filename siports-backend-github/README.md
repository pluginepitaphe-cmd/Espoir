# 🚢 SIPORTS v2.0 Backend

Backend FastAPI pour SIPORTS - Plateforme d'événements maritimes avec IA

## 🚀 Déploiement Railway

Ce backend est optimisé pour Railway avec :

- ✅ FastAPI + SQLite
- ✅ Chatbot IA intégré  
- ✅ Authentification JWT
- ✅ Mini-sites exposants
- ✅ Dashboard admin

## 📁 Structure

- `server.py` - Serveur principal FastAPI
- `chatbot_service.py` - Service chatbot IA
- `requirements.txt` - Dépendances Python
- `railway.json` - Configuration Railway
- `instance/` - Base de données SQLite

## 🔧 Variables d'environnement

```env
PORT=8000
JWT_SECRET_KEY=siports-jwt-production-secure-2024
DATABASE_URL=instance/siports_production.db
PYTHONPATH=/app
```

## 🧪 Endpoints principaux

- `GET /` - API status
- `GET /api/chatbot/health` - Chatbot health check
- `POST /api/auth/login` - Authentification admin
- `GET /api/visitor-packages` - Forfaits visiteurs

## 📊 Fonctionnalités

- **40+ endpoints API**
- **Chatbot IA conversationnel**
- **3 niveaux de mini-sites exposants**
- **Système de forfaits monétisé**
- **Dashboard admin complet**

Déployé automatiquement sur Railway 🚄