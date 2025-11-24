from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infra.repositories import WebhookRepository, CardOperationRepository, CardRepository
from app.domain.models import CardOperation, Card
from app.domain.enums import OperationSource, OperationStatus
from typing import Optional
import uuid


async def check_idempotency(event_id: str, correlation_id: str, db: AsyncSession) -> bool:
    """
    Vérifie si un événement a déjà été traité (idempotence)
    Retourne True si l'événement peut être traité, False s'il a déjà été traité
    """
    repo = WebhookRepository(db)
    event = await repo.get_event(event_id)
    
    if event and event.processed:
        return False
    
    return True


async def check_card_operation_idempotency(
    webhook_id: str,
    operation_type: str,
    db: AsyncSession
) -> bool:
    """
    Vérifie si une opération carte a déjà été traitée pour ce webhookId
    Retourne True si l'opération peut être traitée, False si elle a déjà été traitée
    """
    repo = CardOperationRepository(db)
    operation = await repo.get_by_webhook_id(webhook_id, operation_type)
    
    if operation:
        # Si l'opération existe déjà, elle a déjà été traitée
        return False
    
    return True


async def is_webhook_processed(session: AsyncSession, webhook_id: str) -> bool:
    """
    Vérifie si un webhookId a déjà été traité (SUCCESS, ERROR ou PENDING)
    Retourne True si le webhook a déjà été traité, False sinon
    """
    result = await session.execute(
        select(CardOperation).where(
            CardOperation.skaleet_webhook_id == webhook_id
        )
    )
    operation = result.scalar_one_or_none()
    
    if operation:
        # Si une opération existe avec ce webhookId, elle a déjà été traitée (ou en cours)
        return True
    
    return False


async def mark_webhook_started(
    session: AsyncSession,
    webhook_id: str,
    card_id: int,
    operation_type: str,
    skaleet_event: str,
    skaleet_event_id: str
) -> CardOperation:
    """
    Crée une entrée CardOperation avec status = PENDING
    Retourne l'opération créée
    """
    # Récupérer ou créer la carte
    card_repo = CardRepository(session)
    card = await card_repo.get_or_create(card_id)
    
    # Créer l'opération
    operation = CardOperation(
        card_id=card.id,
        operation_type=operation_type,
        source=OperationSource.SKA.value,
        status=OperationStatus.PENDING.value,
        skaleet_event=skaleet_event,
        skaleet_event_id=skaleet_event_id,
        skaleet_webhook_id=webhook_id
    )
    
    session.add(operation)
    await session.commit()
    await session.refresh(operation)
    
    return operation


async def mark_webhook_finished(
    session: AsyncSession,
    card_operation_id: uuid.UUID,
    status: str,
    ni_result_code: str | None = None
):
    """
    Met à jour le statut d'une opération
    """
    result = await session.execute(
        select(CardOperation).where(CardOperation.id == card_operation_id)
    )
    operation = result.scalar_one_or_none()
    
    if operation:
        operation.status = status
        if ni_result_code:
            operation.ni_result_code = ni_result_code
        await session.commit()
        await session.refresh(operation)
    
    return operation

