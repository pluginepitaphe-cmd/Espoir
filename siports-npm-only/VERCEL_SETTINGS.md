# ⚙️ CONFIGURATION VERCEL EXACTE

## 🚨 SETTINGS CRITIQUES

Pour éviter l'erreur Yarn, configurer EXACTEMENT ces settings dans Vercel :

### 1. Build & Development Settings

Dans **Vercel Dashboard** → **Settings** → **General** :

```
Framework Preset: Vite
Install Command: npm install --no-package-lock
Build Command: npm run build  
Output Directory: dist
Development Command: npm run dev
```

### 2. Environment Variables

Dans **Settings** → **Environment Variables** :

```
VITE_BACKEND_URL = https://siportevent-production.up.railway.app
NPM_CONFIG_PACKAGE_LOCK = false
DISABLE_YARN = true
```

### 3. Node.js Version

Dans **Settings** → **General** :
```
Node.js Version: 18.x
```

### 4. Redéploiement

Après avoir configuré ces settings :
1. **Deployments** → **Redeploy** (bouton avec 3 points)
2. **Use existing Build Cache** → **NO** (décocher)
3. **Redeploy** → SUCCESS ✅

## 🔧 Troubleshooting

### Si Yarn Persiste
1. **Settings** → **General** → **Build & Development**
2. **Override** → Cocher toutes les cases
3. **Install Command** → `npm install --no-package-lock`
4. **Save** → **Redeploy**

### Si Erreur Persist
1. **GitHub/Git** → Supprimer tous .lock files
2. **Vercel** → **Settings** → **Git** → **Reconnect**
3. **Force Redeploy** sans cache

---

## ✅ RÉSULTAT ATTENDU

```bash
✓ Installing dependencies with npm
✓ Building with Vite
✓ Build completed successfully
✓ Deployment ready
```

**Cette configuration élimine l'erreur Yarn définitivement !**