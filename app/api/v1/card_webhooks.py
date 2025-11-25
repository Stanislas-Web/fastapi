from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.webhook import SkaleetWebhook
from app.domain.services import CardWebhookService
from app.infra.db import get_db
from app.utils.correlation import get_correlation_id_from_context
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/skaleet/card")
async def handle_skaleet_card_webhook(
    request: Request,
    webhook: SkaleetWebhook,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint webhook pour recevoir les événements Skaleet concernant les cartes.
    
    IMPORTANT - Sécurité :
    - Cet endpoint est prévu pour être exposé via un API Gateway, et non directement sur Internet
    - La sécurité finale (TLS, IP whitelisting, authentification) se fera au niveau du gateway
    - Le service se concentre sur la validation des données et la logique métier
    
    Événements supportés :
    
    Événements d'action (nécessitent un appel à NI) :
    - card.status.activation_requested
    - card.status.block_requested
    - card.status.unblock_requested
    - card.status.opposed_requested
    
    Événements informatifs de statut :
    - card.status.activated
    - card.status.blocked
    - card.status.unblocked
    - card.status.pending
    - card.status.expired
    - card.status.opposed
    - card.status.removed
    
    Événements de création :
    - card.new
    
    Événements de gestion d'opérations :
    - card.management_operation.accepted
    - card.management_operation.refused
    - card.management_operation.settled
    - card.management_operation.err_settled
    """
    # Récupérer le correlation_id depuis le contexte ou request.state
    correlation_id = get_correlation_id_from_context() or getattr(request.state, "correlation_id", "unknown")
    
    # Logger l'event avec correlation_id
    logger.info(
        "Received Skaleet card webhook",
        extra={
            "correlation_id": correlation_id,
            "event": webhook.event,
            "cardId": webhook.data.cardId,
            "webhookId": webhook.webhookId
        }
    )
    
    # Appeler le service pour traiter le webhook
    service = CardWebhookService(db)
    await service.process_card_webhook(webhook)
    
    return {
        "ok": True,
        "event": webhook.event
    }

