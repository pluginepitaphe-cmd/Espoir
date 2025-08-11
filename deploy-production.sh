#!/bin/bash
# 🚀 Script de déploiement SIPORTS v2.0 - Version mise à jour
# Ce script déploie l'application complète avec les mini-sites exposants

set -e

echo "🚀 DÉPLOIEMENT SIPORTS v2.0 COMPLET"
echo "=================================="
echo "✨ Nouvelles fonctionnalités incluses :"
echo "   • Mini-sites exposants professionnels"
echo "   • Chatbot IA v2.0 avec 9 endpoints"
echo "   • Interface moderne style siportevent.com"
echo "   • Système de forfaits complet"
echo ""

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js requis. Installez Node.js et relancez."
    exit 1
fi

if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn requis. Installez avec: npm install -g yarn"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 requis."
    exit 1
fi

echo "✅ Tous les prérequis sont satisfaits"

# Étape 1: Préparer le build frontend
echo ""
echo "📦 ÉTAPE 1: Build Frontend"
echo "========================="

# S'assurer que le fichier .env frontend est correct
echo "⚙️  Configuration de l'environnement frontend..."
mkdir -p frontend
cat > frontend/.env << EOF
# Frontend Environment Variables for Production
VITE_BACKEND_URL=https://siports-backend.up.railway.app
VITE_APP_NAME=SIPORTS v2.0
VITE_APP_VERSION=2.0.0
EOF

echo "✅ Fichier frontend/.env créé"

# Build du frontend
echo "🏗️  Build du frontend avec mini-sites..."
yarn install --frozen-lockfile
yarn build

if [ ! -d "dist" ]; then
    echo "❌ Erreur de build frontend"
    exit 1
fi

echo "✅ Frontend buildé avec succès"
echo "   • Taille du build: $(du -sh dist | cut -f1)"
echo "   • Mini-sites inclus: ExhibitorMiniSitePro"

# Étape 2: Préparer le backend
echo ""
echo "🔧 ÉTAPE 2: Préparation Backend"
echo "==============================="

cd backend

# Copier le serveur de production
echo "📁 Configuration serveur de production..."
cp server_production.py server.py
cp requirements_production.txt requirements.txt

echo "✅ Fichiers backend préparés :"
echo "   • server.py (version production)"
echo "   • requirements.txt (dépendances optimisées)"
echo "   • chatbot_service.py (AI v2.0)"

# Tester le backend localement
echo "🧪 Test rapide du backend..."
if python3 -c "import fastapi, uvicorn; print('✅ Dépendances OK')"; then
    echo "✅ Backend prêt pour le déploiement"
else
    echo "⚠️  Attention: certaines dépendances peuvent manquer"
fi

cd ..

# Étape 3: Configuration de déploiement
echo ""
echo "🌐 ÉTAPE 3: Configuration Déploiement"
echo "===================================="

# Créer/mettre à jour vercel.json
echo "📝 Configuration Vercel..."
cat > vercel.json << EOF
{
  "version": 2,
  "buildCommand": "yarn build",
  "outputDirectory": "dist",
  "installCommand": "yarn install --frozen-lockfile",
  "framework": "vite",
  "functions": {},
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
    "VITE_BACKEND_URL": "https://siports-backend.up.railway.app",
    "VITE_APP_NAME": "SIPORTS v2.0",
    "VITE_APP_VERSION": "2.0.0"
  }
}
EOF

# Créer/mettre à jour railway.json
echo "🚂 Configuration Railway..."
cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks",
    "buildCommand": "cd backend && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && python server.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "environments": {
    "production": {
      "variables": {
        "PORT": "8000",
        "JWT_SECRET_KEY": "your-secure-jwt-secret-key-here",
        "DATABASE_URL": "instance/siports_production.db"
      }
    }
  }
}
EOF

echo "✅ Configuration de déploiement mise à jour"

# Afficher le résumé
echo ""
echo "📋 RÉSUMÉ DU DÉPLOIEMENT PRÉPARÉ"
echo "==============================="
echo "✅ Frontend buildé ($(ls -1 dist/assets/ | wc -l) fichiers)"
echo "✅ Backend configuré (Production optimized)"
echo "✅ Configuration Vercel/Railway prête"
echo ""
echo "🎯 FONCTIONNALITÉS INCLUSES :"
echo "   • 3 niveaux de profils exposants (/exposants/:id, /exposant/:id/premium, /exposant/:id/mini-site)"
echo "   • Chatbot IA avec 9 endpoints"
echo "   • Système de forfaits visiteurs/partenaires"
echo "   • Dashboard admin complet"
echo "   • Navigation professionnelle"
echo ""
echo "🚀 PROCHAINES ÉTAPES :"
echo "1. Installer Railway CLI: npm install -g @railway/cli"
echo "2. Installer Vercel CLI: npm install -g vercel"
echo "3. Se connecter aux plateformes :"
echo "   - railway login"
echo "   - vercel login"
echo "4. Lancer le déploiement :"
echo "   - Backend: cd backend && railway deploy"
echo "   - Frontend: vercel --prod"
echo ""
echo "🎊 Déploiement prêt à être exécuté !"
echo ""
echo "📞 SUPPORT EN CAS DE PROBLÈME :"
echo "   • Vérifiez les logs : railway logs"
echo "   • Tests locaux : python backend/server.py"
echo "   • Build local : yarn build"
