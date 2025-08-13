#!/bin/bash
# 🚨 Fix rapide pour le repo GitHub Salon

echo "🚨 CORRECTION URGENTE REPO GITHUB SALON"
echo "======================================="
echo ""
echo "❌ ERREUR ACTUELLE :"
echo "   Could not resolve entry module 'index.html'"
echo "   Repo: github.com/pluginepitaphe-cmd/Salon"
echo ""

echo "🎯 PROBLÈME :"
echo "   Vercel cherche index.html à la racine"
echo "   Mais votre repo l'a dans un sous-dossier"
echo ""

echo "✅ SOLUTION :"
echo "   Copier les fichiers essentiels à la RACINE de votre repo GitHub"
echo ""

# Créer un dossier avec les fichiers essentiels pour GitHub
mkdir -p github-root-files

echo "📁 Création des fichiers pour la racine GitHub..."

# index.html pour la racine
cat > github-root-files/index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SIPORTS - Plateforme Maritime</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

# package.json pour la racine
cp package.json github-root-files/

# vite.config.js pour la racine  
cp vite.config.js github-root-files/

# vercel.json corrigé
cat > github-root-files/vercel.json << 'EOF'
{
  "version": 2,
  "buildCommand": "yarn build",
  "outputDirectory": "dist", 
  "installCommand": "yarn install --frozen-lockfile",
  "framework": "vite",
  "routes": [
    {
      "src": "/assets/(.*)",
      "headers": {
        "cache-control": "max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_BACKEND_URL": "https://votre-url-railway.up.railway.app",
    "VITE_APP_NAME": "SIPORTS v2.0"
  }
}
EOF

# yarn.lock si disponible
if [ -f "yarn.lock" ]; then
    cp yarn.lock github-root-files/
    echo "✅ yarn.lock copié"
else
    echo "⚠️  yarn.lock non trouvé - sera généré par Vercel"
fi

echo ""
echo "✅ FICHIERS CRÉÉS DANS github-root-files/ :"
ls -la github-root-files/

echo ""
echo "🚀 INSTRUCTIONS URGENTES :"
echo "========================="
echo ""
echo "1️⃣ Aller dans votre repo GitHub Salon"
echo "2️⃣ Copier ces fichiers À LA RACINE :"
echo "   • github-root-files/index.html"
echo "   • github-root-files/package.json"  
echo "   • github-root-files/vite.config.js"
echo "   • github-root-files/vercel.json"
echo "   • github-root-files/yarn.lock (si présent)"
echo ""
echo "3️⃣ S'assurer que le dossier src/ est à la racine"
echo "4️⃣ Commit et push"
echo "5️⃣ Vercel redeploy → BUILD RÉUSSIRA !"
echo ""
echo "⏱️  Temps estimé : 5 minutes"
echo "🎊 Résultat : Build Vercel sans erreur !"