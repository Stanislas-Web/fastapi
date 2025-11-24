from enum import Enum


class WebhookEventType(str, Enum):
    CARD_CREATED = "card.created"
    CARD_ACTIVATED = "card.activated"
    CARD_BLOCKED = "card.blocked"
    CARD_UNBLOCKED = "card.unblocked"
    TRANSACTION_AUTHORIZED = "transaction.authorized"
    TRANSACTION_DECLINED = "transaction.declined"


class CardAction(str, Enum):
    CREATE = "create"
    ACTIVATE = "activate"
    BLOCK = "block"
    UNBLOCK = "unblock"
    UPDATE = "update"


class OperationType(str, Enum):
    """Types d'opérations sur les cartes"""
    CARD_ACTIVATION = "card_activation"
    CARD_BLOCKING = "card_blocking"
    CARD_UNBLOCKING = "card_unblocking"
    CARD_OPPOSITION = "card_opposition"


class OperationSource(str, Enum):
    """Sources des opérations"""
    SKA = "SKA"
    NI = "NI"
    INTERNAL = "INTERNAL"


class OperationStatus(str, Enum):
    """Statuts des opérations"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

