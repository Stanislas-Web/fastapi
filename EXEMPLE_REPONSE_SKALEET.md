# 📤 Format de Réponse à Skaleet Admin API

## Endpoint

```
POST {baseUrl}/cards/{id}/operation/{operation_type}/{result}
```

Où :
- `{baseUrl}` : URL de base Skaleet Admin (configurée dans `SKALEET_ADMIN_BASE_URL`)
- `{id}` : ID de la carte Skaleet
- `{operation_type}` : Type d'opération (voir liste ci-dessous)
- `{result}` : `accept` ou `error`

## Types d'opérations supportés

- `card_activation`
- `card_blocking`
- `card_code_reissuing`
- `card_creation`
- `card_features_update`
- `card_limits_update`
- `card_opposition`
- `card_renew`
- `card_suppression`
- `card_unblocking`
- `refabrication`

## Format du Body

```json
{
  "pan_alias": "CMS PARTNER-12345",
  "pan_display": "4532****9012",
  "external_id": "NI-12345",
  "exp_month": 12,
  "exp_year": 2028
}
```

### Champs

- **pan_alias** (string, optionnel) : Alias PAN de la carte (ex: "CMS PARTNER-12345")
- **pan_display** (string, optionnel) : PAN masqué pour affichage (ex: "4532****9012")
- **external_id** (string, optionnel) : ID externe (ex: "NI-12345" ou niCardId de NI)
- **exp_month** (integer, optionnel) : Mois d'expiration (1-12)
- **exp_year** (integer, optionnel) : Année d'expiration (ex: 2028)

## Exemple de requête

```bash
curl --request POST \
  --url https://api.skaleet.com/cards/12345/operation/card_activation/accept \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer {token}' \
  --header 'Content-Type: application/json' \
  --data '{
    "pan_alias": "CMS PARTNER-12345",
    "pan_display": "4532****9012",
    "external_id": "NI-12345",
    "exp_month": 12,
    "exp_year": 2028
  }'
```

## Exemple de réponse (succès)

```json
{
  "success": true,
  "message": "Operation accepted"
}
```

## Exemple de réponse (erreur)

```json
{
  "success": false,
  "error": "Operation failed"
}
```

## Mapping des événements → Types d'opération

| Événement Skaleet | Type d'opération |
|-------------------|------------------|
| `card.status.activation_requested` | `card_activation` |
| `card.status.block_requested` | `card_blocking` |
| `card.status.unblock_requested` | `card_unblocking` |
| `card.status.opposed_requested` | `card_opposition` |
| `card.management_operation.accepted` (CARD_CREATION) | `card_creation` |
| `card.management_operation.accepted` (CARD_SUPPRESSION) | `card_suppression` |
| `card.management_operation.accepted` (CARD_FEATURES_UPDATE) | `card_features_update` |

## Source des données

Les données envoyées à Skaleet proviennent de :

1. **pan_alias** : Du webhook Skaleet (`webhook.data.panAlias`)
2. **pan_display** : Généré depuis le `visaCardNumber` (masqué)
3. **external_id** : `niCardId` de la réponse NI ou `NI-{cardId}`
4. **exp_month / exp_year** : De `expiryDate` dans la réponse NI (format "MM/YYYY") ou valeurs par défaut (12/année+3)

## Implémentation

La fonction `send_card_operation_result()` dans `app/infra/skaleet_client.py` :
- Récupère le token OAuth2
- Construit l'URL selon le format Skaleet
- Prépare le body avec tous les champs requis
- Envoie la requête POST à Skaleet

