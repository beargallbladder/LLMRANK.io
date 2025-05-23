"""
LLMPageRank Frontend API Example

This script demonstrates how the llmpagerank.com frontend should authenticate
and access our backend API endpoints.
"""

import requests
import json
import logging
import os
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_URL = "http://localhost:5050"  # Local API server

def get_frontend_api_key() -> Optional[str]:
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

def make_authenticated_request(endpoint: str, api_key: str) -> Dict:
    """
    Make an authenticated request to the API.
    
    Args:
        endpoint: API endpoint to request
        api_key: API key to use for authentication
        
    Returns:
        Response data
    """
    url = f"{API_URL}{endpoint}"
    
    # Set up headers with the API key in the Authorization header
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        logger.info(f"Making request to {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            logger.info(f"Request successful: {url}")
            return response.json()
        else:
            logger.error(f"Request failed: {url} - {response.status_code} - {response.text}")
            return {"error": f"Request failed with status code {response.status_code}"}
    except Exception as e:
        logger.error(f"Request exception: {url} - {e}")
        return {"error": str(e)}

def main():
    """Main function."""
    # Get the frontend API key
    api_key = get_frontend_api_key()
    
    if not api_key:
        logger.error("No frontend API key found. Please run setup_llmpagerank_frontend_key.py create first.")
        return
    
    logger.info(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Example 1: Get health status
    logger.info("\nExample 1: Get health status")
    health_data = make_authenticated_request("/mcp/health", api_key)
    print(json.dumps(health_data, indent=2))
    
    # Example 2: Get RankLLM input data
    logger.info("\nExample 2: Get RankLLM input data")
    rankllm_data = make_authenticated_request("/mcp/rankllm_input", api_key)
    print(json.dumps(rankllm_data, indent=2))
    
    # Example 3: Get drift events for a category
    logger.info("\nExample 3: Get drift events for 'technology' category")
    drift_data = make_authenticated_request("/mcp/drift_events/technology", api_key)
    print(json.dumps(drift_data, indent=2))
    
    # Example 4: Get trust context for a domain
    logger.info("\nExample 4: Get trust context for 'example.com'")
    context_data = make_authenticated_request("/mcp/context/example.com", api_key)
    print(json.dumps(context_data, indent=2))
    
    logger.info("\nThese examples show how llmpagerank.com should authenticate with our backend API.")
    logger.info("Include the API key in the X-API-Key header for all requests.")

if __name__ == "__main__":
    main()