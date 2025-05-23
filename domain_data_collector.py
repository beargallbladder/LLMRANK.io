"""
Domain Data Collector

This module collects real domain ranking data by querying LLM models.
It extracts domain citations and ranks from responses to build the domain memory database.
"""

import os
import json
import logging
import time
import re
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import domain_memory_tracker
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_QUERY_TEMPLATE = "What are the most trustworthy websites for {category}?"
CATEGORIES = [
    "Technology", "Finance", "Healthcare", "Education", "Entertainment",
    "Travel", "Food", "Sports", "News", "Shopping", "Social Media"
]
MAX_DOMAINS_PER_RESPONSE = 15
STANDARD_WAIT_TIME = 1  # seconds between API calls

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class DomainCollector:
    """Collects domain rankings from LLM models."""
    
    def __init__(self):
        """Initialize the domain collector."""
        self.models = {
            "gpt-4o": {
                "provider": "openai",
                "enabled": True
            },
            "claude-3-opus": {
                "provider": "anthropic",
                "enabled": False  # Not implemented in this version
            },
            "gemini-pro": {
                "provider": "google",
                "enabled": False  # Not implemented in this version
            }
        }
        
        self.last_query_time = {}  # Track last query time per model
    
    def _extract_domains_openai(self, response_text: str) -> List[str]:
        """
        Extract domain names from OpenAI response text.
        
        Args:
            response_text: Text response from OpenAI
            
        Returns:
            List of extracted domain names
        """
        # Look for domains mentioned directly
        domains = []
        
        # Common domain patterns with different formats
        patterns = [
            r'\b(?:https?://)?(?:www\.)?([a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)\b',  # matches domain.com, domain.co.uk
            r'\b([a-zA-Z0-9][a-zA-Z0-9-]*(?:\.[a-zA-Z0-9][a-zA-Z0-9-]*)+\.[a-zA-Z]{2,})\b',  # matches sub.domain.com
            r'(?<=\s)([a-zA-Z0-9-]+\.(?:com|org|net|edu|gov|io|co|ai|app))\b'  # matches domain.com specifically
        ]
        
        # Apply all patterns
        for pattern in patterns:
            matches = re.findall(pattern, response_text)
            for match in matches:
                # Clean up domain
                domain = match.lower()
                if domain not in domains:
                    domains.append(domain)
        
        # Check for numbered list format (1. example.com)
        numbered_pattern = r'\d+\.\s+(?:https?://)?(?:www\.)?([a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)'
        numbered_matches = re.findall(numbered_pattern, response_text)
        for match in numbered_matches:
            domain = match.lower()
            if domain not in domains:
                domains.append(domain)
        
        # If no domains found, try extracting from markdown links [Title](domain.com)
        if not domains:
            markdown_pattern = r'\[.*?\]\((?:https?://)?(?:www\.)?([^/]+)\)'
            markdown_matches = re.findall(markdown_pattern, response_text)
            for match in markdown_matches:
                domain = match.lower()
                if domain not in domains:
                    domains.append(domain)
        
        # Last resort: look for text that starts with www. or ends with .com, .org, etc.
        if len(domains) < 3:
            tld_pattern = r'\b(?:www\.)?([a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,})\b'
            tld_matches = re.findall(tld_pattern, response_text)
            for match in tld_matches:
                domain = match.lower()
                if domain not in domains:
                    domains.append(domain)
        
        return domains[:MAX_DOMAINS_PER_RESPONSE]
    
    def query_openai(self, query: str, model: str = "gpt-4o") -> Tuple[str, List[str]]:
        """
        Query OpenAI and extract domains from the response.
        
        Args:
            query: Query text
            model: Model name
            
        Returns:
            Tuple of (response_text, domains_list)
        """
        try:
            # Rate limiting
            now = time.time()
            if model in self.last_query_time:
                elapsed = now - self.last_query_time[model]
                if elapsed < STANDARD_WAIT_TIME:
                    time.sleep(STANDARD_WAIT_TIME - elapsed)
            
            self.last_query_time[model] = time.time()
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Please provide a comprehensive list of trustworthy websites for the requested category. Include the full domain names."},
                    {"role": "user", "content": query}
                ]
            )
            
            response_text = response.choices[0].message.content
            
            # Extract domains
            domains = self._extract_domains_openai(response_text)
            
            return response_text, domains
        except Exception as e:
            logger.error(f"Error querying OpenAI: {e}")
            return f"Error: {str(e)}", []
    
    def collect_domain_data(self, category: str, models: Optional[List[str]] = None) -> Dict:
        """
        Collect domain data for a category across models.
        
        Args:
            category: Category to query
            models: Optional list of models to use (defaults to all enabled models)
            
        Returns:
            Dictionary with collection results
        """
        if not models:
            models = [model for model, config in self.models.items() if config["enabled"]]
        
        query = DEFAULT_QUERY_TEMPLATE.format(category=category)
        results = {}
        
        for model in models:
            if model not in self.models:
                logger.warning(f"Unknown model: {model}")
                continue
                
            if not self.models[model]["enabled"]:
                logger.warning(f"Model not enabled: {model}")
                continue
                
            provider = self.models[model]["provider"]
            
            if provider == "openai":
                response_text, domains = self.query_openai(query, model)
                
                # Record results
                results[model] = {
                    "response": response_text,
                    "domains": domains,
                    "query": query
                }
                
                # Update domain memory tracker with rankings
                for i, domain in enumerate(domains):
                    rank = i + 1  # Rank 1 is first position
                    
                    try:
                        domain_memory_tracker.update_domain_rank(
                            domain=domain,
                            model=model,
                            query_category=category,
                            rank=rank,
                            query_text=query
                        )
                    except Exception as e:
                        logger.error(f"Error updating domain rank: {e}")
            else:
                # Not implemented for other providers in this version
                results[model] = {
                    "response": "Not implemented",
                    "domains": [],
                    "query": query
                }
        
        return {
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": results
        }
    
    def collect_all_categories(self, models: Optional[List[str]] = None, 
                             categories: Optional[List[str]] = None) -> List[Dict]:
        """
        Collect data for all categories.
        
        Args:
            models: Optional list of models to use
            categories: Optional list of categories to query (defaults to all categories)
            
        Returns:
            List of collection result dictionaries
        """
        if not categories:
            categories = CATEGORIES
        
        results = []
        
        for category in categories:
            logger.info(f"Collecting data for category: {category}")
            result = self.collect_domain_data(category, models)
            results.append(result)
        
        return results

# Create collector instance
collector = DomainCollector()

def collect_domain_data(category: str, models: Optional[List[str]] = None) -> Dict:
    """
    Collect domain data for a category across models.
    
    Args:
        category: Category to query
        models: Optional list of models to use
        
    Returns:
        Dictionary with collection results
    """
    return collector.collect_domain_data(category, models)

def collect_all_categories(models: Optional[List[str]] = None, 
                         categories: Optional[List[str]] = None) -> List[Dict]:
    """
    Collect data for all categories.
    
    Args:
        models: Optional list of models to use
        categories: Optional list of categories to query
        
    Returns:
        List of collection result dictionaries
    """
    return collector.collect_all_categories(models, categories)

def schedule_collection_job():
    """Schedule regular data collection for all categories."""
    import schedule
    import time
    import threading
    
    def run_collection():
        logger.info("Running scheduled collection job")
        collect_all_categories()
    
    # Schedule daily collection at midnight
    schedule.every().day.at("00:00").do(run_collection)
    
    # Run in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    logger.info("Collection job scheduled")
    
    return thread

if __name__ == "__main__":
    # Test with a single category
    print("Testing domain data collection...")
    result = collect_domain_data("Technology", ["gpt-4o"])
    
    # Print results
    if "results" in result and "gpt-4o" in result["results"]:
        domains = result["results"]["gpt-4o"]["domains"]
        print(f"\nFound {len(domains)} domains:")
        for i, domain in enumerate(domains):
            print(f"{i+1}. {domain}")
    else:
        print("No domains found or error occurred.")