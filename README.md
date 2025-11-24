# Card Connector

Microservice FastAPI conçu pour intégrer Skaleet (webhooks Carte + Admin API) avec le processor cartes Visa (NI).

## Résumé

Le **Card Connector** est un microservice qui fait le pont entre l'écosystème Skaleet et le processor de cartes NI (Visa). Il gère le cycle de vie complet des cartes bancaires en orchestrant les opérations entre les deux systèmes.

### Fonctionnalités principales

- **Réception de webhooks Skaleet** : Le service expose un endpoint webhook pour recevoir les événements de cartes depuis Skaleet (activation, blocage, déblocage, opposition).

- **Intégration avec NI** : Appelle les APIs du processor NI pour exécuter les opérations demandées sur les cartes.

- **Notification Skaleet** : Renvoie les résultats des opérations à Skaleet via l'API Admin pour synchroniser les statuts.

- **Gestion du cycle de vie** : Suivi complet des opérations avec traçabilité, idempotence et gestion des erreurs.

## Architecture

Le microservice est construit avec une architecture modulaire et scalable :

### Stack technique

- **FastAPI** : Framework web asynchrone pour les endpoints REST
- **PostgreSQL + SQLAlchemy** : Base de données relationnelle avec ORM async
- **httpx** : Client HTTP asynchrone pour les appels aux APIs externes (Skaleet Admin, NI)
- **Alembic** : Gestion des migrations de schéma de base de données
- **pytest** : Framework de tests unitaires et d'intégration

### Structure du projet

```
app/
├── api/v1/          # Endpoints REST (health, webhooks)
├── domain/          # Logique métier (services, modèles, enums)
├── infra/           # Intégrations externes (clients HTTP, repositories, DB)
├── core/            # Configuration, logging, sécurité
├── schemas/         # Modèles Pydantic pour validation
└── utils/           # Utilitaires (idempotence, correlation ID)
```

### Principes d'architecture

- **Séparation des responsabilités** : API, domaine métier et infrastructure sont clairement séparés
- **Idempotence** : Tous les webhooks sont traités de manière idempotente via `webhookId`
- **Traçabilité** : Chaque requête est tracée avec un `correlation_id` unique
- **Logging structuré** : Logs en JSON avec correlation ID pour faciliter le debugging

## Endpoints principaux

### Health Check

```
GET /api/v1/health
```

Retourne le statut du service :
```json
{
  "status": "ok"
}
```

### Webhook Skaleet

```
POST /api/v1/webhooks/skaleet/card
```

Endpoint principal pour recevoir les webhooks de Skaleet concernant les cartes.

**Body** (exemple pour activation) :
```json
{
  "id": "2401597",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
  "type": "card",
  "event": "card.status.activation_requested",
  "data": {
    "cardId": 12345,
    "panAlias": "CMSPARTNER-12345"
  }
}
```

**Réponse** :
```json
{
  "ok": true,
  "event": "card.status.activation_requested"
}
```

**Événements supportés** :
- `card.status.activation_requested`
- `card.status.block_requested`
- `card.status.unblock_requested`
- `card.status.opposed_requested`

> **Note** : D'autres endpoints internes peuvent être ajoutés ultérieurement pour la gestion administrative ou la réconciliation.

## Intégration Gateway

Le microservice est conçu pour être déployé derrière un API Gateway dans les environnements d'intégration et de production.

### Architecture de déploiement

Dans un environnement avec API Gateway :

```
Internet → API Gateway → Card Connector (service interne)
```

Le service n'est **pas directement exposé sur Internet**. La sécurité (TLS, IP whitelisting, authentification) est gérée au niveau du gateway.

### Convention de chemins

Le service suit une convention de nommage pour faciliter le routing via le gateway :

#### Chemins publics (exposés via le gateway)

- `POST /webhooks/skaleet/card` : Webhook principal pour recevoir les événements Skaleet
- `POST /webhooks/ni/card` : Webhook pour recevoir les callbacks NI (à implémenter)

#### Chemins internes (non exposés publiquement)

- `/internal/cards/...` : Endpoints internes pour la gestion administrative, réconciliation, etc.

**Exemple de routing** :
- Route publique : `POST /webhooks/skaleet/card` → routé vers le service interne
- Routes internes : Accessibles uniquement depuis le réseau interne, non routées via le gateway public

Le service se concentre sur la logique métier. La sécurité réseau est déléguée au gateway.

## Démarrage

### Prérequis

- Python 3.12
- PostgreSQL 15+
- Variables d'environnement configurées (voir `.env.example`)

### Installation via pip

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec les valeurs appropriées
```

4. Appliquer les migrations :
```bash
alembic upgrade head
```

5. Lancer le service :
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Lancement via Docker Compose

1. Configurer le fichier `.env` :
```bash
cp .env.example .env
# Éditer .env avec les valeurs appropriées
```

2. Lancer les services :
```bash
docker-compose up -d
```

Cette commande démarre :
- Un conteneur PostgreSQL avec une base de données `card_connector_db`
- Le microservice `card-connector` sur le port 8000

3. Appliquer les migrations :
```bash
docker-compose exec card-connector alembic upgrade head
```

4. Accéder au service :
- Health check : http://localhost:8000/api/v1/health
- Documentation API : http://localhost:8000/docs
- Webhook endpoint : http://localhost:8000/api/v1/webhooks/skaleet/card

5. Arrêter les services :
```bash
docker-compose down
```

Pour supprimer aussi les volumes (données PostgreSQL) :
```bash
docker-compose down -v
```

## Migrations de base de données

Le projet utilise Alembic pour gérer les migrations de schéma.

### Appliquer les migrations

```bash
alembic upgrade head
```

Dans un environnement Docker :
```bash
docker-compose exec card-connector alembic upgrade head
```

### Créer une nouvelle migration

Avec autogenerate (recommandé) :
```bash
alembic revision --autogenerate -m "description de la migration"
```

Migration vide :
```bash
alembic revision -m "description de la migration"
```

## Tests

Lancer les tests :
```bash
pytest
```

Avec couverture :
```bash
pytest --cov=app tests/
```

## Prochaines étapes

Les évolutions prévues pour le microservice incluent :

1. **Gestion des callbacks NI** : Si le processor NI envoie des événements asynchrones (callbacks), ajout d'un endpoint pour les recevoir et mettre à jour les statuts en conséquence.

2. **Service de réconciliation** : Mise en place d'un mécanisme de réconciliation périodique pour s'assurer que les statuts entre Skaleet et NI sont synchronisés, avec détection et correction automatique des incohérences.

3. **Intégration avec un API Gateway** : Intégration du microservice dans l'architecture globale via un API Gateway pour la gestion centralisée de l'authentification, du rate limiting et du routing.

4. **Monitoring et observabilité** : Ajout de métriques (Prometheus), de traces distribuées et d'alertes pour le suivi en production.

5. **Gestion des erreurs avancée** : Implémentation d'un système de retry avec backoff exponentiel et d'une file d'attente pour les opérations en échec.

## Variables d'environnement

Voir `.env.example` pour la liste complète des variables d'environnement requises.

Variables principales :
- `DATABASE_URL` : URL de connexion PostgreSQL
- `SKALEET_ADMIN_BASE_URL` : URL de l'API Admin Skaleet
- `SKALEET_ADMIN_CLIENT_ID` / `SKALEET_ADMIN_CLIENT_SECRET` : Credentials OAuth2 Skaleet
- `NI_BASE_URL` : URL de l'API NI
- `NI_API_KEY` : Clé API NI
- `WEBHOOK_SECRET` : Secret pour valider les signatures des webhooks (optionnel)

## Support

Pour toute question ou problème, contacter l'équipe de développement.
