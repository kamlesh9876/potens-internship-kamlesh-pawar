import time
from typing import Optional, Any
from app.core.logging import logger


class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self.ttls = {}
        self.default_ttl = 300  # 5 minutes default
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        ttl = self.ttls.get(key, self.default_ttl)
        if key in self.timestamps:
            if time.time() - self.timestamps[key] > ttl:
                self.delete(key)
                return None
        
        logger.debug(f"Cache hit for key: {key}")
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
        self.ttls[key] = ttl if ttl else self.default_ttl
        logger.debug(f"Cache set for key: {key}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        self.ttls.pop(key, None)
        logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.ttls.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "total_keys": len(self.cache),
            "keys": list(self.cache.keys())
        }


# Global cache instance
cache = SimpleCache()
