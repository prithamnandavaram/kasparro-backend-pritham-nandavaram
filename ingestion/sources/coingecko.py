import httpx
from datetime import datetime
from ingestion.sources.base import BaseSource

from core.config import get_settings

class CoinGeckoSource(BaseSource):
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    @property
    def source_name(self) -> str:
        return "coingecko"

    async def fetch_data(self):
        headers = {}
        settings = get_settings()
        key = settings.COINGECKO_API_KEY
        
        # Only attach header if key is valid and not a placeholder
        if key and not key.startswith("your_") and not key.startswith("replace_"):
            # CoinGecko Demo API header
            headers["x-cg-demo-api-key"] = key
            
        async with httpx.AsyncClient(headers=headers) as client:
            # CoinGecko /coins/markets endpoint is good for a list
            # vs_currency=usd
            # Reference: https://www.coingecko.com/en/api/documentation
            try:
                response = await client.get(
                    f"{self.BASE_URL}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": 50,
                        "page": 1,
                        "sparkline": "false"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                for item in data:
                    yield item
                    if self.rate_limit_delay > 0:
                        import asyncio
                        await asyncio.sleep(self.rate_limit_delay)
            except Exception as e:
                # Basic error handling - yield nothing if fails, pipeline will log.
                # In production we might want to re-raise or log specifically here.
                # For now, let the pipeline catch general errors or just stop this source.
                print(f"Error fetching CoinGecko data: {e}") 
                pass

    def normalize(self, raw_item: dict) -> dict:
        # CoinGecko structure (partial):
        # {
        #   "id": "bitcoin",
        #   "symbol": "btc",
        #   "name": "Bitcoin",
        #   "current_price": 50000.0,
        #   "market_cap": 10000000,
        #   "last_updated": "2024-01-01T00:00:00.000Z"
        # }
        
        return {
            "symbol": raw_item.get("symbol", "").upper(), # Normalize to uppercase
            "name": raw_item.get("name"),
            "price_usd": float(raw_item.get("current_price", 0) or 0),
            "market_cap_usd": float(raw_item.get("market_cap", 0) or 0),
            "source": self.source_name,
            "external_id": raw_item.get("id"),
            # CoinGecko uses ISO 8601 with Z usually
            "data_timestamp": datetime.fromisoformat(raw_item.get("last_updated").replace("Z", "+00:00"))
        }
