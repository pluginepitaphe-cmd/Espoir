#!/bin/bash
# 🎯 One-click deployment pour SIPORTS v2.0

echo "🚀 SIPORTS v2.0 - DÉPLOIEMENT ONE-CLICK"
echo "========================================"
echo ""
echo "Ce script va automatiquement :"
echo "1. 🔧 Déployer le backend sur Railway"
echo "2. 🌐 Déployer le frontend sur Vercel" 
echo "3. 🧪 Tester l'intégration complète"
echo ""

read -p "Continuer ? (y/n): " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ Déploiement annulé"
    exit 1
fi

echo ""
echo "🎬 Début du déploiement automatique..."

# Étape 1: Railway
echo ""
echo "📍 ÉTAPE 1/3: Déploiement Railway"
echo "================================="
if ./deploy-railway.sh; then
    echo "✅ Railway déployé avec succès"
else
    echo "❌ Erreur déploiement Railway"
    exit 1
fi

# Attendre un peu
sleep 5

# Étape 2: Vercel  
echo ""
echo "📍 ÉTAPE 2/3: Déploiement Vercel"
echo "================================"
if ./deploy-vercel.sh; then
    echo "✅ Vercel déployé avec succès"
else
    echo "❌ Erreur déploiement Vercel"
    exit 1
fi

# Attendre que les services se stabilisent
echo ""
echo "⏳ Attente stabilisation des services (30s)..."
sleep 30

# Étape 3: Tests
echo ""
echo "📍 ÉTAPE 3/3: Tests automatisés"
echo "==============================="
if ./test-deployment.sh; then
    echo "✅ Tests passés avec succès"
else
    echo "⚠️  Certains tests ont échoué (vérifiez manuellement)"
fi

echo ""
echo "🎉 DÉPLOIEMENT ONE-CLICK TERMINÉ !"
echo "=================================="

if [ -f "vercel-url.txt" ] && [ -f "railway-url.txt" ]; then
    VERCEL_URL=$(cat vercel-url.txt)
    RAILWAY_URL=$(cat railway-url.txt)
    
    echo ""
    echo "🌐 VOS URLS DE PRODUCTION :"
    echo "Frontend: $VERCEL_URL"
    echo "Backend:  $RAILWAY_URL"
    echo "Admin:    $VERCEL_URL/admin/dashboard"
    echo ""
    echo "👤 CONNEXION ADMIN :"
    echo "Email: admin@siportevent.com"
    echo "Password: admin123"
    echo ""
    echo "🤖 CHATBOT disponible sur toutes les pages (bouton bleu)"
fi

echo ""
echo "📋 PROCHAINES ÉTAPES :"
echo "1. Ouvrir votre site web"
echo "2. Tester toutes les fonctionnalités"
echo "3. Configurer WordPress si nécessaire"
echo "4. Ajouter un domaine personnalisé"
echo ""
echo "🎊 SIPORTS v2.0 est maintenant en ligne !"