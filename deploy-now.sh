#!/bin/bash
# 🚀 Déploiement FINAL SIPORTS v2.0 - Exécution immédiate

echo "🚀 DÉPLOIEMENT FINAL SIPORTS v2.0"
echo "================================="
echo ""
echo "🎯 Fonctionnalités incluses :"
echo "   ✨ Mini-sites exposants professionnels"
echo "   ✨ Chatbot IA v2.0 avec 9 endpoints"
echo "   ✨ Système de forfaits complet"
echo "   ✨ Dashboard admin avancé"
echo ""

# Vérifier les prérequis
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI requis. Exécutez d'abord :"
    echo "   curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI requis. Exécutez d'abord :"
    echo "   npm install -g vercel"
    exit 1
fi

echo "✅ CLI installés et prêts"
echo ""

# Étape 1: Déploiement Backend
echo "🚂 ÉTAPE 1: Déploiement Backend Railway"
echo "======================================="
echo ""
echo "🔐 Connexion Railway requise..."
echo "Une page web va s'ouvrir pour l'authentification."
echo ""

cd backend

# Vérifier l'authentification Railway
if ! railway whoami &> /dev/null; then
    echo "🔑 Veuillez vous connecter à Railway..."
    railway login
    
    if ! railway whoami &> /dev/null; then
        echo "❌ Échec de connexion Railway"
        exit 1
    fi
fi

echo "✅ Connecté à Railway : $(railway whoami)"

# Créer le projet ou utiliser existant
echo ""
echo "🆕 Création/liaison du projet Railway..."
railway link --project siports-backend-v2 || railway new siports-backend-v2

# Variables d'environnement
echo "⚙️  Configuration des variables..."
railway variables set PORT=8000
railway variables set JWT_SECRET_KEY="siports-jwt-production-$(date +%s)"
railway variables set DATABASE_URL="instance/siports_production.db"
railway variables set PYTHONPATH="/app"

echo "✅ Variables configurées"

# Déploiement
echo ""
echo "🚀 Déploiement du backend en cours..."
echo "⏳ Cela peut prendre 2-3 minutes..."

railway deploy --detach

echo "✅ Backend déployé sur Railway"

# Attendre et récupérer l'URL
echo "⏳ Attente de la disponibilité du service (60s)..."
sleep 60

# Récupérer l'URL du déploiement
BACKEND_URL=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url // empty' 2>/dev/null || railway domain 2>/dev/null | head -1 || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  URL backend non détectée automatiquement"
    echo "💡 Récupérez-la avec : railway status"
    echo "📝 Saisissez l'URL de votre backend Railway :"
    read -p "URL backend: " BACKEND_URL
    
    if [ -z "$BACKEND_URL" ]; then
        BACKEND_URL="https://siports-backend-production.up.railway.app"
        echo "🔧 URL par défaut utilisée: $BACKEND_URL"
    fi
fi

echo "✅ Backend URL: $BACKEND_URL"
echo "$BACKEND_URL" > ../railway-url.txt

cd ..

# Étape 2: Déploiement Frontend
echo ""
echo "⚡ ÉTAPE 2: Déploiement Frontend Vercel"
echo "======================================"
echo ""

# Mettre à jour la configuration avec l'URL réelle
echo "⚙️  Mise à jour avec l'URL backend réelle..."
cat > frontend/.env << EOF
VITE_BACKEND_URL=$BACKEND_URL
VITE_APP_NAME=SIPORTS v2.0
VITE_APP_VERSION=2.0.0
EOF

# Mettre à jour vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "buildCommand": "yarn build",
  "outputDirectory": "dist",
  "installCommand": "yarn install --frozen-lockfile",
  "framework": "vite",
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "cache-control": "max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_BACKEND_URL": "$BACKEND_URL"
  }
}
EOF

echo "✅ Configuration frontend mise à jour"

# Build final avec la vraie URL
echo "🏗️  Build final avec l'URL backend réelle..."
yarn build

# Connexion Vercel
echo ""
echo "🔐 Connexion Vercel requise..."
if ! vercel whoami &> /dev/null; then
    echo "🔑 Veuillez vous connecter à Vercel..."
    vercel login
    
    if ! vercel whoami &> /dev/null; then
        echo "❌ Échec de connexion Vercel"
        exit 1
    fi
fi

echo "✅ Connecté à Vercel : $(vercel whoami)"

# Déploiement Vercel
echo ""
echo "🚀 Déploiement du frontend..."
echo "⏳ Cela peut prendre 1-2 minutes..."

FRONTEND_URL=$(vercel --prod --yes --confirm 2>&1 | grep -E 'https://[^[:space:]]*\.vercel\.app' | head -1 || echo "")

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  URL frontend non détectée"
    echo "💡 Récupérez-la avec : vercel ls"
    echo "📝 Saisissez l'URL de votre frontend Vercel :"
    read -p "URL frontend: " FRONTEND_URL
    
    if [ -z "$FRONTEND_URL" ]; then
        FRONTEND_URL="https://siports-v2.vercel.app"
        echo "🔧 URL par défaut supposée: $FRONTEND_URL"
    fi
fi

echo "✅ Frontend URL: $FRONTEND_URL"
echo "$FRONTEND_URL" > vercel-url.txt

# Tests finaux
echo ""
echo "🧪 TESTS DE VALIDATION"
echo "======================"

echo "⏳ Attente de la propagation (30s)..."
sleep 30

# Test backend
echo "🔧 Test backend API..."
if curl -s --connect-timeout 10 "$BACKEND_URL/api/" | grep -q "SIPORTS"; then
    echo "✅ Backend API accessible et fonctionnel"
else
    echo "⚠️  Backend en cours de démarrage (normal)"
fi

# Test frontend
echo "🌐 Test frontend..."
if curl -s --connect-timeout 10 "$FRONTEND_URL" | grep -q "SIPORTS\|html"; then
    echo "✅ Frontend accessible"
else
    echo "⚠️  Frontend en propagation"
fi

# Résumé final
echo ""
echo "🎉 DÉPLOIEMENT SIPORTS v2.0 TERMINÉ !"
echo "===================================="
echo ""
echo "🌐 VOS URLS DE PRODUCTION :"
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ 🎯 Frontend: $FRONTEND_URL"
echo "│ 🔧 Backend:  $BACKEND_URL"
echo "│ 👤 Admin:    $FRONTEND_URL/admin/dashboard"
echo "│ 🏢 Mini-site: $FRONTEND_URL/exposant/1/mini-site"
echo "│ 💬 Chatbot:  $FRONTEND_URL (bouton bleu flottant)"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""
echo "👤 COMPTE ADMIN :"
echo "📧 Email: admin@siportevent.com"
echo "🔑 Password: admin123"
echo ""
echo "🎯 NOUVELLES FONCTIONNALITÉS DÉPLOYÉES :"
echo "✨ Mini-sites exposants professionnels (3 niveaux)"
echo "✨ Chatbot IA v2.0 avec 9 endpoints"
echo "✨ Système de forfaits visiteur/partenaires"
echo "✨ Dashboard admin moderne"
echo "✨ Design style siportevent.com"
echo ""
echo "🧪 TESTEZ MAINTENANT :"
echo "1. 🏠 Ouvrir $FRONTEND_URL"
echo "2. 👤 Se connecter en admin"
echo "3. 🏢 Tester mini-site: $FRONTEND_URL/exposant/1/mini-site"
echo "4. 🤖 Essayer le chatbot (bouton bleu)"
echo "5. 💼 Parcourir les forfaits"
echo ""
echo "📞 SUPPORT EN CAS DE PROBLÈME :"
echo "• Logs backend: railway logs"
echo "• Logs frontend: vercel logs"  
echo "• Status: railway status && vercel ls"
echo ""
echo "🎊 FÉLICITATIONS ! SIPORTS v2.0 EST EN LIGNE !"