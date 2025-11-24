import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.infra.db import Base, get_db


# Base de données de test en mémoire (SQLite async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override de get_db pour les tests"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
def client():
    """Fixture pour créer un client de test FastAPI avec base de données de test"""
    # Créer les tables avant chaque test
    import asyncio
    async def setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(setup())
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    
    # Nettoyer après chaque test
    async def cleanup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    asyncio.run(cleanup())

