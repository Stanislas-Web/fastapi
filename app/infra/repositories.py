from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.models import WebhookEvent, Card, CardOperation
from app.schemas.webhook import WebhookRequest
from datetime import datetime
from typing import Optional


class WebhookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_event(self, webhook_data: WebhookRequest, correlation_id: str) -> WebhookEvent:
        event = WebhookEvent(
            id=webhook_data.id,
            event_type=webhook_data.event_type,
            correlation_id=correlation_id,
            payload=webhook_data.data,
            processed=False
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event
    
    async def get_event(self, event_id: str) -> Optional[WebhookEvent]:
        result = await self.db.execute(
            select(WebhookEvent).where(WebhookEvent.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def mark_as_processed(self, event_id: str, response: dict):
        event = await self.get_event(event_id)
        if event:
            event.processed = True
            event.processed_at = datetime.utcnow()
            event.response = response
            await self.db.commit()


class CardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_skaleet_id(self, skaleet_card_id: int) -> Optional[Card]:
        """Récupère une carte par son ID Skaleet"""
        result = await self.db.execute(
            select(Card).where(Card.skaleet_card_id == skaleet_card_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, skaleet_card_id: int, pan_alias: Optional[str] = None) -> Card:
        """Crée une nouvelle carte"""
        card = Card(
            skaleet_card_id=skaleet_card_id,
            pan_alias=pan_alias,
            status_skaleet="PENDING",
            status_ni=None
        )
        self.db.add(card)
        await self.db.commit()
        await self.db.refresh(card)
        return card
    
    async def get_or_create(self, skaleet_card_id: int, pan_alias: Optional[str] = None) -> Card:
        """Récupère une carte ou la crée si elle n'existe pas"""
        card = await self.get_by_skaleet_id(skaleet_card_id)
        if not card:
            card = await self.create(skaleet_card_id, pan_alias)
        return card
    
    async def update_status_ni(self, card_id, status_ni: str):
        """Met à jour le statut NI d'une carte"""
        result = await self.db.execute(
            select(Card).where(Card.id == card_id)
        )
        card = result.scalar_one_or_none()
        if card:
            card.status_ni = status_ni
            await self.db.commit()
            await self.db.refresh(card)
        return card


class CardOperationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        card_id,
        operation_type: str,
        source: str,
        status: str,
        skaleet_event: Optional[str] = None,
        skaleet_webhook_id: Optional[str] = None,
        raw_webhook: Optional[dict] = None
    ) -> CardOperation:
        """Crée une nouvelle opération carte"""
        operation = CardOperation(
            card_id=card_id,
            operation_type=operation_type,
            source=source,
            status=status,
            skaleet_event=skaleet_event,
            skaleet_webhook_id=skaleet_webhook_id,
            raw_webhook=raw_webhook
        )
        self.db.add(operation)
        await self.db.commit()
        await self.db.refresh(operation)
        return operation
    
    async def update_status(self, operation_id, status: str, ni_result_code: Optional[str] = None):
        """Met à jour le statut d'une opération"""
        result = await self.db.execute(
            select(CardOperation).where(CardOperation.id == operation_id)
        )
        operation = result.scalar_one_or_none()
        if operation:
            operation.status = status
            if ni_result_code:
                operation.ni_result_code = ni_result_code
            await self.db.commit()
            await self.db.refresh(operation)
        return operation
    
    async def get_by_webhook_id(self, webhook_id: str, operation_type: str) -> Optional[CardOperation]:
        """Récupère une opération par webhookId et operation_type"""
        result = await self.db.execute(
            select(CardOperation).where(
                CardOperation.skaleet_webhook_id == webhook_id,
                CardOperation.operation_type == operation_type
            )
        )
        return result.scalar_one_or_none()

