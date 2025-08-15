# SIPORTS Frontend - Package Vercel Corrigé

## 🎯 Package prêt pour déploiement Vercel

Ce package contient la version corrigée du frontend SIPORTS v2.0 configuré pour déployer sur Vercel avec connexion au backend Railway.

### ✅ Corrections Appliquées

1. **Backend URL corrigée** : Pointe vers `https://siportevent-production.up.railway.app`
2. **Variables d'environnement** : Configurées pour Vite et Vercel
3. **Configuration Vercel** : Routes API proxy vers Railway backend
4. **Dependencies** : Toutes les dépendances nécessaires incluses
5. **Tailwind** : Configuration complète pour le styling

### 🚀 Déploiement Vercel

1. **Uploader ce dossier** sur Vercel ou connecter via GitHub
2. **Configurer les variables d'environnement** (déjà dans .env.production)
3. **Déployer** - La configuration est automatique

### 📋 Variables d'Environnement

```env
VITE_BACKEND_URL=https://siportevent-production.up.railway.app
VITE_APP_NAME=SIPORTS v2.0
VITE_APP_VERSION=2.0.0
REACT_APP_BACKEND_URL=https://siportevent-production.up.railway.app
```

### 🔧 Scripts Disponibles

```bash
yarn dev      # Développement local
yarn build    # Build production
yarn preview  # Aperçu local du build
```

### 🏗️ Backend Railway

Le frontend se connecte automatiquement au backend Railway :
- URL : https://siportevent-production.up.railway.app
- Database : PostgreSQL
- Features : Authentification, Chatbot IA, Packages, Admin Dashboard

### 🧪 Comptes de Test

- **Admin** : admin@siportevent.com / admin123
- **Exposant** : exposant@example.com / exhibitor123  
- **Visiteur** : visitor@example.com / visitor123

### 📱 Fonctionnalités Incluses

- ✅ Authentification multi-rôles
- ✅ Dashboard admin complet
- ✅ Système de packages visiteur/partenaire
- ✅ Chatbot IA SIPORTS v2.0
- ✅ Mini-sites exposants professionnels
- ✅ Calendrier et réseautage
- ✅ Analytics en temps réel
- ✅ Interface responsive

---

**Date de création** : 15 Août 2025  
**Version** : 2.0.0  
**Status** : Prêt pour production