"""
LLMPageRank Partner Key Creation

This script allows creating and activating API keys for LLMPageRank.com integration.
"""

import os
import sys
import logging
import api_key_manager as km

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_llmpagerank_key(api_key: str, environment: str = "production"):
    """
    Add an LLMPageRank.com API key to the system.
    
    Args:
        api_key: The LLMPageRank API key to add
        environment: The environment (development, staging, production)
    
    Returns:
        Success message if key was added
    """
    try:
        # Validate key format
        if not api_key.startswith("llmpr_"):
            logger.warning("Warning: LLMPageRank keys typically start with 'llmpr_'. Please verify the key.")
        
        # Add key to the system
        key_id = km.add_api_key(
            service="llmpagerank",
            key_value=api_key,
            environment=environment,
            description=f"LLMPageRank API key for {environment}"
        )
        
        logger.info(f"Successfully added LLMPageRank API key (ID: {key_id})")
        
        # Get service info to verify
        service_info = km.get_service_info("llmpagerank")
        
        return {
            "success": True,
            "key_id": key_id,
            "service": "llmpagerank",
            "environment": environment,
            "current_key": service_info.get("current_key") == key_id
        }
    
    except Exception as e:
        logger.error(f"Error adding LLMPageRank API key: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def check_llmpagerank_key():
    """
    Check if an LLMPageRank API key is configured and active.
    
    Returns:
        Status information about the key
    """
    try:
        # Get service info
        service_info = km.get_service_info("llmpagerank")
        
        # Check if key exists
        current_key_id = service_info.get("current_key")
        has_key = current_key_id is not None
        
        # Get key info if available
        key_info = {}
        if has_key:
            key_info = km.get_key_info("llmpagerank", key_id=current_key_id)
        
        return {
            "has_key": has_key,
            "key_id": current_key_id if has_key else None,
            "environment": key_info.get("environment") if has_key else None,
            "last_used": key_info.get("last_used") if has_key else None,
            "rotation_needed": service_info.get("rotation_needed", False)
        }
    
    except Exception as e:
        logger.error(f"Error checking LLMPageRank API key: {e}")
        return {
            "has_key": False,
            "error": str(e)
        }

def test_llmpagerank_key():
    """
    Test the configured LLMPageRank API key.
    
    Returns:
        Test results
    """
    try:
        # Get the API key
        api_key = km.get_api_key(
            service="llmpagerank",
            agent_name="key_tester"
        )
        
        if api_key is None:
            return {
                "success": False,
                "error": "No API key configured for LLMPageRank"
            }
        
        # For now, we just check if the key exists
        # In a real implementation, this would make a test request to the API
        
        return {
            "success": True,
            "message": "API key retrieved successfully"
            # Would include API response details in a real implementation
        }
    
    except Exception as e:
        logger.error(f"Error testing LLMPageRank API key: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python create_partner_key.py check")
        print("  python create_partner_key.py create <api_key> [environment]")
        print("  python create_partner_key.py test")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        result = check_llmpagerank_key()
        print("LLMPageRank API Key Status:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    
    elif command == "create":
        if len(sys.argv) < 3:
            print("Error: API key required")
            print("Usage: python create_partner_key.py create <api_key> [environment]")
            return
        
        api_key = sys.argv[2]
        environment = sys.argv[3] if len(sys.argv) > 3 else "production"
        
        result = create_llmpagerank_key(api_key, environment)
        
        if result["success"]:
            print(f"Successfully added LLMPageRank API key (ID: {result['key_id']})")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    elif command == "test":
        result = test_llmpagerank_key()
        
        if result["success"]:
            print("LLMPageRank API Key Test: SUCCESS")
            print(f"  {result.get('message', '')}")
        else:
            print("LLMPageRank API Key Test: FAILED")
            print(f"  Error: {result.get('error', 'Unknown error')}")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: check, create, test")

if __name__ == "__main__":
    main()