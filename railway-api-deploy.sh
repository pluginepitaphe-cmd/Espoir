#!/bin/bash
# 🚂 Déploiement Railway via API REST - SIPORTS Backend

set -e

echo "🚂 DÉPLOIEMENT RAILWAY VIA API"
echo "==============================="
echo ""

TOKEN="$1"
if [ -z "$TOKEN" ]; then
    echo "❌ Token Railway requis"
    exit 1
fi

echo "✅ Token Railway fourni : ${TOKEN:0:8}...${TOKEN: -8}"

# Fonction pour appeler l'API Railway
call_railway_api() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        curl -s -X POST \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "https://backboard.railway.app/graphql$endpoint"
    else
        curl -s -H "Authorization: Bearer $TOKEN" \
            "https://backboard.railway.app/graphql$endpoint"
    fi
}

# Test de l'API
echo "🧪 Test de l'authentification API..."
AUTH_TEST=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "https://backboard.railway.app/graphql" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query":"query { me { id email } }", "variables":{}}' 2>/dev/null)

if echo "$AUTH_TEST" | grep -q '"me"'; then
    USER_EMAIL=$(echo "$AUTH_TEST" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Authentification réussie : $USER_EMAIL"
else
    echo "❌ Échec d'authentification API"
    echo "🔍 Réponse API : $AUTH_TEST"
    echo ""
    echo "💡 SOLUTIONS POSSIBLES :"
    echo "1. Vérifier que le token est correct"
    echo "2. Railway.app → Account → Tokens → Vérifier permissions"
    echo "3. Régénérer un nouveau token si nécessaire"
    echo ""
    echo "📋 MÉTHODE ALTERNATIVE :"
    echo "Si l'API ne fonctionne pas, utilisez :"
    echo "• ./railway-manual-setup.sh (méthode manuelle)"
    echo "• RAILWAY_GUIDE_SIMPLE.md (guide étapes)"
    exit 1
fi

echo ""
echo "🎯 API fonctionnelle ! Création du projet via interface web recommandée..."

# Créer un guide spécifique avec le token fonctionnel
cat > railway-token-guide.md << EOF
# 🚂 Votre Token Railway Fonctionne !

## ✅ **TOKEN VALIDÉ**
Votre token Railway est **authentifié et fonctionnel** !

## 🎯 **MÉTHODE RECOMMANDÉE**

Puisque votre token fonctionne, voici la méthode la plus simple :

### 1️⃣ **Créer le projet sur Railway**
- Aller sur **railway.app**
- **New Project** → **Empty Project**
- Nommer : \`siports-backend-v2\`

### 2️⃣ **Déployer via CLI avec votre token**
\`\`\`bash
# Configurer le token
export RAILWAY_TOKEN=$TOKEN

# Dans le dossier backend
cd deployment-final/backend

# Lier au projet (sélectionner siports-backend-v2)
railway link

# Variables d'environnement
railway variables set PORT=8000
railway variables set JWT_SECRET_KEY="siports-jwt-production-\$(date +%s)"
railway variables set DATABASE_URL="instance/siports_production.db"
railway variables set PYTHONPATH="/app"

# Déployer
railway deploy
\`\`\`

### 3️⃣ **Récupérer l'URL**
\`\`\`bash
railway status
# Copier l'URL générée
\`\`\`

### 4️⃣ **Connecter à Vercel**
- Vercel → Settings → Environment Variables
- \`VITE_BACKEND_URL\` = URL Railway
- Redeploy

## 🎊 **VOTRE STACK SERA COMPLÈTE !**
EOF

echo "✅ Guide créé : railway-token-guide.md"

echo ""
echo "🎊 RÉSULTAT"
echo "==========="
echo "✅ Votre token Railway est **valide et fonctionnel**"
echo "✅ API accessible et authentifiée"
echo "📋 Guide personnalisé créé : railway-token-guide.md"
echo ""
echo "🚀 PROCHAINES ÉTAPES :"
echo "1. Suivre railway-token-guide.md"
echo "2. Ou utiliser RAILWAY_GUIDE_SIMPLE.md"
echo "3. Avec votre token validé, le déploiement sera rapide !"
echo ""
echo "⏱️  Temps estimé : 10-15 minutes avec votre token"