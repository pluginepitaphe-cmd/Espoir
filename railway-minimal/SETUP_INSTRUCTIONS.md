# 🚀 SETUP RAILWAY - 4 FICHIERS MINIMAL

## ✅ PostgreSQL URL mise à jour

**Votre URL :** `postgresql://postgres:EwHGholrYryNDKptvWQbCBYNYgYcSkUy@postgres.railway.internal:5432/railway`

## 🔧 Variables Railway à configurer

**Railway** → **Backend Service** → **Variables** :

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:EwHGholrYryNDKptvWQbCBYNYgYcSkUy@postgres.railway.internal:5432/railway
```

## 📤 Instructions upload GitHub

1. **Décompressez** ce package
2. **GitHub** → **Supprimez** tous les anciens fichiers
3. **Upload** ces 4 fichiers :
   - server.py
   - database.py  
   - requirements.txt
   - railway.toml
4. **Commit** : "🚀 Minimal Railway deployment"

## 🧪 Tests après déploiement

```bash
# Test API
curl https://votre-app.up.railway.app/

# Test health check  
curl https://votre-app.up.railway.app/health

# Test database connection
curl https://votre-app.up.railway.app/api/test
```

## ✅ Réponses attendues

**Health check :**
```json
{
  "status": "healthy",
  "database_type": "postgresql", 
  "checks": {"database": "healthy"}
}
```

**API Test :**
```json
{
  "message": "API Test successful",
  "database_connected": true,
  "database_type": "postgresql"
}
```

## 🎉 Fonctionnalités

- ✅ FastAPI backend minimal
- ✅ PostgreSQL automatique  
- ✅ Health checks
- ✅ Gunicorn production
- ✅ 4 endpoints de test

**Téléchargez → Upload GitHub → Configurez variables → Ça marche ! 🚀**