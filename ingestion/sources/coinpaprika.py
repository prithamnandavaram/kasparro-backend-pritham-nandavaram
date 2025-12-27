import httpx
from datetime import datetime
from ingestion.sources.base import BaseSource
from core.config import get_settings

class CoinPaprikaSource(BaseSource):
    BASE_URL = "https://api.coinpaprika.com/v1"
    
    @property
    def source_name(self) -> str:
        return "coinpaprika"

    async def fetch_data(self):
        headers = {}
        settings = get_settings()
        key = settings.COINPAPRIKA_API_KEY
        
        # Only attach header if key is valid and not a placeholder
        if key and not key.startswith("your_") and not key.startswith("replace_"):
            headers["Authorization"] = key

        async with httpx.AsyncClient(headers=headers) as client:
            # Fetch tickers for top 50 to keep it manageable
            # Note: API might be rate limited.
            response = await client.get(f"{self.BASE_URL}/tickers?limit=50")
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                yield item
                if self.rate_limit_delay > 0:
                    import asyncio
                    await asyncio.sleep(self.rate_limit_delay)

    def normalize(self, raw_item: dict) -> dict:
        # CoinPaprika structure:
        # {
        #   "id": "btc-bitcoin",
        #   "name": "Bitcoin",
        #   "symbol": "BTC",
        #   "rank": 1,
        #   "quotes": {
        #       "USD": {
        #           "price": 38000.0,
        #           "market_cap": 700000000000
        #       }
        #   },
        #   "last_updated": "2024-01-01T00:00:00Z"
        # }
        
        # Safe extraction
        quotes = raw_item.get("quotes", {}).get("USD", {})
        
        return {
            "symbol": raw_item.get("symbol"),
            "name": raw_item.get("name"),
            "price_usd": quotes.get("price"),
            "market_cap_usd": quotes.get("market_cap"),
            "source": self.source_name,
            "external_id": raw_item.get("id"),
            "data_timestamp": datetime.fromisoformat(raw_item.get("last_updated").replace("Z", "+00:00"))
        }
