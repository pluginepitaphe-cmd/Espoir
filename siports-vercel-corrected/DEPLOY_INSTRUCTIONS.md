# 🚀 Instructions de Déploiement Vercel - SIPORTS v2.0

## Étapes de Déploiement

### 1. Préparation
```bash
# Le package est prêt, tous les fichiers nécessaires sont inclus
# Vérifiez que vous avez ce dossier complet : siports-vercel-corrected/
```

### 2. Déploiement via Vercel Dashboard

1. **Connectez-vous à Vercel** : https://vercel.com
2. **Import Project** → Upload le dossier `siports-vercel-corrected`
3. **Configure le projet** :
   - Project Name: `siports-frontend` ou nom de votre choix
   - Framework: Vite (détecté automatiquement)
   - Root Directory: `./` (racine)
   - Build Command: `yarn build` (défini automatiquement)
   - Output Directory: `dist` (défini automatiquement)

### 3. Variables d'Environnement (Optionnel)

Les variables sont déjà dans `.env.production`, mais vous pouvez les ajouter dans Vercel Dashboard :

```
VITE_BACKEND_URL = https://siportevent-production.up.railway.app
VITE_APP_NAME = SIPORTS v2.0
VITE_APP_VERSION = 2.0.0
```

### 4. Déploiement via CLI Vercel (Alternative)

```bash
# Installer Vercel CLI
npm i -g vercel

# Dans le dossier siports-vercel-corrected
cd siports-vercel-corrected
vercel --prod
```

### 5. Déploiement via GitHub (Recommandé)

1. **Créer un repo GitHub** avec le contenu de `siports-vercel-corrected/`
2. **Connecter Vercel à GitHub** 
3. **Import depuis GitHub** dans Vercel Dashboard
4. **Auto-deploy** à chaque push

## ✅ Vérification Post-Déploiement

### Tests à Effectuer :

1. **Page d'accueil** : Chargement correct
2. **Connexion Admin** : admin@siportevent.com / admin123
3. **Dashboard Admin** : Accès et statistiques
4. **Pages principales** : Navigation complète
5. **Backend connection** : Vérifier les appels API

### URLs de Test :
- `https://votre-domain.vercel.app/` - Page d'accueil
- `https://votre-domain.vercel.app/admin/dashboard` - Admin dashboard
- `https://votre-domain.vercel.app/exposants` - Annuaire exposants
- `https://votre-domain.vercel.app/forfaits` - Forfaits visiteur

## 🔧 Configuration Avancée

### Domaine Personnalisé
1. Dans Vercel Dashboard → Settings → Domains
2. Ajouter votre domaine (ex: siportevent.com)
3. Configurer les DNS selon les instructions Vercel

### CORS Backend
Le backend Railway est déjà configuré pour accepter les requêtes Vercel.

## 📞 Support

Si problèmes de déploiement :
1. Vérifier les logs de build dans Vercel Dashboard
2. Vérifier que le backend Railway fonctionne : https://siportevent-production.up.railway.app
3. Tester les variables d'environnement

---

**✨ Votre application SIPORTS sera accessible mondialement via Vercel !**