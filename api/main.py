from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from core.config import get_settings
from api.routes import health, data
from ingestion.pipeline import run_pipeline
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run migrations (optional, or rely on manual step)
    # Ideally we should run migrations here if we want "fully automated"
    # But for safety, let's assume valid DB or run a subprocess.
    # We'll just start the ETL background task.
    
    logger.info("Application starting up...")
    
    # Run ETL once on startup for the assignment requirements
    # Logic to run it specifically as a background task
    asyncio.create_task(run_startup_task())
    
    yield
    
    logger.info("Application shutting down...")

async def run_startup_task():
    """Runs initial ETL and keeps running it periodically if needed."""
    logger.info("Running initial ETL job...")
    try:
        await run_pipeline()
    except Exception as e:
        logger.error(f"ETL Job failed: {e}")

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(data.router, prefix="/data", tags=["data"])
from api.routes import stats
app.include_router(stats.router, prefix="/stats", tags=["stats"])

@app.get("/")
async def root():
    return {"message": "Welcome to Kasparro Backend Assignment"}
