# 🔍 Guide de Dépannage des Erreurs 422

## Qu'est-ce qu'une erreur 422 ?

Une erreur **422 Unprocessable Entity** signifie que le serveur comprend le format de la requête, mais **les données ne respectent pas le schéma de validation**.

---

## 🛠️ Comment Diagnostiquer

Depuis la dernière mise à jour, **toutes les erreurs 422 sont loggées en détail** dans les logs de l'application.

### Voir les erreurs en temps réel

```bash
# Suivre les logs en direct
docker-compose logs -f card-connector

# Filtrer uniquement les erreurs 422
docker-compose logs -f card-connector | grep "422"

# Voir les 50 dernières erreurs détaillées
docker logs card-connector-app 2>&1 | grep "Validation Error 422" -A 2
```

### Format du log d'erreur

```json
{
  "level": "ERROR",
  "message": "❌ Validation Error 422 - URL: /api/v1/webhooks/skaleet/card | Method: POST | Client: 192.168.65.1 | Body: {\"invalid\": \"payload\"} | Errors: [{'type': 'missing', 'loc': ('body', 'id'), 'msg': 'Field required', ...}]"
}
```

**Contient:**
- L'URL de l'endpoint
- L'IP du client qui a fait la requête
- Le body JSON envoyé (les 500 premiers caractères)
- Les erreurs de validation détaillées

---

## 📋 Schéma Attendu

L'endpoint `/api/v1/webhooks/skaleet/card` attend le format suivant:

### Champs Obligatoires

```json
{
  "id": "string",              // ✅ Obligatoire
  "webhookId": "string",       // ✅ Obligatoire
  "type": "string",            // ✅ Obligatoire
  "event": "string",           // ✅ Obligatoire
  "data": {                    // ✅ Obligatoire
    "cardId": 0                // ✅ Obligatoire (nombre entier)
  }
}
```

### Champs Optionnels dans `data`

```json
{
  "data": {
    "cardId": 0,                    // ✅ Obligatoire
    "panAlias": "string",           // ⚠️ Optionnel
    "status": "string",             // ⚠️ Optionnel
    "cardType": "string",           // ⚠️ Optionnel
    "accountId": "string",          // ⚠️ Optionnel
    "metadata": {},                 // ⚠️ Optionnel
    "operationId": 0,               // ⚠️ Optionnel (nombre entier si présent)
    "operationNature": "string",    // ⚠️ Optionnel
    "operationType": "string",      // ⚠️ Optionnel
    "operationState": "string",     // ⚠️ Optionnel
    "parameters": {}                // ⚠️ Optionnel
  }
}
```

---

## 🚨 Erreurs Courantes

### 1. Champ `cardId` en string au lieu de number

❌ **Incorrect:**
```json
{
  "data": {
    "cardId": "12345"  // String
  }
}
```

✅ **Correct:**
```json
{
  "data": {
    "cardId": 12345  // Number
  }
}
```

**Log d'erreur:**
```
{'type': 'int_parsing', 'loc': ('body', 'data', 'cardId'), 'msg': 'Input should be a valid integer'}
```

---

### 2. Champs obligatoires manquants

❌ **Incorrect:**
```json
{
  "id": "123",
  "data": {
    "cardId": 12345
  }
}
```

✅ **Correct:**
```json
{
  "id": "123",
  "webhookId": "456",  // ✅ Ajouté
  "type": "card",      // ✅ Ajouté
  "event": "card.new", // ✅ Ajouté
  "data": {
    "cardId": 12345
  }
}
```

**Log d'erreur:**
```
[
  {'type': 'missing', 'loc': ('body', 'webhookId'), 'msg': 'Field required'},
  {'type': 'missing', 'loc': ('body', 'type'), 'msg': 'Field required'},
  {'type': 'missing', 'loc': ('body', 'event'), 'msg': 'Field required'}
]
```

---

### 3. Header `Content-Type` manquant

❌ **Incorrect:**
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -d '{"id": "123", ...}'
```

✅ **Correct:**
```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -H "Content-Type: application/json" \  # ✅ Header ajouté
  -d '{"id": "123", ...}'
```

---

### 4. JSON mal formaté

❌ **Incorrect:**
```json
{
  "id": "123",
  "data": {
    "cardId": 12345,  // Virgule en trop
  }
}
```

✅ **Correct:**
```json
{
  "id": "123",
  "data": {
    "cardId": 12345
  }
}
```

---

## 🧪 Tester en Local

### Test avec payload minimal valide

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "webhookId": "webhook-456",
    "type": "card",
    "event": "card.new",
    "data": {
      "cardId": 99999
    }
  }'
```

**Réponse attendue:** HTTP 200
```json
{
  "ok": true,
  "event": "card.new"
}
```

### Test avec payload invalide (pour voir l'erreur)

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks/skaleet/card" \
  -H "Content-Type: application/json" \
  -d '{
    "invalid": "payload"
  }'
```

**Réponse attendue:** HTTP 422
```json
{
  "detail": [
    {"type": "missing", "loc": ["body", "id"], "msg": "Field required"},
    {"type": "missing", "loc": ["body", "webhookId"], "msg": "Field required"},
    ...
  ]
}
```

Puis vérifier les logs:
```bash
docker logs card-connector-app 2>&1 | grep "Validation Error 422" | tail -1
```

---

## 🔧 Utiliser les Scripts de Test

Les scripts incluent des payloads valides pré-configurés:

```bash
# Test activation (payload complet)
./scripts/test_webhook.sh

# Test management operation
./scripts/test_webhook_management_operation.sh
```

---

## 📊 Statistiques des Erreurs 422

Pour voir combien d'erreurs 422 tu as reçues:

```bash
# Compter les 422 dans les logs
docker logs card-connector-app 2>&1 | grep -c "422 Unprocessable Entity"

# Voir les IPs qui envoient des 422
docker logs card-connector-app 2>&1 | grep "Validation Error 422" | grep -oP "Client: \K[0-9.]+" | sort | uniq -c

# Voir les 10 derniers payloads invalides
docker logs card-connector-app 2>&1 | grep "Validation Error 422" | tail -10
```

---

## 🌐 Sources des Erreurs 422

Les erreurs 422 peuvent venir de:

1. **Skaleet Admin API** (webhooks mal configurés)
   - Vérifier la configuration des webhooks dans Skaleet
   - S'assurer que le format correspond au contrat

2. **Tests manuels** (curl, Postman, etc.)
   - Vérifier le format JSON
   - Vérifier le header `Content-Type`

3. **Cloudflare Tunnel ou proxy**
   - Parfois les proxies modifient le body
   - Tester d'abord en local (`localhost:8000`)

4. **Scans/bots**
   - Si l'URL est publique, des bots peuvent la tester
   - Les IPs publiques dans les logs indiquent des scans

---

## ✅ Checklist de Dépannage

Avant de signaler un bug, vérifier:

- [ ] Le header `Content-Type: application/json` est présent
- [ ] Tous les champs obligatoires sont présents (`id`, `webhookId`, `type`, `event`, `data`)
- [ ] Le champ `data.cardId` est un **nombre** (pas une string)
- [ ] Le champ `data.operationId` est un **nombre** (si présent)
- [ ] Le JSON est valide (pas de virgules en trop, guillemets corrects)
- [ ] Les logs montrent le détail de l'erreur: `docker logs card-connector-app | grep "Validation Error 422"`

---

## 📞 Support

Si le problème persiste après avoir vérifié la checklist:

1. **Capturer les logs détaillés:**
   ```bash
   docker logs card-connector-app 2>&1 | grep "Validation Error 422" -A 2 > errors_422.log
   ```

2. **Partager:**
   - Le fichier `errors_422.log`
   - Le payload que tu essaies d'envoyer
   - La commande `curl` complète (si applicable)

---

## 🎯 Exemples Valides Complets

### Activation de carte (minimal)
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

### Activation de carte (complet)
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
      "customField": "value"
    },
    "operationId": 1700459,
    "operationNature": "LIFE_CYCLE",
    "operationType": "CARD_ACTIVATION",
    "operationState": "ACCEPTED",
    "parameters": {
      "channel": "mobile"
    }
  }
}
```

### Management Operation
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
    "operationType": "CARD_CREATION",
    "operationState": "SETTLED"
  }
}
```
