"""
Test script for domain data collector

This script tests the domain data collector module by running a collection
for a sample category and visualizing the results.
"""

import json
import os
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

import domain_data_collector
import domain_memory_tracker
import notification_agent
import mcp_integration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_domain_collection():
    """Test domain data collection with OpenAI."""
    print("\n=== Testing Domain Data Collection ===\n")
    
    # Test categories
    test_categories = ["Technology", "Finance", "News"]
    
    # Run collection for each category
    all_results = []
    
    for category in test_categories:
        print(f"\nCollecting domain data for category: {category}")
        result = domain_data_collector.collect_domain_data(category, ["gpt-4o"])
        all_results.append(result)
        
        # Print domains found
        if "results" in result and "gpt-4o" in result["results"]:
            domains = result["results"]["gpt-4o"]["domains"]
            print(f"Found {len(domains)} domains:")
            for i, domain in enumerate(domains):
                print(f"{i+1}. {domain}")
        else:
            print("No domains found or error occurred.")
            
        # Wait a bit between requests to avoid rate limiting
        time.sleep(2)
    
    # Save results
    os.makedirs("data/results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f"data/results/domain_collection_{timestamp}.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to data/results/domain_collection_{timestamp}.json")
    
    return all_results

def test_memory_tracking():
    """Test memory tracking with sample data."""
    print("\n=== Testing Domain Memory Tracking ===\n")
    
    # Test domain
    domain = "example.com"
    model = "gpt-4o"
    category = "Technology"
    
    # Add some sample rankings
    current_timestamp = datetime.now()
    
    # Update rank a few times with different positions
    ranks = [5, 3, 7, 2, 4]
    
    for i, rank in enumerate(ranks):
        # Create timestamp with some time difference
        timestamp = current_timestamp.replace(day=current_timestamp.day - i)
        
        print(f"Adding rank {rank} for {domain} at {timestamp}")
        
        domain_memory_tracker.update_domain_rank(
            domain=domain,
            model=model,
            query_category=category,
            rank=rank,
            query_text=f"Test query for {category}",
            timestamp=timestamp.isoformat()
        )
    
    # Get rank history
    history = domain_memory_tracker.get_rank_history(domain, model, category)
    
    print(f"\nRank history for {domain}:")
    for entry in history:
        print(f"  {entry['timestamp']}: Rank {entry['rank']}")
    
    # Calculate memory metrics
    decay = domain_memory_tracker.get_memory_decay(domain, model, category)
    
    print(f"\nMemory decay metrics for {domain}:")
    if decay and "models" in decay and model in decay["models"] and category in decay["models"][model]:
        metrics = decay["models"][model][category]
        print(f"  Decay score: {metrics['decay_score']}")
        print(f"  Trend: {metrics['trend']}")
        print(f"  Stability: {metrics['stability']}")
        print(f"  Volatility: {metrics['volatility']}")
    else:
        print("  No memory decay metrics found.")
    
    return history

def test_notification():
    """Test notification system."""
    print("\n=== Testing Notification System ===\n")
    
    # Create a test notification
    notification_id = notification_agent.create_notification(
        title="Test Notification",
        message="This is a test notification from the domain data collector test script.",
        severity="info",
        category="test",
        source="test_script"
    )
    
    print(f"Created notification with ID: {notification_id}")
    
    # Get the notification
    notification = notification_agent.get_notification(notification_id)
    
    print(f"\nNotification details:")
    print(f"  Title: {notification['title']}")
    print(f"  Message: {notification['message']}")
    print(f"  Severity: {notification['severity']}")
    print(f"  Category: {notification['category']}")
    print(f"  Created: {notification['created_at']}")
    print(f"  Status: {notification['status']}")
    
    return notification

def test_mcp_integration():
    """Test MCP integration."""
    print("\n=== Testing MCP Integration ===\n")
    
    # Test domain
    domain = "example.com"
    model = "gpt-4o"
    category = "Technology"
    
    # Publish domain ranking
    ranking_result = mcp_integration.publish_domain_ranking(
        domain=domain,
        model=model,
        query_category=category,
        rank=3,
        query_text="What are the best technology websites?"
    )
    
    print(f"Published domain ranking:")
    print(f"  Result: {ranking_result}")
    
    # Publish memory decay
    decay_result = mcp_integration.publish_memory_decay(
        domain=domain,
        model=model,
        query_category=category,
        decay_score=0.75,
        trend="improving"
    )
    
    print(f"\nPublished memory decay:")
    print(f"  Result: {decay_result}")
    
    # Publish insight event
    event_result = mcp_integration.publish_insight_event(
        event_type="rank_improvement",
        domain=domain,
        model=model,
        query_category=category,
        details={
            "previous_rank": 5,
            "current_rank": 3,
            "delta": 2,
            "query_text": "What are the best technology websites?"
        }
    )
    
    print(f"\nPublished insight event:")
    print(f"  Result: {event_result}")
    
    return {
        "ranking": ranking_result,
        "decay": decay_result,
        "event": event_result
    }

def run_all_tests():
    """Run all tests."""
    collection_results = test_domain_collection()
    memory_results = test_memory_tracking()
    notification_result = test_notification()
    mcp_results = test_mcp_integration()
    
    print("\n=== All Tests Completed ===\n")
    
    return {
        "collection": collection_results,
        "memory": memory_results,
        "notification": notification_result,
        "mcp": mcp_results
    }

if __name__ == "__main__":
    run_all_tests()