from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from core.database import get_db
from core.models import UnifiedCryptoData, IngestionCheckpoint

router = APIRouter()

@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Exposes ETL summaries:
    - Records processed (Total in Unified)
    - Last success timestamps per source
    - Run metadata (basic)
    """
    
    # Total records processed
    total_records = await db.scalar(select(func.count()).select_from(UnifiedCryptoData))
    
    # Checkpoints (Last Success)
    checkpoints = await db.execute(select(IngestionCheckpoint))
    checkpoint_data = {
        cp.source_name: cp.last_ingested_timestamp 
        for cp in checkpoints.scalars().all()
    }
    
    # Last Updates per source (Run comparison / anomaly detection foundation)
    last_updates_query = select(
        UnifiedCryptoData.source, 
        func.max(UnifiedCryptoData.ingested_at).label("last_run_at"),
        func.count(UnifiedCryptoData.id).label("count")
    ).group_by(UnifiedCryptoData.source)
    
    last_updates_res = await db.execute(last_updates_query)
    source_stats = {
        row.source: {"last_run": row.last_run_at, "total_records": row.count}
        for row in last_updates_res.all()
    }

    return {
        "summary": {
            "total_records_processed": total_records or 0,
            "status": "healthy"
        },
        "last_ingestion_checkpoints": checkpoint_data,
        "source_breakdown": source_stats
    }
