from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.webhook import WebhookRequest, SkaleetWebhook, SkaleetCardEvent
from app.infra.repositories import WebhookRepository, CardRepository, CardOperationRepository
from app.infra.skaleet_client import SkaleetClient, send_card_operation_result
from app.infra.ni_client import NIClient
from app.domain.enums import WebhookEventType, OperationType, OperationSource, OperationStatus
from app.utils.idempotency import (
    check_card_operation_idempotency,
    is_webhook_processed,
    mark_webhook_started,
    mark_webhook_finished
)
import logging

logger = logging.getLogger(__name__)


class CardWebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.webhook_repo = WebhookRepository(db)
        self.card_repo = CardRepository(db)
        self.card_operation_repo = CardOperationRepository(db)
        self.skaleet_client = SkaleetClient()
        self.ni_client = NIClient()
    
    async def process_webhook(self, webhook_data: WebhookRequest, correlation_id: str):
        try:
            # Enregistrer l'événement
            await self.webhook_repo.create_event(webhook_data, correlation_id)
            
            # Traiter selon le type d'événement
            if webhook_data.event_type == WebhookEventType.CARD_CREATED:
                result = await self._handle_card_created(webhook_data)
            elif webhook_data.event_type == WebhookEventType.CARD_ACTIVATED:
                result = await self._handle_card_activated(webhook_data)
            elif webhook_data.event_type == WebhookEventType.CARD_BLOCKED:
                result = await self._handle_card_blocked(webhook_data)
            elif webhook_data.event_type == WebhookEventType.CARD_UNBLOCKED:
                result = await self._handle_card_unblocked(webhook_data)
            else:
                result = {"status": "ignored", "message": f"Event type {webhook_data.event_type} not handled"}
            
            # Marquer comme traité
            await self.webhook_repo.mark_as_processed(webhook_data.id, result)
            
            return result
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            raise
    
    async def _handle_card_created(self, webhook_data: WebhookRequest):
        card_id = webhook_data.data.get("card_id")
        if not card_id:
            raise ValueError("card_id missing in webhook data")
        
        # Appeler NI pour créer la carte
        ni_response = await self.ni_client.create_card(card_id, webhook_data.data)
        
        return {
            "status": "processed",
            "card_id": card_id,
            "ni_response": ni_response
        }
    
    async def _handle_card_activated(self, webhook_data: WebhookRequest):
        card_id = webhook_data.data.get("card_id")
        if not card_id:
            raise ValueError("card_id missing in webhook data")
        
        # Appeler NI pour activer la carte
        ni_response = await self.ni_client.activate_card(card_id)
        
        return {
            "status": "processed",
            "card_id": card_id,
            "ni_response": ni_response
        }
    
    async def _handle_card_blocked(self, webhook_data: WebhookRequest):
        card_id = webhook_data.data.get("card_id")
        if not card_id:
            raise ValueError("card_id missing in webhook data")
        
        # Appeler NI pour bloquer la carte
        ni_response = await self.ni_client.block_card(card_id)
        
        return {
            "status": "processed",
            "card_id": card_id,
            "ni_response": ni_response
        }
    
    async def _handle_card_unblocked(self, webhook_data: WebhookRequest):
        card_id = webhook_data.data.get("card_id")
        if not card_id:
            raise ValueError("card_id missing in webhook data")
        
        # Appeler NI pour débloquer la carte
        ni_response = await self.ni_client.unblock_card(card_id)
        
        return {
            "status": "processed",
            "card_id": card_id,
            "ni_response": ni_response
        }
    
    async def process_card_webhook(self, webhook: SkaleetWebhook) -> dict:
        """
        Traite un webhook Skaleet Carte
        """
        try:
            # Récupérer les données du webhook
            card_id = webhook.data.cardId
            pan_alias = webhook.data.panAlias
            webhook_id = webhook.webhookId
            event = webhook.event
            
            logger.info(f"Processing Skaleet card webhook: {event} for cardId: {card_id}, webhookId: {webhook_id}")
            
            # Traiter selon le type d'événement
            if event == SkaleetCardEvent.ACTIVATION_REQUESTED.value:
                return await self._handle_activation(webhook, card_id, pan_alias, webhook_id, event)
            elif event == SkaleetCardEvent.BLOCK_REQUESTED.value:
                return await self._handle_block(webhook, card_id, pan_alias, webhook_id, event)
            elif event == SkaleetCardEvent.UNBLOCK_REQUESTED.value:
                return await self._handle_unblock(webhook, card_id, pan_alias, webhook_id, event)
            elif event == "card.status.opposed_requested":
                return await self._handle_oppose(webhook, card_id, pan_alias, webhook_id, event)
            else:
                logger.warning(f"Event type {event} not yet implemented")
                return {
                    "cardId": card_id,
                    "event": event,
                    "ni_success": False,
                    "message": f"Event type {event} not yet implemented"
                }
        except Exception as e:
            logger.error(f"Error processing card webhook: {e}", exc_info=True)
            raise
    
    async def _handle_operation(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str,
        operation_type: str,
        ni_method,
        success_status: str
    ) -> dict:
        """
        Handler générique pour traiter une opération carte
        """
        # 1. Vérifier l'idempotence basée sur webhookId
        if await is_webhook_processed(self.db, webhook_id):
            logger.info(f"Webhook {webhook_id} already processed (idempotent)")
            return {
                "cardId": card_id,
                "event": event,
                "ni_success": False,
                "idempotent": True,
                "message": "Webhook already processed"
            }
        
        # 2. Créer ou récupérer la carte
        card = await self.card_repo.get_or_create(card_id, pan_alias)
        if pan_alias and not card.pan_alias:
            card.pan_alias = pan_alias
            await self.db.commit()
            await self.db.refresh(card)
        
        # 3. Marquer le webhook comme démarré (créer CardOperation avec PENDING)
        operation = await mark_webhook_started(
            self.db,
            webhook_id,
            card_id,
            operation_type,
            event,
            webhook.id
        )
        
        # Ajouter le raw_webhook à l'opération
        operation.raw_webhook = webhook.dict()
        await self.db.commit()
        await self.db.refresh(operation)
        
        # 4. Appeler NI
        ni_response = await ni_method(card_id, pan_alias)
        ni_success = ni_response.success
        
        # Extraire le numéro VISA de la réponse NI (si disponible)
        visa_card_number = None
        ni_details = None
        if ni_response.details:
            visa_card_number = ni_response.details.get("visaCardNumber") or ni_response.details.get("panNumber")
            ni_details = ni_response.details
        
        # 5. Traiter la réponse NI
        if ni_success:
            # Mettre à jour Card.status_ni
            await self.card_repo.update_status_ni(card.id, success_status)
            
            # Si on a un numéro VISA, le sauvegarder dans la base
            if visa_card_number and hasattr(card, 'ni_card_ref'):
                card.ni_card_ref = visa_card_number
                await self.db.commit()
                await self.db.refresh(card)
            
            # Marquer le webhook comme terminé avec SUCCESS
            await mark_webhook_finished(
                self.db,
                operation.id,
                OperationStatus.SUCCESS.value,
                ni_result_code=ni_response.status
            )
            
            # Appeler Skaleet Admin avec le numéro VISA
            try:
                await send_card_operation_result(
                    card_id, 
                    operation_type, 
                    "accept",
                    visa_card_number=visa_card_number,
                    ni_details=ni_details
                )
            except Exception as e:
                logger.error(f"Error sending result to Skaleet: {e}", exc_info=True)
        else:
            # Marquer le webhook comme terminé avec ERROR
            await mark_webhook_finished(
                self.db,
                operation.id,
                OperationStatus.ERROR.value,
                ni_result_code=ni_response.status
            )
            
            # Appeler Skaleet Admin avec erreur
            try:
                await send_card_operation_result(card_id, operation_type, "error")
            except Exception as e:
                logger.error(f"Error sending error result to Skaleet: {e}", exc_info=True)
        
        logger.info(f"{operation_type} processed for card {card_id}: NI success={ni_success}")
        
        return {
            "cardId": card_id,
            "event": event,
            "ni_success": ni_success
        }
    
    async def _handle_activation(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """Traite l'événement card.status.activation_requested"""
        return await self._handle_operation(
            webhook,
            card_id,
            pan_alias,
            webhook_id,
            event,
            OperationType.CARD_ACTIVATION.value,
            self.ni_client.activate_card_in_ni,
            "ACTIVE"
        )
    
    async def _handle_block(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """Traite l'événement card.status.block_requested"""
        return await self._handle_operation(
            webhook,
            card_id,
            pan_alias,
            webhook_id,
            event,
            OperationType.CARD_BLOCKING.value,
            self.ni_client.block_card_in_ni,
            "BLOCKED"
        )
    
    async def _handle_unblock(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """Traite l'événement card.status.unblock_requested"""
        return await self._handle_operation(
            webhook,
            card_id,
            pan_alias,
            webhook_id,
            event,
            OperationType.CARD_UNBLOCKING.value,
            self.ni_client.unblock_card_in_ni,
            "ACTIVE"
        )
    
    async def _handle_oppose(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """Traite l'événement card.status.opposed_requested"""
        return await self._handle_operation(
            webhook,
            card_id,
            pan_alias,
            webhook_id,
            event,
            OperationType.CARD_OPPOSITION.value,
            self.ni_client.oppose_card_in_ni,
            "OPPOSED"
        )

