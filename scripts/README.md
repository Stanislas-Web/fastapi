# Scripts de Test

Ce dossier contient des scripts utiles pour tester l'application.

## Scripts de Test Webhook

### `test_webhook.sh`

Teste l'endpoint webhook avec un événement `card.status.activation_requested`.

**Usage:**
```bash
./scripts/test_webhook.sh
```

**Prérequis:**
- L'application doit être lancée (via `docker-compose up` ou localement)
- L'endpoint doit être accessible sur `http://localhost:8000`
- `jq` (optionnel, pour un affichage formaté du JSON)

**Body de test:**
```json
{
  "id": "2401597",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
  "type": "card",
  "event": "card.status.activation_requested",
  "data": {
    "cardId": 12345,
    "panAlias": "CMSPARTNER-12345",
    "status": "ACTIVATION_REQUESTED",
    "cardType": "PHYSICAL",
    "accountId": "ACC-123456",
    "metadata": {
      "customField": "customValue",
      "source": "mobile-app"
    },
    "operationId": 1700459,
    "operationNature": "LIFE_CYCLE",
    "operationType": "CARD_ACTIVATION",
    "operationState": "ACCEPTED",
    "parameters": {
      "activationChannel": "mobile",
      "requestedBy": "user-123"
    }
  }
}
```

---

### `test_webhook_management_operation.sh`

Teste l'endpoint webhook avec un événement `card.management_operation.settled`.

**Usage:**
```bash
./scripts/test_webhook_management_operation.sh
```

**Body de test:**
```json
{
  "id": "2401598",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5522d",
  "type": "card",
  "event": "card.management_operation.settled",
  "data": {
    "cardId": 2401598,
    "panAlias": "CMS PARTNER-2401598",
    "operationId": 1700459,
    "operationNature": "LIFE_CYCLE",
    "operationType": "CARD_FEATURES_UPDATE",
    "operationState": "SETTLED",
    "parameters": {
      "updatedField": "contactless_enabled",
      "newValue": true
    }
  }
}
```

---

## Test Manuel avec curl

Si vous préférez tester manuellement avec `curl`:

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2401597",
    "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
    "type": "card",
    "event": "card.status.activation_requested",
    "data": {
      "cardId": 12345,
      "panAlias": "CMSPARTNER-12345"
    }
  }'
```

---

## Dépannage

### Erreur 422 (Unprocessable Entity)

Si vous obtenez une erreur 422, vérifiez:

1. **Le header `Content-Type`** est bien `application/json`
2. **Les types de champs** correspondent:
   - `cardId`: doit être un **nombre entier** (pas une chaîne)
   - `operationId`: doit être un **nombre entier** (si présent)
3. **Les champs obligatoires** sont présents:
   - `id`, `webhookId`, `type`, `event`
   - `data.cardId` (obligatoire)
4. **La casse des champs** est correcte (sensible à la casse)

FastAPI retourne un body détaillé pour les erreurs 422, indiquant quel champ pose problème.

### Erreur de connexion

Si vous obtenez `Connection refused`:

1. Vérifiez que l'application est lancée:
   ```bash
   docker-compose ps
   # ou
   curl http://localhost:8000/health
   ```

2. Vérifiez que le port 8000 n'est pas occupé par un autre service:
   ```bash
   lsof -nP -iTCP:8000 | grep LISTEN
   ```

3. Si vous utilisez Docker, assurez-vous que le port est bien mappé:
   ```bash
   docker-compose logs card-connector
   ```

---

## Événements Supportés

L'endpoint `/api/v1/webhooks/skaleet/card` supporte les événements suivants:

### Événements d'action (déclenchent un appel à NI)
- `card.status.activation_requested`
- `card.status.block_requested`
- `card.status.unblock_requested`
- `card.status.opposed_requested`

### Événements informatifs de statut
- `card.status.activated`
- `card.status.blocked`
- `card.status.unblocked`
- `card.status.pending`
- `card.status.expired`
- `card.status.opposed`
- `card.status.removed`

### Événements de création
- `card.new`

### Événements de gestion d'opérations
- `card.management_operation.accepted`
- `card.management_operation.refused`
- `card.management_operation.settled`
- `card.management_operation.err_settled`
