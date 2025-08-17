# 🚀 Déploiement Backend SIPORTS sur Railway

## 📋 Prérequis

1. **Compte Railway** : https://railway.app
2. **GitHub Repository** (optionnel mais recommandé)
3. **Variables d'environnement** configurées

## 🚀 Déploiement Rapide

### Option 1: Déploiement Direct

1. **Connectez-vous à Railway** : https://railway.app
2. **Nouveau Projet** → "Deploy from GitHub" ou "Deploy Now"
3. **Uploadez** le dossier `backend/`
4. **Railway détecte** automatiquement Python/FastAPI
5. **Variables d'environnement** (voir section ci-dessous)
6. **Deploy** automatique

### Option 2: Via GitHub (Recommandé)

1. **Créer un repo GitHub** avec le contenu de `backend/`
2. **Connecter Railway** à votre repo
3. **Auto-deploy** sur chaque push
4. **Variables d'environnement** dans Railway Dashboard

## 🔧 Configuration Variables d'Environnement

Dans Railway Dashboard → Settings → Variables :

```env
# JWT Secret (OBLIGATOIRE)
JWT_SECRET_KEY=votre-clé-super-secrète-production

# Database (Automatique avec Railway PostgreSQL)
DATABASE_URL=${{DATABASE_URL}}

# Optionnel
CORS_ORIGINS=*
DEBUG=false
LOG_LEVEL=INFO
```

## 🗄️ Base de Données PostgreSQL

1. **Ajouter PostgreSQL** dans Railway :
   - Dashboard → Add Service → PostgreSQL
   - Connexion automatique via `${{DATABASE_URL}}`

2. **Variables automatiques** :
   - `DATABASE_URL` - URL complète de connexion
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

## 🔍 Configuration Railway

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:$PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PORT = "8001"

[healthcheck]
path = "/"
timeout = 300
interval = 30
```

### Procfile (Fallback)
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --host 0.0.0.0 --port $PORT
```

## ✅ Vérification du Déploiement

### 1. Health Check
```bash
curl https://votre-app.up.railway.app/
```

### 2. API Documentation
```
https://votre-app.up.railway.app/api/docs
```

### 3. Test Authentification
```bash
curl -X POST "https://votre-app.up.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@siportevent.com","password":"admin123"}'
```

## 🔧 Troubleshooting

### Problèmes Courants

1. **Build Failed** :
   - Vérifier `requirements.txt`
   - Vérifier Python version (3.11+)

2. **Database Connection** :
   - Vérifier que PostgreSQL est ajouté
   - Vérifier `DATABASE_URL`

3. **Port Issues** :
   - Railway utilise `$PORT` automatiquement
   - Server.py doit écouter sur `0.0.0.0:$PORT`

### Logs de Debug
```bash
# Via Railway CLI
railway logs
```

## 🔐 Sécurité Production

1. **JWT_SECRET_KEY** unique et complexe
2. **CORS_ORIGINS** limité aux domaines autorisés
3. **DEBUG=false** en production
4. **HTTPS** activé automatiquement par Railway

## 📊 Monitoring

1. **Railway Dashboard** - Métriques automatiques
2. **Health Checks** - Configurés automatiquement
3. **Logs** - Centralisés dans Railway

---

**🎯 Votre backend sera accessible à** : `https://votre-projet.up.railway.app`