# SIPORTS - Salon International des Ports

Application complète de gestion d'événements maritimes avec frontend React et backend Flask.

## 🚀 Fonctionnalités

### Frontend React
- **Page d'accueil** : Présentation de l'événement SIPORTS
- **Exposants** : Liste complète avec filtres avancés et mini-sites
- **Partenaires** : Partenaires classés par niveaux (Platine, Or, Argent, Bronze)
- **Réseautage** : Plateforme de connexion entre exposants, partenaires et visiteurs
- **Système de rendez-vous** : Calendrier dynamique avec gestion des créneaux
- **Messagerie** : Contact direct avec les exposants
- **Chatbot** : Assistant intelligent pour l'aide aux utilisateurs

### Backend Flask
- **API RESTful** complète
- **Base de données SQLite** avec modèles complets
- **Gestion des exposants et partenaires**
- **Système de rendez-vous** avec statuts (pending, accepted, rejected)
- **Messagerie** entre visiteurs et exposants
- **Tableaux de bord** pour exposants et partenaires
- **Analytics** et statistiques
- **API de réseautage**

## 📁 Structure du Projet

```
siports-backend/
├── src/
│   ├── main.py                 # Point d'entrée de l'application
│   ├── models/
│   │   ├── user.py            # Modèle utilisateur
│   │   └── exhibitor.py       # Modèles exposants, rendez-vous, messages
│   ├── routes/
│   │   ├── user.py            # Routes utilisateurs
│   │   ├── exhibitor.py       # Routes exposants
│   │   ├── networking.py      # Routes réseautage
│   │   └── dashboard.py       # Routes tableaux de bord
│   ├── database/
│   │   └── seed.py            # Données de test
│   └── static/                # Frontend React compilé
├── requirements.txt           # Dépendances Python
└── README.md                 # Cette documentation
```

## 🛠️ Installation et Démarrage

### Prérequis
- Python 3.11+
- pip

### Installation

1. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

2. **Démarrer l'application** :
```bash
cd src
python main.py
```

L'application sera accessible sur `http://localhost:5000`

### Développement

Pour le développement, vous pouvez également démarrer le frontend séparément :

```bash
# Dans le dossier frontend
npm install
npm run dev
```

## 🗄️ Base de Données

La base de données SQLite est automatiquement créée au premier démarrage avec des données de test incluant :

- **6 exposants** de différentes catégories
- **4 partenaires** avec niveaux (Platine, Or, Argent, Bronze)
- **Rendez-vous de démonstration**
- **Messages de test**

### Modèles Principaux

- **Exhibitor** : Exposants et partenaires
- **Appointment** : Rendez-vous avec gestion des statuts
- **Message** : Messages entre visiteurs et exposants
- **User** : Utilisateurs du système

## 🔌 API Endpoints

### Exposants
- `GET /api/exhibitors` - Liste des exposants avec filtres
- `GET /api/exhibitors/{id}` - Détails d'un exposant
- `GET /api/exhibitors/{name}` - Exposant par nom (mini-sites)
- `POST /api/exhibitors/{id}/appointments` - Créer un rendez-vous
- `POST /api/exhibitors/{id}/messages` - Envoyer un message

### Partenaires
- `GET /api/partners` - Liste des partenaires

### Réseautage
- `GET /api/networking/profiles` - Profils pour réseautage
- `POST /api/networking/connect` - Demande de connexion
- `GET /api/networking/stats` - Statistiques de réseautage

### Tableaux de Bord
- `GET /api/dashboard/exhibitor/{id}` - Dashboard exposant
- `GET /api/dashboard/partner/{id}` - Dashboard partenaire
- `GET /api/dashboard/appointments/{id}` - Rendez-vous
- `GET /api/dashboard/messages/{id}` - Messages

## 🎨 Technologies Utilisées

### Frontend
- **React 18** avec Vite
- **React Router** pour la navigation
- **Tailwind CSS** pour le styling
- **Lucide React** pour les icônes

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM pour la base de données
- **Flask-CORS** - Support CORS
- **SQLite** - Base de données

## 🚀 Déploiement

L'application est prête pour le déploiement avec :
- Frontend compilé dans `/src/static/`
- Configuration CORS pour production
- Serveur Flask configuré pour `0.0.0.0`

## 📝 Fonctionnalités Détaillées

### Système de Rendez-vous
- Calendrier dynamique 4 jours (15-18 Mars 2025)
- Créneaux matin/après-midi
- Types : Présentation, Démo, Réunion, Consultation, Partenariat
- Workflow : Demande → Pending → Accepted/Rejected/Proposed

### Mini-sites Exposants
- Page dédiée pour chaque exposant
- Informations complètes : produits, services, certifications
- Contact direct et prise de rendez-vous

### Réseautage
- Regroupement exposants + partenaires
- Filtres avancés par secteur, type, recherche
- Système de connexion et messagerie

### Chatbot
- Assistant maritime intelligent
- Réponses sur exposants, rendez-vous, informations générales
- Interface moderne avec animations

## 🔧 Configuration

### Variables d'Environnement
- `FLASK_ENV` : Environnement (development/production)
- `SECRET_KEY` : Clé secrète Flask (définie dans main.py)

### Base de Données
- SQLite par défaut : `src/database/app.db`
- Modifiable dans `main.py` via `SQLALCHEMY_DATABASE_URI`

## 📞 Support

Pour toute question ou support technique, contactez l'équipe de développement SIPORTS.

---

**SIPORTS 2025** - Salon International des Ports
*Connecter l'industrie maritime mondiale*

