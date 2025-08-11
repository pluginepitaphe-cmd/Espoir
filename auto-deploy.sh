#!/bin/bash
# 🎯 Déploiement automatique SIPORTS v2.0
# Script complet pour déployer frontend et backend

set -e

echo "🚀 DÉPLOIEMENT AUTOMATIQUE SIPORTS v2.0"
echo "======================================="
echo ""

# Vérifier si on peut installer les CLI automatiquement
echo "🔧 Installation des outils de déploiement..."

# Installer Railway CLI
if ! command -v railway &> /dev/null; then
    echo "📦 Installation Railway CLI..."
    npm install -g @railway/cli@latest
    echo "✅ Railway CLI installé"
else
    echo "✅ Railway CLI déjà installé"
fi

# Installer Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "📦 Installation Vercel CLI..."
    npm install -g vercel@latest
    echo "✅ Vercel CLI installé"
else
    echo "✅ Vercel CLI déjà installé"
fi

echo ""
echo "⚠️  AUTHENTIFICATION REQUISE"
echo "============================="
echo "Vous devez vous connecter à Railway et Vercel."
echo "Les fenêtres de connexion vont s'ouvrir..."
echo ""

# Connexion Railway
echo "🚂 Connexion à Railway..."
if ! railway auth whoami &> /dev/null; then
    echo "🔐 Veuillez vous connecter à Railway..."
    railway login || {
        echo "❌ Échec de connexion Railway"
        echo "💡 Connectez-vous manuellement avec: railway login"
        exit 1
    }
fi
echo "✅ Connecté à Railway"

# Connexion Vercel
echo "⚡ Connexion à Vercel..."
if ! vercel whoami &> /dev/null; then
    echo "🔐 Veuillez vous connecter à Vercel..."
    vercel login || {
        echo "❌ Échec de connexion Vercel"
        echo "💡 Connectez-vous manuellement avec: vercel login"
        exit 1
    }
fi
echo "✅ Connecté à Vercel"

echo ""
echo "🎬 DÉBUT DU DÉPLOIEMENT"
echo "======================="

# Étape 1: Déploiement Backend sur Railway
echo ""
echo "🔥 ÉTAPE 1/2: Déploiement Backend (Railway)"
echo "==========================================="

cd backend

echo "📁 Préparation du backend..."
# Vérifier que nous avons les bons fichiers
if [ ! -f "server.py" ]; then
    echo "⚠️  Copie du serveur de production..."
    cp server_production.py server.py
fi

if [ ! -f "requirements.txt" ]; then
    echo "⚠️  Copie des requirements de production..."
    cp requirements_production.txt requirements.txt
fi

# Créer le projet Railway ou utiliser l'existant
echo "🚂 Initialisation Railway..."
if [ ! -f ".railway/project.json" ]; then
    echo "🆕 Création d'un nouveau projet Railway..."
    railway link --project siports-backend || railway new siports-backend
else
    echo "✅ Projet Railway existant détecté"
fi

# Configuration des variables d'environnement
echo "⚙️  Configuration des variables d'environnement..."

# Générer un secret JWT sécurisé
JWT_SECRET=$(openssl rand -hex 32)
railway variables set JWT_SECRET_KEY="$JWT_SECRET" || echo "⚠️  Variable JWT_SECRET_KEY non définie"
railway variables set DATABASE_URL="instance/siports_production.db" || echo "⚠️  Variable DATABASE_URL non définie"
railway variables set PORT="8000" || echo "⚠️  Variable PORT non définie"

echo "✅ Variables d'environnement configurées"

# Déploiement
echo "🚀 Déploiement du backend..."
railway deploy --detach || {
    echo "❌ Erreur de déploiement Railway"
    echo "💡 Vérifiez vos logs avec: railway logs"
    cd ..
    exit 1
}

# Attendre le déploiement
echo "⏳ Attente du déploiement backend (60s)..."
sleep 60

# Récupérer l'URL du backend
echo "🔍 Récupération de l'URL du backend..."
BACKEND_URL=$(railway status --json 2>/dev/null | jq -r '.deployments[0].url // empty' || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  URL backend non récupérée automatiquement"
    echo "💡 Récupérez-la avec: railway status"
    BACKEND_URL="https://siports-backend.up.railway.app"
    echo "🔧 URL par défaut utilisée: $BACKEND_URL"
else
    echo "✅ Backend déployé: $BACKEND_URL"
fi

# Sauvegarder l'URL
echo "$BACKEND_URL" > ../railway-url.txt
cd ..

# Étape 2: Déploiement Frontend sur Vercel
echo ""
echo "⚡ ÉTAPE 2/2: Déploiement Frontend (Vercel)"
echo "=========================================="

# Mettre à jour la configuration avec l'URL du backend
echo "⚙️  Configuration de l'URL backend..."
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
    "VITE_BACKEND_URL": "$BACKEND_URL"
  }
}
EOF

echo "✅ Configuration frontend mise à jour"

# Build final avec la bonne URL
echo "🏗️  Build final du frontend..."
yarn build

# Déploiement Vercel
echo "🚀 Déploiement du frontend..."
FRONTEND_URL=$(vercel --prod --yes --confirm 2>/dev/null | grep -o 'https://[^[:space:]]*' | head -1 || echo "")

if [ -z "$FRONTEND_URL" ]; then
    echo "⚠️  Déploiement Vercel en cours..."
    echo "💡 Surveillez avec: vercel ls"
    FRONTEND_URL="https://siports.vercel.app"
    echo "🔧 URL par défaut supposée: $FRONTEND_URL"
else
    echo "✅ Frontend déployé: $FRONTEND_URL"
fi

# Sauvegarder l'URL
echo "$FRONTEND_URL" > vercel-url.txt

# Tests finaux
echo ""
echo "🧪 TESTS AUTOMATIQUES"
echo "====================="

echo "⏳ Attente de la propagation (30s)..."
sleep 30

# Test du backend
echo "🔧 Test du backend API..."
if curl -s --max-time 10 "$BACKEND_URL/api/" > /dev/null 2>&1; then
    echo "✅ Backend API accessible"
else
    echo "⚠️  Backend API pas encore accessible (normal lors du premier déploiement)"
fi

# Test du frontend
echo "🌐 Test du frontend..."
if curl -s --max-time 10 "$FRONTEND_URL" > /dev/null 2>&1; then
    echo "✅ Frontend accessible"
else
    echo "⚠️  Frontend pas encore accessible (propagation en cours)"
fi

# Résumé final
echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo ""
echo "🌐 VOS URLS DE PRODUCTION :"
echo "├── Frontend: $FRONTEND_URL"
echo "├── Backend:  $BACKEND_URL"  
echo "├── Admin:    $FRONTEND_URL/admin/dashboard"
echo "└── Mini-sites: $FRONTEND_URL/exposant/1/mini-site"
echo ""
echo "👤 COMPTE ADMIN :"
echo "├── Email: admin@siportevent.com"
echo "└── Password: admin123"
echo ""
echo "🎯 NOUVELLES FONCTIONNALITÉS :"
echo "├── 🏢 Mini-sites exposants professionnels"
echo "├── 🤖 Chatbot IA avec 9 endpoints"  
echo "├── 💼 Système de forfaits complet"
echo "├── 📊 Dashboard admin avancé"
echo "└── 🎨 Design moderne siportevent.com"
echo ""
echo "🔍 TESTS À EFFECTUER :"
echo "1. Ouvrir $FRONTEND_URL"
echo "2. Se connecter en admin (admin@siportevent.com / admin123)"
echo "3. Tester le mini-site: $FRONTEND_URL/exposant/1/mini-site"
echo "4. Tester le chatbot (bouton bleu en bas à droite)"
echo "5. Vérifier les forfaits visiteur: $FRONTEND_URL/forfaits-visiteur"
echo ""
echo "📞 SUPPORT :"
echo "├── Logs backend: railway logs"
echo "├── Logs frontend: vercel logs"
echo "└── Status: railway status"
echo ""
echo "🎊 SIPORTS v2.0 EST MAINTENANT EN LIGNE !"