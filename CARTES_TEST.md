# 🎴 Cartes de Test - Card Connector

## Liste des cartes mockées disponibles

### Carte 1
- **cardId**: `12345`
- **panAlias**: `CMSPARTNER-12345`
- **visaCardNumber**: `4532123456789012` (généré par NI après activation)
- **status**: `PENDING`
- **cardType**: `VIRTUAL`
- **accountId**: `ACC-001`

### Carte 2
- **cardId**: `12346`
- **panAlias**: `CMSPARTNER-12346`
- **visaCardNumber**: `4532123456789013` (généré par NI après activation)
- **status**: `ACTIVE`
- **cardType**: `PHYSICAL`
- **accountId**: `ACC-002`

### Carte 3
- **cardId**: `12347`
- **panAlias**: `CMSPARTNER-12347`
- **visaCardNumber**: `4532123456789014` (généré par NI après activation)
- **status**: `BLOCKED`
- **cardType**: `VIRTUAL`
- **accountId**: `ACC-003`

### Carte 4
- **cardId**: `12348`
- **panAlias**: `CMSPARTNER-12348`
- **visaCardNumber**: `4532123456789015` (généré par NI après activation)
- **status**: `ACTIVE`
- **cardType**: `VIRTUAL`
- **accountId**: `ACC-004`

### Carte 5
- **cardId**: `12349`
- **panAlias**: `CMSPARTNER-12349`
- **visaCardNumber**: `4532123456789016` (généré par NI après activation)
- **status**: `PENDING`
- **cardType**: `PHYSICAL`
- **accountId**: `ACC-005`

## 📋 Résumé rapide

| cardId | panAlias            | visaCardNumber      | status   | cardType | accountId |
|--------|---------------------|---------------------|----------|----------|-----------|
| 12345  | CMSPARTNER-12345    | 4532123456789012    | PENDING  | VIRTUAL  | ACC-001   |
| 12346  | CMSPARTNER-12346    | 4532123456789013    | ACTIVE   | PHYSICAL | ACC-002   |
| 12347  | CMSPARTNER-12347    | 4532123456789014    | BLOCKED  | VIRTUAL  | ACC-003   |
| 12348  | CMSPARTNER-12348    | 4532123456789015    | ACTIVE   | VIRTUAL  | ACC-004   |
| 12349  | CMSPARTNER-12349    | 4532123456789016    | PENDING  | PHYSICAL | ACC-005   |

> 💡 **Note** : Les numéros VISA sont générés par NI après activation et renvoyés à Skaleet via l'API Admin. Voir `CARTES_VISA.md` pour plus de détails.

## Webhooks de test

### Activation
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

### Blocage
```json
{
  "id": "2401598",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521d",
  "type": "card",
  "event": "card.status.block_requested",
  "data": {
    "cardId": 12346,
    "panAlias": "CMSPARTNER-12346"
  }
}
```

### Déblocage
```json
{
  "id": "2401599",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521e",
  "type": "card",
  "event": "card.status.unblock_requested",
  "data": {
    "cardId": 12347,
    "panAlias": "CMSPARTNER-12347"
  }
}
```

### Opposition
```json
{
  "id": "2401600",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521f",
  "type": "card",
  "event": "card.status.opposed_requested",
  "data": {
    "cardId": 12345,
    "panAlias": "CMSPARTNER-12345"
  }
}
```

## Utilisation

Pour tester avec ces cartes, utilise les endpoints suivants :

```bash
# Activation de la carte 12345
curl -X POST http://localhost:8000/api/v1/webhooks/skaleet/card \
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

## Notes

- Assure-toi d'avoir `NI_USE_MOCK=true` dans ton `.env` pour utiliser les données mockées
- Les webhookId doivent être uniques pour chaque test (idempotence)
- Tu peux modifier les cardId et panAlias dans `app/utils/mock_data.py` si besoin

