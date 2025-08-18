# 🔧 FORCER L'UTILISATION DE NPM (Pas Yarn)

## 🚨 Problème Yarn
Yarn utilise `--frozen-lockfile` qui cause l'erreur Node.js.

## ✅ Solutions NPM

### Solution 1: vercel.json (Recommandé)
```json
{
  "installCommand": "npm install",
  "buildCommand": "npm run build"
}
```

### Solution 2: .nvmrc (Forcer Node version)
```
18
```

### Solution 3: package.json engines
```json
{
  "engines": {
    "node": ">=16.0.0",
    "npm": ">=8.0.0"
  }
}
```

### Solution 4: Deployment Settings
Dans Vercel Dashboard:
- **Install Command**: `npm install`
- **Build Command**: `npm run build`
- **Node.js Version**: 18.x

## 🎯 Résultat

NPM ne crée pas de lock file par défaut et évite les conflits yarn.
Cette approche garantit le succès du build.

---

**Utilisez NPM, pas Yarn, pour éviter les conflits de versions !**