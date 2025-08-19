#!/bin/bash

echo "🧪 TEST DES COMMANDES YARN - DIAGNOSTIC"
echo "======================================="

cd /app/Espoir

echo "📦 Test de la commande originale (problème):"
echo "yarn install --frozen-lockfile=false --network-timeout 300000 --production=false"
echo ""

# Test si les options existent
echo "🔍 Vérification des options yarn disponibles:"
yarn --help | grep -E "(frozen-lockfile|production)" || echo "❌ Options non trouvées dans l'aide yarn"

echo ""
echo "✅ Commandes corrigées à tester:"
echo "1. yarn install --network-timeout 300000 --ignore-engines"
echo "2. yarn install --no-lockfile --network-timeout 300000"
echo "3. npm install --no-package-lock --legacy-peer-deps"

echo ""
echo "📋 Versions actuelles:"
echo "Node: $(node --version)"
echo "Yarn: $(yarn --version)"
echo "NPM: $(npm --version)"

echo ""
echo "🎯 Analyse du package.json:"
if [ -f package.json ]; then
    echo "✅ package.json trouvé"
    grep -E "(react|vite|node)" package.json | head -5
else
    echo "❌ package.json non trouvé"
fi

echo ""
echo "🔒 Analyse du yarn.lock:"
if [ -f yarn.lock ]; then
    echo "✅ yarn.lock trouvé ($(wc -l < yarn.lock) lignes)"
    head -10 yarn.lock
else
    echo "❌ yarn.lock non trouvé"
fi