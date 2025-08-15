# 🚨 SIPORTS EMERGENCY - DIAGNOSTIC MODE

## 🎯 OBJECTIF

Cette version ultra-simple permet de :
1. **Diagnostic** - Identifier pourquoi le health check échoue
2. **Test Railway** - Vérifier que Railway peut démarrer l'app
3. **Debug logs** - Obtenir des informations de débogage

## 🔧 Variables Railway MINIMUM

**Railway** → **Backend Service** → **Variables** :

```env
ENVIRONMENT=emergency
PORT=8000
```

**NE PAS METTRE DATABASE_URL** pour l'instant !

## 🧪 Tests après déploiement

### **1. API Status**
```bash
curl https://votre-app.up.railway.app/
```

### **2. Health Check (CRITIQUE)**
```bash
curl https://votre-app.up.railway.app/health
```

### **3. Debug Info**
```bash
curl https://votre-app.up.railway.app/debug
```

### **4. Test Simple**
```bash
curl https://votre-app.up.railway.app/test
```

## 🔍 DIAGNOSTIC ÉTAPES

### **SI HEALTH CHECK MARCHE :**
✅ Railway peut démarrer l'app
✅ Le problème vient de la version complexe
➡️ Ajouter progressivement les fonctionnalités

### **SI HEALTH CHECK ÉCHOUE ENCORE :**
❌ Problème Railway de base
❌ Vérifier les logs Railway
❌ Problème de port ou configuration

## 📊 LOGS RAILWAY À VÉRIFIER

**Railway** → **Deployments** → **Logs** :

Chercher :
- `🚨 SIPORTS Emergency API starting...`
- `✅ Emergency API ready`
- `Starting server on port XXXX`
- Erreurs Python/FastAPI

## 🎯 PROCHAINES ÉTAPES

### **Si Emergency fonctionne :**
1. ✅ Ajouter DATABASE_URL
2. ✅ Ajouter connexion PostgreSQL
3. ✅ Ajouter endpoints progressivement
4. ✅ Migrer vers version complète

### **Si Emergency échoue :**
1. ❌ Vérifier logs Railway
2. ❌ Problème configuration Railway
3. ❌ Contacter support Railway

## 🚀 UTILISATION

1. **Upload** ces 4 fichiers sur GitHub
2. **Variables** : ENVIRONMENT=emergency
3. **Deploy** et regarder les logs
4. **Test** tous les endpoints
5. **Diagnostic** selon les résultats

---

# ✅ CETTE VERSION DOIT MARCHER !

**Pas de base de données, pas de dépendances complexes, just FastAPI basique.**