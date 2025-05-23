"""
MCP API Key Generator

This script generates a secure MCP API key for monitoring and accessing
the LLMPageRank system programmatically.
"""

import os
import json
import uuid
import hashlib
import datetime
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MCP_KEYS_DIR = "data/mcp/keys"
MCP_KEY_PREFIX = "mcp_"

# Ensure directories exist
os.makedirs(MCP_KEYS_DIR, exist_ok=True)

def generate_secure_key() -> str:
    """Generate a secure MCP API key."""
    key_uuid = uuid.uuid4()
    timestamp = datetime.datetime.now().timestamp()
    random_seed = f"{key_uuid}-{timestamp}"
    key_hash = hashlib.sha256(random_seed.encode()).hexdigest()[:32]
    return f"{MCP_KEY_PREFIX}{key_hash}"

def save_key_metadata(key: str, metadata: Dict[str, Any]) -> bool:
    """
    Save key metadata to disk.
    
    Args:
        key: The MCP API key
        metadata: Key metadata
        
    Returns:
        Whether the operation was successful
    """
    try:
        file_path = os.path.join(MCP_KEYS_DIR, f"{key}.json")
        with open(file_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving key metadata: {e}")
        return False

def create_admin_mcp_key() -> Dict[str, Any]:
    """
    Create an admin MCP API key with full access.
    
    Returns:
        Key data including the key and metadata
    """
    # Generate key
    key = generate_secure_key()
    
    # Create metadata
    metadata = {
        "key": key,
        "owner": "admin",
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": None,  # Never expires
        "permissions": [
            "read:all",
            "write:all",
            "admin:all"
        ],
        "rate_limit": {
            "requests_per_minute": 1000,
            "requests_per_day": 100000
        },
        "status": "active"
    }
    
    # Save metadata
    success = save_key_metadata(key, metadata)
    
    if success:
        logger.info(f"Created admin MCP API key: {key}")
    else:
        logger.error("Failed to create admin MCP API key")
    
    return {
        "key": key,
        "metadata": metadata,
        "success": success
    }

if __name__ == "__main__":
    # Create admin MCP API key
    result = create_admin_mcp_key()
    
    if result["success"]:
        print("\n====== MCP API KEY GENERATED SUCCESSFULLY ======")
        print(f"API Key: {result['key']}")
        print("\nPermissions: Full admin access")
        print("Expires: Never")
        print("\nStore this key securely as it provides full access to the MCP system.")
        print("======================================================\n")
    else:
        print("\nERROR: Failed to generate MCP API key.")