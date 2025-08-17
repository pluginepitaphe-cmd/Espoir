# 🌐 Déploiement Frontend SIPORTS sur Vercel

## 📋 Prérequis

1. **Compte Vercel** : https://vercel.com
2. **Backend déployé** sur Railway
3. **Variables d'environnement** configurées

## 🚀 Déploiement Rapide

### Option 1: Déploiement Direct

1. **Connectez-vous à Vercel** : https://vercel.com
2. **New Project** → "Import Third-Party Git Repository"
3. **Uploadez** le dossier `frontend/`
4. **Vercel détecte** automatiquement Vite
5. **Variables d'environnement** (voir section ci-dessous)
6. **Deploy** automatique

### Option 2: Via GitHub (Recommandé)

1. **Créer un repo GitHub** avec le contenu de `frontend/`
2. **Import Project** depuis GitHub dans Vercel
3. **Auto-deploy** sur chaque push
4. **Variables d'environnement** dans Vercel Dashboard

## 🔧 Configuration Variables d'Environnement

Dans Vercel Dashboard → Settings → Environment Variables :

```env
# Backend URL (OBLIGATOIRE)
VITE_BACKEND_URL=https://votre-backend.up.railway.app

# App Info
VITE_APP_NAME=SIPORTS v2.0
VITE_APP_VERSION=2.0.0

# Optionnel - Analytics
VITE_GOOGLE_ANALYTICS_ID=votre-id-ga

# Optionnel - Error Tracking
VITE_SENTRY_DSN=votre-sentry-dsn
```

## ⚙️ Configuration Vercel

### vercel.json
```json
{
  "version": 2,
  "framework": "vite",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "cleanUrls": true,
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://votre-backend.up.railway.app/api/$1"
    }
  ]
}
```

### Build Settings (Auto-détectées)
- **Framework** : Vite
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm install`
- **Dev Command** : `npm run dev`

## 🔗 Connexion Backend

### 1. URL Backend
Remplacez dans `VITE_BACKEND_URL` :
```env
VITE_BACKEND_URL=https://siportevent-production.up.railway.app
```

### 2. Test de Connexion
Après déploiement, ouvrez F12 et testez :
```javascript
fetch(import.meta.env.VITE_BACKEND_URL + '/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email:'admin@siportevent.com', password:'admin123'})
}).then(r => r.json()).then(console.log)
```

## ✅ Vérification du Déploiement

### 1. Page d'Accueil
```
https://votre-app.vercel.app/
```

### 2. Test Connexion Admin
- Email: `admin@siportevent.com`
- Mot de passe: `admin123`

### 3. Pages Principales
- `/exposants` - Annuaire exposants
- `/forfaits` - Forfaits visiteur
- `/admin/dashboard` - Dashboard admin (après connexion)

## 🔧 Troubleshooting

### Problèmes Courants

1. **Build Failed** :
   - Vérifier `package.json`
   - Vérifier Node.js version (18+)
   - Vérifier variables d'environnement

2. **API Connection Failed** :
   - Vérifier `VITE_BACKEND_URL`
   - Vérifier que backend Railway fonctionne
   - Vérifier CORS sur backend

3. **404 on Routes** :
   - `vercel.json` doit avoir `cleanUrls: true`
   - SPA routing configuré

### Debug Console
Ouvrez F12 → Console pour voir les erreurs :
```javascript
// Test backend connection
debugAPI.runFullDiagnostic()
```

## 🌐 Domaine Personnalisé

### Configurer votre domaine
1. **Vercel Dashboard** → Settings → Domains
2. **Add Domain** → `votre-domaine.com`
3. **Configure DNS** selon instructions Vercel
4. **SSL automatique** par Vercel

### Update Backend CORS
Mettre à jour les CORS sur Railway :
```env
CORS_ORIGINS=https://votre-domaine.com,https://votre-app.vercel.app
```

## 📊 Performance

### Optimisations Automatiques
- **Code Splitting** - Chunks optimisés
- **Tree Shaking** - Code inutile supprimé
- **Asset Optimization** - Images/CSS minifiés
- **CDN Global** - Distribution mondiale
- **HTTP/2** - Performance améliorée

### Métriques Vercel
- **Analytics** - Built-in dans dashboard
- **Web Vitals** - Performance metrics
- **Function Logs** - Pour debugging

## 🔐 Sécurité

1. **HTTPS** automatique avec certificats SSL
2. **Headers sécurisés** configurés
3. **Variables d'environnement** sécurisées
4. **CORS** correctement configuré

---

**🎯 Votre frontend sera accessible à** : `https://votre-projet.vercel.app`