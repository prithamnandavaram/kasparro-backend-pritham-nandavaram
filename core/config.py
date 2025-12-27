from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kasparro Backend"
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str
    
    # API Keys
    COINPAPRIKA_API_KEY: str | None = None
    COINGECKO_API_KEY: str | None = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
