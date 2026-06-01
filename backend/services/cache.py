try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    import unittest.mock as mock
    redis = mock.MagicMock()
    REDIS_AVAILABLE = False
import json
import logging
from typing import Optional, Any
from backend.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class CacheService:
    """Redis-based caching service."""
    
    def __init__(self):
        self.enabled = settings.redis_enabled and REDIS_AVAILABLE
        self.client: Optional[redis.Redis] = None
        
        if self.enabled:
            try:
                self.client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                self.client.ping()
                logger.info("✅ Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"⚠️  Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL."""
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.setex(
                key, 
                ttl, 
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache."""
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if not self.enabled or not self.client:
            return
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")


# Global cache instance
cache = CacheService()


def cached(key_prefix: str, ttl: int = 60):
    """Decorator for caching function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator