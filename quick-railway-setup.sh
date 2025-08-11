#!/bin/bash
# 🚂 Setup rapide Railway - SIPORTS Backend

echo "🚂 SETUP RAILWAY RÉEL - SIPORTS BACKEND"
echo "======================================"
echo ""

# Vérifier le dossier backend
if [ ! -d "deployment-final/backend" ]; then
    echo "❌ Dossier deployment-final/backend non trouvé"
    echo "💡 Exécutez d'abord : ./deploy-production-final.sh"
    exit 1
fi

echo "✅ Dossier backend trouvé"
echo ""

# Aller dans le dossier backend
cd deployment-final/backend

echo "📋 CONTENU DU DOSSIER BACKEND :"
echo "=============================="
ls -la
echo ""

echo "🎯 OPTIONS RAILWAY DISPONIBLES :"
echo "==============================="
echo ""
echo "1️⃣ **MÉTHODE CLI (Recommandée)**"
echo "   • Railway : New Project → Empty Project"
echo "   • Installer CLI : curl -fsSL https://railway.app/install.sh | sh"
echo "   • Se connecter : railway login"
echo "   • Lier projet : railway link"
echo "   • Déployer : railway deploy"
echo ""
echo "2️⃣ **MÉTHODE GITHUB**"
echo "   • Créer repo GitHub : siports-backend-v2"
echo "   • Push ce dossier vers GitHub"
echo "   • Railway : Deploy from GitHub repo"
echo ""
echo "3️⃣ **MÉTHODE MANUELLE**"
echo "   • Railway : Empty Project → Add Service"
echo "   • Upload via interface ou CLI"
echo ""

# Créer un script Git pour méthode GitHub
echo "📦 CRÉATION SCRIPT GIT :"
echo "======================="

cat > setup-github.sh << 'EOF'
#!/bin/bash
echo "🐙 Configuration GitHub pour Railway"
echo "===================================="

# Initialiser git si pas fait
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git initialisé"
else
    echo "✅ Git déjà initialisé"
fi

# Ajouter tous les fichiers
git add .
git commit -m "SIPORTS Backend v2.0 - Ready for Railway deployment"

echo ""
echo "📝 PROCHAINES ÉTAPES :"
echo "1. Créer un repo GitHub : siports-backend-v2"
echo "2. Exécuter :"
echo "   git remote add origin https://github.com/YOUR-USERNAME/siports-backend-v2.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "3. Sur Railway : Deploy from GitHub repo"
EOF

chmod +x setup-github.sh
echo "✅ Script setup-github.sh créé"
echo ""

# Créer un script CLI pour méthode Railway CLI
cat > setup-railway-cli.sh << 'EOF'
#!/bin/bash
echo "🚂 Configuration Railway CLI"
echo "============================"

# Vérifier si Railway CLI est installé
if ! command -v railway &> /dev/null; then
    echo "📦 Installation Railway CLI..."
    curl -fsSL https://railway.app/install.sh | sh
    echo "✅ Railway CLI installé"
else
    echo "✅ Railway CLI déjà installé"
fi

echo ""
echo "🔐 Connexion Railway..."
railway login

echo ""
echo "🔗 Liaison du projet..."
echo "💡 Créez d'abord un Empty Project sur railway.app"
echo "💡 Puis exécutez : railway link"
echo "💡 Et enfin : railway deploy"
EOF

chmod +x setup-railway-cli.sh
echo "✅ Script setup-railway-cli.sh créé"
echo ""

# Afficher les variables d'environnement
echo "⚙️  VARIABLES D'ENVIRONNEMENT :"
echo "============================="
if [ -f ".env" ]; then
    echo "Variables dans .env :"
    cat .env
else
    echo "Variables à configurer dans Railway :"
    echo "PORT=8000"
    echo "JWT_SECRET_KEY=siports-jwt-production-2024"
    echo "DATABASE_URL=instance/siports_production.db"
    echo "PYTHONPATH=/app"
fi
echo ""

# Créer un package ZIP au cas où
echo "📦 CRÉATION PACKAGE ZIP :"
echo "========================"
cd ..
zip -r siports-backend-railway.zip backend/ > /dev/null 2>&1
if [ -f "siports-backend-railway.zip" ]; then
    echo "✅ Package ZIP créé : siports-backend-railway.zip ($(ls -lh siports-backend-railway.zip | awk '{print $5}'))"
else
    echo "⚠️  Erreur création ZIP"
fi
cd backend
echo ""

# Instructions finales
echo "🎯 CHOISISSEZ VOTRE MÉTHODE :"
echo "============================"
echo ""
echo "🚂 **MÉTHODE 1 : Railway CLI**"
echo "   1. Aller sur railway.app"
echo "   2. New Project → Empty Project"
echo "   3. Exécuter : ./setup-railway-cli.sh"
echo ""
echo "🐙 **MÉTHODE 2 : GitHub**"
echo "   1. Exécuter : ./setup-github.sh"
echo "   2. Créer repo GitHub et push"
echo "   3. Railway : Deploy from GitHub repo"
echo ""
echo "📦 **MÉTHODE 3 : ZIP Upload**"
echo "   1. Utiliser siports-backend-railway.zip"
echo "   2. Interface Railway pour upload"
echo ""

echo "⏱️  Temps estimé : 15-20 minutes"
echo "🎊 Bonne chance avec Railway !"