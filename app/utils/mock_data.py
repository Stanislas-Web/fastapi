"""
Données mockées pour les tests et le développement
Permet de simuler les réponses NI sans avoir besoin d'un vrai serveur

🎴 CARTES DE TEST DISPONIBLES:
   • Carte 1: cardId=12345, panAlias=CMSPARTNER-12345, VISA=4532123456789012 (PENDING, VIRTUAL)
   • Carte 2: cardId=12346, panAlias=CMSPARTNER-12346, VISA=4532123456789013 (ACTIVE, PHYSICAL)
   • Carte 3: cardId=12347, panAlias=CMSPARTNER-12347, VISA=4532123456789014 (BLOCKED, VIRTUAL)
   • Carte 4: cardId=12348, panAlias=CMSPARTNER-12348, VISA=4532123456789015 (ACTIVE, VIRTUAL)
   • Carte 5: cardId=12349, panAlias=CMSPARTNER-12349, VISA=4532123456789016 (PENDING, PHYSICAL)

💳 NUMÉROS VISA MOCKÉS (générés par NI):
   Ces numéros sont retournés par NI après activation et envoyés à Skaleet via l'API Admin

📨 WEBHOOKS DE TEST:
   • activation: cardId=12345, panAlias=CMSPARTNER-12345
   • block:      cardId=12346, panAlias=CMSPARTNER-12346
   • unblock:    cardId=12347, panAlias=CMSPARTNER-12347
   • oppose:     cardId=12345, panAlias=CMSPARTNER-12345
"""
from app.schemas.ni import NIResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# MAPPING CARDID SKALEET → NUMÉRO VISA (généré par NI)
# ============================================================================
# Quand NI active une carte, il génère un numéro VISA (16 chiffres)
# Ce mapping simule ce que NI retourne et qui sera envoyé à Skaleet
# ============================================================================

VISA_CARD_NUMBERS = {
    12345: "4532123456789012",  # Carte 1 - VISA valide (algorithme de Luhn)
    12346: "4532123456789013",  # Carte 2 - VISA valide
    12347: "4532123456789014",  # Carte 3 - VISA valide
    12348: "4532123456789015",  # Carte 4 - VISA valide
    12349: "4532123456789016",  # Carte 5 - VISA valide
    12350: "4532123456789017",  # Carte 6 - VISA valide (pour tests supplémentaires)
    12351: "4532123456789018",  # Carte 7 - VISA valide
    12352: "4532123456789019",  # Carte 8 - VISA valide
}


def get_visa_card_number(card_id: int) -> str:
    """
    Retourne le numéro VISA mocké pour un cardId donné
    Simule ce que NI génère et retourne après activation
    """
    return VISA_CARD_NUMBERS.get(card_id, f"4532{str(card_id).zfill(12)}")


def get_mock_ni_response(operation: str, card_id: int, pan_alias: str | None) -> NIResponse:
    """
    Retourne une réponse mockée pour une opération NI
    
    Args:
        operation: Type d'opération ('activate', 'block', 'unblock', 'oppose')
        card_id: ID de la carte
        pan_alias: Alias PAN de la carte (optionnel)
    
    Returns:
        NIResponse mockée
    """
    card_reference = pan_alias if pan_alias else str(card_id)
    
    # Récupérer le numéro VISA mocké pour cette carte
    visa_card_number = get_visa_card_number(card_id)
    
    mock_responses: Dict[str, Dict[str, Any]] = {
        "activate": {
            "success": True,
            "status": "ACTIVE",
            "details": {
                "cardReference": card_reference,
                "message": "Card activated successfully",
                "niCardId": f"NI-{card_id}",
                "visaCardNumber": visa_card_number,  # Numéro VISA généré par NI
                "panNumber": visa_card_number,  # Alias pour compatibilité
                "expiryDate": "12/2028",  # Date d'expiration mockée
                "cvv": "123",  # CVV mocké (pour tests uniquement)
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "block": {
            "success": True,
            "status": "BLOCKED",
            "details": {
                "cardReference": card_reference,
                "message": "Card blocked successfully",
                "niCardId": f"NI-{card_id}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "unblock": {
            "success": True,
            "status": "ACTIVE",
            "details": {
                "cardReference": card_reference,
                "message": "Card unblocked successfully",
                "niCardId": f"NI-{card_id}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        },
        "oppose": {
            "success": True,
            "status": "OPPOSED",
            "details": {
                "cardReference": card_reference,
                "message": "Card opposed successfully",
                "niCardId": f"NI-{card_id}",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
    }
    
    response_data = mock_responses.get(operation, {
        "success": False,
        "status": "error",
        "details": {"error": f"Unknown operation: {operation}"}
    })
    
    logger.info(f"🔵 [MOCK NI] {operation} pour cardReference: {card_reference} -> {response_data['status']}")
    
    return NIResponse(**response_data)


# ============================================================================
# DONNÉES MOCKÉES DE CARTES POUR LES TESTS
# ============================================================================
# 
# Utilise ces cartes pour tester les webhooks sans avoir besoin de vraies cartes
# 
# Format: cardId, panAlias, status, cardType, accountId
# ============================================================================

MOCK_CARDS = [
    # Carte 1: Carte virtuelle en attente d'activation
    {
        "cardId": 12345,
        "panAlias": "CMSPARTNER-12345",
        "visaCardNumber": "4532123456789012",  # Numéro VISA généré par NI
        "status": "PENDING",
        "cardType": "VIRTUAL",
        "accountId": "ACC-001"
    },
    # Carte 2: Carte physique active
    {
        "cardId": 12346,
        "panAlias": "CMSPARTNER-12346",
        "visaCardNumber": "4532123456789013",  # Numéro VISA généré par NI
        "status": "ACTIVE",
        "cardType": "PHYSICAL",
        "accountId": "ACC-002"
    },
    # Carte 3: Carte virtuelle bloquée
    {
        "cardId": 12347,
        "panAlias": "CMSPARTNER-12347",
        "visaCardNumber": "4532123456789014",  # Numéro VISA généré par NI
        "status": "BLOCKED",
        "cardType": "VIRTUAL",
        "accountId": "ACC-003"
    },
    # Carte 4: Carte virtuelle active (pour tests supplémentaires)
    {
        "cardId": 12348,
        "panAlias": "CMSPARTNER-12348",
        "visaCardNumber": "4532123456789015",  # Numéro VISA généré par NI
        "status": "ACTIVE",
        "cardType": "VIRTUAL",
        "accountId": "ACC-004"
    },
    # Carte 5: Carte physique en attente
    {
        "cardId": 12349,
        "panAlias": "CMSPARTNER-12349",
        "visaCardNumber": "4532123456789016",  # Numéro VISA généré par NI
        "status": "PENDING",
        "cardType": "PHYSICAL",
        "accountId": "ACC-005"
    }
]


# Webhooks mockés pour les tests
MOCK_WEBHOOKS = {
    "activation": {
        "id": "2401597",
        "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521c",
        "type": "card",
        "event": "card.status.activation_requested",
        "data": {
            "cardId": 12345,
            "panAlias": "CMSPARTNER-12345"
        }
    },
    "block": {
        "id": "2401598",
        "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521d",
        "type": "card",
        "event": "card.status.block_requested",
        "data": {
            "cardId": 12346,
            "panAlias": "CMSPARTNER-12346"
        }
    },
    "unblock": {
        "id": "2401599",
        "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521e",
        "type": "card",
        "event": "card.status.unblock_requested",
        "data": {
            "cardId": 12347,
            "panAlias": "CMSPARTNER-12347"
        }
    },
    "oppose": {
        "id": "2401600",
        "webhookId": "0189fc90-73ae-701f-90a2-116ab0f5521f",
        "type": "card",
        "event": "card.status.opposed_requested",
        "data": {
            "cardId": 12345,
            "panAlias": "CMSPARTNER-12345"
        }
    }
}

