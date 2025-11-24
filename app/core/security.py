import hmac
import hashlib
from typing import Optional, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.utils.correlation import get_or_create_correlation_id
from app.core.logging import correlation_id_var


def verify_webhook_signature(payload: bytes, signature: str, secret: Optional[str] = None) -> bool:
    if not secret:
        secret = settings.webhook_secret
    
    if not secret:
        return False
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware pour gérer le correlation_id dans les requêtes"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extraire ou générer le correlation_id
        correlation_id = get_or_create_correlation_id(request)
        
        # Attacher au state de la requête
        request.state.correlation_id = correlation_id
        
        # Définir dans le contexte pour les logs
        correlation_id_var.set(correlation_id)
        
        # Ajouter le correlation_id dans les headers de réponse
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response

