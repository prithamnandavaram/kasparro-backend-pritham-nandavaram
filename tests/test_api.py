import pytest
from unittest.mock import MagicMock, AsyncMock
from core.database import get_db

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

@pytest.mark.asyncio
async def test_get_data_empty(async_client):
    # Mocking DB dependency would be ideal here to avoid needing a real DB
    # For now, if we run this without a DB, it depends on how get_db is handled.
    # We'll assume the fixture environment handles it or we accept failure if DB not up.
    # But strictly for "Minimal Test Suite" P0.4, unit tests of logic are safest.
    
    # Overriding dependency for this test
    async def mock_get_db():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result
        mock_session.scalar.return_value = 0
        yield mock_session

    app = async_client._transport.app
    app.dependency_overrides[get_db] = mock_get_db
    
    response = await async_client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    
    app.dependency_overrides = {}
