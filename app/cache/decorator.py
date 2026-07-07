import functools
from typing import Callable
from app.cache.cache import cache
from app.core.logging import logger


def cached(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache keys matching a pattern"""
    cache_keys = list(cache.cache.keys())
    for key in cache_keys:
        if pattern in key:
            cache.delete(key)
    logger.info(f"Invalidated cache keys matching pattern: {pattern}")
