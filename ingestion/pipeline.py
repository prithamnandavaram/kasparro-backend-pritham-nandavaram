import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.database import AsyncSessionLocal
from core.models import RawCoinPaprika, RawCSV, UnifiedCryptoData, IngestionCheckpoint
from ingestion.sources.coinpaprika import CoinPaprikaSource
from ingestion.sources.csv_source import CSVSource
from ingestion.sources.coingecko import CoinGeckoSource
from schemas.pydantic_models import UnifiedItem

logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self):
        # Configure rate limits (e.g., 0.1s delay between items)
        self.sources = [
            CoinPaprikaSource(rate_limit_delay=0.1),
            CSVSource(), # Local file, no limit needed
            CoinGeckoSource(rate_limit_delay=0.5) # CoinGecko free tier is strict
        ]

    async def run(self):
        """Runs the full ETL pipeline for all sources."""
        logger.info("Starting ETL pipeline...")
        
        async with AsyncSessionLocal() as session:
            for source in self.sources:
                try:
                    await self.process_source(source, session)
                except Exception as e:
                    logger.error(f"Error processing source {source.source_name}: {e}")
                    # In a real system, we might want to alert here.
            
            await session.commit()
        
        logger.info("ETL pipeline finished.")

    async def process_source(self, source, session: AsyncSession):
        logger.info(f"Processing source: {source.source_name}")
        
        # Get last checkpoint
        checkpoint = await session.scalar(
            select(IngestionCheckpoint).where(IngestionCheckpoint.source_name == source.source_name)
        )
        last_ingested = checkpoint.last_ingested_timestamp if checkpoint else None
        new_max_timestamp = last_ingested
        
        # Configure expected keys for drift detection (Example for CoinPaprika)
        expected_keys = set()
        if source.source_name == "coinpaprika":
            expected_keys = {"id", "name", "symbol", "rank", "circulating_supply", "total_supply", "max_supply", "beta_value", "first_data_at", "last_updated", "quotes"}
        
        # Failure Injection Check
        import os
        simulate_failure = os.getenv("SIMULATE_FAILURE", "false").lower() == "true"
        fail_after = 5
        processed_count = 0

        async for raw_item in source.fetch_data():
            processed_count += 1
            
            # Failure Injection
            if simulate_failure and processed_count > fail_after:
                logger.error("SIMULATED FAILURE INJECTED! Crashing pipeline.")
                raise RuntimeError("Simulated ETL Failure")

            # Drift Detection
            if expected_keys:
                drift_keys = source.detect_drift(raw_item, expected_keys)
                if drift_keys:
                    logger.warning(f"SCHEMA DRIFT DETECTED in {source.source_name}: Found new keys {drift_keys}")

            # 2. Normalize first to get timestamp for filtering
            try:
                normalized_dict = source.normalize(raw_item)
                unified_item = UnifiedItem(**normalized_dict)
            except Exception as e:
                logger.warning(f"Validation failed for item from {source.source_name}: {e}")
                continue

            item_timestamp = unified_item.data_timestamp
            
            # Incremental check: Skip if older than checkpoint
            if last_ingested and item_timestamp <= last_ingested:
                continue

            # Update max timestamp seen in this run
            if new_max_timestamp is None or item_timestamp > new_max_timestamp:
                new_max_timestamp = item_timestamp

            # 1. Store Raw Data (Only new ones)
            await self.save_raw_data(source.source_name, raw_item, session)

            # 3. Load Unified Data (Upsert)
            await self.upsert_unified_data(unified_item, session)
            
        # Update checkpoint
        if new_max_timestamp and (last_ingested is None or new_max_timestamp > last_ingested):
            if checkpoint:
                checkpoint.last_ingested_timestamp = new_max_timestamp
            else:
                checkpoint = IngestionCheckpoint(source_name=source.source_name, last_ingested_timestamp=new_max_timestamp)
                session.add(checkpoint)
            logger.info(f"Updated checkpoint for {source.source_name} to {new_max_timestamp}")

    async def save_raw_data(self, source_name: str, data: dict, session: AsyncSession):
        # Dispatch to correct table
        if source_name == "coinpaprika":
            model = RawCoinPaprika
            # We assume 'id' is unique for the source at a point in time, but for raw history we keep inserting?
            # P0.1 says "no reprocessing old data" -> logic usually implies checking if we saw this ID + updated_at before.
            # For simplicity in P0, we just insert. A better approach is to check existence.
            obj = model(
                coin_id=data.get("id"),
                name=data.get("name"),
                symbol=data.get("symbol"),
                rank=data.get("rank"),
                price_usd=data.get("quotes", {}).get("USD", {}).get("price"),
                last_updated_at=None, # Todo parse
                raw_data=data
            )
            session.add(obj)
            
        elif source_name == "csv":
            model = RawCSV
            obj = model(
                external_id=data.get("id"),
                symbol=data.get("symbol"),
                name=data.get("name"),
                price_usd=float(data.get("price_usd")),
                raw_data=data
            )
            session.add(obj)
            
        elif source_name == "coingecko":
            from core.models import RawCoinGecko
            model = RawCoinGecko
            obj = model(
                coin_id=data.get("id"),
                name=data.get("name"),
                symbol=data.get("symbol"),
                current_price=data.get("current_price"),
                last_updated=None, # Todo parse if needed for raw storage specifically or let Pydantic handle validation later
                raw_data=data
            )
            session.add(obj)

    async def upsert_unified_data(self, item: UnifiedItem, session: AsyncSession):
        stmt = pg_insert(UnifiedCryptoData).values(
            symbol=item.symbol,
            name=item.name,
            price_usd=item.price_usd,
            market_cap_usd=item.market_cap_usd,
            source=item.source,
            external_id=item.external_id,
            data_timestamp=item.data_timestamp
        )
        
        # Upsert: Update if (source, external_id, data_timestamp) conflict
        # Actually, P1.2 says "Idempotent writes".
        # If the exact same data point exists, do nothing or update.
        # Since we have a unique constraint on (source, external_id, data_timestamp),
        # we can do ON CONFLICT DO NOTHING (or UPDATE if we expect changes for same timestamp?)
        # Usually same timestamp means same data version.
        
        stmt = stmt.on_conflict_do_update(
            constraint='uq_source_data_point',
            set_={
                "price_usd": item.price_usd,
                "market_cap_usd": item.market_cap_usd,
                "name": item.name
            }
        )
        
        await session.execute(stmt)

async def run_pipeline():
    pipeline = ETLPipeline()
    await pipeline.run()
