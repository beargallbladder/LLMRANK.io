"""
Test script for MCP API endpoints
"""

import requests
import json
import sys

# Base URL for the MCP API
BASE_URL = "http://localhost:8080/mcp"

# Test API key (for testing purposes only)
TEST_API_KEY = "test_key_b7d29f38c6144ea3b1982b4a4429018d"

def test_endpoint(endpoint, method="GET", data=None):
    """
    Test a specific MCP API endpoint.
    
    Args:
        endpoint: API endpoint to test
        method: HTTP method (GET, POST, etc.)
        data: Data to send (for POST, PUT, etc.)
    
    Returns:
        Response from the API
    """
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TEST_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Response:")
            try:
                json_response = response.json()
                print(json.dumps(json_response, indent=2))
                return json_response
            except json.JSONDecodeError:
                print("Invalid JSON response")
                print(response.text)
                return None
        else:
            print(f"Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_all_endpoints():
    """Test all MCP API endpoints."""
    # Test health endpoint
    test_endpoint("health")
    
    # Test context endpoint
    test_endpoint("context/asana.com")
    
    # Test drift events endpoint
    test_endpoint("drift_events/SaaS%20Productivity")
    
    # Test prompt suggestions endpoint
    test_endpoint("prompt_suggestions/trust_assessment")
    
    # Test FOMA threats endpoint
    test_endpoint("foma_threats/asana.com")
    
    # Test RankLLM leaderboard endpoint
    test_endpoint("rankllm_input")
    
    # Test agent registration endpoint
    agent_data = {
        "agent_id": "test_agent",
        "status": "active",
        "cookies_awarded": 0,
        "last_prompt": None,
        "foma_triggered": False
    }
    test_endpoint("agent_register", method="POST", data=agent_data)
    
    # Test agent update endpoint
    update_data = {
        "status": "active",
        "cookies_awarded": 5,
        "last_prompt": "Test prompt",
        "foma_triggered": True
    }
    test_endpoint(f"agent_update/test_agent", method="PUT", data=update_data)

if __name__ == "__main__":
    # Check if specific endpoint is provided
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        test_endpoint(endpoint)
    else:
        test_all_endpoints()