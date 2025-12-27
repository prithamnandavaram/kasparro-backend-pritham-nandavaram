from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CoinPaprikaItem(BaseModel):
    id: str
    name: str
    symbol: str
    rank: int
    quotes: dict # Just take the whole quotes dict for now and process inside
    # We could be more specific:
    # price_usd: float = Field(alias="quotes.USD.price")
    # But nested alias in pydantic can be tricky without pre-validators.
    # Let's keep it simple and process in logic.
    last_updated: str

class CSVItem(BaseModel):
    id: str
    symbol: str
    name: str
    price_usd: float
    last_updated: datetime

class CoinGeckoItem(BaseModel):
    id: str
    symbol: str
    name: str
    current_price: float
    last_updated: str

class UnifiedItem(BaseModel):
    symbol: str
    name: str
    price_usd: float
    market_cap_usd: float | None = None
    source: str
    external_id: str
    data_timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    items: list[UnifiedItem]
    total: int
    page: int
    size: int
    request_id: str
    api_latency_ms: float
