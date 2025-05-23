"""
API Rate Limiter Module

This module provides enhanced rate limiting functionality for
the LLMPageRank API to handle increased partner traffic efficiently.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, Tuple, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API endpoints with tiered limits and burst handling."""
    
    def __init__(self):
        """Initialize the rate limiter."""
        # API key -> {timestamp -> request_count}
        self.daily_request_counts = {}
        self.minute_request_counts = {}
        self.lock = threading.RLock()
        
        # Start cleanup thread
        self.start_cleanup_thread()
        logger.info("Rate limiter initialized")
    
    def start_cleanup_thread(self):
        """Start a thread to clean up expired rate limit entries."""
        def cleanup_loop():
            """Cleanup loop to remove expired entries."""
            while True:
                self.cleanup()
                time.sleep(60)  # Run cleanup every minute
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("Rate limiter cleanup thread started")
    
    def cleanup(self):
        """Clean up expired rate limit entries."""
        now = time.time()
        day_seconds = 24 * 60 * 60
        minute_seconds = 60
        
        with self.lock:
            # Clean up daily counts
            for api_key in list(self.daily_request_counts.keys()):
                for timestamp in list(self.daily_request_counts[api_key].keys()):
                    if now - timestamp > day_seconds:
                        del self.daily_request_counts[api_key][timestamp]
                
                # Remove empty entries
                if not self.daily_request_counts[api_key]:
                    del self.daily_request_counts[api_key]
            
            # Clean up minute counts
            for api_key in list(self.minute_request_counts.keys()):
                for timestamp in list(self.minute_request_counts[api_key].keys()):
                    if now - timestamp > minute_seconds:
                        del self.minute_request_counts[api_key][timestamp]
                
                # Remove empty entries
                if not self.minute_request_counts[api_key]:
                    del self.minute_request_counts[api_key]
    
    def check_rate_limit(self, api_key: str, daily_limit: int, minute_limit: int = 20) -> Tuple[bool, Dict]:
        """
        Check if a request from a specific API key is within rate limits.
        
        Args:
            api_key: API key
            daily_limit: Daily request limit
            minute_limit: Per-minute request limit
            
        Returns:
            Tuple of (allowed, limits) where allowed is a boolean and limits is a dictionary with rate limit information
        """
        with self.lock:
            # Initialize if needed
            if api_key not in self.daily_request_counts:
                self.daily_request_counts[api_key] = {}
            
            if api_key not in self.minute_request_counts:
                self.minute_request_counts[api_key] = {}
            
            # Get current timestamps
            now = time.time()
            today_timestamp = int(now / (24 * 60 * 60)) * (24 * 60 * 60)  # Start of day
            minute_timestamp = int(now / 60) * 60  # Start of minute
            
            # Calculate daily count
            daily_count = sum(self.daily_request_counts[api_key].values())
            
            # Calculate minute count
            minute_count = 0
            if minute_timestamp in self.minute_request_counts[api_key]:
                minute_count = self.minute_request_counts[api_key][minute_timestamp]
            
            # Check limits
            if daily_count >= daily_limit:
                return False, {
                    "allowed": False,
                    "reason": "daily_limit_exceeded",
                    "daily_limit": daily_limit,
                    "daily_count": daily_count,
                    "reset_at": today_timestamp + (24 * 60 * 60)
                }
            
            if minute_count >= minute_limit:
                return False, {
                    "allowed": False,
                    "reason": "minute_limit_exceeded",
                    "minute_limit": minute_limit,
                    "minute_count": minute_count,
                    "reset_at": minute_timestamp + 60
                }
            
            # Increment counters
            if today_timestamp not in self.daily_request_counts[api_key]:
                self.daily_request_counts[api_key][today_timestamp] = 0
            self.daily_request_counts[api_key][today_timestamp] += 1
            
            if minute_timestamp not in self.minute_request_counts[api_key]:
                self.minute_request_counts[api_key][minute_timestamp] = 0
            self.minute_request_counts[api_key][minute_timestamp] += 1
            
            return True, {
                "allowed": True,
                "daily_limit": daily_limit,
                "daily_remaining": daily_limit - (daily_count + 1),
                "minute_limit": minute_limit,
                "minute_remaining": minute_limit - (minute_count + 1)
            }
    
    def get_usage_stats(self, api_key: str = None) -> Dict:
        """
        Get usage statistics.
        
        Args:
            api_key: Optional API key to get stats for
            
        Returns:
            Dictionary with usage statistics
        """
        with self.lock:
            if api_key:
                # Get stats for specific API key
                daily_count = sum(self.daily_request_counts.get(api_key, {}).values())
                
                # Calculate minute counts
                now = time.time()
                minute_timestamp = int(now / 60) * 60
                minute_count = 0
                if api_key in self.minute_request_counts and minute_timestamp in self.minute_request_counts[api_key]:
                    minute_count = self.minute_request_counts[api_key][minute_timestamp]
                
                return {
                    "api_key": api_key,
                    "daily_count": daily_count,
                    "minute_count": minute_count
                }
            else:
                # Get stats for all API keys
                stats = {
                    "total_api_keys": len(self.daily_request_counts),
                    "total_daily_requests": sum(sum(counts.values()) for counts in self.daily_request_counts.values()),
                    "api_keys": []
                }
                
                for key in self.daily_request_counts:
                    stats["api_keys"].append(self.get_usage_stats(key))
                
                return stats


# Singleton instance
_instance = None

def get_rate_limiter() -> RateLimiter:
    """
    Get the rate limiter singleton instance.
    
    Returns:
        Rate limiter instance
    """
    global _instance
    
    if _instance is None:
        _instance = RateLimiter()
    
    return _instance


def check_rate_limit(api_key: str, daily_limit: int, minute_limit: int = 20) -> Tuple[bool, Dict]:
    """
    Check if a request from a specific API key is within rate limits.
    
    Args:
        api_key: API key
        daily_limit: Daily request limit
        minute_limit: Per-minute request limit
        
    Returns:
        Tuple of (allowed, limits) where allowed is a boolean and limits is a dictionary with rate limit information
    """
    return get_rate_limiter().check_rate_limit(api_key, daily_limit, minute_limit)


def get_usage_stats(api_key: str = None) -> Dict:
    """
    Get usage statistics.
    
    Args:
        api_key: Optional API key to get stats for
        
    Returns:
        Dictionary with usage statistics
    """
    return get_rate_limiter().get_usage_stats(api_key)