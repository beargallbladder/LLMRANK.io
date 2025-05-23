"""
LLMPageRank V3 Crawl Planner

This module handles the prioritization of domains for crawling based on
commercial intent, visibility investment, and other metrics specified in the V3 PRD.
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Import from project modules
from config import CATEGORIES, DATA_DIR
import database as db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SCAN_PROFILES_DIR = f"{DATA_DIR}/scan_profiles"
BENCHMARK_SETS_DIR = f"{DATA_DIR}/category_benchmark_sets"
SCHEDULE_OVERRIDE_FILE = f"{DATA_DIR}/schedule_override.json"

# Ensure directories exist
os.makedirs(SCAN_PROFILES_DIR, exist_ok=True)
os.makedirs(BENCHMARK_SETS_DIR, exist_ok=True)

class CrawlPlanner:
    """
    Manages domain crawl prioritization according to V3 specifications.
    """
    
    def __init__(self):
        """Initialize the crawl planner with configuration."""
        self.domains_by_category = {}
        self.scan_profiles = {}
        self.benchmark_sets = {}
        self.schedule_overrides = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing domains, scan profiles, and benchmark sets."""
        # Load domains by category
        self.domains_by_category = db.load_domains_by_category()
        
        # Load scan profiles if they exist
        for domain_file in os.listdir(SCAN_PROFILES_DIR):
            if domain_file.endswith('.json'):
                domain = domain_file.replace('.json', '')
                profile_path = os.path.join(SCAN_PROFILES_DIR, domain_file)
                try:
                    with open(profile_path, 'r') as f:
                        self.scan_profiles[domain] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading scan profile for {domain}: {e}")
        
        # Load benchmark sets if they exist
        for category_file in os.listdir(BENCHMARK_SETS_DIR):
            if category_file.endswith('.json'):
                category = category_file.replace('.json', '')
                benchmark_path = os.path.join(BENCHMARK_SETS_DIR, category_file)
                try:
                    with open(benchmark_path, 'r') as f:
                        self.benchmark_sets[category] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading benchmark set for {category}: {e}")
        
        # Load schedule overrides if they exist
        if os.path.exists(SCHEDULE_OVERRIDE_FILE):
            try:
                with open(SCHEDULE_OVERRIDE_FILE, 'r') as f:
                    self.schedule_overrides = json.load(f)
            except Exception as e:
                logger.error(f"Error loading schedule overrides: {e}")
    
    def _score_commercial_intent(self, domain_info: Dict) -> float:
        """
        Score a domain's commercial intent based on metadata.
        
        Args:
            domain_info: Domain information including metadata
        
        Returns:
            Commercial intent score (0-1)
        """
        metadata = domain_info.get('metadata', {})
        category = domain_info.get('category', '')
        
        # Base score
        score = 0.0
        
        # Category-based scoring (some categories have inherently higher commercial intent)
        high_intent_categories = ['finance', 'saas', 'ecommerce', 'enterprise_tech']
        medium_intent_categories = ['healthcare', 'legal', 'ai_infrastructure']
        
        if category in high_intent_categories:
            score += 0.3
        elif category in medium_intent_categories:
            score += 0.2
        else:
            score += 0.1
        
        # Metadata-based scoring
        if metadata.get('has_ads', False):
            score += 0.2
        if metadata.get('has_conversion_path', False):
            score += 0.25
        if metadata.get('has_ecommerce', False):
            score += 0.25
        if metadata.get('has_pricing_page', False):
            score += 0.2
        
        # Normalize to 0-1
        return min(1.0, score)
    
    def _score_visibility_investment(self, domain_info: Dict) -> float:
        """
        Score a domain's visibility investment based on metadata.
        
        Args:
            domain_info: Domain information including metadata
        
        Returns:
            Visibility investment score (0-1)
        """
        metadata = domain_info.get('metadata', {})
        
        # Base score
        score = 0.0
        
        # Metadata-based scoring
        if metadata.get('has_schema', False):
            score += 0.3
        if metadata.get('has_seo_stack', False):
            score += 0.2
        if metadata.get('has_amp', False):
            score += 0.15
        if metadata.get('has_meta_tags', False):
            score += 0.15
        if metadata.get('content_freshness', 0) > 0.7:
            score += 0.2
        
        # Normalize to 0-1
        return min(1.0, score)
    
    def _has_complete_peer_set(self, domain: str, category: str) -> bool:
        """
        Check if a domain has a complete peer set (≥3 domains) in its category.
        
        Args:
            domain: Domain name
            category: Domain category
        
        Returns:
            True if the domain has a complete peer set, False otherwise
        """
        # Get all domains in the category
        category_domains = self.domains_by_category.get(category, [])
        
        # If benchmark set already exists, use that
        if category in self.benchmark_sets:
            benchmark = self.benchmark_sets[category]
            if benchmark.get('primary_domain') == domain and len(benchmark.get('peer_set', [])) >= 3:
                return True
        
        # Count domains in category (excluding the current domain)
        peer_count = sum(1 for d in category_domains if d.get('domain') != domain)
        
        # Need at least 3 peers
        return peer_count >= 3
    
    def calculate_qa_intensity(self, domain: str) -> float:
        """
        Calculate QA intensity score for a domain based on signal volatility,
        model disagreement, and prompt effectiveness.
        
        Args:
            domain: Domain name
        
        Returns:
            QA intensity score (0-1)
        """
        # Get domain test results
        domain_results = db.get_domain_history(domain)
        
        if not domain_results:
            # No history, set default QA intensity
            return 0.5
        
        # Factors for QA intensity
        volatility = 0.0
        model_disagreement = 0.0
        prompt_efficacy = 0.0
        
        # Calculate signal volatility (based on score changes)
        if len(domain_results) >= 2:
            scores = [result.get('visibility_score', 0) for result in domain_results]
            volatility = np.std(scores) / max(1, np.mean(scores))
            # Normalize to 0-1
            volatility = min(1.0, volatility * 5)  # Scale factor to normalize
        
        # Calculate model disagreement
        latest_result = domain_results[0]
        citation_coverage = latest_result.get('citation_coverage', {})
        if citation_coverage:
            # Calculate variance in citation coverage across models
            coverage_values = list(citation_coverage.values())
            if coverage_values:
                model_disagreement = np.std(coverage_values) * 2  # Scale factor
                model_disagreement = min(1.0, model_disagreement)
        
        # Calculate prompt efficacy (based on number of successful citations)
        citation_counts = latest_result.get('citation_counts', {})
        if citation_counts:
            total_citations = 0
            total_prompts = 0
            
            for model, counts in citation_counts.items():
                direct = counts.get('direct', 0)
                paraphrased = counts.get('paraphrased', 0)
                none = counts.get('none', 0)
                
                total_citations += direct + paraphrased
                total_prompts += direct + paraphrased + none
            
            prompt_efficacy = 1.0 - (total_citations / max(1, total_prompts))
        
        # Combine factors (weighted average)
        qa_intensity = (volatility * 0.4) + (model_disagreement * 0.4) + (prompt_efficacy * 0.2)
        
        return qa_intensity
    
    def update_scan_profile(self, domain: str, domain_info: Dict) -> Dict:
        """
        Update scan profile for a domain with latest scoring.
        
        Args:
            domain: Domain name
            domain_info: Domain information
        
        Returns:
            Updated scan profile
        """
        # Get existing profile or create new one
        profile = self.scan_profiles.get(domain, {
            'domain': domain,
            'last_updated': time.time(),
            'scan_count': 0,
            'last_scan': None
        })
        
        # Update profile with new scores
        category = domain_info.get('category', '')
        commercial_score = self._score_commercial_intent(domain_info)
        visibility_score = self._score_visibility_investment(domain_info)
        qa_intensity = self.calculate_qa_intensity(domain)
        
        profile.update({
            'category': category,
            'commercial_intent_score': commercial_score,
            'visibility_investment_score': visibility_score,
            'qa_intensity_score': qa_intensity,
            'has_complete_peer_set': self._has_complete_peer_set(domain, category),
            'last_updated': time.time()
        })
        
        # Calculate priority score
        priority_score = (commercial_score * 0.4) + (visibility_score * 0.3) + (qa_intensity * 0.3)
        
        # Check for schedule override
        if domain in self.schedule_overrides:
            override = self.schedule_overrides[domain]
            priority_score = override.get('priority_override', priority_score)
            profile['priority_override'] = True
        else:
            profile['priority_override'] = False
        
        profile['priority_score'] = priority_score
        
        # Save profile
        profile_path = os.path.join(SCAN_PROFILES_DIR, f"{domain}.json")
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            # Update in-memory cache
            self.scan_profiles[domain] = profile
            
            logger.info(f"Updated scan profile for {domain} with priority score {priority_score:.2f}")
        except Exception as e:
            logger.error(f"Error saving scan profile for {domain}: {e}")
        
        return profile
    
    def create_benchmark_set(self, category: str) -> Dict:
        """
        Create a benchmark set for a category.
        
        Args:
            category: Category name
        
        Returns:
            Benchmark set information
        """
        # Get all domains in the category
        category_domains = self.domains_by_category.get(category, [])
        
        if len(category_domains) < 4:  # Need at least 4 domains (1 primary + 3 peers)
            return {
                'category': category,
                'primary_domain': None,
                'peer_set': [],
                'peer_set_size': 0,
                'benchmark_status': 'invalid_insufficient_domains'
            }
        
        # Score domains by priority (using commercial intent and visibility investment)
        scored_domains = []
        for domain_info in category_domains:
            domain = domain_info.get('domain', '')
            commercial_score = self._score_commercial_intent(domain_info)
            visibility_score = self._score_visibility_investment(domain_info)
            combined_score = (commercial_score * 0.6) + (visibility_score * 0.4)
            
            scored_domains.append({
                'domain': domain,
                'score': combined_score
            })
        
        # Sort by score (descending)
        scored_domains.sort(key=lambda x: x['score'], reverse=True)
        
        # Select primary domain (highest score)
        primary_domain = scored_domains[0]['domain'] if scored_domains else None
        
        # Select peer set (next N domains)
        peer_set_size = min(5, len(scored_domains) - 1)
        peer_set = [d['domain'] for d in scored_domains[1:peer_set_size+1]]
        
        # Create benchmark set
        benchmark_set = {
            'category': category,
            'primary_domain': primary_domain,
            'peer_set': peer_set,
            'peer_set_size': len(peer_set),
            'benchmark_status': 'valid' if len(peer_set) >= 3 else 'invalid_insufficient_peers'
        }
        
        # Save benchmark set
        benchmark_path = os.path.join(BENCHMARK_SETS_DIR, f"{category}.json")
        try:
            with open(benchmark_path, 'w') as f:
                json.dump(benchmark_set, f, indent=2)
            
            # Update in-memory cache
            self.benchmark_sets[category] = benchmark_set
            
            logger.info(f"Created benchmark set for {category} with {len(peer_set)} peers")
        except Exception as e:
            logger.error(f"Error saving benchmark set for {category}: {e}")
        
        return benchmark_set
    
    def create_all_benchmark_sets(self) -> Dict[str, Dict]:
        """
        Create benchmark sets for all categories.
        
        Returns:
            Dictionary of category benchmark sets
        """
        benchmark_sets = {}
        
        for category in self.domains_by_category.keys():
            benchmark_set = self.create_benchmark_set(category)
            benchmark_sets[category] = benchmark_set
        
        return benchmark_sets
    
    def prioritize_domains(self, limit: int = 50) -> List[Dict]:
        """
        Prioritize domains for crawling based on V3 criteria.
        
        Args:
            limit: Maximum number of domains to return
        
        Returns:
            List of domains sorted by priority
        """
        # Get all domains
        all_domains = []
        for category, domains in self.domains_by_category.items():
            for domain_info in domains:
                domain = domain_info.get('domain', '')
                if domain:
                    # Update scan profile with latest data
                    profile = self.update_scan_profile(domain, domain_info)
                    
                    # Add to list for sorting
                    all_domains.append({
                        'domain': domain,
                        'category': category,
                        'priority_score': profile['priority_score'],
                        'last_scan': profile.get('last_scan'),
                        'scan_count': profile.get('scan_count', 0),
                        'qa_intensity': profile.get('qa_intensity_score', 0.5)
                    })
        
        # Sort by priority score (descending)
        all_domains.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Return top N domains
        return all_domains[:limit]
    
    def run_daily_prioritization(self) -> Dict:
        """
        Run daily domain prioritization and benchmark set creation.
        
        Returns:
            Dictionary with prioritization results
        """
        start_time = time.time()
        logger.info("Starting daily crawl prioritization")
        
        # Reload data to ensure we have the latest
        self._load_data()
        
        # Create benchmark sets for all categories
        benchmark_sets = self.create_all_benchmark_sets()
        
        # Prioritize domains
        prioritized_domains = self.prioritize_domains(limit=100)
        
        # Prepare results summary
        results = {
            'timestamp': start_time,
            'date': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d'),
            'domains_prioritized': len(prioritized_domains),
            'benchmark_sets_created': len(benchmark_sets),
            'top_priority_domains': [d['domain'] for d in prioritized_domains[:10]],
            'valid_benchmarks': sum(1 for b in benchmark_sets.values() if b['benchmark_status'] == 'valid'),
            'completion_time': time.time() - start_time
        }
        
        # Save results
        try:
            with open(f"{DATA_DIR}/crawl_priority_results.json", 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Daily crawl prioritization completed in {results['completion_time']:.2f} seconds")
        except Exception as e:
            logger.error(f"Error saving crawl prioritization results: {e}")
        
        return results

# Create a global instance
crawl_planner = CrawlPlanner()

def get_prioritized_domains(limit: int = 50) -> List[Dict]:
    """
    Get prioritized domains for crawling.
    
    Args:
        limit: Maximum number of domains to return
    
    Returns:
        List of domains sorted by priority
    """
    return crawl_planner.prioritize_domains(limit=limit)

def run_daily_prioritization() -> Dict:
    """
    Run daily domain prioritization and benchmark set creation.
    
    Returns:
        Dictionary with prioritization results
    """
    return crawl_planner.run_daily_prioritization()

if __name__ == "__main__":
    # Run daily prioritization
    results = run_daily_prioritization()
    print(f"Prioritized {results['domains_prioritized']} domains")
    print(f"Created {results['benchmark_sets_created']} benchmark sets ({results['valid_benchmarks']} valid)")
    print(f"Top priority domains: {', '.join(results['top_priority_domains'])}")