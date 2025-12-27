from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from core.database import Base

class RawCoinPaprika(Base):
    __tablename__ = "raw_coinpaprika"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    name = Column(String)
    symbol = Column(String)
    rank = Column(Integer)
    price_usd = Column(Float)
    last_updated_at = Column(DateTime(timezone=True))
    raw_data = Column(JSON) # Store full raw response
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class RawCSV(Base):
    __tablename__ = "raw_csv"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True) # ID from CSV
    symbol = Column(String)
    name = Column(String)
    price_usd = Column(Float)
    last_updated_at = Column(DateTime(timezone=True))
    raw_data = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class RawCoinGecko(Base):
    __tablename__ = "raw_coingecko"

    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String, index=True)
    symbol = Column(String)
    name = Column(String)
    current_price = Column(Float)
    last_updated = Column(DateTime(timezone=True))
    raw_data = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class UnifiedCryptoData(Base):
    __tablename__ = "unified_crypto_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True) # Normalized symbol (e.g., BTC)
    name = Column(String)
    price_usd = Column(Float)
    market_cap_usd = Column(Float, nullable=True) # Optional extra
    source = Column(String, index=True) # coinpaprika, csv, coingecko
    external_id = Column(String) # Original ID from source
    
    # Metadata
    data_timestamp = Column(DateTime(timezone=True)) # When the data was valid
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints to avoid duplicates from same source at same time (idempotency helper)
    __table_args__ = (
        UniqueConstraint('source', 'external_id', 'data_timestamp', name='uq_source_data_point'),
    )

class IngestionCheckpoint(Base):
    __tablename__ = "ingestion_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True) # coinpaprika, csv, etc.
    last_ingested_timestamp = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
