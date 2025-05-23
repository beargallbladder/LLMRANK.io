"""
Setup LLMPageRank Frontend API Key

This script creates a special API key for the LLMPageRank frontend (llmpagerank.com)
with the appropriate permissions to access our backend services.
"""

import os
import sys
import logging
import datetime
import json
import uuid
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_KEYS_PATH = "data/system_feedback/api_keys.json"

def create_frontend_api_key() -> str:
    """
    Create a special API key for the LLMPageRank frontend with appropriate permissions.
    
    Returns:
        Generated API key
    """
    # Define frontend access permissions
    frontend_permissions = [
        "rankllm_input",      # Access to leaderboard data
        "context",            # Access to trust context
        "drift_events",       # Access to drift events
        "foma_threats",       # Access to FOMA threats
        "prompt_suggestions", # Access to prompt suggestions
        "health",             # Access to health metrics
        "vulnerability_data", # Access to memory vulnerability scores
        "admin_metrics"       # Access to important admin metrics
    ]
    
    # Generate a unique API key
    api_key = f"llmpagerank_frontend_{uuid.uuid4().hex}"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(API_KEYS_PATH), exist_ok=True)
    
    # Load existing API keys
    api_keys = {}
    if os.path.exists(API_KEYS_PATH):
        try:
            with open(API_KEYS_PATH, "r") as f:
                api_keys = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
    
    # Add the new frontend API key
    api_keys[api_key] = {
        "agent_id": "llmpagerank_frontend",
        "access": frontend_permissions,
        "created": datetime.datetime.now().isoformat(),
        "expires": None,
        "rate_limit": 100000  # Higher limit for frontend
    }
    
    # Save updated API keys
    with open(API_KEYS_PATH, "w") as f:
        json.dump(api_keys, f, indent=2)
    
    logger.info(f"Created frontend API key: {api_key[:12]}...{api_key[-4:]}")
    
    # Also store frontend key info in our own location
    key_info = {
        "key": api_key,
        "created_at": datetime.datetime.now().isoformat(),
        "permissions": frontend_permissions,
        "rate_limit": 100000
    }
    
    # Make sure the directory exists
    os.makedirs("data/api_keys", exist_ok=True)
    
    # Save key info to a secure file
    with open("data/api_keys/frontend_key.json", "w") as f:
        json.dump(key_info, f, indent=2)
    
    logger.info("Saved frontend key info to data/api_keys/frontend_key.json")
    
    return api_key

def get_frontend_api_key() -> Optional[str]:
    """
    Get the current frontend API key if it exists.
    
    Returns:
        Frontend API key or None if not found
    """
    try:
        if os.path.exists("data/api_keys/frontend_key.json"):
            with open("data/api_keys/frontend_key.json", "r") as f:
                key_info = json.load(f)
                return key_info.get("key")
        return None
    except Exception as e:
        logger.error(f"Error getting frontend API key: {e}")
        return None

def revoke_frontend_api_key() -> bool:
    """
    Revoke the current frontend API key.
    
    Returns:
        Whether the key was successfully revoked
    """
    current_key = get_frontend_api_key()
    
    if current_key:
        success = revoke_api_key(current_key)
        
        if success:
            # Update the stored key info
            if os.path.exists("data/api_keys/frontend_key.json"):
                try:
                    with open("data/api_keys/frontend_key.json", "r") as f:
                        key_info = json.load(f)
                    
                    key_info["revoked_at"] = datetime.datetime.now().isoformat()
                    key_info["status"] = "revoked"
                    
                    with open("data/api_keys/frontend_key.json", "w") as f:
                        json.dump(key_info, f, indent=2)
                except Exception as e:
                    logger.error(f"Error updating frontend key info: {e}")
            
            logger.info(f"Revoked frontend API key: {current_key[:8]}...{current_key[-4:]}")
            return True
        else:
            logger.error(f"Failed to revoke frontend API key: {current_key[:8]}...{current_key[-4:]}")
            return False
    else:
        logger.warning("No frontend API key found to revoke")
        return False

def rotate_frontend_api_key() -> Optional[str]:
    """
    Rotate the frontend API key by revoking the old one and creating a new one.
    
    Returns:
        New API key if rotation was successful, None otherwise
    """
    # Revoke old key
    revoke_frontend_api_key()
    
    # Create new key
    return create_frontend_api_key()

def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_llmpagerank_frontend_key.py create")
        print("  python setup_llmpagerank_frontend_key.py get")
        print("  python setup_llmpagerank_frontend_key.py revoke")
        print("  python setup_llmpagerank_frontend_key.py rotate")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        api_key = create_frontend_api_key()
        print(f"Created frontend API key: {api_key}")
        print("IMPORTANT: Store this key securely. It will be used by the frontend to access the backend API.")
    
    elif command == "get":
        api_key = get_frontend_api_key()
        if api_key:
            print(f"Current frontend API key: {api_key}")
        else:
            print("No frontend API key found.")
    
    elif command == "revoke":
        success = revoke_frontend_api_key()
        if success:
            print("Successfully revoked frontend API key.")
        else:
            print("Failed to revoke frontend API key.")
    
    elif command == "rotate":
        new_key = rotate_frontend_api_key()
        if new_key:
            print(f"Rotated frontend API key. New key: {new_key}")
            print("IMPORTANT: Update the frontend configuration with this new key.")
        else:
            print("Failed to rotate frontend API key.")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, get, revoke, rotate")

if __name__ == "__main__":
    main()