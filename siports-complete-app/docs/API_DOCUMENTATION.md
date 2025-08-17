# 📡 Documentation API SIPORTS v2.0

## 🔗 Base URL

```
Production: https://siportevent-production.up.railway.app/api
Local: http://localhost:8001/api
```

## 🔐 Authentification

Toutes les routes protégées nécessitent un token JWT dans l'header :
```
Authorization: Bearer <token>
```

---

## 🔑 Authentification

### POST /auth/login
Connexion utilisateur

**Body:**
```json
{
  "email": "admin@siportevent.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "admin@siportevent.com",
    "user_type": "admin",
    "first_name": "Admin",
    "last_name": "SIPORTS"
  }
}
```

### POST /auth/register
Inscription utilisateur

**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "visitor",
  "company": "Company Name"
}
```

### POST /auth/visitor-login
Connexion visiteur anonyme

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "user": {
    "user_type": "visitor",
    "session_id": "visitor_session_123"
  }
}
```

---

## 👥 Administration

### GET /admin/dashboard/stats
Statistiques dashboard admin (Admin uniquement)

**Response:**
```json
{
  "total_users": 10,
  "total_visitors": 5,
  "total_exhibitors": 3,
  "total_partners": 2,
  "total_revenue": 89750,
  "recent_registrations": 2
}
```

### GET /admin/users/pending
Utilisateurs en attente de validation

**Query Params:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response:**
```json
{
  "users": [
    {
      "id": 2,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "user_type": "exhibitor",
      "status": "pending",
      "created_at": "2025-08-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### POST /admin/users/{id}/validate
Valider un utilisateur

**Body:**
```json
{
  "admin_email": "admin@siportevent.com"
}
```

### POST /admin/users/{id}/reject
Rejeter un utilisateur

**Body:**
```json
{
  "raison": "Documents incomplets",
  "commentaire": "Merci de fournir...",
  "admin_email": "admin@siportevent.com"
}
```

---

## 📦 Packages & Forfaits

### GET /visitor-packages
Liste des forfaits visiteur

**Response:**
```json
[
  {
    "id": "free",
    "name": "Free Pass",
    "price": 0,
    "duration": "Accès limité",
    "features": [
      "Accès à l'espace exposition",
      "Conférences publiques",
      "Documentation générale"
    ],
    "limitations": ["Accès limité aux espaces"]
  },
  {
    "id": "basic",
    "name": "Basic Pass",
    "price": 150,
    "duration": "1 jour d'accès",
    "rdv_b2b": 2,
    "features": [
      "Accès aux expositions",
      "2 réunions B2B garanties"
    ]
  }
]
```

### GET /partnership-packages
Liste des forfaits partenaires

**Response:**
```json
[
  {
    "id": "platinum",
    "name": "Partenaire Platinum",
    "price": 25000,
    "features": [
      "Stand premium 50m²",
      "Mini-site SIPORTS Premium dédié",
      "20 réunions B2B garanties"
    ]
  }
]
```

### POST /update-package
Mettre à jour le forfait utilisateur

**Body:**
```json
{
  "user_id": 1,
  "package_id": "premium",
  "admin_email": "admin@siportevent.com"
}
```

---

## 🤖 Chatbot IA

### POST /chat
Chat principal avec contextes multiples

**Body:**
```json
{
  "message": "Quels sont les forfaits disponibles ?",
  "session_id": "user_session_123",
  "context": "general"
}
```

**Response:**
```json
{
  "response": "SIPORTS propose 4 forfaits visiteur...",
  "confidence": 0.92,
  "context": "package",
  "suggested_actions": [
    "Voir les forfaits détaillés",
    "Comparer les prix",
    "Réserver un forfait"
  ]
}
```

### POST /chat/exhibitor
Chat spécialisé exposants

### POST /chat/package
Chat spécialisé forfaits

### POST /chat/event
Chat spécialisé événements

### GET /chatbot/health
État de santé du service chatbot

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "mode": "mock",
  "uptime": "5 days, 10:30:15"
}
```

---

## 📊 Analytics & Matching

### GET /matching/analytics
Analytics système de matching

### POST /matching/generate
Générer des recommandations matching

### POST /user-interaction
Enregistrer interaction utilisateur

---

## 🔍 Health & Status

### GET /
Health check principal

**Response:**
```json
{
  "message": "SIPORTS v2.0 Production Complete",
  "status": "active",
  "version": "2.0.0",
  "database": {
    "connected": true,
    "type": "postgresql"
  }
}
```

### GET /api/docs
Documentation Swagger interactive

---

## ❌ Codes d'Erreur

- **200** - Succès
- **400** - Bad Request
- **401** - Non authentifié
- **403** - Accès refusé
- **404** - Resource non trouvée
- **422** - Erreur de validation
- **500** - Erreur serveur

**Format erreur:**
```json
{
  "detail": "Message d'erreur détaillé",
  "error": "Type d'erreur",
  "status_code": 400
}
```

---

## 🧪 Données de Test

### Utilisateurs
- **Admin**: admin@siportevent.com / admin123
- **Exposant**: exposant@example.com / exhibitor123
- **Visiteur**: visitor@example.com / visitor123

### Sessions Chatbot
- Session test: `test_session_123`
- Contextes: `general`, `exhibitor`, `package`, `event`