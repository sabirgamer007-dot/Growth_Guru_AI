import hashlib
import json
from typing import Optional, Dict, Any

class ValidationCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def generate_fingerprint(self, business_type: str, headers: list, sample_json: str, row_count: int) -> str:
        """
        Generates a SHA256 cryptographic fingerprint for the dataset context.
        Ensures 100% identical datasets completely bypass Groq.
        """
        payload = {
            "business_type": business_type,
            "headers": sorted([str(h).lower() for h in headers]),
            "row_count": row_count,
            "sample": sample_json
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def get(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(fingerprint)

    def set(self, fingerprint: str, result: Dict[str, Any]) -> None:
        self._cache[fingerprint] = result

# Global instance
validation_cache = ValidationCache()
