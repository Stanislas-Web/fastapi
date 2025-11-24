from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Modèles basés sur le contrat d'interface Carte Skaleet
# Documentation: Contrat Skaleet Carte - Webhooks
# ============================================================================


class SkaleetCardEvent(str, Enum):
    """Événements carte principaux selon le contrat Skaleet"""
    ACTIVATION_REQUESTED = "card.status.activation_requested"
    BLOCK_REQUESTED = "card.status.block_requested"
    UNBLOCK_REQUESTED = "card.status.unblock_requested"
    CREATED = "card.created"
    ACTIVATED = "card.activated"
    BLOCKED = "card.blocked"
    UNBLOCKED = "card.unblocked"


class SkaleetWebhookData(BaseModel):
    """
    Données du webhook Skaleet Carte
    Basé sur le contrat d'interface Skaleet Carte
    """
    cardId: int
    panAlias: Optional[str] = None
    # Autres champs optionnels possibles selon le contrat
    status: Optional[str] = None
    cardType: Optional[str] = None
    accountId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SkaleetWebhook(BaseModel):
    """
    Modèle complet d'un webhook Skaleet Carte
    Basé sur le contrat d'interface Skaleet Carte
    
    Exemple:
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
    """
    id: str
    webhookId: str
    type: str
    event: str
    data: SkaleetWebhookData


# ============================================================================
# Modèle générique pour compatibilité interne
# ============================================================================


class WebhookRequest(BaseModel):
    """Modèle générique pour les webhooks (usage interne)"""
    id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    correlation_id: Optional[str] = None

