# Guide de Diagnostic - Docker & PostgreSQL

Ce guide vous aide à diagnostiquer et résoudre les problèmes courants avec Docker et PostgreSQL.

## Problème 1: "invalid length of startup packet" (PostgreSQL)

### Symptôme
Dans les logs PostgreSQL (`docker-compose logs postgres`), vous voyez:
```
LOG: invalid length of startup packet
```

### Causes Possibles

1. **Requête HTTP vers le port PostgreSQL (5432)**
   - Quelque chose envoie du trafic HTTP/TCP non-PostgreSQL vers le port 5432
   - Exemple: healthcheck mal configuré, scan de port, probe HTTP

2. **Conflit avec PostgreSQL local**
   - Un PostgreSQL local tourne déjà sur le port 5432
   - Docker essaie d'exposer le port mais rencontre un conflit

3. **Scan/probe réseau**
   - Si le port 5432 est exposé publiquement, des scans automatisés peuvent le sonder

### Diagnostic

**1. Vérifier les logs détaillés:**
```bash
docker-compose logs postgres | grep "invalid length" -B 5 -A 5
```
Cherchez l'adresse IP du client qui a provoqué l'erreur.

**2. Vérifier qui utilise le port 5432 sur l'hôte:**
```bash
# macOS / zsh
lsof -nP -iTCP:5432 | grep LISTEN

# Linux
sudo netstat -tulpn | grep 5432
```

**3. Vérifier les conteneurs actifs:**
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

**4. Tester la connexion PostgreSQL:**
```bash
# Depuis l'hôte (si port mappé)
psql -h localhost -p 5432 -U carduser -d card_connector_db

# Depuis le conteneur
docker exec -it card-connector-postgres psql -U carduser -d card_connector_db
```

### Solutions

**Solution 1: Arrêter le PostgreSQL local**
```bash
# macOS (si installé via Homebrew)
brew services stop postgresql@15

# Linux (systemd)
sudo systemctl stop postgresql
```

**Solution 2: Changer le port exposé par Docker**
Éditez `docker-compose.yml`:
```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # Expose sur 5433 au lieu de 5432
```

Puis:
```bash
docker-compose down
docker-compose up -d
```

**Solution 3: Ne pas exposer le port (si l'accès depuis l'hôte n'est pas nécessaire)**
Éditez `docker-compose.yml`:
```yaml
services:
  postgres:
    # ports:  # Commentez cette ligne
    #   - "5432:5432"
```

Les conteneurs Docker pourront toujours communiquer entre eux via le nom du service (`postgres:5432`).

---

## Problème 2: Erreur de connexion DB depuis card-connector

### Symptôme
Dans les logs de `card-connector`, vous voyez:
```
sqlalchemy.exc.OperationalError: ... could not connect to server
```

### Diagnostic

**1. Vérifier que PostgreSQL est prêt:**
```bash
docker-compose logs postgres | grep "database system is ready"
```

**2. Vérifier le healthcheck:**
```bash
docker inspect card-connector-postgres | jq '.[0].State.Health'
```

**3. Vérifier la configuration DATABASE_URL:**
```bash
docker-compose exec card-connector env | grep DATABASE_URL
```

Doit être: `postgresql+asyncpg://carduser:cardpass@postgres:5432/card_connector_db`

**4. Tester la connexion réseau entre conteneurs:**
```bash
docker-compose exec card-connector ping postgres
```

### Solutions

**Solution 1: Attendre le healthcheck**
Assurez-vous que `docker-compose.yml` contient:
```yaml
services:
  card-connector:
    depends_on:
      postgres:
        condition: service_healthy
```

**Solution 2: Vérifier DATABASE_URL**
Dans `docker-compose.yml`:
```yaml
services:
  card-connector:
    environment:
      DATABASE_URL: postgresql+asyncpg://carduser:cardpass@postgres:5432/card_connector_db
```

**Important:** Utilisez `postgres` (nom du service) comme hostname, **pas** `localhost` ou `host.docker.internal`.

**Solution 3: Redémarrer les services dans le bon ordre**
```bash
docker-compose down -v  # -v supprime aussi les volumes
docker-compose up -d postgres
# Attendre que postgres soit healthy
docker-compose up -d card-connector
```

---

## Problème 3: Erreur 422 (Unprocessable Entity) sur l'endpoint webhook

### Symptôme
Requête vers `/api/v1/webhooks/skaleet/card` retourne HTTP 422.

### Diagnostic

**1. Voir le détail de l'erreur:**
```bash
curl -v -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -H "Content-Type: application/json" \
  -d '{"id": "123", "webhookId": "456", "type": "card", "event": "card.new", "data": {"cardId": "wrong_type"}}'
```

Le body de la réponse 422 indique précisément quel champ pose problème.

**2. Vérifier les logs de l'application:**
```bash
docker-compose logs card-connector | tail -n 50
```

### Solutions

**Vérifier le body de la requête:**

✅ **Correct:**
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

❌ **Incorrect:**
```json
{
  "id": "2401597",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
  "type": "card",
  "event": "card.status.activation_requested",
  "data": {
    "cardId": "12345",  // ❌ String au lieu de int
    "panAlias": "CMSPARTNER-12345"
  }
}
```

**Points à vérifier:**
- `cardId` doit être un **nombre** (pas une chaîne)
- `operationId` doit être un **nombre** (si présent)
- Header `Content-Type: application/json` obligatoire
- Tous les champs obligatoires présents: `id`, `webhookId`, `type`, `event`, `data`, `data.cardId`

**Utiliser le script de test:**
```bash
./scripts/test_webhook.sh
```

---

## Commandes Utiles

### Redémarrage complet
```bash
# Arrêter et supprimer tous les conteneurs/volumes
docker-compose down -v

# Rebuild et relancer
docker-compose up -d --build

# Voir les logs en temps réel
docker-compose logs -f
```

### Vérifier l'état des services
```bash
# État des conteneurs
docker-compose ps

# Santé du conteneur postgres
docker inspect card-connector-postgres --format='{{.State.Health.Status}}'

# Logs d'un service spécifique
docker-compose logs postgres
docker-compose logs card-connector
```

### Accéder à PostgreSQL
```bash
# Via psql dans le conteneur
docker-compose exec postgres psql -U carduser -d card_connector_db

# Lister les tables
docker-compose exec postgres psql -U carduser -d card_connector_db -c "\dt"

# Voir les connexions actives
docker-compose exec postgres psql -U carduser -d card_connector_db -c "SELECT * FROM pg_stat_activity;"
```

### Tests de connectivité
```bash
# Health check de l'API
curl http://localhost:8000/health

# Ping entre conteneurs
docker-compose exec card-connector ping postgres

# Vérifier les ports exposés
docker-compose port card-connector 8000
docker-compose port postgres 5432
```

### Nettoyage
```bash
# Supprimer les conteneurs arrêtés
docker-compose down

# Supprimer aussi les volumes (⚠️ perte de données)
docker-compose down -v

# Supprimer les images inutilisées
docker image prune -a

# Nettoyage complet Docker
docker system prune -a --volumes
```

---

## Checklist de Dépannage

Avant de poser une question, vérifiez:

- [ ] Les logs des deux services (`docker-compose logs postgres card-connector`)
- [ ] L'état des conteneurs (`docker-compose ps`)
- [ ] La variable `DATABASE_URL` dans le conteneur (`docker-compose exec card-connector env | grep DATABASE_URL`)
- [ ] Qu'aucun service local n'utilise les ports 5432 ou 8000 (`lsof -nP -iTCP:5432,8000`)
- [ ] Le healthcheck de postgres (`docker inspect card-connector-postgres | jq '.[0].State.Health'`)
- [ ] Un test simple avec curl vers l'API (`curl http://localhost:8000/health`)

Si le problème persiste, fournissez:
1. La sortie de `docker-compose logs --tail=100`
2. La sortie de `docker-compose ps`
3. La sortie de `lsof -nP -iTCP:5432`
