#!/bin/bash
# 🚀 Commandes de déploiement SIPORTS v2.0 - Exécution manuelle

echo "🚀 DÉPLOIEMENT SIPORTS v2.0 - COMMANDES MANUELLES"
echo "================================================="
echo ""
echo "⚠️  ATTENTION : Ces commandes nécessitent une exécution dans un terminal interactif"
echo "avec accès à un navigateur web pour l'authentification."
echo ""

echo "🔧 ÉTAPE 1: PRÉPARATION TERMINÉE"
echo "==============================="
echo "✅ Backend configuré (Railway)"
echo "✅ Frontend buildé (Vercel)"
echo "✅ CLI installés"
echo ""

echo "🔐 ÉTAPE 2: AUTHENTIFICATION REQUISE"
echo "===================================="
echo "Exécutez ces commandes dans votre terminal local :"
echo ""
echo "# Connexion Railway"
echo "railway login"
echo ""
echo "# Connexion Vercel"
echo "vercel login"
echo ""

echo "🚂 ÉTAPE 3: DÉPLOIEMENT BACKEND (Railway)"
echo "========================================="
echo "cd backend"
echo ""
echo "# Créer le projet Railway"
echo 'railway new "siports-backend-v2"'
echo ""
echo "# Configurer les variables"
echo "railway variables set PORT=8000"
echo 'railway variables set JWT_SECRET_KEY="siports-jwt-production-$(date +%s)"'
echo 'railway variables set DATABASE_URL="instance/siports_production.db"'
echo 'railway variables set PYTHONPATH="/app"'
echo ""
echo "# Déployer"
echo "railway deploy"
echo ""
echo "# Récupérer l'URL"
echo "railway status"
echo "# Notez l'URL fournie (ex: https://siports-backend-production.up.railway.app)"
echo ""

echo "⚡ ÉTAPE 4: DÉPLOIEMENT FRONTEND (Vercel)"
echo "========================================"
echo "cd .."
echo ""
echo "# Mettre à jour l'URL backend dans frontend/.env"
echo 'echo "VITE_BACKEND_URL=https://VOTRE-URL-RAILWAY.up.railway.app" > frontend/.env'
echo 'echo "VITE_APP_NAME=SIPORTS v2.0" >> frontend/.env'
echo 'echo "VITE_APP_VERSION=2.0.0" >> frontend/.env'
echo ""
echo "# Rebuild avec la vraie URL"
echo "yarn build"
echo ""
echo "# Déployer sur Vercel"
echo "vercel --prod"
echo ""

echo "🧪 ÉTAPE 5: TESTS"
echo "================"
echo "# Tester le backend"
echo 'curl "https://VOTRE-URL-RAILWAY.up.railway.app/api/"'
echo ""
echo "# Tester le frontend"
echo 'curl "https://VOTRE-URL-VERCEL.vercel.app"'
echo ""

echo "🎊 URLS FINALES"
echo "==============="
echo "Frontend: https://VOTRE-URL-VERCEL.vercel.app"
echo "Backend:  https://VOTRE-URL-RAILWAY.up.railway.app"
echo "Admin:    https://VOTRE-URL-VERCEL.vercel.app/admin/dashboard"
echo "Mini-site: https://VOTRE-URL-VERCEL.vercel.app/exposant/1/mini-site"
echo ""
echo "👤 COMPTE ADMIN:"
echo "Email: admin@siportevent.com"
echo "Password: admin123"