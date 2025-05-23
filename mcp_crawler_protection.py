"""
MCP Crawler Protection Module

This module implements crawler protection mechanisms for the MCP API
as specified in PRD20.
"""

import time
import hmac
import hashlib
import logging
import datetime
from typing import Dict, List, Set, Optional, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crawler detection storage
class CrawlerProtection:
    """Manages crawler protection mechanisms."""
    
    def __init__(self):
        """Initialize crawler protection."""
        # IP bans: IP -> expiry timestamp
        self.ip_bans = {}
        
        # API key bans: key -> expiry timestamp
        self.key_bans = {}
        
        # Request patterns: key -> {endpoint -> timestamp}
        self.key_patterns = {}
        
        # Trap endpoint hits: IP -> [timestamps]
        self.trap_hits = {}
        
        # Known crawler user agents
        self.crawler_agents = [
            "curl", "python", "scrapy", "wget", "go-http-client", "axios", 
            "postman", "bot", "crawler", "spider", "scan", "selenium", "headless",
            "scraper", "beautifulsoup", "httpclient", "java", "playwright"
        ]
        
        logger.info("Crawler protection initialized")
    
    def is_ip_banned(self, ip: str) -> bool:
        """Check if an IP is banned."""
        if ip in self.ip_bans:
            if time.time() < self.ip_bans[ip]:
                return True
            else:
                # Ban expired
                del self.ip_bans[ip]
        return False
    
    def is_key_banned(self, key: str) -> bool:
        """Check if an API key is banned."""
        if key in self.key_bans:
            if time.time() < self.key_bans[key]:
                return True
            else:
                # Ban expired
                del self.key_bans[key]
        return False
    
    def ban_ip(self, ip: str, hours: int = 24):
        """Ban an IP for a specified number of hours."""
        self.ip_bans[ip] = time.time() + (hours * 3600)
        logger.warning(f"Banned IP {ip} for {hours} hours")
    
    def ban_key(self, key: str, hours: int = 24):
        """Ban an API key for a specified number of hours."""
        self.key_bans[key] = time.time() + (hours * 3600)
        logger.warning(f"Banned API key {key} for {hours} hours")
    
    def is_crawler_user_agent(self, user_agent: str) -> bool:
        """Check if a user agent matches known crawler patterns."""
        if not user_agent:
            return False
        
        user_agent = user_agent.lower()
        return any(agent in user_agent for agent in self.crawler_agents)
    
    def record_endpoint_access(self, key: str, endpoint: str):
        """Record endpoint access for pattern detection."""
        now = time.time()
        
        if key not in self.key_patterns:
            self.key_patterns[key] = {}
        
        self.key_patterns[key][endpoint] = now
    
    def check_pattern_violation(self, key: str) -> bool:
        """
        Check if an API key is accessing too many unique endpoints too quickly.
        Returns True if a violation is detected.
        """
        if key not in self.key_patterns:
            return False
        
        now = time.time()
        five_min_ago = now - 300  # 5 minutes
        
        # Count unique endpoints accessed in the last 5 minutes
        recent_endpoints = 0
        for endpoint, timestamp in self.key_patterns[key].items():
            if timestamp > five_min_ago:
                recent_endpoints += 1
        
        # Check if too many unique endpoints were accessed
        return recent_endpoints >= 12
    
    def record_trap_hit(self, ip: str, key: str = None):
        """
        Record a hit to a trap endpoint.
        Returns True if the IP and/or key should be banned.
        """
        now = time.time()
        
        if ip not in self.trap_hits:
            self.trap_hits[ip] = []
        
        self.trap_hits[ip].append(now)
        
        # Ban IP
        self.ban_ip(ip)
        
        # Ban key if provided
        if key:
            self.ban_key(key)
        
        logger.warning(f"Trap endpoint hit by IP {ip}" + (f", key {key}" if key else ""))
        return True
    
    def get_tier_delay(self, tier: str) -> float:
        """Get the random delay for a specific tier."""
        if tier == "free":
            return random.uniform(0.05, 0.25)  # 50-250ms
        elif tier == "partner_1":
            return random.uniform(0, 0.1)  # 0-100ms
        else:
            return 0  # No delay for higher tiers
    
    def verify_timestamp_signature(self, key: str, timestamp: str, 
                                 path: str, signature: str) -> bool:
        """
        Verify the HMAC signature of a request.
        Returns True if valid, False otherwise.
        """
        if not all([key, timestamp, path, signature]):
            return False
        
        try:
            # Parse timestamp
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # Check if timestamp is within ±5 minutes
            delta = abs((now - dt).total_seconds())
            if delta > 300:  # 5 minutes
                logger.warning(f"Timestamp out of range: {delta} seconds")
                return False
            
            # Compute expected signature
            message = f"{timestamp}{path}"
            expected = hmac.new(
                key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False


# Singleton instance
_instance = None

def get_crawler_protection() -> CrawlerProtection:
    """Get the crawler protection singleton instance."""
    global _instance
    
    if _instance is None:
        _instance = CrawlerProtection()
    
    return _instance


class CrawlerProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to protect against crawlers."""
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware."""
        super().__init__(app)
        self.protection = get_crawler_protection()
    
    async def dispatch(self, request: Request, call_next):
        """Process the request for crawler protection."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is banned
        if self.protection.is_ip_banned(client_ip):
            raise HTTPException(status_code=403, detail="IP address banned")
        
        # Get API key from Authorization header
        api_key = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
        
        # Check if API key is banned
        if api_key and self.protection.is_key_banned(api_key):
            raise HTTPException(status_code=403, detail="API key banned")
        
        # Check for trap endpoint
        if request.url.path == "/api/internal/seed_debug":
            self.protection.record_trap_hit(client_ip, api_key)
            # Return a deceptive 200 response
            from starlette.responses import JSONResponse
            return JSONResponse(content={"status": "ok", "debug": "enabled"})
        
        # Check User-Agent for known crawlers
        user_agent = request.headers.get("User-Agent", "")
        if self.protection.is_crawler_user_agent(user_agent):
            logger.warning(f"Crawler user agent detected: {user_agent}")
            # We don't ban immediately, but add a delay later
        
        # Record endpoint access for pattern detection
        if api_key:
            self.protection.record_endpoint_access(api_key, request.url.path)
            
            # Check for pattern violation
            if self.protection.check_pattern_violation(api_key):
                logger.warning(f"Pattern violation detected for API key: {api_key}")
                # Soft-throttle by adding a significant delay
                await asyncio.sleep(2.0)
        
        # Check for timestamp and signature validation
        # Only for non-documentation and non-root endpoints
        if (api_key and 
            not request.url.path.startswith("/docs") and 
            not request.url.path.startswith("/redoc") and
            not request.url.path == "/api-docs" and
            not request.url.path == "/api-reference" and
            not request.url.path == "/"):
            
            timestamp = request.headers.get("x-timestamp")
            signature = request.headers.get("x-signature")
            
            # Skip validation if either header is missing (for backward compatibility)
            if timestamp and signature:
                if not self.protection.verify_timestamp_signature(
                    api_key, timestamp, request.url.path, signature
                ):
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid request signature or timestamp"
                    )
        
        # Add random delay based on tier if a valid API key is present
        if api_key:
            try:
                # Import locally to avoid circular imports
                from mcp_auth import get_mcp_auth
                
                # Get API key data
                mcp_auth = get_mcp_auth()
                key_data = mcp_auth.api_keys.get(api_key, {})
                
                # Determine tier based on rate limit
                rate_limit = key_data.get("rate_limit", 500)
                
                tier = "free"
                if rate_limit >= 50000:
                    tier = "enterprise"
                elif rate_limit >= 10000:
                    tier = "partner_2"
                elif rate_limit >= 3000:
                    tier = "partner_1"
                
                # Apply delay based on tier
                delay = self.protection.get_tier_delay(tier)
                if delay > 0:
                    import asyncio
                    await asyncio.sleep(delay)
            except ImportError:
                # Default to free tier delay if mcp_auth is not available
                import asyncio
                await asyncio.sleep(self.protection.get_tier_delay("free"))
            except Exception as e:
                logger.error(f"Error applying tier delay: {e}")
        
        # Process the request and return the response
        return await call_next(request)