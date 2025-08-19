#!/bin/bash
# Script d'installation personnalisé pour éviter --frozen-lockfile

echo "🚀 Installation SIPORTS sans frozen-lockfile..."

# Supprimer les conflits
rm -f package-lock.json

# Installation avec timeout étendu ET devDependencies pour le build
yarn install --network-timeout 300000 --ignore-engines --production=false

echo "✅ Installation terminée avec succès!"