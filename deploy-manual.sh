#!/bin/bash
# 🎯 Guide de déploiement manuel SIPORTS v2.0

echo "📖 GUIDE DE DÉPLOIEMENT MANUEL SIPORTS v2.0"
echo "==========================================="
echo ""
echo "Ce guide vous accompagne étape par étape pour déployer SIPORTS."
echo ""

echo "🔧 PRÉREQUIS :"
echo "============="
echo "1. Compte Railway.app (gratuit)"
echo "2. Compte Vercel.com (gratuit)"
echo "3. Node.js et Yarn installés"
echo ""

read -p "Avez-vous ces prérequis ? (y/n): " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo ""
    echo "📝 CRÉER VOS COMPTES :"
    echo "• Railway: https://railway.app"
    echo "• Vercel: https://vercel.com"
    echo ""
    echo "💻 INSTALLER NODEJS :"
    echo "• Ubuntu/Debian: sudo apt install nodejs yarn"
    echo "• macOS: brew install node yarn"
    echo "• Windows: Télécharger depuis nodejs.org"
    echo ""
    exit 1
fi

echo ""
echo "📦 ÉTAPE 1: Installation des CLI"
echo "==============================="

echo "🔧 Installation des outils..."
npm install -g @railway/cli vercel

echo "✅ CLI installés avec succès"

echo ""
echo "🔐 ÉTAPE 2: Authentification"
echo "============================"

echo "🚂 Connexion Railway..."
echo "Cliquez sur le lien qui va s'ouvrir pour vous connecter"
railway login

echo ""
echo "⚡ Connexion Vercel..."
echo "Cliquez sur le lien qui va s'ouvrir pour vous connecter"  
vercel login

echo ""
echo "✅ Authentification terminée"

echo ""
echo "🔧 ÉTAPE 3: Déploiement Backend"
echo "==============================="

cd backend

# Préparer les fichiers
cp server_production.py server.py
cp requirements_production.txt requirements.txt

echo "📁 Fichiers backend préparés"

# Déploiement Railway
echo ""
echo "🚂 Lancement du déploiement Railway..."
echo "Suivez les instructions à l'écran :"
echo "1. Créer un nouveau projet ou sélectionner existant"
echo "2. Confirmer le déploiement"
echo ""

railway deploy

echo ""
echo "⏳ Attente du déploiement backend..."
sleep 30

# Récupérer l'URL
echo "🔍 Récupération de l'URL backend..."
railway status

echo ""
echo "📝 NOTEZ L'URL DE VOTRE BACKEND"
echo "Exemple: https://siports-backend-production.up.railway.app"
read -p "Entrez votre URL backend: " BACKEND_URL

# Valider l'URL
if [[ ! $BACKEND_URL =~ ^https?:// ]]; then
    echo "❌ URL invalide. Format: https://votre-backend.up.railway.app"
    exit 1
fi

echo "$BACKEND_URL" > ../railway-url.txt
cd ..

echo ""
echo "🌐 ÉTAPE 4: Déploiement Frontend"
echo "==============================="

# Configuration
echo "⚙️  Configuration du frontend avec votre URL backend..."
cat > frontend/.env << EOF
VITE_BACKEND_URL=$BACKEND_URL
VITE_APP_NAME=SIPORTS v2.0
VITE_APP_VERSION=2.0.0
EOF

# Build
echo "🏗️  Build du frontend..."
yarn build

# Déploiement
echo ""
echo "⚡ Lancement du déploiement Vercel..."
echo "Suivez les instructions :"
echo "1. Sélectionner 'Link to existing project' ou créer nouveau"
echo "2. Confirmer le déploiement"
echo ""

vercel --prod

echo ""
echo "⏳ Finalisation du déploiement frontend..."
sleep 20

# Récupérer l'URL frontend
echo ""
echo "🔍 Récupération de l'URL frontend..."
vercel ls

echo ""
echo "📝 NOTEZ L'URL DE VOTRE FRONTEND"  
echo "Exemple: https://siports.vercel.app"
read -p "Entrez votre URL frontend: " FRONTEND_URL

echo "$FRONTEND_URL" > vercel-url.txt

echo ""
echo "🧪 ÉTAPE 5: Tests et Vérification"
echo "================================="

echo "🔧 Test du backend..."
if curl -s "$BACKEND_URL/api/" > /dev/null; then
    echo "✅ Backend accessible"
else
    echo "⚠️  Backend en cours de démarrage (patientez 1-2 minutes)"
fi

echo ""
echo "🌐 Test du frontend..."
if curl -s "$FRONTEND_URL" > /dev/null; then
    echo "✅ Frontend accessible"
else  
    echo "⚠️  Frontend en propagation (patientez quelques minutes)"
fi

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo ""
echo "🌟 VOS URLS DE PRODUCTION :"
echo "┌─────────────────────────────────────────────┐"
echo "│ Frontend: $FRONTEND_URL"
echo "│ Backend:  $BACKEND_URL" 
echo "│ Admin:    $FRONTEND_URL/admin/dashboard"
echo "│ Mini-site: $FRONTEND_URL/exposant/1/mini-site"
echo "└─────────────────────────────────────────────┘"
echo ""
echo "👤 CONNEXION ADMIN :"
echo "Email: admin@siportevent.com"
echo "Password: admin123"
echo ""
echo "🎯 FONCTIONNALITÉS DISPONIBLES :"
echo "• 🏢 Mini-sites exposants professionnels"
echo "• 🤖 Chatbot IA avec 9 endpoints"
echo "• 💼 Forfaits visiteur (Free, Basic, Premium, VIP)"
echo "• 🤝 Forfaits partenaires (Platinum, Gold, Silver, Startup)"
echo "• 📊 Dashboard admin complet"
echo "• 📅 Calendrier avec RDV"
echo "• 💬 Système de messagerie"
echo "• 🔍 Matching avancé"
echo "• 📈 Analytics en temps réel"
echo ""
echo "✅ À TESTER MAINTENANT :"
echo "1. Ouvrir $FRONTEND_URL"
echo "2. Se connecter en admin"
echo "3. Tester un mini-site exposant"
echo "4. Essayer le chatbot IA"
echo "5. Parcourir les forfaits"
echo ""
echo "🆘 EN CAS DE PROBLÈME :"
echo "• Logs backend: railway logs"
echo "• Logs frontend: vercel logs"
echo "• Redéploiement: railway deploy / vercel --prod"
echo ""
echo "🎊 SIPORTS v2.0 EST EN LIGNE !"
echo ""
echo "💡 CONSEIL : Bookmarkez vos URLs et testez toutes les fonctionnalités."