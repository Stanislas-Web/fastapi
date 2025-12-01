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
            # Événements qui nécessitent une action (appel à NI)
            if event == SkaleetCardEvent.ACTIVATION_REQUESTED.value:
                return await self._handle_activation(webhook, card_id, pan_alias, webhook_id, event)
            elif event == SkaleetCardEvent.BLOCK_REQUESTED.value:
                return await self._handle_block(webhook, card_id, pan_alias, webhook_id, event)
            elif event == SkaleetCardEvent.UNBLOCK_REQUESTED.value:
                return await self._handle_unblock(webhook, card_id, pan_alias, webhook_id, event)
            elif event == SkaleetCardEvent.OPPOSED_REQUESTED.value:
                return await self._handle_oppose(webhook, card_id, pan_alias, webhook_id, event)
            
            # Événements informatifs de statut (mise à jour du statut uniquement)
            elif event in [
                SkaleetCardEvent.ACTIVATED.value,
                SkaleetCardEvent.BLOCKED.value,
                SkaleetCardEvent.UNBLOCKED.value,
                SkaleetCardEvent.PENDING.value,
                SkaleetCardEvent.EXPIRED.value,
                SkaleetCardEvent.OPPOSED.value,
                SkaleetCardEvent.REMOVED.value
            ]:
                return await self._handle_status_update(webhook, card_id, pan_alias, webhook_id, event)
            
            # Événement de création de carte
            elif event == SkaleetCardEvent.NEW.value:
                return await self._handle_card_new(webhook, card_id, pan_alias, webhook_id, event)
            
            # Événements de gestion d'opérations
            elif event in [
                SkaleetCardEvent.MANAGEMENT_OPERATION_ACCEPTED.value,
                SkaleetCardEvent.MANAGEMENT_OPERATION_REFUSED.value,
                SkaleetCardEvent.MANAGEMENT_OPERATION_SETTLED.value,
                SkaleetCardEvent.MANAGEMENT_OPERATION_ERR_SETTLED.value
            ]:
                return await self._handle_management_operation(webhook, card_id, pan_alias, webhook_id, event)
            
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
                    pan_alias=pan_alias,
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
                await send_card_operation_result(
                    card_id, 
                    operation_type, 
                    "error",
                    pan_alias=pan_alias
                )
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
    
    async def _handle_status_update(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """
        Traite les événements informatifs de statut (activated, blocked, unblocked, etc.)
        Ces événements informent d'un changement de statut, pas d'une demande d'action
        """
        # Vérifier l'idempotence
        if await is_webhook_processed(self.db, webhook_id):
            logger.info(f"Webhook {webhook_id} already processed (idempotent)")
            return {
                "cardId": card_id,
                "event": event,
                "idempotent": True,
                "message": "Webhook already processed"
            }
        
        # Créer ou récupérer la carte
        card = await self.card_repo.get_or_create(card_id, pan_alias)
        if pan_alias and not card.pan_alias:
            card.pan_alias = pan_alias
            await self.db.commit()
            await self.db.refresh(card)
        
        # Extraire le statut de l'événement
        status_map = {
            SkaleetCardEvent.ACTIVATED.value: "ACTIVE",
            SkaleetCardEvent.BLOCKED.value: "BLOCKED",
            SkaleetCardEvent.UNBLOCKED.value: "ACTIVE",
            SkaleetCardEvent.PENDING.value: "PENDING",
            SkaleetCardEvent.EXPIRED.value: "EXPIRED",
            SkaleetCardEvent.OPPOSED.value: "OPPOSED",
            SkaleetCardEvent.REMOVED.value: "REMOVED"
        }
        
        new_status = status_map.get(event, "UNKNOWN")
        
        # Mettre à jour le statut Skaleet
        card.status_skaleet = new_status
        await self.db.commit()
        await self.db.refresh(card)
        
        # Enregistrer l'opération pour traçabilité
        operation = await mark_webhook_started(
            self.db,
            webhook_id,
            card_id,
            "status_update",
            event,
            webhook.id
        )
        operation.raw_webhook = webhook.dict()
        operation.status = OperationStatus.SUCCESS.value
        await self.db.commit()
        
        logger.info(f"Status updated for card {card_id}: {new_status} (event: {event})")
        
        return {
            "cardId": card_id,
            "event": event,
            "status": new_status,
            "message": "Status updated"
        }
    
    async def _handle_card_new(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """
        Traite l'événement card.new (création d'une nouvelle carte)
        """
        # Vérifier l'idempotence
        if await is_webhook_processed(self.db, webhook_id):
            logger.info(f"Webhook {webhook_id} already processed (idempotent)")
            return {
                "cardId": card_id,
                "event": event,
                "idempotent": True,
                "message": "Webhook already processed"
            }
        
        # Créer la carte
        card = await self.card_repo.get_or_create(card_id, pan_alias)
        if pan_alias and not card.pan_alias:
            card.pan_alias = pan_alias
        card.status_skaleet = "PENDING"
        await self.db.commit()
        await self.db.refresh(card)
        
        # Enregistrer l'opération
        operation = await mark_webhook_started(
            self.db,
            webhook_id,
            card_id,
            "card_creation",
            event,
            webhook.id
        )
        operation.raw_webhook = webhook.dict()
        operation.status = OperationStatus.SUCCESS.value
        await self.db.commit()
        
        logger.info(f"New card created: {card_id} (panAlias: {pan_alias})")
        # Inform Skaleet Admin about the card creation (accept)
        try:
            await send_card_operation_result(
                card_id,
                "CARD_CREATION",
                "accept",
                pan_alias=pan_alias
            )
        except Exception as e:
            logger.error(f"Error notifying Skaleet Admin about card creation: {e}", exc_info=True)

        return {
            "cardId": card_id,
            "event": event,
            "status": "PENDING",
            "message": "Card created"
        }
    
    async def _handle_management_operation(
        self,
        webhook: SkaleetWebhook,
        card_id: int,
        pan_alias: str | None,
        webhook_id: str,
        event: str
    ) -> dict:
        """
        Traite les événements card.management_operation.*
        Ces événements informent du résultat d'une opération de gestion
        """
        # Vérifier l'idempotence
        if await is_webhook_processed(self.db, webhook_id):
            logger.info(f"Webhook {webhook_id} already processed (idempotent)")
            return {
                "cardId": card_id,
                "event": event,
                "idempotent": True,
                "message": "Webhook already processed"
            }
        
        # Créer ou récupérer la carte
        card = await self.card_repo.get_or_create(card_id, pan_alias)
        if pan_alias and not card.pan_alias:
            card.pan_alias = pan_alias
            await self.db.commit()
            await self.db.refresh(card)
        
        # Extraire les informations de l'opération
        operation_id = webhook.data.operationId
        operation_type = webhook.data.operationType
        operation_state = webhook.data.operationState
        operation_nature = webhook.data.operationNature
        parameters = webhook.data.parameters or {}
        
        # Déterminer le type d'opération pour CardOperation
        operation_type_mapping = {
            "CARD_CREATION": "card_creation",
            "CARD_SUPPRESSION": "card_suppression",
            "CARD_FEATURES_UPDATE": "card_features_update",
            "CARD_ACTIVATION": "card_activation",
            "CARD_BLOCKING": "card_blocking",
            "CARD_UNBLOCKING": "card_unblocking",
            "CARD_OPPOSITION": "card_opposition"
        }
        
        mapped_operation_type = operation_type_mapping.get(operation_type, operation_type.lower() if operation_type else "unknown")
        
        # Déterminer le statut
        status_map = {
            "ACCEPTED": OperationStatus.SUCCESS.value,
            "REFUSED": OperationStatus.ERROR.value,
            "SETTLED": OperationStatus.SUCCESS.value,
            "ERR_SETTLED": OperationStatus.ERROR.value
        }
        operation_status = status_map.get(operation_state, OperationStatus.PENDING.value) if operation_state else OperationStatus.PENDING.value
        
        # Enregistrer l'opération
        operation = await mark_webhook_started(
            self.db,
            webhook_id,
            card_id,
            mapped_operation_type,
            event,
            webhook.id
        )
        operation.raw_webhook = webhook.dict()
        operation.status = operation_status
        if operation_state:
            operation.ni_result_code = operation_state
        await self.db.commit()
        await self.db.refresh(operation)
        
        # Mettre à jour le statut de la carte si nécessaire
        if operation_state == "ACCEPTED" and operation_type == "CARD_CREATION":
            card.status_skaleet = "ACTIVE"
            await self.db.commit()
        
        logger.info(
            f"Management operation processed: cardId={card_id}, "
            f"operationId={operation_id}, type={operation_type}, state={operation_state}"
        )
        
        return {
            "cardId": card_id,
            "event": event,
            "operationId": operation_id,
            "operationType": operation_type,
            "operationState": operation_state,
            "message": f"Management operation {operation_state}" if operation_state else "Management operation processed"
        }

