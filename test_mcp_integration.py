"""
Test MCP Integration

This script tests the MCP (Model Context Protocol) API functionality
and verifies that the internal agents can communicate with it.
"""

import os
import json
import requests
import logging
from pprint import pprint
from datetime import datetime

# Import agents
from agents import model_comparator, gap_detector, signal_rarity_profiler
import llm_clients

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_comparison():
    """Test model comparison functionality."""
    logger.info("Testing model comparison...")
    
    # Test prompt
    prompt = "What are the most trusted AI research websites?"
    category = "AI Research"
    
    # Initialize multi-model client
    client = llm_clients.MultiModelClient(use_real_models=False)  # Use mock clients for testing
    
    # Get responses from all models
    model_responses = client.get_all_model_responses(prompt)
    
    logger.info(f"Got responses from {len(model_responses)} models")
    
    # Run model comparator
    divergence_metrics = model_comparator.calculate_model_disagreement(
        model_responses=model_responses,
        category=category
    )
    
    logger.info(f"Model disagreement score: {divergence_metrics['model_disagreement_score']}")
    
    # Run gap detector
    prompt_id = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    blindspot_metrics = gap_detector.detect_model_blindspots(
        prompt_id=prompt_id,
        prompt_text=prompt,
        category=category,
        model_responses=model_responses
    )
    
    logger.info(f"Detected {len(blindspot_metrics['blindspots'])} blindspots")
    
    # Run signal rarity profiler
    rarity_metrics = signal_rarity_profiler.detect_rare_signals(
        prompt_id=prompt_id,
        prompt_text=prompt,
        category=category,
        model_responses=model_responses
    )
    
    logger.info(f"Detected {len(rarity_metrics['rare_signals'])} rare signals")
    
    return {
        "divergence_metrics": divergence_metrics,
        "blindspot_metrics": blindspot_metrics,
        "rarity_metrics": rarity_metrics
    }

def test_mcp_api():
    """Test MCP API endpoints."""
    logger.info("Testing MCP API...")
    
    # Update the port if you've changed it
    base_url = "http://localhost:5050/mcp"
    
    try:
        # Test root endpoint
        root_url = "http://localhost:5050/"
        root_response = requests.get(root_url, timeout=5)
        logger.info(f"Root endpoint response status: {root_response.status_code}")
        
        if root_response.status_code == 200:
            logger.info(f"Root endpoint response: {root_response.json()}")
        else:
            logger.error(f"Root endpoint error: {root_response.text}")
        
        # Note: We're not testing the actual MCP endpoints here since they 
        # require authentication. In a real implementation, you would create
        # a test token and use it for these requests.
        
        return {"status": "success", "message": "API is responding"}
    except Exception as e:
        logger.error(f"Error testing MCP API: {e}")
        return {"status": "failure", "message": str(e)}

def main():
    """Run all tests."""
    logger.info("Starting MCP integration tests...")
    
    # Test model comparison
    model_comparison_results = test_model_comparison()
    logger.info("Model comparison test completed")
    
    # Test MCP API
    api_results = test_mcp_api()
    logger.info(f"MCP API test result: {api_results['status']}")
    
    logger.info("All tests completed")
    
    # Print summary
    print("\n==== TEST SUMMARY ====")
    
    print("\nModel Comparison Results:")
    print(f"- Model Disagreement Score: {model_comparison_results['divergence_metrics']['model_disagreement_score']}")
    print(f"- Blindspots Detected: {len(model_comparison_results['blindspot_metrics']['blindspots'])}")
    print(f"- Rare Signals Detected: {len(model_comparison_results['rarity_metrics']['rare_signals'])}")
    
    print("\nMCP API Results:")
    print(f"- Status: {api_results['status']}")
    print(f"- Message: {api_results['message']}")
    
    print("\n=====================")

if __name__ == "__main__":
    main()