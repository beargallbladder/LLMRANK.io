"""
LLMPageRank Model Context Protocol (MCP) Authentication

This module implements the authentication system for the MCP API endpoints
as specified in the MCP API Authentication Specification.
"""

import os
import json
import time
import datetime
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from fastapi import Request, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Constants
API_KEYS_PATH = "data/system_feedback/api_keys.json"
API_LOGS_PATH = "data/system_feedback/api_access_logs.json"

# Create security scheme
security = HTTPBearer()


class MCPAuth:
    """MCP Authentication handler."""
    
    def __init__(self):
        """Initialize the MCP authentication."""
        logger.info("Initializing MCP Authentication")
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(API_KEYS_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(API_LOGS_PATH), exist_ok=True)
        
        # Load API keys
        self.api_keys = self._load_api_keys()
        
        # Initialize rate limit tracking
        self.rate_limits = {}
        
        logger.info(f"Loaded {len(self.api_keys)} API keys")
    
    def _load_api_keys(self) -> Dict:
        """
        Load API keys from file.
        
        Returns:
            API keys dictionary
        """
        if os.path.exists(API_KEYS_PATH):
            try:
                with open(API_KEYS_PATH, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load API keys: {e}")
        
        # Default API keys with a test key and site-specific keys
        default_keys = {
            "test_key_b7d29f38c6144ea3b1982b4a4429018d": {
                "agent_id": "test_agent",
                "access": ["rankllm_input", "drift_events", "prompt_suggestions", 
                          "context", "foma_threats", "agent_register", "agent_update", "health"],
                "created": datetime.datetime.now().isoformat(),
                "expires": None,
                "rate_limit": 1000
            },
            "llmrank_io_bd741a2f59664e8c9d17b836c4503e2d": {
                "agent_id": "llmrank_io",
                "access": ["rankllm_input", "drift_events", "prompt_suggestions", 
                          "context", "foma_threats", "agent_register", "agent_update", "health"],
                "created": datetime.datetime.now().isoformat(),
                "expires": None,
                "rate_limit": 10000
            },
            "outcited_com_e7c38f1b2d5a47b9a4d1c8e6f2b3a9d7": {
                "agent_id": "outcited_com",
                "access": ["rankllm_input", "drift_events", "prompt_suggestions", 
                          "context", "foma_threats", "agent_register", "agent_update", "health"],
                "created": datetime.datetime.now().isoformat(),
                "expires": None,
                "rate_limit": 10000
            }
        }
        
        # Save default keys
        with open(API_KEYS_PATH, "w") as f:
            json.dump(default_keys, f, indent=2)
        
        return default_keys
    
    def _save_api_keys(self) -> None:
        """Save API keys to file."""
        try:
            with open(API_KEYS_PATH, "w") as f:
                json.dump(self.api_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
    
    def _log_api_access(self, agent_id: str, endpoint: str, status: int, ip: str) -> None:
        """
        Log API access.
        
        Args:
            agent_id: Agent identifier
            endpoint: API endpoint
            status: HTTP status code
            ip: Client IP address
        """
        log_entry = {
            "agent_id": agent_id,
            "endpoint": endpoint,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "ip": ip
        }
        
        # Append to logs
        try:
            logs = []
            
            if os.path.exists(API_LOGS_PATH):
                try:
                    with open(API_LOGS_PATH, "r") as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            
            logs.append(log_entry)
            
            # Keep only the last 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(API_LOGS_PATH, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log API access: {e}")
    
    def _check_rate_limit(self, api_key: str) -> bool:
        """
        Check if the API key has exceeded its rate limit.
        
        Args:
            api_key: API key to check
            
        Returns:
            Whether the rate limit has been exceeded
        """
        try:
            # Import here to avoid circular imports
            from api_rate_limiter import check_rate_limit
            
            # Get rate limit for this key
            rate_limit = self.api_keys.get(api_key, {}).get("rate_limit", 1000)
            
            # Use enhanced rate limiter with daily and per-minute limits
            # Default per-minute limit is 20 requests
            allowed, _ = check_rate_limit(api_key, rate_limit)
            
            return allowed
        except ImportError:
            # Fall back to simple rate limiting if enhanced limiter not available
            logger.warning("Enhanced rate limiter not available, using simple rate limiting")
            
            # Get rate limit for this key
            rate_limit = self.api_keys.get(api_key, {}).get("rate_limit", 1000)
            
            # Get current day
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Initialize rate limit tracking for this key if needed
            if api_key not in self.rate_limits:
                self.rate_limits[api_key] = {}
            
            # Initialize rate limit tracking for today if needed
            if today not in self.rate_limits[api_key]:
                self.rate_limits[api_key][today] = 0
            
            # Check if rate limit is exceeded
            if self.rate_limits[api_key][today] >= rate_limit:
                return False
            
            # Increment rate limit counter
            self.rate_limits[api_key][today] += 1
            
            return True
    
    def validate_token(self, credentials: HTTPAuthorizationCredentials, request: Request) -> Dict:
        """
        Validate API key token.
        
        Args:
            credentials: HTTP authorization credentials
            request: HTTP request
            
        Returns:
            API key data if valid
            
        Raises:
            HTTPException: If API key is missing, invalid, or rate limit is exceeded
        """
        # Check if token is provided
        if not credentials:
            logger.warning("API key missing")
            raise HTTPException(
                status_code=403,
                detail={"error": "unauthorized", "reason": "API key missing"}
            )
        
        api_key = credentials.credentials
        
        # Check if API key is valid
        if api_key not in self.api_keys:
            logger.warning(f"Invalid API key: {api_key}")
            raise HTTPException(
                status_code=403,
                detail={"error": "unauthorized", "reason": "invalid token"}
            )
        
        # Get API key data
        key_data = self.api_keys[api_key]
        
        # Check if API key has expired
        if key_data.get("expires") and datetime.datetime.fromisoformat(key_data["expires"]) < datetime.datetime.now():
            logger.warning(f"Expired API key: {api_key}")
            raise HTTPException(
                status_code=403,
                detail={"error": "unauthorized", "reason": "token expired"}
            )
        
        # Check rate limit
        if not self._check_rate_limit(api_key):
            logger.warning(f"Rate limit exceeded for API key: {api_key}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "limit": key_data.get("rate_limit", 1000),
                    "period": "24h"
                }
            )
        
        # Log API access
        self._log_api_access(
            agent_id=key_data.get("agent_id", "unknown"),
            endpoint=request.url.path,
            status=200,
            ip=request.client.host
        )
        
        return key_data
    
    def generate_api_key(self, agent_id: str, access: List[str], 
                         rate_limit: int = 1000, expires: Optional[str] = None) -> str:
        """
        Generate a new API key.
        
        Args:
            agent_id: Agent identifier
            access: List of allowed access endpoints
            rate_limit: Rate limit (requests per day)
            expires: Expiry date (ISO format)
            
        Returns:
            Generated API key
        """
        # Generate a new API key
        api_key = f"key_{uuid.uuid4().hex}"
        
        # Create API key data
        key_data = {
            "agent_id": agent_id,
            "access": access,
            "created": datetime.datetime.now().isoformat(),
            "expires": expires,
            "rate_limit": rate_limit
        }
        
        # Add API key
        self.api_keys[api_key] = key_data
        
        # Save API keys
        self._save_api_keys()
        
        logger.info(f"Generated API key for agent: {agent_id}")
        
        return api_key
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            Whether the API key was revoked
        """
        # Check if API key exists
        if api_key not in self.api_keys:
            return False
        
        # Remove API key
        del self.api_keys[api_key]
        
        # Save API keys
        self._save_api_keys()
        
        logger.info(f"Revoked API key: {api_key}")
        
        return True


# Singleton instance
_instance = None

def get_mcp_auth() -> MCPAuth:
    """
    Get the MCP authentication singleton instance.
    
    Returns:
        MCP authentication instance
    """
    global _instance
    
    if _instance is None:
        _instance = MCPAuth()
    
    return _instance

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict:
    """
    Verify API key token.
    
    Args:
        credentials: HTTP authorization credentials
        request: HTTP request
        
    Returns:
        API key data if valid
    """
    return get_mcp_auth().validate_token(credentials, request)

def generate_api_key(agent_id: str, access: List[str], 
                     rate_limit: int = 1000, expires: Optional[str] = None) -> str:
    """
    Generate a new API key.
    
    Args:
        agent_id: Agent identifier
        access: List of allowed access endpoints
        rate_limit: Rate limit (requests per day)
        expires: Expiry date (ISO format)
        
    Returns:
        Generated API key
    """
    return get_mcp_auth().generate_api_key(agent_id, access, rate_limit, expires)

def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key.
    
    Args:
        api_key: API key to revoke
        
    Returns:
        Whether the API key was revoked
    """
    return get_mcp_auth().revoke_api_key(api_key)