#!/bin/bash
# 🚂 Script d'aide pour déploiement Railway SIPORTS Backend

echo "🚂 DÉPLOIEMENT RAILWAY - SIPORTS BACKEND"
echo "========================================"
echo ""

# Vérifier si le dossier backend existe
if [ ! -d "deployment-final/backend" ]; then
    echo "❌ Dossier deployment-final/backend non trouvé"
    echo "💡 Exécutez d'abord : ./deploy-production-final.sh"
    exit 1
fi

echo "✅ Dossier backend trouvé"
echo ""

# Afficher le contenu du backend
echo "📁 CONTENU DU BACKEND À DÉPLOYER :"
echo "=================================="
cd deployment-final/backend
ls -la
echo ""

# Vérifier les fichiers essentiels
echo "🔍 VÉRIFICATION DES FICHIERS :"
echo "=============================="

files=("server.py" "requirements.txt" "Procfile" "railway.toml" ".env")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
    fi
done
echo ""

# Afficher les variables d'environnement
echo "⚙️  VARIABLES D'ENVIRONNEMENT À CONFIGURER :"
echo "=========================================="
if [ -f ".env" ]; then
    echo "Variables automatiques depuis .env :"
    cat .env
else
    echo "Variables à ajouter manuellement dans Railway :"
    echo "PORT=8000"
    echo "JWT_SECRET_KEY=siports-jwt-production-2024-secure"
    echo "DATABASE_URL=instance/siports_production.db"
    echo "PYTHONPATH=/app"
fi
echo ""

# Instructions Railway
echo "🚂 INSTRUCTIONS RAILWAY :"
echo "========================"
echo ""
echo "1️⃣ Aller sur https://railway.app"
echo "2️⃣ Cliquer 'New Project'"
echo "3️⃣ Sélectionner 'Deploy from local directory'"
echo "4️⃣ Glisser-déposer ce dossier : $(pwd)"
echo "5️⃣ Railway détecte automatiquement Python"
echo "6️⃣ Attendre le déploiement (2-3 minutes)"
echo "7️⃣ Récupérer l'URL générée"
echo ""

# Test du backend local
echo "🧪 TEST LOCAL DU BACKEND :"
echo "=========================="
if command -v python3 &> /dev/null; then
    echo "▶️  Test des imports Python..."
    python3 -c "
try:
    import fastapi
    import uvicorn
    from server import app
    print('✅ Tous les imports fonctionnent')
except Exception as e:
    print(f'❌ Erreur import: {e}')
    " 2>/dev/null || echo "⚠️  Certains imports peuvent échouer (normal si dans un environnement différent)"
else
    echo "⚠️  Python3 non disponible pour test local"
fi
echo ""

# Informations sur les endpoints
echo "🌐 ENDPOINTS BACKEND ATTENDUS :"
echo "=============================="
echo "Après déploiement, testez ces URLs :"
echo ""
echo "• https://votre-railway-url.up.railway.app/api/"
echo "  ↳ Status API principal"
echo ""
echo "• https://votre-railway-url.up.railway.app/api/chatbot/health"
echo "  ↳ Health check du chatbot IA"
echo ""
echo "• https://votre-railway-url.up.railway.app/api/visitor-packages"
echo "  ↳ Liste des forfaits visiteur"
echo ""
echo "• https://votre-railway-url.up.railway.app/api/auth/login"
echo "  ↳ Endpoint d'authentification"
echo ""

# Commandes CLI Railway (optionnel)
echo "📱 COMMANDES CLI RAILWAY (OPTIONNEL) :"
echo "====================================="
echo ""
echo "Si vous préférez utiliser le CLI :"
echo ""
echo "# Installation"
echo "curl -fsSL https://railway.app/install.sh | sh"
echo ""
echo "# Connexion"
echo "railway login"
echo ""
echo "# Création projet"
echo "railway new siports-backend-v2"
echo ""
echo "# Déploiement"
echo "railway deploy"
echo ""
echo "# Voir les logs"
echo "railway logs"
echo ""

# Retour au dossier parent
cd ../..

echo "🎯 RÉCAPITULATIF :"
echo "================="
echo "1. Votre backend est prêt dans deployment-final/backend/"
echo "2. Suivez les instructions Railway ci-dessus"
echo "3. Une fois déployé, mettez à jour l'URL dans Vercel"
echo "4. Testez les endpoints listés"
echo ""
echo "⏱️  Temps estimé : 10-15 minutes"
echo "🎊 Bonne chance avec votre déploiement Railway !"