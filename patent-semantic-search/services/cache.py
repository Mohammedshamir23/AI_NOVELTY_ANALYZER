"""
Service response cache module for API queries and heavy computational results.
"""

import os
import json
import time
from typing import Any, Optional, Dict

class ServiceCache:
    """
    Simple in-memory and disk-persistent JSON cache.
    """
    def __init__(self, cache_file: str = "data/service_cache.json", ttl_seconds: int = 86400):
        self.cache_file = cache_file
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.cache_file)), exist_ok=True)
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"[ServiceCache] Failed to save cache: {e}")

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry.get('timestamp', 0) < self.ttl_seconds:
                return entry.get('data')
        return None

    def set(self, key: str, data: Any):
        self.cache[key] = {
            'timestamp': time.time(),
            'data': data
        }
        self._save_cache()
