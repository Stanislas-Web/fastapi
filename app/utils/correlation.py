import uuid
from fastapi import Request
from typing import Optional
from app.core.logging import correlation_id_var


def generate_correlation_id() -> str:
    """Génère un nouveau correlation_id (UUID)"""
    return str(uuid.uuid4())


def get_or_create_correlation_id(request: Request) -> str:
    """
    Extrait le correlation ID depuis les headers de la requête,
    ou en génère un nouveau si absent
    """
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = request.headers.get("X-Request-ID")
    if not correlation_id:
        correlation_id = request.headers.get("X-Trace-ID")
    
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    return correlation_id


def get_correlation_id(request: Request) -> str:
    """
    Extrait le correlation ID depuis les headers de la requête
    (fonction de compatibilité)
    """
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = request.headers.get("X-Request-ID")
    if not correlation_id:
        correlation_id = request.headers.get("X-Trace-ID")
    
    return correlation_id or "unknown"


def get_correlation_id_from_context() -> Optional[str]:
    """Récupère le correlation_id depuis le contexte"""
    correlation_id = correlation_id_var.get()
    return correlation_id if correlation_id else None

