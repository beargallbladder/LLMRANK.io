"""
MCP System Integration Test

This script runs a full system integration test to verify that all components
of the LLMPageRank system are working correctly together.
"""

import os
import sys
import json
import logging
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MCP_API_KEY = "mcp_81b5be8a0aeb934314741b4c3f4b9436"
MCP_API_URL = "http://localhost:8000/api"
MCP_LOGO_API_URL = "http://localhost:6500/api"
TEST_DOMAINS = [
    "apple.com",
    "google.com",
    "microsoft.com",
    "amazon.com",
    "meta.com",
    "netflix.com",
    "tesla.com",
    "walmart.com",
    "target.com"
]

class TestResult:
    """Class to track test results."""
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.start_time = time.time()
        self.end_time = None
        self.success = False
        self.response_time = None
        self.status_code = None
        self.error = None
        self.response_data = None
    
    def complete(self, success: bool, status_code: Optional[int] = None, 
                response_data: Any = None, error: Optional[str] = None):
        """
        Complete the test result.
        
        Args:
            success: Whether the test succeeded
            status_code: Response status code
            response_data: Response data
            error: Error message
        """
        self.end_time = time.time()
        self.response_time = self.end_time - self.start_time
        self.success = success
        self.status_code = status_code
        self.response_data = response_data
        self.error = error
    
    def __str__(self) -> str:
        """
        Get string representation of test result.
        
        Returns:
            String representation
        """
        status = "✓ PASS" if self.success else "✗ FAIL"
        time_str = f"{self.response_time:.3f}s" if self.response_time else "N/A"
        error_str = f" - {self.error}" if self.error else ""
        
        return f"{status} | {self.name} | {time_str} | {self.url}{error_str}"

def test_mcp_api_health() -> TestResult:
    """
    Test MCP API health.
    
    Returns:
        Test result
    """
    url = f"{MCP_API_URL}/health"
    result = TestResult("MCP API Health", url)
    
    try:
        response = requests.get(url)
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_mcp_api_auth() -> TestResult:
    """
    Test MCP API authentication.
    
    Returns:
        Test result
    """
    url = f"{MCP_API_URL}/auth/validate"
    result = TestResult("MCP API Auth", url)
    
    try:
        response = requests.post(
            url,
            headers={"api-key": MCP_API_KEY}
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_mcp_logo_api_health() -> TestResult:
    """
    Test MCP Logo API health.
    
    Returns:
        Test result
    """
    url = f"{MCP_LOGO_API_URL}/health"
    result = TestResult("MCP Logo API Health", url)
    
    try:
        response = requests.get(url)
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_logo_retrieval(domain: str) -> TestResult:
    """
    Test logo retrieval for a domain.
    
    Args:
        domain: Domain to test
        
    Returns:
        Test result
    """
    url = f"{MCP_LOGO_API_URL}/logos/{domain}"
    result = TestResult(f"Logo Retrieval ({domain})", url)
    
    try:
        response = requests.get(
            url,
            headers={"api-key": MCP_API_KEY}
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_bulk_logo_retrieval(domains: List[str]) -> TestResult:
    """
    Test bulk logo retrieval.
    
    Args:
        domains: Domains to test
        
    Returns:
        Test result
    """
    url = f"{MCP_LOGO_API_URL}/logos/bulk"
    result = TestResult("Bulk Logo Retrieval", url)
    
    try:
        response = requests.post(
            url,
            headers={"api-key": MCP_API_KEY},
            json={"domains": domains}
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_mcp_brands_endpoint() -> TestResult:
    """
    Test MCP brands endpoint.
    
    Returns:
        Test result
    """
    url = f"{MCP_API_URL}/mcp/brands"
    result = TestResult("MCP Brands Endpoint", url)
    
    try:
        response = requests.post(
            url,
            headers={"api-key": MCP_API_KEY},
            json={
                "request_id": "test_123",
                "timestamp": datetime.now().isoformat()
            }
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_mcp_insights_endpoint() -> TestResult:
    """
    Test MCP insights endpoint.
    
    Returns:
        Test result
    """
    url = f"{MCP_API_URL}/mcp/insights"
    result = TestResult("MCP Insights Endpoint", url)
    
    try:
        response = requests.post(
            url,
            headers={"api-key": MCP_API_KEY},
            json={
                "request_id": "test_123",
                "timestamp": datetime.now().isoformat(),
                "limit": 5,
                "offset": 0
            }
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def test_mcp_statistics_endpoint() -> TestResult:
    """
    Test MCP statistics endpoint.
    
    Returns:
        Test result
    """
    url = f"{MCP_API_URL}/mcp/statistics"
    result = TestResult("MCP Statistics Endpoint", url)
    
    try:
        response = requests.get(
            url,
            headers={"api-key": MCP_API_KEY}
        )
        result.complete(
            success=response.status_code == 200,
            status_code=response.status_code,
            response_data=response.json()
        )
    except Exception as e:
        result.complete(success=False, error=str(e))
    
    return result

def run_all_tests() -> List[TestResult]:
    """
    Run all tests.
    
    Returns:
        List of test results
    """
    results = []
    
    # Core API tests
    results.append(test_mcp_api_health())
    results.append(test_mcp_api_auth())
    results.append(test_mcp_logo_api_health())
    
    # Logo retrieval tests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_domain = {executor.submit(test_logo_retrieval, domain): domain for domain in TEST_DOMAINS[:5]}
        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error testing logo retrieval for {domain}: {e}")
    
    # Bulk logo retrieval test
    results.append(test_bulk_logo_retrieval(TEST_DOMAINS))
    
    # MCP API endpoint tests
    results.append(test_mcp_brands_endpoint())
    results.append(test_mcp_insights_endpoint())
    results.append(test_mcp_statistics_endpoint())
    
    return results

def print_test_report(results: List[TestResult]) -> None:
    """
    Print test report.
    
    Args:
        results: List of test results
    """
    pass_count = sum(1 for r in results if r.success)
    fail_count = len(results) - pass_count
    pass_rate = pass_count / len(results) * 100 if results else 0
    
    print("\n===== MCP SYSTEM INTEGRATION TEST REPORT =====\n")
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {fail_count}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    print("\nTest Results:")
    for result in results:
        print(f"  {result}")
    
    if fail_count > 0:
        print("\nFailed Tests:")
        for result in results:
            if not result.success:
                print(f"  {result}")
                if result.error:
                    print(f"    Error: {result.error}")
    
    print("\n==============================================\n")

def main():
    """Main function."""
    logger.info("Starting MCP system integration test")
    
    try:
        results = run_all_tests()
        print_test_report(results)
        
        # Determine success based on pass rate
        pass_count = sum(1 for r in results if r.success)
        pass_rate = pass_count / len(results) * 100 if results else 0
        
        if pass_rate >= 80:
            logger.info(f"Integration test passed with {pass_rate:.1f}% success rate")
            return 0
        else:
            logger.error(f"Integration test failed with {pass_rate:.1f}% success rate")
            return 1
    except Exception as e:
        logger.error(f"Error running integration test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())