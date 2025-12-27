from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()

@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "unhealthy"
    etl_status = "unknown"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
        
        # Check last ETL run
        from core.models import IngestionCheckpoint
        from sqlalchemy import select, func
        last_cp = await db.scalar(select(func.max(IngestionCheckpoint.last_ingested_timestamp)))
        if last_cp:
            etl_status = f"last_run_at_{last_cp.isoformat()}"
        else:
            etl_status = "no_runs_yet"
            
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "online",
        "database": db_status,
        "etl_last_run": etl_status
    }
