#!/bin/bash
# 🚀 Script automatisé de déploiement Railway pour SIPORTS v2.0

set -e

echo "🚀 DÉPLOIEMENT RAILWAY - SIPORTS v2.0 BACKEND"
echo "=============================================="

# Vérifier si Railway CLI est installé
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI non trouvé. Installation..."
    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
    else
        echo "❌ npm non trouvé. Installez Node.js puis relancez ce script."
        exit 1
    fi
fi

# Vérifier si l'utilisateur est connecté
if ! railway whoami &> /dev/null; then
    echo "🔐 Connexion à Railway requise..."
    railway login
fi

# Préparer les fichiers de production
echo "📁 Préparation des fichiers..."
cd backend

# Copier les fichiers de production
cp server_production_wp.py server.py
cp requirements_production_wp.txt requirements.txt

echo "✅ Fichiers copiés :"
echo "   - server.py (version WordPress)"
echo "   - requirements.txt (dépendances complètes)"

# Créer le projet Railway
echo "🏗️  Création du projet Railway..."
PROJECT_NAME="siports-backend-$(date +%s)"

# Initialiser le projet
railway new $PROJECT_NAME

echo "⚙️  Configuration des variables d'environnement..."

# Variables essentielles
JWT_SECRET=$(openssl rand -hex 32)
railway variables set JWT_SECRET_KEY="$JWT_SECRET"
railway variables set DATABASE_URL="instance/siports_production.db"
railway variables set PORT="8001"

# Variables WordPress (désactivées par défaut)
railway variables set WORDPRESS_ENABLED="false"
railway variables set WP_DB_HOST="localhost"
railway variables set WP_DB_NAME="wordpress"
railway variables set WP_DB_USER="root"
railway variables set WP_DB_PASSWORD=""
railway variables set WP_SITE_URL="https://siportevent.com"

# Générer secret WordPress
WP_JWT_SECRET=$(openssl rand -hex 32)
railway variables set WP_JWT_SECRET="$WP_JWT_SECRET"

echo "✅ Variables configurées :"
echo "   - JWT_SECRET_KEY: ✓ (généré automatiquement)"
echo "   - DATABASE_URL: ✓"
echo "   - WORDPRESS_ENABLED: false (peut être activé plus tard)"

# Déployer
echo "🚀 Déploiement en cours..."
railway deploy

echo ""
echo "⏳ Attente du déploiement (cela peut prendre 2-5 minutes)..."
sleep 10

# Obtenir l'URL
echo "🔍 Récupération de l'URL de déploiement..."
RAILWAY_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")

if [ -z "$RAILWAY_URL" ]; then
    echo "⚠️  URL non disponible automatiquement. Utilisez :"
    echo "   railway status"
    echo ""
else
    echo "✅ Backend déployé avec succès !"
    echo "🌐 URL: $RAILWAY_URL"
    echo ""
    
    # Tester l'API
    echo "🧪 Test de l'API..."
    sleep 30  # Attendre que le service démarre
    
    if curl -s "$RAILWAY_URL/health" > /dev/null; then
        echo "✅ API fonctionne correctement !"
    else
        echo "⚠️  API pas encore prête. Attendez quelques minutes et testez :"
        echo "   curl $RAILWAY_URL/health"
    fi
fi

# Afficher les prochaines étapes
echo ""
echo "📋 PROCHAINES ÉTAPES :"
echo "1. Notez l'URL Railway ci-dessus"
echo "2. Utilisez cette URL pour configurer Vercel"
echo "3. Lancez le script deploy-vercel.sh"
echo ""
echo "🔧 Commandes utiles :"
echo "   railway logs         # Voir les logs"
echo "   railway status       # Statut du déploiement"
echo "   railway variables    # Voir les variables"
echo ""

# Sauvegarder l'URL dans un fichier
if [ ! -z "$RAILWAY_URL" ]; then
    echo "$RAILWAY_URL" > ../railway-url.txt
    echo "💾 URL sauvegardée dans railway-url.txt"
fi

echo "🎉 Déploiement Railway terminé !"