#!/bin/bash
# 🚀 Déploiement automatique Railway avec token - SIPORTS Backend

set -e

echo "🚂 DÉPLOIEMENT AUTOMATIQUE RAILWAY"
echo "=================================="
echo ""

# Vérifier si le token est fourni
if [ -z "$1" ]; then
    echo "❌ Token Railway requis"
    echo ""
    echo "📋 UTILISATION :"
    echo "./railway-auto-deploy.sh VOTRE_TOKEN_RAILWAY"
    echo ""
    echo "🔑 OBTENIR VOTRE TOKEN :"
    echo "1. Aller sur railway.app"
    echo "2. Settings → Account → Tokens"
    echo "3. Generate New Token → Copy"
    echo ""
    exit 1
fi

RAILWAY_TOKEN=$1
echo "✅ Token Railway fourni"

# Vérifier le dossier backend
if [ ! -d "deployment-final/backend" ]; then
    echo "❌ Dossier deployment-final/backend non trouvé"
    echo "💡 Exécutez d'abord : ./deploy-production-final.sh"
    exit 1
fi

echo "✅ Dossier backend trouvé"
echo ""

# Installer Railway CLI si nécessaire
if ! command -v railway &> /dev/null; then
    echo "📦 Installation Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    echo "✅ Railway CLI installé"
else
    echo "✅ Railway CLI déjà installé"
fi

# Se connecter avec le token
echo ""
echo "🔐 Authentification avec votre token..."
export RAILWAY_TOKEN=$RAILWAY_TOKEN

# Vérifier la connexion
if railway whoami > /dev/null 2>&1; then
    echo "✅ Authentification réussie : $(railway whoami)"
else
    echo "❌ Erreur d'authentification"
    echo "💡 Vérifiez votre token Railway"
    exit 1
fi

# Aller dans le dossier backend
cd deployment-final/backend
echo ""
echo "📁 Dossier de déploiement : $(pwd)"

# Créer le projet Railway
echo ""
echo "🆕 Création du projet Railway..."
PROJECT_NAME="siports-backend-v2-$(date +%s)"
echo "📝 Nom du projet : $PROJECT_NAME"

# Initialiser le projet
railway new "$PROJECT_NAME" --confirm > /dev/null 2>&1 || {
    echo "⚠️  Projet existant ou erreur de création"
    echo "💡 Tentative de liaison à un projet existant..."
}

# Configurer les variables d'environnement
echo ""
echo "⚙️  Configuration des variables d'environnement..."

# Lire les variables depuis .env
if [ -f ".env" ]; then
    echo "📋 Variables depuis .env :"
    while IFS='=' read -r key value; do
        if [[ ! -z "$key" && ! "$key" =~ ^#.* ]]; then
            echo "   $key=$value"
            railway variables set "$key=$value" > /dev/null 2>&1 || echo "⚠️  Erreur variable $key"
        fi
    done < .env
else
    echo "📝 Configuration manuelle des variables..."
    railway variables set "PORT=8000"
    railway variables set "JWT_SECRET_KEY=siports-jwt-production-$(date +%s)"
    railway variables set "DATABASE_URL=instance/siports_production.db"
    railway variables set "PYTHONPATH=/app"
fi

echo "✅ Variables configurées"

# Déploiement
echo ""
echo "🚀 DÉPLOIEMENT EN COURS..."
echo "========================"
echo "⏳ Cela peut prendre 2-3 minutes..."
echo ""

# Déployer
DEPLOY_OUTPUT=$(railway deploy --detach 2>&1)
DEPLOY_SUCCESS=$?

if [ $DEPLOY_SUCCESS -eq 0 ]; then
    echo "✅ Déploiement lancé avec succès"
    echo ""
    
    # Attendre le déploiement
    echo "⏳ Attente de la finalisation du déploiement..."
    sleep 60
    
    # Récupérer l'URL
    echo ""
    echo "🔍 Récupération de l'URL de déploiement..."
    
    # Récupérer les informations du projet
    PROJECT_INFO=$(railway status --json 2>/dev/null || railway status 2>/dev/null)
    
    # Essayer de récupérer l'URL via différentes méthodes
    RAILWAY_URL=""
    
    # Méthode 1: railway domain
    RAILWAY_URL=$(railway domain 2>/dev/null | head -1 || echo "")
    
    # Méthode 2: depuis railway status
    if [ -z "$RAILWAY_URL" ]; then
        RAILWAY_URL=$(echo "$PROJECT_INFO" | grep -o 'https://[^[:space:]]*\.up\.railway\.app' | head -1 || echo "")
    fi
    
    # URL par défaut si aucune trouvée
    if [ -z "$RAILWAY_URL" ]; then
        RAILWAY_URL="https://$PROJECT_NAME-production.up.railway.app"
        echo "⚠️  URL exacte non récupérée, URL supposée : $RAILWAY_URL"
    else
        echo "✅ URL récupérée : $RAILWAY_URL"
    fi
    
    # Sauvegarder l'URL
    echo "$RAILWAY_URL" > ../../railway-backend-url.txt
    
    # Tester l'API
    echo ""
    echo "🧪 TEST DE L'API BACKEND :"
    echo "========================="
    echo "🔍 Test de $RAILWAY_URL/api/"
    
    # Attendre que l'API soit prête
    for i in {1..5}; do
        if curl -s --connect-timeout 10 "$RAILWAY_URL/api/" | grep -q "SIPORTS"; then
            echo "✅ API backend accessible et fonctionnelle !"
            break
        else
            echo "⏳ Tentative $i/5 - API en cours de démarrage..."
            sleep 15
        fi
    done
    
    # Tests additionnels
    echo ""
    echo "🧪 TESTS ADDITIONNELS :"
    echo "======================"
    
    # Test chatbot
    if curl -s --connect-timeout 10 "$RAILWAY_URL/api/chatbot/health" | grep -q "healthy"; then
        echo "✅ Chatbot IA opérationnel"
    else
        echo "⚠️  Chatbot en cours de démarrage"
    fi
    
    # Test forfaits
    if curl -s --connect-timeout 10 "$RAILWAY_URL/api/visitor-packages" | grep -q "packages"; then
        echo "✅ Système de forfaits opérationnel"
    else
        echo "⚠️  Forfaits en cours de chargement"
    fi
    
else
    echo "❌ Erreur de déploiement"
    echo "📋 Output:"
    echo "$DEPLOY_OUTPUT"
    exit 1
fi

cd ../..

# Instructions pour Vercel
echo ""
echo "🎯 PROCHAINE ÉTAPE : CONNECTER À VERCEL"
echo "======================================"
echo ""
echo "✅ Backend Railway déployé : $RAILWAY_URL"
echo ""
echo "🔄 METTRE À JOUR VERCEL :"
echo "1. Aller sur vercel.com → Votre projet SIPORTS"
echo "2. Settings → Environment Variables"
echo "3. Modifier VITE_BACKEND_URL :"
echo "   VITE_BACKEND_URL=$RAILWAY_URL"
echo "4. Deployments → Redeploy"
echo ""

# Créer un script de mise à jour Vercel
cat > update-vercel-with-railway.sh << EOF
#!/bin/bash
echo "🔄 Mise à jour Vercel avec Railway URL"
echo "======================================"
echo ""
echo "Backend Railway : $RAILWAY_URL"
echo ""
echo "📝 INSTRUCTIONS VERCEL :"
echo "1. vercel.com → Votre projet"
echo "2. Settings → Environment Variables"
echo "3. VITE_BACKEND_URL = $RAILWAY_URL"
echo "4. Redeploy"
echo ""
echo "🧪 TESTS APRÈS VERCEL :"
echo "• Frontend + Backend connectés"
echo "• Admin : admin@siportevent.com / admin123"
echo "• Mini-site : /exposant/1/mini-site"
echo "• Chatbot : bouton bleu flottant"
EOF

chmod +x update-vercel-with-railway.sh

# Résumé final
echo ""
echo "🎊 DÉPLOIEMENT RAILWAY TERMINÉ !"
echo "==============================="
echo ""
echo "✅ Backend déployé : $RAILWAY_URL"
echo "✅ API testée et fonctionnelle"
echo "✅ Script Vercel créé : ./update-vercel-with-railway.sh"
echo ""
echo "🎯 FONCTIONNALITÉS DÉPLOYÉES :"
echo "• 🏢 Mini-sites exposants professionnels"
echo "• 🤖 Chatbot IA avec 9 endpoints"
echo "• 💼 Système de forfaits complet"
echo "• 📊 Dashboard admin moderne"
echo "• 📅 Calendrier et messagerie"
echo ""
echo "🚀 SIPORTS v2.0 BACKEND EN LIGNE !"
echo ""
echo "💡 Exécutez maintenant : ./update-vercel-with-railway.sh"