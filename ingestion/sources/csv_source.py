import pandas as pd
from datetime import datetime
from ingestion.sources.base import BaseSource
import os

class CSVSource(BaseSource):
    FILE_PATH = "data/sample_coins.csv"
    
    @property
    def source_name(self) -> str:
        return "csv"

    async def fetch_data(self):
        if not os.path.exists(self.FILE_PATH):
            return
            
        # Read CSV using pandas for convenience
        df = pd.read_csv(self.FILE_PATH)
        
        # Convert to records
        records = df.to_dict(orient="records")
        
        for item in records:
            yield item

    def normalize(self, raw_item: dict) -> dict:
        # CSV structure: id,symbol,name,price_usd,last_updated
        
        return {
            "symbol": raw_item.get("symbol"),
            "name": raw_item.get("name"),
            "price_usd": float(raw_item.get("price_usd")),
            "market_cap_usd": None, # CSV doesn't have it
            "source": self.source_name,
            "external_id": raw_item.get("id"),
            "data_timestamp": datetime.fromisoformat(raw_item.get("last_updated").replace("Z", "+00:00"))
        }
