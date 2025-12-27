import pytest
from ingestion.sources.coinpaprika import CoinPaprikaSource
from ingestion.sources.csv_source import CSVSource

@pytest.mark.asyncio
async def test_coinpaprika_normalization():
    source = CoinPaprikaSource()
    raw_item = {
        "id": "btc-bitcoin",
        "name": "Bitcoin",
        "symbol": "BTC",
        "rank": 1,
        "quotes": {
            "USD": {
                "price": 50000.0,
                "market_cap": 1000000
            }
        },
        "last_updated": "2023-01-01T12:00:00Z"
    }
    
    normalized = source.normalize(raw_item)
    
    assert normalized["symbol"] == "BTC"
    assert normalized["price_usd"] == 50000.0
    assert normalized["source"] == "coinpaprika"
    assert normalized["external_id"] == "btc-bitcoin"

@pytest.mark.asyncio
async def test_csv_normalization():
    source = CSVSource()
    raw_item = {
        "id": "eth-ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
        "price_usd": "3000.50",
        "last_updated": "2023-01-02T12:00:00Z"
    }
    
    normalized = source.normalize(raw_item)
    
    assert normalized["symbol"] == "ETH"
    assert normalized["price_usd"] == 3000.50
    assert normalized["source"] == "csv"
