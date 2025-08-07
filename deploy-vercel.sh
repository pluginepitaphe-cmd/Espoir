#!/bin/bash
# 🚀 Script automatisé de déploiement Vercel pour SIPORTS v2.0

set -e

echo "🚀 DÉPLOIEMENT VERCEL - SIPORTS v2.0 FRONTEND"
echo "=============================================="

# Vérifier si Vercel CLI est installé
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI non trouvé. Installation..."
    if command -v npm &> /dev/null; then
        npm install -g vercel
    elif command -v yarn &> /dev/null; then
        yarn global add vercel
    else
        echo "❌ npm/yarn non trouvé. Installez Node.js puis relancez ce script."
        exit 1
    fi
fi

# Vérifier si l'utilisateur est connecté
if ! vercel whoami &> /dev/null; then
    echo "🔐 Connexion à Vercel requise..."
    vercel login
fi

# Demander l'URL Railway
RAILWAY_URL=""
if [ -f "railway-url.txt" ]; then
    RAILWAY_URL=$(cat railway-url.txt)
    echo "📖 URL Railway trouvée: $RAILWAY_URL"
else
    echo "🔗 Entrez l'URL de votre backend Railway :"
    echo "   (ex: https://siports-backend.up.railway.app)"
    read -p "URL Railway: " RAILWAY_URL
fi

# Valider l'URL
if [[ ! $RAILWAY_URL =~ ^https?:// ]]; then
    echo "❌ URL invalide. Elle doit commencer par http:// ou https://"
    exit 1
fi

# Créer le fichier .env.production
echo "⚙️  Configuration des variables d'environnement..."
echo "VITE_BACKEND_URL=$RAILWAY_URL" > .env.production

echo "✅ Variables configurées :"
echo "   - VITE_BACKEND_URL: $RAILWAY_URL"

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    if [ -f "yarn.lock" ]; then
        yarn install
    else
        npm install
    fi
fi

# Build de production
echo "🏗️  Build de production..."
if [ -f "yarn.lock" ]; then
    yarn build
else
    npm run build
fi

echo "✅ Build terminé avec succès !"

# Vérifier que le dossier dist existe
if [ ! -d "dist" ]; then
    echo "❌ Dossier dist non trouvé. Erreur de build."
    exit 1
fi

# Déploiement Vercel
echo "🚀 Déploiement sur Vercel..."

# Premier déploiement (preview)
echo "📤 Déploiement preview..."
PREVIEW_URL=$(vercel --yes --confirm | grep -o 'https://[^[:space:]]*')

if [ ! -z "$PREVIEW_URL" ]; then
    echo "✅ Preview déployé: $PREVIEW_URL"
    
    # Test de l'URL preview
    echo "🧪 Test du frontend preview..."
    sleep 10
    
    if curl -s "$PREVIEW_URL" > /dev/null; then
        echo "✅ Frontend preview accessible !"
        
        # Demander confirmation pour production
        echo ""
        echo "🎯 Déployer en production ? (y/n)"
        read -p "Production: " DEPLOY_PROD
        
        if [[ $DEPLOY_PROD =~ ^[Yy]$ ]]; then
            echo "🚀 Déploiement production..."
            PROD_URL=$(vercel --prod --yes --confirm | grep -o 'https://[^[:space:]]*')
            
            if [ ! -z "$PROD_URL" ]; then
                echo "✅ Production déployée: $PROD_URL"
                
                # Sauvegarder l'URL
                echo "$PROD_URL" > vercel-url.txt
                echo "💾 URL sauvegardée dans vercel-url.txt"
                
                # Mettre à jour Railway avec l'URL frontend
                echo "🔄 Mise à jour des CORS sur Railway..."
                cd backend
                if railway variables set FRONTEND_URL="$PROD_URL"; then
                    echo "✅ CORS mis à jour sur Railway"
                    railway deploy
                else
                    echo "⚠️  Impossible de mettre à jour Railway automatiquement"
                    echo "   Exécutez manuellement :"
                    echo "   cd backend && railway variables set FRONTEND_URL=\"$PROD_URL\""
                fi
                cd ..
            else
                echo "❌ Erreur lors du déploiement production"
                exit 1
            fi
        else
            echo "ℹ️  Production non déployée. URL preview disponible."
        fi
    else
        echo "⚠️  Frontend pas encore accessible. URL: $PREVIEW_URL"
    fi
else
    echo "❌ Erreur lors du déploiement Vercel"
    exit 1
fi

# Afficher les résultats
echo ""
echo "🎉 DÉPLOIEMENT VERCEL TERMINÉ !"
echo "================================"

if [ ! -z "$PROD_URL" ]; then
    echo "🌐 Frontend Production: $PROD_URL"
    echo "🔧 Backend Railway: $RAILWAY_URL"
    echo ""
    echo "✅ SIPORTS v2.0 est maintenant en ligne !"
    echo ""
    echo "🧪 TESTS À EFFECTUER :"
    echo "1. Ouvrir: $PROD_URL"
    echo "2. Tester le chatbot (bouton bleu en bas à droite)"
    echo "3. S'inscrire/Se connecter"
    echo "4. Tester le dashboard admin :"
    echo "   - Email: admin@siportevent.com"
    echo "   - Password: admin123"
    echo ""
else
    echo "🌐 Frontend Preview: $PREVIEW_URL"
    echo "ℹ️  Production disponible avec: vercel --prod"
fi

echo "🔧 COMMANDES UTILES :"
echo "   vercel logs          # Voir les logs"
echo "   vercel ls            # Lister les déploiements"
echo "   vercel domains       # Gérer les domaines"
echo ""
echo "📊 MONITORING :"
echo "   Dashboard Vercel: https://vercel.com/dashboard"
echo "   Analytics: Disponible dans le dashboard"