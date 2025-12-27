import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from core.database import get_db, Base, engine
from core.models import UnifiedCryptoData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

# Use sqlite for testing or just mock? 
# Using a separate test DB is better. 
# For P0 simplicity, let's use an in-memory SQLite for unit tests if possible, 
# or just mock the DB session for API tests.
# But ETL tests need DB interaction or mocking.

# Let's mock the session for API tests for speed and isolation.
@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
