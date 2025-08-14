# 🚢 SIPORTS v2.0 Backend - Production Ready

Backend FastAPI optimisé pour Railway avec configuration de production.

## 🚀 Configuration Production

- ✅ **Gunicorn + Uvicorn Workers** - Performance optimale
- ✅ **Health Checks** - Monitoring intégré
- ✅ **SQLite + Migration ready** - Base de données flexible
- ✅ **JWT Authentication** - Sécurité renforcée
- ✅ **CORS configuré** - Frontend integration
- ✅ **Chatbot IA** - Service intelligent

## 🔧 Variables d'environnement Railway

```env
ENVIRONMENT=production
LOG_LEVEL=INFO
JWT_SECRET_KEY=your-secure-jwt-key
DATABASE_URL=instance/siports_production.db
```

## 📊 Endpoints principaux

- `GET /` - API status
- `GET /health` - Health check avec DB validation
- `POST /api/auth/login` - Authentication
- `GET /api/visitor-packages` - Packages
- `POST /api/chatbot/chat` - AI Chat

## 🧪 Tests rapides

```bash
curl https://your-app.up.railway.app/
curl https://your-app.up.railway.app/health
```

**Déployé avec Railway 🚄 - Configuration optimisée pour la production**