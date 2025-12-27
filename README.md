# Kasparro Backend & ETL Assignment

## Project Overview
This project implements a production-grade backend system for ingesting, normalizing, and serving cryptocurrency data. It follows a Clean Architecture pattern and includes a robust ETL pipeline, REST API, and comprehensive testing.

## 🚀 Features
- **Multi-Source Ingestion**: CoinPaprika, CoinGecko, and CSV.
- **Robust ETL**: Incremental loading, checkpoints, and idempotency.
- **Observability**: `/stats` endpoint and `/health` checks.
- **Resilience**: Rate limiting, schema drift detection, and failure recovery.
- **Containerized**: Fully Dockerized environment.

## 🛠 Setup & Run

### 1. Prerequisites
- Docker & Docker Compose
- Make (optional, but recommended)
- API Keys (Free tiers):
    - [CoinPaprika API Key](https://coinpaprika.com/api/)
    - [CoinGecko API Key](https://www.coingecko.com/en/api)

### 2. Configuration
The project uses a `.env` file for configuration. A starter file is provided.
**IMPORTANT**: You must update the `.env` file with your actual API keys.

```bash
# Edit .env file
vim .env
```

Contents of `.env`:
```ini
COINPAPRIKA_API_KEY=your_coinpaprika_key_here
COINGECKO_API_KEY=your_coingecko_key_here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/kasparro
```

### 3. Run the System
```bash
make up
```
This will:
1. Build the backend image.
2. Start Postgres and the App.
3. Run migrations automatically (integrated in app startup).
4. **Trigger the ETL pipeline** immediately.

### 4. Verify
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Data Endpoint**: [http://localhost:8000/data](http://localhost:8000/data)
- **Stats Endpoint**: [http://localhost:8000/stats](http://localhost:8000/stats)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run Tests
```bash
make test
```

## 🏗 Architecture
The project follows a modular **Clean Architecture**:
- `api/`: FastAPI routes and entry points.
- `core/`: Configuration, database logic, and SQLAlchemy models.
- `ingestion/`: ETL logic.
    - `pipeline.py`: Main orchestrator (Extraction, Transformation, Loading).
    - `sources/`: Source-specific adapters (CoinPaprika, CoinGecko, CSV).
- `schemas/`: Pydantic models for data validation.
- `tests/`: Pytest suite (Unit + Integration/Scenario tests).

### Key Design Decisions
- **Unified Schema**: All sources map to a single `UnifiedCryptoData` table for easy querying.
- **Incremental Ingestion**: Uses `IngestionCheckpoint` to track timestamps and avoid re-processing.
- **Drift Detection**: The pipeline warns if it detects unexpected fields in API responses (P2 Feature).
- **Failure Injection**: Support for `SIMULATE_FAILURE` env var to test recovery mechanics.

## 📦 Submission Note
This repository follows the naming convention: `kasparro-backend-<firstname>-<lastname>`.
Please ensure you rename the folder/repo accordingly before submitting.
