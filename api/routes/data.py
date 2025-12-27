from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.models import UnifiedCryptoData
from schemas.pydantic_models import PaginatedResponse, UnifiedItem
import time
import uuid

router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_data(
    source: str | None = None,
    symbol: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    query = select(UnifiedCryptoData)
    
    if source:
        query = query.where(UnifiedCryptoData.source == source)
    if symbol:
        query = query.where(UnifiedCryptoData.symbol.ilike(f"%{symbol}%"))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(UnifiedCryptoData.data_timestamp.desc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    latency = (time.time() - start_time) * 1000
    
    return {
        "items": items,
        "total": total or 0,
        "page": page,
        "size": size,
        "request_id": request_id,
        "api_latency_ms": latency
    }
