#!/bin/bash
# 🚀 Déploiement Final SIPORTS v2.0 - Version Production

set -e

echo "🚀 DÉPLOIEMENT FINAL SIPORTS v2.0"
echo "================================="
echo ""
echo "🎯 Application complète avec :"
echo "   ✨ Mini-sites exposants professionnels" 
echo "   ✨ Chatbot IA v2.0"
echo "   ✨ Système de forfaits"
echo "   ✨ Dashboard admin"
echo ""

# Créer les répertoires de déploiement
echo "📁 Création des packages de déploiement..."
mkdir -p deployment-final/{backend,frontend}

# Copier le backend optimisé
echo "🔧 Préparation backend..."
cp -r backend/* deployment-final/backend/
cd deployment-final/backend

# Optimiser les fichiers pour la production
echo "PORT=8000" > .env
echo "JWT_SECRET_KEY=siports-jwt-production-$(date +%s)" >> .env
echo "DATABASE_URL=instance/siports_production.db" >> .env
echo "PYTHONPATH=/app" >> .env

# Créer un script de démarrage optimisé
cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Démarrage SIPORTS Backend v2.0..."
python server.py
EOF
chmod +x start.sh

cd ../..

# Copier le frontend optimisé  
echo "⚡ Préparation frontend..."
cp -r dist/* deployment-final/frontend/
cp vercel.json deployment-final/
cp package.json deployment-final/

# Créer le package de distribution
echo "📦 Création du package final..."
cd deployment-final
tar -czf ../siports-v2-production.tar.gz .
cd ..

echo ""
echo "✅ PACKAGE DE PRODUCTION CRÉÉ !"
echo "==============================="
echo ""
echo "📊 Taille : $(ls -lh siports-v2-production.tar.gz | awk '{print $5}')"
echo "📁 Contenu :"
echo "   • Backend optimisé avec Docker"
echo "   • Frontend buildé et optimisé"
echo "   • Base de données avec données de test"
echo "   • Configuration production"
echo ""

# Instructions de déploiement
echo "🚀 INSTRUCTIONS DE DÉPLOIEMENT :"
echo "==============================="
echo ""
echo "1️⃣ RAILWAY (Backend) :"
echo "   • Aller sur railway.app"
echo "   • New Project → Deploy from local directory"
echo "   • Upload le dossier deployment-final/backend/"
echo "   • Railway détecte automatiquement Python"
echo ""
echo "2️⃣ VERCEL (Frontend) :"
echo "   • Aller sur vercel.com"
echo "   • New Project → Upload"
echo "   • Upload le dossier deployment-final/frontend/"
echo "   • Framework: Static"
echo ""
echo "3️⃣ NETLIFY (Alternative Frontend) :"
echo "   • Aller sur netlify.com"  
echo "   • Drag & drop deployment-final/frontend/"
echo "   • Deploy automatique"
echo ""

# URLs de test
echo "🧪 TESTS POST-DÉPLOIEMENT :"
echo "==========================="
echo ""
echo "Backend :"
echo "• https://votre-backend.up.railway.app/api/"
echo "• https://votre-backend.up.railway.app/api/chatbot/health"
echo ""
echo "Frontend :"
echo "• https://votre-frontend.vercel.app/"
echo "• https://votre-frontend.vercel.app/admin/dashboard"
echo "• https://votre-frontend.vercel.app/exposant/1/mini-site ⭐"
echo ""

# Comptes de test
echo "👤 COMPTES DE TEST :"
echo "==================="
echo "Admin : admin@siportevent.com / admin123"
echo "Exhibitor : exposant@example.com / expo123"
echo "Visitor : visiteur@example.com / visit123"
echo ""

echo "🎊 SIPORTS v2.0 PRÊT POUR LA PRODUCTION !"
echo ""
echo "💡 CONSEIL : Téléchargez 'siports-v2-production.tar.gz'"
echo "    et suivez les instructions ci-dessus."