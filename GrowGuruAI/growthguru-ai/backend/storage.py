"""
GrowthGuru AI — Storage Abstraction
=====================================
A simple memory-based storage for the hackathon.
In a real production app, this would use Redis, PostgreSQL, or S3.
"""

import time
import pandas as pd
from typing import Dict, Any, Tuple, Optional

class MemoryStorageProvider:
    def __init__(self):
        # Maps file_id -> (DataFrame, timestamp)
        self._data: Dict[str, Tuple[pd.DataFrame, float]] = {}
        # Maps file_id -> (ContextDict, timestamp)
        self._context_data: Dict[str, Tuple[Dict[str, Any], float]] = {}

    def save(self, file_id: str, df: pd.DataFrame) -> None:
        """Stores a dataframe in memory."""
        self._data[file_id] = (df, time.time())

    def get(self, file_id: str) -> Optional[pd.DataFrame]:
        """Retrieves a dataframe if it exists and hasn't expired."""
        record = self._data.get(file_id)
        if not record:
            return None
        return record[0]
        
    def save_context(self, file_id: str, context: Dict[str, Any]) -> None:
        self._context_data[file_id] = (context, time.time())
        
    def get_context(self, file_id: str) -> Optional[Dict[str, Any]]:
        record = self._context_data.get(file_id)
        if not record:
            return None
        return record[0]

# Global singleton
storage = MemoryStorageProvider()
