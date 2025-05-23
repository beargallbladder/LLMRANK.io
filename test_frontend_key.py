"""
Test LLMPageRank Frontend API Key

This script tests the frontend API key against the backend API server.
"""

import requests
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_URL = "http://localhost:5050"  # Local API server

def get_frontend_api_key():
    """Get the frontend API key."""
    try:
        if os.path.exists("data/api_keys/frontend_key.json"):
            with open("data/api_keys/frontend_key.json", "r") as f:
                key_info = json.load(f)
                return key_info.get("key")
        return None
    except Exception as e:
        logger.error(f"Error getting frontend API key: {e}")
        return None

def test_key_validation(api_key):
    """Test API key validation endpoint."""
    endpoint = f"{API_URL}/mcp/validate_key/{api_key}"
    
    try:
        logger.info(f"Testing key validation: {endpoint}")
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Key validation result: {result}")
            return result
        else:
            logger.error(f"Error validating key: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during key validation: {e}")
        return None

def test_api_endpoints(api_key):
    """Test various API endpoints with the frontend key."""
    headers = {"X-API-Key": api_key}
    
    endpoints = [
        "/mcp/health",
        "/mcp/rankllm_input",
        "/mcp/drift_events/technology"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{API_URL}{endpoint}"
        
        try:
            logger.info(f"Testing endpoint: {url}")
            response = requests.get(url, headers=headers)
            
            status = response.status_code
            results[endpoint] = {
                "status": status,
                "success": 200 <= status < 300
            }
            
            if status == 200:
                logger.info(f"Success: {endpoint}")
            else:
                logger.warning(f"Failed ({status}): {endpoint} - {response.text}")
                
        except Exception as e:
            logger.error(f"Exception testing {endpoint}: {e}")
            results[endpoint] = {
                "status": "error",
                "success": False,
                "error": str(e)
            }
    
    return results

def main():
    """Main function."""
    logger.info("Testing LLMPageRank Frontend API Key")
    
    # Get the frontend API key
    api_key = get_frontend_api_key()
    
    if not api_key:
        logger.error("No frontend API key found. Please run setup_llmpagerank_frontend_key.py create first.")
        return
    
    logger.info(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Test key validation
    validation = test_key_validation(api_key)
    
    if validation and validation.get("valid"):
        logger.info("✓ API key is valid")
        logger.info(f"  Plan: {validation.get('plan')}")
        logger.info(f"  Scope: {', '.join(validation.get('scope', []))}")
        logger.info(f"  Usage: {validation.get('usage')} / {validation.get('limit')}")
        
        # Test API endpoints
        endpoint_results = test_api_endpoints(api_key)
        
        # Report results
        logger.info("\nEndpoint Test Results:")
        for endpoint, result in endpoint_results.items():
            status = "✓" if result.get("success") else "✗"
            logger.info(f"  {status} {endpoint}: {result.get('status')}")
        
        # Overall success?
        success_count = sum(1 for r in endpoint_results.values() if r.get("success"))
        if success_count == len(endpoint_results):
            logger.info("\n✅ All tests passed! The frontend API key is working correctly.")
        else:
            logger.warning(f"\n⚠️ {success_count}/{len(endpoint_results)} tests passed.")
    else:
        logger.error("✗ API key validation failed.")
        if validation:
            logger.error(f"  Reason: {validation.get('reason')}")

if __name__ == "__main__":
    main()