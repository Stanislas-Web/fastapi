from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from typing import AsyncGenerator

# Convertir postgresql:// en postgresql+asyncpg:// pour SQLAlchemy async
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Créer l'engine async
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    future=True
)

# Créer la session factory async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def init_db():
    """Initialise la base de données (création des tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance FastAPI pour obtenir une session de base de données async
    Usage: async def endpoint(db: AsyncSession = Depends(get_db))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

