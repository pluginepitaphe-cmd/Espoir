# 🚀 Guide d'Installation SIPORTS WordPress Integration

Ce guide vous accompagne dans l'intégration complète de SIPORTS avec votre site WordPress `siportevent.com`.

## 📋 PRÉREQUIS

### Serveur
- ✅ WordPress 5.8+ installé
- ✅ PHP 8.0+
- ✅ MySQL 5.7+
- ✅ Python 3.9+ (pour le backend)
- ✅ Accès FTP/SSH au serveur

### Accès
- ✅ Admin WordPress : `user@website.com`
- ✅ Base de données MySQL
- ✅ Accès aux fichiers WordPress

## 🎯 ÉTAPE 1 : Installation du Plugin WordPress

### 1.1 Télécharger les fichiers
Copiez le dossier `wordpress-integration` sur votre serveur :

```bash
# Via FTP ou panneau d'administration
/wp-content/plugins/siports-integration/
├── siports-integration.php
├── build/
│   ├── static/
│   │   ├── js/init.js
│   │   └── css/main.css
```

### 1.2 Activer le plugin
1. Connectez-vous à `/wp-admin/` avec `user@website.com`
2. Allez dans **Plugins** → **Extensions installées**
3. Trouvez "SIPORTS Integration" et cliquez **Activer**

### 1.3 Configuration initiale
1. Allez dans **Réglages** → **SIPORTS Config**
2. Configurez :
   - **URL API SIPORTS** : `https://3af9f13b-c7da-4bc1-b1f4-89ae2ae52faa.preview.emergentagent.com/api`
   - **Clé secrète JWT** : Générez une clé sécurisée (32 caractères)
   - **Synchronisation automatique** : ☑️ Activé

## 🔧 ÉTAPE 2 : Modification du Backend SIPORTS

### 2.1 Installation des dépendances
Dans votre environnement SIPORTS actuel :

```bash
pip install mysql-connector-python PyJWT python-multipart
```

### 2.2 Variables d'environnement
Ajoutez dans `/app/backend/.env` :

```env
# WordPress Database
WP_DB_HOST=localhost
WP_DB_NAME=siportevent_db
WP_DB_USER=your_wp_user
WP_DB_PASSWORD=your_wp_password
WP_TABLE_PREFIX=wp_

# JWT Configuration
JWT_SECRET_KEY=votre-clé-secrète-jwt-32-caractères

# WordPress URL
WORDPRESS_URL=https://siportevent.com
```

### 2.3 Modifier server.py
Ajoutez au début de `/app/backend/server.py` :

```python
# Import WordPress extensions
from wordpress_extensions import init_wordpress_integration

# À la fin de la configuration de l'app
init_wordpress_integration(app)
```

### 2.4 Ajouter les fichiers WordPress
Copiez ces fichiers dans `/app/backend/` :
- `wordpress_config.py`
- `wordpress_extensions.py`

## 📱 ÉTAPE 3 : Intégration Frontend React

### 3.1 Build de production
Dans votre environnement React SIPORTS :

```bash
cd /app/frontend
npm run build
```

### 3.2 Copier les fichiers build
Copiez le contenu de `build/` vers :
```
/wp-content/plugins/siports-integration/build/
```

### 3.3 Scripts d'initialisation
Le fichier `init.js` est automatiquement chargé et initialise les composants React dans WordPress.

## 🎨 ÉTAPE 4 : Utilisation dans WordPress

### 4.1 Shortcodes disponibles

#### Dashboard Admin
```php
[siports_app component="admin" height="800px"]
```

#### Gestionnaire de Packages  
```php
[siports_app component="packages" height="600px"]
```

#### Système de Matching
```php
[siports_app component="matching" height="700px"]
```

#### Application complète
```php
[siports_app component="main" height="900px"]
```

### 4.2 Exemples d'intégration

#### Dans une page WordPress
1. Créer une nouvelle page : **SIPORTS Dashboard**
2. Ajouter le shortcode dans l'éditeur :
```
[siports_app component="admin" height="800px"]
```

#### Dans un article
```
Découvrez notre plateforme SIPORTS :

[siports_app component="packages" height="600px"]

Plus d'informations disponibles...
```

#### Dans un template PHP
```php
<?php echo do_shortcode('[siports_app component="main"]'); ?>
```

## 🔄 ÉTAPE 5 : Configuration de la Synchronisation

### 5.1 Interface de synchronisation
Accédez à `/wp-admin/` → **SIPORTS Sync**

### 5.2 Synchronisation manuelle
- **Synchroniser utilisateurs** : Transfère les utilisateurs SIPORTS vers WordPress
- **Synchroniser packages** : Transfère les packages SIPORTS comme posts WordPress
- **Synchronisation complète** : Synchronise tout en une fois

### 5.3 Synchronisation automatique
1. Activée via **Réglages** → **SIPORTS Config** 
2. Se déclenche automatiquement toutes les 30 minutes
3. Logs disponibles dans **SIPORTS Sync**

## 🛡️ ÉTAPE 6 : Sécurité et Authentification

### 6.1 Authentification unifiée
- Les utilisateurs WordPress sont automatiquement connectés à SIPORTS
- Session unique entre WordPress et SIPORTS
- Tokens JWT sécurisés avec expiration 24h

### 6.2 Permissions
- **Administrateurs** : Accès complet à la synchronisation
- **Éditeurs** : Synchronisation des packages uniquement
- **Autres rôles** : Lecture seulement

### 6.3 Sécurisation
1. Changez la clé JWT par défaut
2. Utilisez HTTPS en production
3. Limitez les tentatives de connexion
4. Activez les logs de sécurité WordPress

## 🧪 ÉTAPE 7 : Tests et Validation

### 7.1 Test d'authentification
1. Connectez-vous à WordPress avec `user@website.com`
2. Accédez à une page avec shortcode SIPORTS
3. Vérifiez que l'interface SIPORTS se charge

### 7.2 Test de synchronisation
1. Allez dans **SIPORTS Sync**
2. Cliquez **Synchroniser utilisateurs**
3. Vérifiez que les utilisateurs SIPORTS apparaissent dans **Utilisateurs** WordPress

### 7.3 Test des composants
Testez chaque composant :
- ✅ Dashboard admin
- ✅ Gestionnaire packages
- ✅ Système matching
- ✅ Application principale

## 🚨 DÉPANNAGE

### Problème : Plugin ne s'active pas
**Solution** :
1. Vérifiez les permissions de fichiers (755 pour dossiers, 644 pour fichiers)
2. Consultez les logs WordPress : `/wp-content/debug.log`
3. Vérifiez la syntaxe PHP avec : `php -l siports-integration.php`

### Problème : Shortcode ne fonctionne pas
**Solution** :
1. Vérifiez que le plugin est activé
2. Effacez le cache WordPress/plugins de cache
3. Vérifiez la console navigateur pour erreurs JavaScript

### Problème : Synchronisation échoue
**Solution** :
1. Vérifiez la configuration base de données dans `.env`
2. Testez la connexion : `mysql -h host -u user -p database`
3. Vérifiez les logs backend : `/app/logs/wordpress_integration.log`

### Problème : Authentification ne fonctionne pas
**Solution** :
1. Vérifiez la clé JWT (même dans WordPress et backend)
2. Videz le cache/cookies navigateur
3. Vérifiez les headers CORS dans la console réseau

## 📊 MONITORING ET MAINTENANCE

### 7.1 Logs à surveiller
- **WordPress** : `/wp-content/debug.log`
- **SIPORTS Backend** : `/app/logs/wordpress_integration.log`
- **Serveur Web** : `/var/log/nginx/error.log` ou `/var/log/apache2/error.log`

### 7.2 Sauvegarde
**Avant mise à jour** :
```bash
# Sauvegarde base WordPress
mysqldump -u user -p database_name > backup_wordpress.sql

# Sauvegarde base SIPORTS  
cp /app/backend/siports.db backup_siports.db

# Sauvegarde plugin
tar -czf siports-plugin-backup.tar.gz /wp-content/plugins/siports-integration/
```

### 7.3 Mises à jour
1. **Plugin** : Remplacez les fichiers et réactivez le plugin
2. **Backend** : Redémarrez les services après modification
3. **Frontend** : Rebuild React et copiez vers WordPress

## 📞 SUPPORT

### Documentation
- Configuration WordPress : `/wp-admin/admin.php?page=siports-config`
- Synchronisation : `/wp-admin/admin.php?page=siports-sync`
- Logs : Consultez les fichiers de logs mentionnés

### Vérification de santé
```bash
# Test connexion WordPress
curl -X GET "https://siportevent.com/wp-json/siports/v1/status"

# Test backend SIPORTS
curl -X GET "https://3af9f13b-c7da-4bc1-b1f4-89ae2ae52faa.preview.emergentagent.com/api/sync/status"
```

## ✅ CHECKLIST DE DÉPLOIEMENT

- [ ] Plugin WordPress installé et activé
- [ ] Configuration SIPORTS complétée  
- [ ] Variables d'environnement backend configurées
- [ ] Extensions WordPress ajoutées au backend
- [ ] Build React copié dans le plugin
- [ ] Test d'authentification réussi
- [ ] Synchronisation testée et fonctionnelle
- [ ] Shortcodes testés sur différentes pages
- [ ] Permissions et sécurité vérifiées
- [ ] Sauvegarde effectuée
- [ ] Monitoring mis en place

---

🎉 **Félicitations !** Votre intégration SIPORTS WordPress est maintenant opérationnelle.

Pour toute question ou problème, consultez les logs ou contactez le support technique.