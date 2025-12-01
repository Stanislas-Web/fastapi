from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.v1 import card_webhooks, health
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security import CorrelationIdMiddleware
from app.infra.db import init_db
import logging

# Configuration du logging
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup: initialiser la base de données
    try:
        await init_db()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️ Impossible d'initialiser la base de données: {e}")
        logger.warning("Le service démarre quand même, mais certaines fonctionnalités peuvent ne pas fonctionner")
    yield
    # Shutdown: nettoyage si nécessaire


app = FastAPI(
    title="Card Connector",
    description="Microservice pour intégrer Skaleet avec processor Visa (NI)",
    version="1.0.0",
    lifespan=lifespan
)

# Ajouter le middleware pour correlation_id
app.add_middleware(CorrelationIdMiddleware)


# Exception handler personnalisé pour les erreurs de validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Log détaillé des erreurs de validation (422)
    """
    # Récupérer le body brut pour debug
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
    except:
        body_str = "<unable to decode body>"
    
    # Logger l'erreur avec tous les détails
    logger.error(
        f"❌ Validation Error 422 - URL: {request.url.path} | "
        f"Method: {request.method} | "
        f"Client: {request.client.host if request.client else 'unknown'} | "
        f"Body: {body_str[:500]} | "
        f"Errors: {exc.errors()}"
    )
    
    # Retourner la réponse 422 standard
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


# Inclusion des routes
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(card_webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

