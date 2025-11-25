# 💳 Numéros de Cartes VISA Mockés

## Vue d'ensemble

Quand NI (processor Visa) active une carte, il génère un **numéro de carte VISA** (16 chiffres) qui est ensuite renvoyé à Skaleet via l'API Admin.

## Flow complet

1. **Skaleet** envoie un webhook avec `cardId` et `panAlias`
2. **Card Connector** appelle **NI** pour activer la carte
3. **NI** génère un numéro VISA (16 chiffres commençant par 4)
4. **NI** retourne le numéro VISA dans sa réponse
5. **Card Connector** envoie le numéro VISA à **Skaleet** via l'API Admin

## Mapping CardId → Numéro VISA

| cardId Skaleet | panAlias            | Numéro VISA (généré par NI) | Status   | Type     |
|----------------|---------------------|----------------------------|----------|----------|
| 12345          | CMSPARTNER-12345    | 4532123456789012           | PENDING  | VIRTUAL  |
| 12346          | CMSPARTNER-12346    | 4532123456789013           | ACTIVE   | PHYSICAL |
| 12347          | CMSPARTNER-12347    | 4532123456789014           | BLOCKED  | VIRTUAL  |
| 12348          | CMSPARTNER-12348    | 4532123456789015           | ACTIVE   | VIRTUAL  |
| 12349          | CMSPARTNER-12349    | 4532123456789016           | PENDING  | PHYSICAL |
| 12350          | CMSPARTNER-12350    | 4532123456789017           | ACTIVE   | VIRTUAL  |
| 12351          | CMSPARTNER-12351    | 4532123456789018           | ACTIVE   | PHYSICAL |
| 12352          | CMSPARTNER-12352    | 4532123456789019           | PENDING  | VIRTUAL  |

## Format des numéros VISA

- **16 chiffres** au total
- **Commence par 4** (identifiant VISA)
- **Valide selon l'algorithme de Luhn** (pour les tests)

## Exemple de réponse NI (mockée)

Quand NI active une carte, il retourne :

```json
{
  "success": true,
  "status": "ACTIVE",
  "details": {
    "cardReference": "CMSPARTNER-12345",
    "message": "Card activated successfully",
    "niCardId": "NI-12345",
    "visaCardNumber": "4532123456789012",
    "panNumber": "4532123456789012",
    "expiryDate": "12/2028",
    "cvv": "123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Exemple de payload envoyé à Skaleet Admin API

Quand Card Connector notifie Skaleet du succès de l'activation :

```bash
POST /cards/12345/operation/card_activation/accept
```

**Body** :
```json
{
  "visaCardNumber": "4532123456789012",
  "panNumber": "4532123456789012",
  "expiryDate": "12/2028",
  "niCardId": "NI-12345",
  "niDetails": {
    "cardReference": "CMSPARTNER-12345",
    "message": "Card activated successfully",
    "niCardId": "NI-12345",
    "visaCardNumber": "4532123456789012",
    "panNumber": "4532123456789012",
    "expiryDate": "12/2028",
    "cvv": "123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Utilisation dans les tests

Pour tester avec une carte VISA mockée :

```bash
# 1. Activer le mode mock dans .env
NI_USE_MOCK=true

# 2. Envoyer un webhook d'activation
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

# 3. Le service va :
#    - Appeler NI (mock) qui retourne visaCardNumber: "4532123456789012"
#    - Envoyer ce numéro VISA à Skaleet via l'API Admin
```

## Notes importantes

⚠️ **Sécurité** :
- Ces numéros VISA sont **uniquement pour les tests**
- Ils ne sont **pas valides** pour de vraies transactions
- Ne jamais utiliser ces numéros en production

✅ **Format** :
- Les numéros respectent le format VISA standard (16 chiffres, commence par 4)
- Ils sont valides selon l'algorithme de Luhn pour les tests

📝 **Modification** :
- Tu peux ajouter/modifier des numéros VISA dans `app/utils/mock_data.py`
- Fonction `get_visa_card_number(card_id)` retourne le numéro VISA pour un cardId

