from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import card_webhooks, health
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security import CorrelationIdMiddleware
from app.infra.db import init_db

# Configuration du logging
setup_logging()


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

# Inclusion des routes
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(card_webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

