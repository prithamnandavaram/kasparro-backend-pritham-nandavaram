import pytest
from core.models import UnifiedCryptoData, IngestionCheckpoint
from ingestion.sources.base import BaseSource
from ingestion.pipeline import ETLPipeline
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from typing import Any

class MockSource(BaseSource):
    def __init__(self, name="csv", items=None):
        self._name = name
        self.items = items or []

    @property
    def source_name(self) -> str:
        return self._name

    async def fetch_data(self):
        for item in self.items:
            yield item

    def normalize(self, raw_item: Any) -> dict:
        return raw_item

# Test logic for P2.2 Failure Injection
# We will iterate a MockSource that yields enough items to trigger failure
# Then run again without failure to see if it resumes.

# Needs env var mocking.
import os
from unittest.mock import patch

@pytest.mark.asyncio
async def test_failure_injection_recovery():
    pipeline = ETLPipeline()
    # AsyncSession.add is synchronous, execute/commit/scalar are async
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.scalar = AsyncMock()
    mock_session.scalar.return_value = None # No checkpoint initially
    
    # 10 items
    items = [{"symbol": f"S{i}", "name": f"N{i}", "price_usd": 1.0, "source": "mock", "external_id": str(i), "data_timestamp": datetime.now()} for i in range(10)]
    source = MockSource(items=items)
    
    # Mock source detection in pipeline (since we hardcoded 'coinpaprika' for keys)
    # We can just test the logic block directly or subclass properly.
    # For unit test simplicity, let's verify the Environment Variable triggers the raise.
    
    with patch.dict(os.environ, {"SIMULATE_FAILURE": "true"}):
        # We need to re-instantiate or re-read env inside the method if it was cached?
        # Our implementation reads os.getenv inside the method loop, so patch should work.
        
        with pytest.raises(RuntimeError, match="Simulated ETL Failure"):
           await pipeline.process_source(source, mock_session)
           
    # Verify processed count before failure (should be around 6 items: > 5)
    # calls to add/execute should reflect partial progress.
    assert mock_session.add.call_count >= 5

@pytest.mark.asyncio
async def test_drift_detection():
    # Test P2.1
    from ingestion.sources.coinpaprika import CoinPaprikaSource
    source = CoinPaprikaSource()
    
    expected = {"a", "b"}
    
    # Case 1: No drift
    assert source.detect_drift({"a": 1, "b": 2}, expected) == []
    
    # Case 2: Drift
    drift = source.detect_drift({"a": 1, "b": 2, "c": 3}, expected)
    assert "c" in drift
