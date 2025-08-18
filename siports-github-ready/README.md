# 🚀 SIPORTS v2.0 - Production Complete

## 📦 Application Maritime Complète

SIPORTS v2.0 est une plateforme événementielle maritime complète avec backend FastAPI et frontend React.

### 🏗️ Architecture

- **Backend** : FastAPI + PostgreSQL (déployé sur Railway)
- **Frontend** : React + Vite + Tailwind (déployé sur Vercel)
- **Database** : PostgreSQL en production, SQLite en local
- **Authentication** : JWT multi-rôles

### 🚀 Déploiement Rapide

#### Backend (Railway)
1. Créer nouveau projet Railway
2. Connecter ce repo GitHub
3. Ajouter service PostgreSQL
4. Variables d'environnement :
   ```
   JWT_SECRET_KEY=votre-clé-secrète-production
   DATABASE_URL=${DATABASE_URL} (auto-fourni par Railway)
   ```

#### Frontend (Vercel)
1. Créer nouveau projet Vercel
2. Connecter ce repo GitHub
3. Variables d'environnement :
   ```
   VITE_BACKEND_URL=https://votre-backend.up.railway.app
   VITE_APP_NAME=SIPORTS v2.0
   ```

### 🧪 Comptes de Test

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | admin@siportevent.com | admin123 |
| Exposant | exposant@example.com | exhibitor123 |
| Visiteur | visitor@example.com | visitor123 |

### 📱 Fonctionnalités

- ✅ Authentification multi-rôles
- ✅ Dashboard administrateur
- ✅ Annuaire exposants avec profils
- ✅ Système de forfaits visiteur/partenaire
- ✅ Chatbot IA SIPORTS v2.0
- ✅ Mini-sites exposants professionnels
- ✅ Calendrier et réseautage
- ✅ Analytics temps réel

### 🔧 Développement Local

```bash
# Backend
cd backend/
pip install -r requirements.txt
python server.py

# Frontend
cd frontend/
npm install
npm run dev
```

### 📡 API Endpoints

- `POST /api/auth/login` - Authentification
- `GET /api/exposants` - Liste exposants
- `GET /api/visitor-packages` - Forfaits visiteur
- `GET /api/admin/dashboard/stats` - Stats admin
- `POST /api/chat` - Chatbot IA

### 🌐 URLs Production

- **API Backend** : https://siportevent-production.up.railway.app
- **Frontend App** : https://votre-app.vercel.app
- **API Docs** : https://votre-backend.up.railway.app/api/docs

---

**Version** : 2.0.0  
**Status** : Production Ready ✅