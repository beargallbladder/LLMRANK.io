"""
MCP Rate Limit Middleware

This module provides FastAPI middleware to add rate limit headers to responses.
"""

import time
import logging
from typing import Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses."""
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware."""
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Add rate limit headers to API responses.
        
        Args:
            request: The HTTP request
            call_next: The next middleware in the chain
            
        Returns:
            The HTTP response with rate limit headers
        """
        # Process the request and get the response
        response = await call_next(request)
        
        # Check if this is an API request using Bearer authentication
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
            
            try:
                # Import here to avoid circular imports
                from api_rate_limiter import get_usage_stats, check_rate_limit
                from mcp_auth import get_mcp_auth
                
                # Get rate limit for this API key
                mcp_auth = get_mcp_auth()
                rate_limit = mcp_auth.api_keys.get(api_key, {}).get("rate_limit", 1000)
                
                # Get rate limit information (making a test check with no impact)
                _, limit_info = check_rate_limit(api_key, rate_limit, 0)
                
                # Get current usage
                usage = get_usage_stats(api_key)
                
                # Add rate limit headers
                response.headers["X-RateLimit-Limit"] = str(rate_limit)
                response.headers["X-RateLimit-Remaining"] = str(limit_info.get("daily_remaining", 0))
                response.headers["X-RateLimit-Reset"] = str(int(time.time() + 86400))  # Reset at midnight
                response.headers["X-RateLimit-Minute-Limit"] = str(limit_info.get("minute_limit", 20))
                response.headers["X-RateLimit-Minute-Remaining"] = str(limit_info.get("minute_remaining", 0))
            except (ImportError, Exception) as e:
                logger.error(f"Error adding rate limit headers: {e}")
        
        return response