#!/bin/bash

# Script de test pour l'endpoint webhook Skaleet - management_operation
# Usage: ./scripts/test_webhook_management_operation.sh

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Test Webhook Skaleet - card.management_operation.settled ===${NC}\n"

# URL de l'endpoint (modifier si nécessaire)
ENDPOINT="http://localhost:8000/api/v1/webhooks/skaleet/card"

echo "Endpoint: $ENDPOINT"
echo ""

# Body complet du webhook pour management_operation
BODY='{
  "id": "2401598",
  "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5522d",
  "type": "card",
  "event": "card.management_operation.settled",
  "data": {
    "cardId": 2401598,
    "panAlias": "CMS PARTNER-2401598",
    "status": "ACTIVE",
    "cardType": "VIRTUAL",
    "accountId": "ACC-789012",
    "metadata": {
      "customField": "customValue"
    },
    "operationId": 1700459,
    "operationNature": "LIFE_CYCLE",
    "operationType": "CARD_FEATURES_UPDATE",
    "operationState": "SETTLED",
    "parameters": {
      "updatedField": "contactless_enabled",
      "newValue": true
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
