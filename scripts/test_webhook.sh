#!/bin/bash

# Script de test pour l'endpoint webhook Skaleet
# Usage: ./scripts/test_webhook.sh

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Test Webhook Skaleet - card.status.activation_requested ===${NC}\n"

# URL de l'endpoint (modifier si nécessaire)
ENDPOINT="http://localhost:8000/api/v1/webhooks/skaleet/card"

echo "Endpoint: $ENDPOINT"
echo ""

# Body complet du webhook avec tous les champs
BODY='{
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
}'

echo -e "${YELLOW}Body de la requête:${NC}"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

# Faire la requête
echo -e "${YELLOW}Envoi de la requête...${NC}\n"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d "$BODY")

# Extraire le code HTTP et le body
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

# Afficher le résultat
echo -e "${YELLOW}Réponse (HTTP $HTTP_CODE):${NC}"
echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
echo ""

# Vérifier le résultat
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Test réussi !${NC}"
    exit 0
else
    echo -e "${RED}✗ Test échoué (HTTP $HTTP_CODE)${NC}"
    exit 1
fi
