# 🔧 SIPORTS Debug Version - Résolution "Failed to fetch"

## 🚨 Version DEBUG pour diagnostiquer les problèmes

Cette version inclut un système de debug complet pour identifier et résoudre le problème "Failed to fetch".

## 🔍 Fonctionnalités de Debug

### 1. **API Debug Complète** (`/src/utils/debugAPI.js`)
- Test de connectivité backend
- Test CORS détaillé  
- Test d'authentification avec logs complets
- Diagnostic automatique complet

### 2. **Logs Console Détaillés**
Tous les appels API affichent maintenant :
- URLs appelées
- Headers envoyés/reçus
- Données de réponse
- Erreurs détaillées avec stack trace

### 3. **Backend Forcé**
- URL hardcodée : `https://siportevent-production.up.railway.app/api`
- Plus de logique de détection d'environnement
- Connection directe garantie

## 🚀 Utilisation

### Étape 1: Déploiement Debug
1. Extraire et déployer cette version sur Vercel
2. Ouvrir la console développeur (F12)
3. Tenter une connexion admin

### Étape 2: Diagnostic Automatique
Dans la console, exécuter :
```javascript
debugAPI.runFullDiagnostic()
```

### Étape 3: Analyse des Logs
La console affichera :
- 🔍 Test de connectivité backend
- 🌐 Test CORS preflight
- 🔑 Test de connexion admin
- 📊 Résultats diagnostiques complets

## 🧪 Tests de Connexion

### Test Backend (via console)
```javascript
// Test simple
debugAPI.testConnection()

// Test authentification
debugAPI.testLogin('admin@siportevent.com', 'admin123')

// Test CORS
debugAPI.testCORS()
```

### Test Direct (via console)
```javascript
fetch('https://siportevent-production.up.railway.app/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email:'admin@siportevent.com',password:'admin123'})
}).then(r=>r.json()).then(console.log).catch(console.error)
```

## 🎯 Objectifs Debug

1. **Identifier la cause exacte** du "Failed to fetch"
2. **Vérifier si c'est CORS, réseau, ou config**
3. **Tester la connexion directe** sans proxy Vercel
4. **Débugger en temps réel** les requêtes

## 📞 Analyse des Résultats

Partagez les logs console pour diagnostic :
- Erreurs rouges dans console
- Résultats de `debugAPI.runFullDiagnostic()`
- Status et headers des requêtes réseau (onglet Network)

---

**Cette version va nous dire EXACTEMENT pourquoi ça ne fonctionne pas !** 🔍