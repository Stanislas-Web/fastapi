from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Modèles basés sur le contrat d'interface Carte Skaleet
# Documentation: Contrat Skaleet Carte - Webhooks
# ============================================================================


class SkaleetCardEvent(str, Enum):
    """Événements carte selon le contrat Skaleet"""
    # Événements de statut de carte
    ACTIVATION_REQUESTED = "card.status.activation_requested"
    BLOCK_REQUESTED = "card.status.block_requested"
    UNBLOCK_REQUESTED = "card.status.unblock_requested"
    OPPOSED_REQUESTED = "card.status.opposed_requested"
    ACTIVATED = "card.status.activated"
    BLOCKED = "card.status.blocked"
    UNBLOCKED = "card.status.unblocked"
    PENDING = "card.status.pending"
    EXPIRED = "card.status.expired"
    OPPOSED = "card.status.opposed"
    REMOVED = "card.status.removed"
    
    # Événements de création
    NEW = "card.new"
    
    # Événements de gestion d'opérations
    MANAGEMENT_OPERATION_ACCEPTED = "card.management_operation.accepted"
    MANAGEMENT_OPERATION_REFUSED = "card.management_operation.refused"
    MANAGEMENT_OPERATION_SETTLED = "card.management_operation.settled"
    MANAGEMENT_OPERATION_ERR_SETTLED = "card.management_operation.err_settled"


class SkaleetWebhookData(BaseModel):
    """
    Données du webhook Skaleet Carte
    Basé sur le contrat d'interface Skaleet Carte
    
    Supporte deux formats :
    1. Format simple (événements de statut) :
       {"cardId": 12345, "panAlias": "CMS PARTNER-12345"}
    
    2. Format avec opération (événements management_operation) :
       {
         "cardId": 2401598,
         "panAlias": "CMS PARTNER-2401598",
         "operationId": 1700459,
         "operationNature": "LIFE_CYCLE",
         "operationType": "CARD_SUPPRESSION",
         "operationState": "ACCEPTED",
         "parameters": {}
       }
    """
    cardId: int
    panAlias: Optional[str] = None
    
    # Champs pour les événements de statut simples
    status: Optional[str] = None
    cardType: Optional[str] = None
    accountId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Champs pour les événements management_operation
    operationId: Optional[int] = None
    operationNature: Optional[str] = None  # Ex: "LIFE_CYCLE"
    operationType: Optional[str] = None  # Ex: "CARD_CREATION", "CARD_SUPPRESSION", "CARD_FEATURES_UPDATE"
    operationState: Optional[str] = None  # Ex: "ACCEPTED", "REFUSED", "SETTLED", "ERR_SETTLED"
    parameters: Optional[Dict[str, Any]] = None  # Paramètres spécifiques à l'opération


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

