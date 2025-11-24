from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.infra.db import Base
from datetime import datetime
import uuid


class Card(Base):
    """Modèle représentant une carte dans le système"""
    __tablename__ = "cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skaleet_card_id = Column(Integer, nullable=False, index=True)
    pan_alias = Column(String, unique=True, nullable=True)
    ni_card_ref = Column(String, nullable=True)
    status_skaleet = Column(String, nullable=False)
    status_ni = Column(String, nullable=True)
    product_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relation avec les opérations
    operations = relationship("CardOperation", back_populates="card", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_skaleet_card_id', 'skaleet_card_id'),
    )


class CardOperation(Base):
    """Modèle représentant une opération sur une carte"""
    __tablename__ = "card_operations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    operation_type = Column(String, nullable=False)
    source = Column(String, nullable=False)  # SKA, NI, INTERNAL
    status = Column(String, nullable=False)  # PENDING, SUCCESS, ERROR
    skaleet_event = Column(String, nullable=True)
    skaleet_event_id = Column(String, nullable=True)
    skaleet_webhook_id = Column(String, nullable=True)
    ni_result_code = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True, index=True)
    raw_webhook = Column(JSON, nullable=True)  # PostgreSQL supporte JSON nativement
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relation avec la carte
    card = relationship("Card", back_populates="operations")
    
    __table_args__ = (
        Index('idx_card_id', 'card_id'),
        Index('idx_correlation_id', 'correlation_id'),
        Index('idx_created_at', 'created_at'),
    )


class WebhookEvent(Base):
    """Modèle pour l'historique des webhooks reçus"""
    __tablename__ = "webhook_events"
    
    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    correlation_id = Column(String, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    payload = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)

