"""
LLMPageRank API Key Manager

This module handles secure storage, retrieval, and rotation of API keys
for the LLMPageRank system.
"""

import os
import json
import logging
import datetime
import secrets
import hashlib
import uuid
import re
from typing import Dict, Optional, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
CONFIG_DIR = os.path.join(DATA_DIR, "config")
API_KEYS_DIR = os.path.join(DATA_DIR, "api_keys")
KEY_STORE_PATH = os.path.join(CONFIG_DIR, "key_store.json")
KEY_ACCESS_LOG_PATH = os.path.join(CONFIG_DIR, "key_access_log.json")
USER_KEYS_PATH = os.path.join(API_KEYS_DIR, "user_keys.json")
API_KEYS_PATH = os.path.join(API_KEYS_DIR, "api_keys.json")

# Plan rate limits
PLAN_RATE_LIMITS = {
    "free_temp": 100,     # 100 calls per day
    "free": 500,          # 500 calls per day
    "starter": 2000,      # 2,000 calls per day
    "pro": 10000,         # 10,000 calls per day
    "enterprise": 50000   # 50,000 calls per day
}

# Plan scopes
PLAN_SCOPES = {
    "free_temp": ["read:basic", "read:category"],
    "free": ["read:basic", "read:category", "read:insights:basic"],
    "starter": ["read:basic", "read:category", "read:insights:basic", "read:insights:detailed"],
    "pro": ["read:basic", "read:category", "read:insights:basic", "read:insights:detailed", "read:trends", "write:basic"],
    "enterprise": ["read:basic", "read:category", "read:insights:basic", "read:insights:detailed", "read:trends", "write:basic", "write:advanced", "admin:basic"]
}

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(API_KEYS_DIR, exist_ok=True)

class APIKeyManager:
    """
    Manages API keys for external services, with support for multiple
    environments and rotation policies.
    """
    
    def __init__(self):
        """Initialize the API Key Manager."""
        self.key_store = self._load_key_store()
        self.access_log = self._load_access_log()
    
    def _load_key_store(self) -> Dict:
        """Load the key store from disk or create default if not exists."""
        try:
            if os.path.exists(KEY_STORE_PATH):
                with open(KEY_STORE_PATH, 'r') as f:
                    return json.load(f)
            else:
                # Create default key store
                key_store = {
                    "services": {
                        "llmpagerank": {
                            "keys": {},
                            "current_key": None,
                            "rotation_frequency_days": 90,
                            "last_rotation": None
                        }
                    },
                    "environments": ["development", "staging", "production"]
                }
                
                # Save default key store
                with open(KEY_STORE_PATH, 'w') as f:
                    json.dump(key_store, f, indent=2)
                
                return key_store
        except Exception as e:
            logger.error(f"Error loading key store: {e}")
            return {"services": {}, "environments": []}
    
    def _save_key_store(self) -> bool:
        """Save the key store to disk."""
        try:
            with open(KEY_STORE_PATH, 'w') as f:
                json.dump(self.key_store, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving key store: {e}")
            return False
    
    def _load_access_log(self) -> List:
        """Load the access log from disk or create empty if not exists."""
        try:
            if os.path.exists(KEY_ACCESS_LOG_PATH):
                with open(KEY_ACCESS_LOG_PATH, 'r') as f:
                    return json.load(f)
            else:
                # Create empty access log
                log = []
                
                # Save empty log
                with open(KEY_ACCESS_LOG_PATH, 'w') as f:
                    json.dump(log, f, indent=2)
                
                return log
        except Exception as e:
            logger.error(f"Error loading access log: {e}")
            return []
    
    def _save_access_log(self) -> bool:
        """Save the access log to disk."""
        try:
            with open(KEY_ACCESS_LOG_PATH, 'w') as f:
                json.dump(self.access_log, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving access log: {e}")
            return False
    
    def _log_access(self, service: str, key_id: str, environment: str, agent_name: Optional[str] = None) -> None:
        """
        Log an API key access event.
        
        Args:
            service: Name of the service
            key_id: ID of the key accessed
            environment: Environment the key is for
            agent_name: Name of the agent accessing the key
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "service": service,
            "key_id": key_id,
            "environment": environment,
            "agent_name": agent_name
        }
        
        self.access_log.append(log_entry)
        
        # Trim log if too large (keep last 1000 entries)
        if len(self.access_log) > 1000:
            self.access_log = self.access_log[-1000:]
        
        # Save log
        self._save_access_log()
    
    def _generate_key_id(self) -> str:
        """
        Generate a unique key ID.
        
        Returns:
            Unique key ID
        """
        # Generate a random token and hash it
        token = secrets.token_hex(16)
        key_id = hashlib.sha256(token.encode()).hexdigest()[:12]
        
        return f"key_{key_id}"
    
    def add_api_key(self, service: str, key_value: str, environment: str = "production", 
                  make_current: bool = True, description: Optional[str] = None) -> str:
        """
        Add a new API key to the key store.
        
        Args:
            service: Name of the service
            key_value: Actual API key value
            environment: Environment the key is for
            make_current: Whether to make this the current key
            description: Optional description
            
        Returns:
            Key ID
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            # Create service entry
            self.key_store["services"][service] = {
                "keys": {},
                "current_key": None,
                "rotation_frequency_days": 90,
                "last_rotation": None
            }
        
        service_data = self.key_store["services"][service]
        
        # Generate key ID
        key_id = self._generate_key_id()
        
        # Add key
        service_data["keys"][key_id] = {
            "value": key_value,
            "environment": environment,
            "added": datetime.datetime.now().isoformat(),
            "last_used": None,
            "description": description
        }
        
        # Make current if requested
        if make_current:
            service_data["current_key"] = key_id
            service_data["last_rotation"] = datetime.datetime.now().isoformat()
        
        # Save key store
        self._save_key_store()
        
        logger.info(f"Added new API key for {service} in {environment} environment")
        
        return key_id
    
    def get_api_key(self, service: str, environment: Optional[str] = None, 
                   agent_name: Optional[str] = None) -> Optional[str]:
        """
        Get an API key value.
        
        Args:
            service: Name of the service
            environment: Environment to get key for (uses current key if None)
            agent_name: Name of the agent requesting the key
            
        Returns:
            API key value or None if not found
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            logger.error(f"Service {service} not found in key store")
            return None
        
        service_data = self.key_store["services"][service]
        keys = service_data["keys"]
        
        # Find appropriate key
        key_id = None
        
        if environment is None:
            # Use current key
            key_id = service_data["current_key"]
        else:
            # Find key for specified environment
            for k_id, k_data in keys.items():
                if k_data["environment"] == environment:
                    key_id = k_id
                    break
        
        if key_id is None or key_id not in keys:
            logger.error(f"No API key found for {service} in {'current' if environment is None else environment} environment")
            return None
        
        # Update last used
        keys[key_id]["last_used"] = datetime.datetime.now().isoformat()
        
        # Log access
        self._log_access(
            service=service,
            key_id=key_id,
            environment=keys[key_id]["environment"],
            agent_name=agent_name
        )
        
        # Save key store
        self._save_key_store()
        
        return keys[key_id]["value"]
    
    def rotate_api_key(self, service: str, new_key_value: str, environment: str = "production",
                     description: Optional[str] = None) -> str:
        """
        Rotate an API key.
        
        Args:
            service: Name of the service
            new_key_value: New API key value
            environment: Environment the key is for
            description: Optional description
            
        Returns:
            New key ID
        """
        # Add new key
        new_key_id = self.add_api_key(
            service=service,
            key_value=new_key_value,
            environment=environment,
            make_current=True,
            description=description
        )
        
        # Log rotation
        logger.info(f"Rotated API key for {service} in {environment} environment")
        
        return new_key_id
    
    def remove_api_key(self, service: str, key_id: str) -> bool:
        """
        Remove an API key from the key store.
        
        Args:
            service: Name of the service
            key_id: ID of the key to remove
            
        Returns:
            Success flag
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            logger.error(f"Service {service} not found in key store")
            return False
        
        service_data = self.key_store["services"][service]
        
        # Check if key exists
        if key_id not in service_data["keys"]:
            logger.error(f"Key {key_id} not found for service {service}")
            return False
        
        # Remove key
        del service_data["keys"][key_id]
        
        # Update current key if needed
        if service_data["current_key"] == key_id:
            service_data["current_key"] = None
        
        # Save key store
        self._save_key_store()
        
        logger.info(f"Removed API key {key_id} for service {service}")
        
        return True
    
    def check_rotation_needed(self, service: str) -> bool:
        """
        Check if key rotation is needed based on rotation frequency.
        
        Args:
            service: Name of the service
            
        Returns:
            Whether rotation is needed
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            logger.error(f"Service {service} not found in key store")
            return False
        
        service_data = self.key_store["services"][service]
        
        # Check last rotation
        last_rotation = service_data.get("last_rotation")
        if last_rotation is None:
            # Never rotated
            return True
        
        # Convert to datetime
        last_rotation_dt = datetime.datetime.fromisoformat(last_rotation)
        
        # Get rotation frequency
        rotation_days = service_data.get("rotation_frequency_days", 90)
        
        # Calculate days since last rotation
        days_since_rotation = (datetime.datetime.now() - last_rotation_dt).days
        
        # Check if rotation is needed
        return days_since_rotation >= rotation_days
    
    def get_key_info(self, service: str, key_id: Optional[str] = None) -> Dict:
        """
        Get information about a specific key or the current key.
        
        Args:
            service: Name of the service
            key_id: ID of the key (uses current key if None)
            
        Returns:
            Key information dictionary
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            logger.error(f"Service {service} not found in key store")
            return {}
        
        service_data = self.key_store["services"][service]
        
        # Determine key ID
        if key_id is None:
            key_id = service_data["current_key"]
        
        if key_id is None or key_id not in service_data["keys"]:
            logger.error(f"No key found for {service} (key_id: {key_id})")
            return {}
        
        # Get key info
        key_info = service_data["keys"][key_id].copy()
        
        # Remove sensitive data
        key_info["value"] = "********" # Mask actual key value
        
        # Add key ID
        key_info["key_id"] = key_id
        
        return key_info
    
    def get_service_info(self, service: str) -> Dict:
        """
        Get information about a service.
        
        Args:
            service: Name of the service
            
        Returns:
            Service information dictionary
        """
        # Check if service exists
        if service not in self.key_store["services"]:
            logger.error(f"Service {service} not found in key store")
            return {}
        
        service_data = self.key_store["services"][service].copy()
        
        # Prepare key infos
        key_infos = {}
        for key_id, key_data in service_data["keys"].items():
            key_info = key_data.copy()
            key_info["value"] = "********" # Mask actual key value
            key_infos[key_id] = key_info
        
        # Replace keys with masked versions
        service_data["keys"] = key_infos
        
        # Add service name
        service_data["service_name"] = service
        
        # Add rotation status
        service_data["rotation_needed"] = self.check_rotation_needed(service)
        
        return service_data
    
    def list_services(self) -> List[str]:
        """
        List all services in the key store.
        
        Returns:
            List of service names
        """
        return list(self.key_store["services"].keys())


# Create singleton instance
_key_manager = None

def get_key_manager() -> APIKeyManager:
    """
    Get the API Key Manager singleton instance.
    
    Returns:
        API Key Manager instance
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager

def add_api_key(service: str, key_value: str, environment: str = "production",
              make_current: bool = True, description: Optional[str] = None) -> str:
    """
    Add a new API key to the key store.
    
    Args:
        service: Name of the service
        key_value: Actual API key value
        environment: Environment the key is for
        make_current: Whether to make this the current key
        description: Optional description
        
    Returns:
        Key ID
    """
    return get_key_manager().add_api_key(
        service=service,
        key_value=key_value,
        environment=environment,
        make_current=make_current,
        description=description
    )

def get_api_key(service: str, environment: Optional[str] = None,
               agent_name: Optional[str] = None) -> Optional[str]:
    """
    Get an API key value.
    
    Args:
        service: Name of the service
        environment: Environment to get key for (uses current key if None)
        agent_name: Name of the agent requesting the key
        
    Returns:
        API key value or None if not found
    """
    return get_key_manager().get_api_key(
        service=service,
        environment=environment,
        agent_name=agent_name
    )

def rotate_api_key(service: str, new_key_value: str, environment: str = "production",
                 description: Optional[str] = None) -> str:
    """
    Rotate an API key.
    
    Args:
        service: Name of the service
        new_key_value: New API key value
        environment: Environment the key is for
        description: Optional description
        
    Returns:
        New key ID
    """
    return get_key_manager().rotate_api_key(
        service=service,
        new_key_value=new_key_value,
        environment=environment,
        description=description
    )

def remove_api_key(service: str, key_id: str) -> bool:
    """
    Remove an API key from the key store.
    
    Args:
        service: Name of the service
        key_id: ID of the key to remove
        
    Returns:
        Success flag
    """
    return get_key_manager().remove_api_key(
        service=service,
        key_id=key_id
    )

def check_rotation_needed(service: str) -> bool:
    """
    Check if key rotation is needed based on rotation frequency.
    
    Args:
        service: Name of the service
        
    Returns:
        Whether rotation is needed
    """
    return get_key_manager().check_rotation_needed(service)

def get_key_info(service: str, key_id: Optional[str] = None) -> Dict:
    """
    Get information about a specific key or the current key.
    
    Args:
        service: Name of the service
        key_id: ID of the key (uses current key if None)
        
    Returns:
        Key information dictionary
    """
    return get_key_manager().get_key_info(
        service=service,
        key_id=key_id
    )

def get_service_info(service: str) -> Dict:
    """
    Get information about a service.
    
    Args:
        service: Name of the service
        
    Returns:
        Service information dictionary
    """
    return get_key_manager().get_service_info(service)

def list_services() -> List[str]:
    """
    List all services in the key store.
    
    Returns:
        List of service names
    """
    return get_key_manager().list_services()


# ===== LLMPageRank API Key Management Functions =====

def _load_api_keys() -> Dict:
    """Load API keys from disk."""
    try:
        if os.path.exists(API_KEYS_PATH):
            with open(API_KEYS_PATH, 'r') as f:
                return json.load(f)
        else:
            # Create default structure
            api_keys = {
                "keys": {}
            }
            
            # Save default structure
            with open(API_KEYS_PATH, 'w') as f:
                json.dump(api_keys, f, indent=2)
            
            return api_keys
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return {"keys": {}}

def _save_api_keys(api_keys: Dict) -> bool:
    """Save API keys to disk."""
    try:
        with open(API_KEYS_PATH, 'w') as f:
            json.dump(api_keys, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving API keys: {e}")
        return False

def _load_user_keys() -> Dict:
    """Load user keys from disk."""
    try:
        if os.path.exists(USER_KEYS_PATH):
            with open(USER_KEYS_PATH, 'r') as f:
                return json.load(f)
        else:
            # Create default structure
            user_keys = {
                "users": {}
            }
            
            # Save default structure
            with open(USER_KEYS_PATH, 'w') as f:
                json.dump(user_keys, f, indent=2)
            
            return user_keys
    except Exception as e:
        logger.error(f"Error loading user keys: {e}")
        return {"users": {}}

def _save_user_keys(user_keys: Dict) -> bool:
    """Save user keys to disk."""
    try:
        with open(USER_KEYS_PATH, 'w') as f:
            json.dump(user_keys, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user keys: {e}")
        return False

def _generate_api_key(prefix: str = "llmpr") -> str:
    """Generate a new API key."""
    random_part = uuid.uuid4().hex[:24]
    return f"{prefix}_{random_part}"

def create_api_key(
    user_id: str,
    plan: str = "free_temp",
    custom_rate_limit: Optional[int] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    verified: bool = False,
    stripe_customer_id: Optional[str] = None
) -> Dict:
    """
    Create a new API key for a user.
    
    Args:
        user_id: User identifier
        plan: Subscription plan
        custom_rate_limit: Custom rate limit (overrides plan default)
        email: User email
        ip_address: User IP address
        verified: Whether the user is verified
        stripe_customer_id: Stripe customer ID for paid plans
        
    Returns:
        API key data
    """
    # Generate API key
    token = _generate_api_key()
    
    # Get rate limit for plan
    rate_limit = custom_rate_limit if custom_rate_limit is not None else PLAN_RATE_LIMITS.get(plan, 100)
    
    # Get scopes for plan
    scope = PLAN_SCOPES.get(plan, ["read:basic"])
    
    # Set expiration for temporary keys
    expires = None
    if plan == "free_temp":
        # 7 days from now
        expires = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
    
    # Create key data
    key_data = {
        "token": token,
        "user_id": user_id,
        "plan": plan,
        "rate_limit": rate_limit,
        "scope": scope,
        "created": datetime.datetime.now().isoformat(),
        "last_used": None,
        "status": "active",
        "email": email,
        "verified": verified,
        "stripe_customer_id": stripe_customer_id,
        "expires": expires,
        "calls_today": 0,
        "total_calls": 0
    }
    
    # Save key to API keys store
    api_keys = _load_api_keys()
    api_keys["keys"][token] = key_data
    _save_api_keys(api_keys)
    
    # Associate key with user
    user_keys = _load_user_keys()
    if user_id not in user_keys["users"]:
        user_keys["users"][user_id] = {
            "email": email,
            "verified": verified,
            "keys": [],
            "stripe_customer_id": stripe_customer_id,
            "created": datetime.datetime.now().isoformat()
        }
    
    # Add key to user's keys
    user_keys["users"][user_id]["keys"].append(token)
    user_keys["users"][user_id]["current_key"] = token
    
    # Update user data
    if email:
        user_keys["users"][user_id]["email"] = email
    user_keys["users"][user_id]["verified"] = verified
    if stripe_customer_id:
        user_keys["users"][user_id]["stripe_customer_id"] = stripe_customer_id
    
    _save_user_keys(user_keys)
    
    # Return key data
    return key_data

def get_api_key(api_key: str, environment: Optional[str] = None, agent_name: Optional[str] = None) -> Optional[str]:
    """
    Get API key value or details.
    
    This function has two modes:
    1. When called with just the api_key parameter, it returns the key details
    2. When called with environment and agent_name, it works with the internal key system
       and returns the key value from the key store
    
    Args:
        api_key: API key token or service name
        environment: Environment (for internal key store)
        agent_name: Name of the agent requesting the key (for internal key store)
        
    Returns:
        API key data or value depending on the mode
    """
    # If environment is provided, this is a call to the internal key store
    if environment is not None:
        return get_key_manager().get_api_key(
            service=api_key,  # In this case, api_key is the service name
            environment=environment,
            agent_name=agent_name
        )
    
    # Otherwise, this is a call to get API key details
    api_keys = _load_api_keys()
    return api_keys["keys"].get(api_key)

def get_all_keys() -> List[Dict]:
    """
    Get all API keys data.
    
    Returns:
        List of API key data dictionaries
    """
    api_keys = _load_api_keys()
    return list(api_keys["keys"].values())

def get_user_api_key(user_id: str) -> Optional[Dict]:
    """
    Get user's current API key.
    
    Args:
        user_id: User identifier
        
    Returns:
        API key data or None if not found
    """
    user_keys = _load_user_keys()
    
    # Check if user exists
    if user_id not in user_keys["users"]:
        return None
    
    # Get user's current key
    current_key = user_keys["users"][user_id].get("current_key")
    
    if not current_key:
        return None
    
    # Get key data
    api_keys = _load_api_keys()
    
    return api_keys["keys"].get(current_key)

def update_api_key_usage(api_key: str) -> bool:
    """
    Update API key usage stats.
    
    Args:
        api_key: API key token
        
    Returns:
        Success flag
    """
    api_keys = _load_api_keys()
    
    # Check if key exists
    if api_key not in api_keys["keys"]:
        return False
    
    # Update usage stats
    api_keys["keys"][api_key]["last_used"] = datetime.datetime.now().isoformat()
    api_keys["keys"][api_key]["calls_today"] += 1
    api_keys["keys"][api_key]["total_calls"] += 1
    
    # Save updated data
    return _save_api_keys(api_keys)

def upgrade_api_key(
    user_id: str,
    new_plan: str,
    verified: bool = True,
    stripe_customer_id: Optional[str] = None
) -> Dict:
    """
    Upgrade user's API key to a new plan.
    
    Args:
        user_id: User identifier
        new_plan: New subscription plan
        verified: Whether the user is verified
        stripe_customer_id: Stripe customer ID for paid plans
        
    Returns:
        Updated API key data
    """
    # Get user's current key
    user_keys = _load_user_keys()
    
    # Check if user exists
    if user_id not in user_keys["users"]:
        # User doesn't exist, create new key
        return create_api_key(
            user_id=user_id,
            plan=new_plan,
            verified=verified,
            stripe_customer_id=stripe_customer_id
        )
    
    # Get user's current key
    current_key = user_keys["users"][user_id].get("current_key")
    
    if not current_key:
        # User has no current key, create new key
        return create_api_key(
            user_id=user_id,
            plan=new_plan,
            verified=verified,
            stripe_customer_id=stripe_customer_id,
            email=user_keys["users"][user_id].get("email")
        )
    
    # Get API keys
    api_keys = _load_api_keys()
    
    # Check if key exists
    if current_key not in api_keys["keys"]:
        # Key doesn't exist, create new key
        return create_api_key(
            user_id=user_id,
            plan=new_plan,
            verified=verified,
            stripe_customer_id=stripe_customer_id,
            email=user_keys["users"][user_id].get("email")
        )
    
    # Update key data
    key_data = api_keys["keys"][current_key]
    
    # Get rate limit for new plan
    rate_limit = PLAN_RATE_LIMITS.get(new_plan, key_data["rate_limit"])
    
    # Get scopes for new plan
    scope = PLAN_SCOPES.get(new_plan, key_data["scope"])
    
    # Update key data
    key_data["plan"] = new_plan
    key_data["rate_limit"] = rate_limit
    key_data["scope"] = scope
    key_data["verified"] = verified
    
    # Remove expiration for non-temporary plans
    if new_plan != "free_temp":
        key_data["expires"] = None
    
    # Update Stripe customer ID if provided
    if stripe_customer_id:
        key_data["stripe_customer_id"] = stripe_customer_id
    
    # Save updated data
    api_keys["keys"][current_key] = key_data
    _save_api_keys(api_keys)
    
    # Update user data
    user_keys["users"][user_id]["verified"] = verified
    if stripe_customer_id:
        user_keys["users"][user_id]["stripe_customer_id"] = stripe_customer_id
    
    _save_user_keys(user_keys)
    
    # Return updated key data
    return key_data

def downgrade_api_key(
    user_id: str,
    new_plan: str
) -> Dict:
    """
    Downgrade user's API key to a new plan.
    
    Args:
        user_id: User identifier
        new_plan: New subscription plan
        
    Returns:
        Updated API key data
    """
    # This is mostly the same as upgrade, but we keep it separate for clarity
    return upgrade_api_key(
        user_id=user_id,
        new_plan=new_plan
    )

def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key.
    
    Args:
        api_key: API key token
        
    Returns:
        Success flag
    """
    api_keys = _load_api_keys()
    
    # Check if key exists
    if api_key not in api_keys["keys"]:
        return False
    
    # Set status to revoked
    api_keys["keys"][api_key]["status"] = "revoked"
    
    # Save updated data
    return _save_api_keys(api_keys)


if __name__ == "__main__":
    # Test API key management
    logger.info("Testing API key management")
    
    # Test internal key management
    test_key = "llmpr_test_api_key_12345"
    key_id = add_api_key(
        service="llmpagerank",
        key_value=test_key,
        environment="development",
        description="Test API key"
    )
    
    logger.info(f"Added test key with ID: {key_id}")
    
    # Get the key
    retrieved_key = get_api_key(
        service="llmpagerank",
        environment="development",
        agent_name="test_agent"
    )
    
    if retrieved_key == test_key:
        logger.info("Successfully retrieved test key")
    else:
        logger.error("Failed to retrieve test key")
    
    # Test API key creation for external users
    user_key_data = create_api_key(
        user_id="test_user",
        email="test@example.com",
        plan="free",
        ip_address="127.0.0.1"
    )
    
    logger.info(f"Created API key for test user: {user_key_data['token']}")
    
    # Test retrieval
    user_key = get_user_api_key("test_user")
    
    if user_key:
        logger.info(f"Retrieved user key: {user_key['token']}")
    else:
        logger.error("Failed to retrieve user key")
    
    # Test upgrade
    upgraded_key = upgrade_api_key(
        user_id="test_user",
        new_plan="pro",
        verified=True
    )
    
    logger.info(f"Upgraded user key to {upgraded_key['plan']} plan")
    
    logger.info("Tests completed")