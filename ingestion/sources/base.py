from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any

class BaseSource(ABC):
    def __init__(self, rate_limit_delay: float = 0.0):
        self.rate_limit_delay = rate_limit_delay

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    async def fetch_data(self) -> AsyncGenerator[Any, None]:
        """Yields raw data items from the source."""
        pass
    
    @abstractmethod
    def normalize(self, raw_item: Any) -> dict:
        """Converts raw item to a dict matching UnifiedItem schema."""
        pass
        
    def detect_drift(self, raw_item: dict, expected_keys: set) -> list[str]:
        """Returns list of unexpected keys found in raw_item."""
        current_keys = set(raw_item.keys())
        # We only care about root level drift for P2 differentiation
        new_keys = current_keys - expected_keys
        if new_keys:
            return list(new_keys)
        return []
