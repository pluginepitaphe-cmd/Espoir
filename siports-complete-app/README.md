# 🚀 SIPORTS v2.0 - Application Complète

## 📦 Package Complet Backend + Frontend

Cette archive contient l'application SIPORTS v2.0 complète avec :
- **Backend FastAPI** (prêt pour Railway + PostgreSQL)
- **Frontend React** (prêt pour Vercel)
- **Documentation complète** de déploiement

## 📁 Structure du Projet

```
siports-complete-app/
├── backend/                # Backend FastAPI complet
│   ├── server.py          # Serveur principal
│   ├── requirements.txt   # Dépendances Python
│   ├── railway.toml       # Config Railway
│   ├── Procfile          # Process definition
│   ├── database.py       # Gestion base de données
│   ├── chatbot_service.py # Service chatbot IA
│   └── .env.example      # Variables d'environnement
├── frontend/              # Frontend React complet
│   ├── src/              # Code source React
│   ├── public/           # Assets statiques
│   ├── package.json      # Dépendances Node.js
│   ├── vercel.json       # Config Vercel
│   ├── vite.config.js    # Config Vite
│   └── .env.example      # Variables d'environnement
├── docs/                 # Documentation
│   ├── DEPLOY_BACKEND.md
│   ├── DEPLOY_FRONTEND.md
│   └── API_DOCUMENTATION.md
├── docker-compose.yml    # Développement local
└── README.md            # Ce fichier
```

## 🚀 Déploiement Rapide

### 🔧 Backend sur Railway
```bash
cd backend/
# Suivre les instructions dans docs/DEPLOY_BACKEND.md
```

### 🌐 Frontend sur Vercel
```bash
cd frontend/
# Suivre les instructions dans docs/DEPLOY_FRONTEND.md
```

## ⚡ Développement Local

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

## 🧪 Comptes de Test

- **Admin**: admin@siportevent.com / admin123
- **Exposant**: exposant@example.com / exhibitor123
- **Visiteur**: visitor@example.com / visitor123

## 📱 Fonctionnalités Incluses

### Backend (FastAPI + PostgreSQL)
- ✅ Authentification JWT multi-rôles
- ✅ API REST complète
- ✅ Dashboard administrateur
- ✅ Gestion packages visiteur/partenaire
- ✅ Service chatbot IA SIPORTS v2.0
- ✅ Mini-sites exposants
- ✅ Analytics temps réel
- ✅ Base de données PostgreSQL

### Frontend (React + Vite)
- ✅ Interface utilisateur moderne
- ✅ Dashboard admin complet
- ✅ Système d'authentification
- ✅ Pages exposants professionnelles
- ✅ Calendrier et réseautage
- ✅ Interface responsive
- ✅ Intégration chatbot

## 🔗 URLs de Production

- **Backend Railway**: https://siportevent-production.up.railway.app
- **Frontend Vercel**: [Votre URL après déploiement]
- **Documentation API**: /api/docs

## 📞 Support

Consultez les fichiers de documentation dans le dossier `docs/` pour :
- Instructions de déploiement détaillées
- Configuration des variables d'environnement  
- Troubleshooting et FAQ
- Documentation API complète

---

**Version**: 2.0.0  
**Date**: 15 Août 2025  
**Status**: Production Ready ✅