"""
API Cache Module

This module provides a simple in-memory cache with TTL support
to optimize LLMPageRank API responses for increased partner traffic.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Tuple, List, Callable

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APICache:
    """Simple in-memory cache with TTL support for API responses."""
    
    def __init__(self):
        """Initialize the cache."""
        self.cache = {}
        self.ttls = {}
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.start_cleanup_thread()
        logger.info("API cache initialized")
    
    def start_cleanup_thread(self):
        """Start the cleanup thread to remove expired entries."""
        if self.cleanup_thread is not None and self.cleanup_thread.is_alive():
            return
        
        def cleanup_loop():
            """Cleanup loop to remove expired entries."""
            while True:
                self.cleanup()
                time.sleep(60)  # Run cleanup every minute
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Cache cleanup thread started")
    
    def cleanup(self):
        """Remove expired entries from the cache."""
        now = time.time()
        expired_keys = []
        
        with self.lock:
            for key, expiry in self.ttls.items():
                if expiry <= now:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.cache.pop(key, None)
                self.ttls.pop(key, None)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set a cache entry with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        with self.lock:
            self.cache[key] = value
            self.ttls[key] = time.time() + ttl
    
    def get(self, key: str) -> Tuple[bool, Any]:
        """
        Get a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Tuple of (hit, value) where hit is a boolean indicating cache hit and value is the cached value
        """
        with self.lock:
            now = time.time()
            
            if key in self.cache and self.ttls.get(key, 0) > now:
                return True, self.cache[key]
            
            # Remove expired entry if it exists
            if key in self.cache and self.ttls.get(key, 0) <= now:
                self.cache.pop(key, None)
                self.ttls.pop(key, None)
            
            return False, None
    
    def delete(self, key: str):
        """
        Delete a cache entry.
        
        Args:
            key: Cache key
        """
        with self.lock:
            self.cache.pop(key, None)
            self.ttls.pop(key, None)
    
    def clear(self):
        """Clear the entire cache."""
        with self.lock:
            self.cache.clear()
            self.ttls.clear()
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            now = time.time()
            expired = sum(1 for ttl in self.ttls.values() if ttl <= now)
            valid = len(self.ttls) - expired
            
            return {
                "size": len(self.cache),
                "valid_entries": valid,
                "expired_entries": expired,
                "cleanup_thread_active": self.cleanup_thread is not None and self.cleanup_thread.is_alive()
            }


# Singleton instance
_instance = None

def get_cache() -> APICache:
    """
    Get the cache singleton instance.
    
    Returns:
        Cache instance
    """
    global _instance
    
    if _instance is None:
        _instance = APICache()
    
    return _instance


def cached(ttl: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cache = get_cache()
            hit, value = cache.get(cache_key)
            
            if hit:
                logger.debug(f"Cache hit for {cache_key}")
                return value
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key} with TTL {ttl}s")
            
            return result
        return wrapper
    return decorator