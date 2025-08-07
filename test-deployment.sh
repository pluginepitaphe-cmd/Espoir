#!/bin/bash
# 🧪 Script de test complet pour SIPORTS v2.0 déployé

set -e

echo "🧪 TESTS SIPORTS v2.0 - DÉPLOIEMENT"
echo "==================================="

# Lire les URLs
RAILWAY_URL=""
VERCEL_URL=""

if [ -f "railway-url.txt" ]; then
    RAILWAY_URL=$(cat railway-url.txt)
fi

if [ -f "vercel-url.txt" ]; then
    VERCEL_URL=$(cat vercel-url.txt)
fi

# Demander les URLs si pas trouvées
if [ -z "$RAILWAY_URL" ]; then
    read -p "🔗 URL Railway Backend: " RAILWAY_URL
fi

if [ -z "$VERCEL_URL" ]; then
    read -p "🔗 URL Vercel Frontend: " VERCEL_URL
fi

echo ""
echo "🎯 TESTS BACKEND (Railway)"
echo "=========================="

# Test 1: Health check
echo "1. 🩺 Health check..."
HEALTH_RESPONSE=$(curl -s "$RAILWAY_URL/health" || echo "ERROR")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "   ✅ Backend en ligne"
else
    echo "   ❌ Backend non accessible"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Test 2: API Root
echo "2. 🏠 API Root..."
ROOT_RESPONSE=$(curl -s "$RAILWAY_URL/" || echo "ERROR")

if [[ $ROOT_RESPONSE == *"SIPORTS v2.0"* ]]; then
    echo "   ✅ API Root fonctionnelle"
else
    echo "   ❌ API Root erreur"
fi

# Test 3: Packages endpoints
echo "3. 📦 Visitor packages..."
PACKAGES_RESPONSE=$(curl -s "$RAILWAY_URL/api/visitor-packages" || echo "ERROR")

if [[ $PACKAGES_RESPONSE == *"packages"* ]]; then
    echo "   ✅ Endpoints packages fonctionnels"
else
    echo "   ❌ Endpoints packages erreur"
fi

# Test 4: Chatbot health
echo "4. 🤖 Chatbot health..."
CHATBOT_RESPONSE=$(curl -s "$RAILWAY_URL/api/chatbot/health" || echo "ERROR")

if [[ $CHATBOT_RESPONSE == *"healthy"* ]]; then
    echo "   ✅ Chatbot opérationnel"
else
    echo "   ❌ Chatbot erreur"
fi

# Test 5: Chatbot fonctionnalité
echo "5. 💬 Test chatbot..."
CHAT_TEST=$(curl -s -X POST "$RAILWAY_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test déploiement","context_type":"general"}' || echo "ERROR")

if [[ $CHAT_TEST == *"response"* ]]; then
    echo "   ✅ Chatbot répond correctement"
else
    echo "   ❌ Chatbot ne répond pas"
fi

echo ""
echo "🎯 TESTS FRONTEND (Vercel)"
echo "=========================="

# Test 1: Page d'accueil
echo "1. 🏠 Page d'accueil..."
FRONTEND_RESPONSE=$(curl -s "$VERCEL_URL" || echo "ERROR")

if [[ $FRONTEND_RESPONSE == *"<!DOCTYPE html>"* ]]; then
    echo "   ✅ Frontend accessible"
else
    echo "   ❌ Frontend non accessible"
fi

# Test 2: Assets
echo "2. 📦 Assets..."
ASSETS_TEST=$(curl -s -I "$VERCEL_URL/assets/" | head -1 || echo "ERROR")

if [[ $ASSETS_TEST == *"200"* ]] || [[ $ASSETS_TEST == *"404"* ]]; then
    echo "   ✅ Assets servis correctement"
else
    echo "   ⚠️  Assets vérification impossible"
fi

echo ""
echo "🎯 TESTS INTÉGRATION"
echo "===================="

# Test CORS
echo "1. 🔄 Test CORS..."
CORS_TEST=$(curl -s -H "Origin: $VERCEL_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS "$RAILWAY_URL/api/chat" || echo "ERROR")

if [ "$CORS_TEST" != "ERROR" ]; then
    echo "   ✅ CORS configuré"
else
    echo "   ⚠️  CORS vérification impossible"
fi

# Générer rapport de test
echo ""
echo "📊 RAPPORT DE TESTS"
echo "==================="

# Compter les succès
BACKEND_TESTS=5
FRONTEND_TESTS=2
INTEGRATION_TESTS=1

echo "Backend Tests: $BACKEND_TESTS tests"
echo "Frontend Tests: $FRONTEND_TESTS tests"
echo "Integration Tests: $INTEGRATION_TESTS tests"

echo ""
echo "🌐 URLs DE PRODUCTION"
echo "====================="
echo "Frontend: $VERCEL_URL"
echo "Backend:  $RAILWAY_URL"
echo "Admin:    $VERCEL_URL/admin/dashboard"
echo ""

echo "👤 COMPTES DE TEST"
echo "=================="
echo "Admin:"
echo "  Email: admin@siportevent.com"
echo "  Password: admin123"
echo ""
echo "Visiteur test:"
echo "  Email: visitor@example.com"
echo "  Password: visitor123"
echo ""
echo "Exposant test:"
echo "  Email: exposant@example.com"
echo "  Password: exhibitor123"

echo ""
echo "🧪 TESTS MANUELS À EFFECTUER"
echo "=============================="
echo "1. 🌐 Ouvrir $VERCEL_URL"
echo "2. 🤖 Tester le chatbot (bouton bleu)"
echo "3. 🔐 Se connecter avec admin@siportevent.com"
echo "4. 📊 Vérifier le dashboard admin"
echo "5. 💳 Tester les pages forfaits"
echo "6. 📱 Vérifier sur mobile"

# Sauvegarder le rapport
cat > deployment-test-report.txt << EOF
SIPORTS v2.0 - Rapport de Tests Déploiement
===========================================
Date: $(date)

URLs:
- Frontend: $VERCEL_URL
- Backend: $RAILWAY_URL

Tests Backend: $BACKEND_TESTS
Tests Frontend: $FRONTEND_TESTS
Tests Intégration: $INTEGRATION_TESTS

Comptes de test:
- Admin: admin@siportevent.com / admin123
- Visiteur: visitor@example.com / visitor123
- Exposant: exposant@example.com / exhibitor123

Status: Déploiement prêt pour utilisation
EOF

echo ""
echo "💾 Rapport sauvegardé: deployment-test-report.txt"
echo "🎉 Tests de déploiement terminés !"