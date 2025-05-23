"""
MCP API Client Example

This script demonstrates how to use the MCP API to access data
programmatically from your external monitoring tools.
"""

import os
import json
import requests
import datetime
from tabulate import tabulate
from typing import Dict, List, Any, Optional

# MCP API configuration
API_BASE_URL = "http://localhost:8000/api"
API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"  # The key generated earlier

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make an API request to the MCP API.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Request data
        
    Returns:
        API response
    """
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {"api-key": API_KEY}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data if data else {})
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error making API request: {e}")
        return {"error": str(e)}

def print_section_header(title: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def validate_api_key() -> bool:
    """
    Validate the API key.
    
    Returns:
        Whether the key is valid
    """
    print_section_header("Validating API Key")
    
    result = make_api_request("auth/validate", method="POST")
    
    if "error" in result:
        print(f"API key validation failed: {result['error']}")
        return False
    
    print(f"API key is valid: {result['valid']}")
    print(f"Owner: {result['owner']}")
    print(f"Permissions: {', '.join(result['permissions'])}")
    
    return result.get("valid", False)

def get_system_statistics() -> None:
    """Get and display system statistics."""
    print_section_header("System Statistics")
    
    result = make_api_request("mcp/statistics")
    
    if "error" in result:
        print(f"Error getting statistics: {result['error']}")
        return
    
    print(f"Timestamp: {result['timestamp']}")
    print(f"Total Brands: {result['brand_count']}")
    print(f"Total Categories: {result['category_count']}")
    print(f"Total Rivalries: {result['rivalry_count']}")
    
    print("\nCategory Breakdown:")
    
    if "categories" in result:
        categories = []
        for category, count in result["categories"].items():
            categories.append([category, count])
        
        if categories:
            headers = ["Category", "Brand Count"]
            print(tabulate(categories, headers=headers, tablefmt="grid"))

def get_brand_data(domain: Optional[str] = None, category: Optional[str] = None) -> None:
    """
    Get and display brand data.
    
    Args:
        domain: Domain to filter by
        category: Category to filter by
    """
    print_section_header(f"Brand Data" + (f" for {domain}" if domain else "") + (f" in {category}" if category else ""))
    
    request_data = {
        "request_id": f"req_{datetime.datetime.now().timestamp()}",
        "timestamp": datetime.datetime.now().isoformat(),
        "domain": domain,
        "category": category
    }
    
    result = make_api_request("mcp/brands", method="POST", data=request_data)
    
    if "error" in result:
        print(f"Error getting brand data: {result['error']}")
        return
    
    print(f"Found {result['count']} brands")
    
    if result['count'] == 0:
        return
    
    # Display brand data
    brands = []
    for brand in result["brands"]:
        brands.append([
            brand.get("name", "N/A"),
            brand.get("domain", "N/A"),
            brand.get("category", "N/A"),
            brand.get("memory_vulnerability_score", "N/A")
        ])
    
    if brands:
        headers = ["Name", "Domain", "Category", "MVS"]
        print(tabulate(brands, headers=headers, tablefmt="grid"))

def get_rivalry_data(category: Optional[str] = None, min_delta: Optional[float] = None) -> None:
    """
    Get and display rivalry data.
    
    Args:
        category: Category to filter by
        min_delta: Minimum delta to filter by
    """
    print_section_header(f"Rivalry Data" + (f" for {category}" if category else ""))
    
    request_data = {
        "request_id": f"req_{datetime.datetime.now().timestamp()}",
        "timestamp": datetime.datetime.now().isoformat(),
        "category": category,
        "min_delta": min_delta,
        "limit": 10,
        "offset": 0
    }
    
    result = make_api_request("mcp/rivalries", method="POST", data=request_data)
    
    if "error" in result:
        print(f"Error getting rivalry data: {result['error']}")
        return
    
    print(f"Found {result['count']} rivalries (of {result['total']} total)")
    
    if result['count'] == 0:
        return
    
    # Display rivalry data
    rivalries = []
    for rivalry in result["rivalries"]:
        top_brand = rivalry.get("top_brand", {})
        laggard_brand = rivalry.get("laggard_brand", {})
        
        rivalries.append([
            rivalry.get("category", "N/A"),
            top_brand.get("name", top_brand.get("domain", "N/A")),
            top_brand.get("signal", "N/A"),
            laggard_brand.get("name", laggard_brand.get("domain", "N/A")),
            laggard_brand.get("signal", "N/A"),
            rivalry.get("delta", "N/A"),
            "Yes" if rivalry.get("outcite_ready", False) else "No"
        ])
    
    if rivalries:
        headers = ["Category", "Top Brand", "Signal", "Laggard Brand", "Signal", "Delta", "Outcite Ready"]
        print(tabulate(rivalries, headers=headers, tablefmt="grid"))

def get_insight_data(domain: Optional[str] = None, category: Optional[str] = None) -> None:
    """
    Get and display insight data.
    
    Args:
        domain: Domain to filter by
        category: Category to filter by
    """
    print_section_header(f"Insight Data" + (f" for {domain}" if domain else "") + (f" in {category}" if category else ""))
    
    request_data = {
        "request_id": f"req_{datetime.datetime.now().timestamp()}",
        "timestamp": datetime.datetime.now().isoformat(),
        "domain": domain,
        "category": category,
        "limit": 10,
        "offset": 0
    }
    
    result = make_api_request("mcp/insights", method="POST", data=request_data)
    
    if "error" in result:
        print(f"Error getting insight data: {result['error']}")
        return
    
    print(f"Found {result['count']} insights")
    
    if result['count'] == 0:
        return
    
    # Display insight data
    insights = []
    for insight in result["insights"]:
        insights.append([
            insight.get("domain", "N/A"),
            insight.get("title", "N/A"),
            insight.get("type", "N/A"),
            insight.get("timestamp", "N/A")
        ])
    
    if insights:
        headers = ["Domain", "Title", "Type", "Timestamp"]
        print(tabulate(insights, headers=headers, tablefmt="grid"))

def main():
    """Main function."""
    print("\n==== LLMPageRank MCP API Client Example ====\n")
    
    # Validate API key
    if not validate_api_key():
        return
    
    # Get system statistics
    get_system_statistics()
    
    # Get technology brands
    get_brand_data(category="Technology")
    
    # Get rivalry data for technology
    get_rivalry_data(category="Technology")
    
    # Get insights for a specific domain
    get_insight_data(domain="apple.com")
    
    print("\n==== Example Complete ====\n")

if __name__ == "__main__":
    main()