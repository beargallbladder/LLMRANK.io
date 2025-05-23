"""
Citation Analysis Module for LLMPageRank V10

This module implements the citation analysis system for LLMPageRank,
tracking how domains are cited, identifying citation patterns, and
generating compelling narratives around citation dynamics.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_test_results(results: Dict, domain: str = None) -> Dict:
    """
    Process test results from the citation analysis system.
    
    Args:
        results: Raw test results data
        domain: Optional domain to filter results for
        
    Returns:
        Processed results with computed metrics
    """
    logger.info(f"Processing test results for domain: {domain if domain else 'all domains'}")
    
    processed_results = {
        "domains_processed": 0,
        "citation_metrics": {},
        "trust_signals": {},
        "summary": {}
    }
    
    try:
        # Extract domain data from results
        domains_data = results.get("domains", {})
        
        # Filter for specific domain if provided
        if domain and domain in domains_data:
            domains_to_process = {domain: domains_data[domain]}
        else:
            domains_to_process = domains_data
            
        # Process each domain
        for domain_name, domain_data in domains_to_process.items():
            # Extract citation data
            citations = domain_data.get("citations", [])
            
            # Calculate citation metrics
            citation_count = len(citations)
            citation_quality = sum(c.get("quality", 0) for c in citations) / max(1, citation_count)
            
            # Store metrics
            processed_results["citation_metrics"][domain_name] = {
                "count": citation_count,
                "quality": round(citation_quality, 2),
                "diversity": round(len(set(c.get("source") for c in citations)) / max(1, citation_count), 2),
                "context": {
                    "positive": sum(1 for c in citations if c.get("context") == "positive"),
                    "neutral": sum(1 for c in citations if c.get("context") == "neutral"),
                    "negative": sum(1 for c in citations if c.get("context") == "negative")
                }
            }
            
            # Calculate trust signals
            trust_score = domain_data.get("trust_score", 0)
            previous_score = domain_data.get("previous_trust_score", trust_score)
            trust_change = trust_score - previous_score
            
            # Store trust signals
            processed_results["trust_signals"][domain_name] = {
                "score": trust_score,
                "change": round(trust_change, 2),
                "trend": "up" if trust_change > 0 else "down" if trust_change < 0 else "stable"
            }
            
            processed_results["domains_processed"] += 1
        
        # Generate summary
        if processed_results["domains_processed"] > 0:
            # Calculate averages
            avg_citation_count = sum(m["count"] for m in processed_results["citation_metrics"].values()) / processed_results["domains_processed"]
            avg_trust_score = sum(s["score"] for s in processed_results["trust_signals"].values()) / processed_results["domains_processed"]
            
            # Identify domains with significant changes
            significant_changes = [
                {
                    "domain": d,
                    "change": s["change"],
                    "trend": s["trend"]
                }
                for d, s in processed_results["trust_signals"].items()
                if abs(s["change"]) >= 2.0  # Threshold for significant change
            ]
            
            # Store summary
            processed_results["summary"] = {
                "average_citation_count": round(avg_citation_count, 2),
                "average_trust_score": round(avg_trust_score, 2),
                "significant_changes": significant_changes,
                "processed_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error processing test results: {e}")
        processed_results["error"] = str(e)
    
    return processed_results

# Constants
DATA_DIR = "data"
CITATION_DIR = f"{DATA_DIR}/citations"
INSIGHT_DIR = f"{DATA_DIR}/insights"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CITATION_DIR, exist_ok=True)
os.makedirs(INSIGHT_DIR, exist_ok=True)

class CitationAnalysis:
    """
    Citation Analysis for LLMPageRank, tracking how domains are cited,
    identifying citation patterns, and generating compelling narratives.
    """
    
    def __init__(self):
        """Initialize citation analysis."""
        self.domains = self._load_domains()
        self.citation_data = self._load_citation_data()
        self.citation_patterns = self._identify_citation_patterns()
        self.citation_leaders = self._identify_citation_leaders()
        self.citation_narratives = self._generate_citation_narratives()
    
    def _load_domains(self) -> Dict:
        """Load domain data from file."""
        domains_file = f"{DATA_DIR}/domains.json"
        
        try:
            if os.path.exists(domains_file):
                with open(domains_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading domains: {e}")
        
        # Create sample domain data if file not found
        domains = {}
        
        sample_domains = [
            "wellsfargo.com", "chase.com", "bankofamerica.com", "schwab.com", 
            "vanguard.com", "fidelity.com", "blackrock.com", "jpmorgan.com",
            "mayoclinic.org", "clevelandclinic.org", "hopkinsmedicine.org", 
            "mountsinai.org", "cedars-sinai.org", "massgeneral.org",
            "findlaw.com", "justia.com", "law.cornell.edu", "scotusblog.com",
            "americanbar.org", "uscourts.gov", "cdc.gov", "nih.gov", "who.int"
        ]
        
        for domain in sample_domains:
            # Determine category
            if any(fin in domain for fin in ["bank", "invest", "capital", "jpmorgan", "wells", "chase", "fidelity", "schwab", "vanguard", "blackrock"]):
                category = "finance"
            elif any(health in domain for health in ["clinic", "health", "hospital", "medical", "mayo", "hopkins", "sinai", "cedars", "cdc", "nih", "who"]):
                category = "healthcare"
            elif any(legal in domain for legal in ["law", "legal", "court", "justice", "findlaw", "justia", "scotus", "bar"]):
                category = "legal"
            else:
                category = random.choice(["finance", "healthcare", "legal", "technology", "education"])
            
            # Create domain data
            domains[domain] = {
                "category": category,
                "trust_score": round(random.uniform(75.0, 95.0), 1),
                "citation_rate": round(random.uniform(0.4, 0.9), 2),
                "authority_score": round(random.uniform(0.6, 0.95), 2)
            }
        
        # Save domains to file
        os.makedirs(os.path.dirname(domains_file), exist_ok=True)
        with open(domains_file, 'w') as f:
            json.dump(domains, f, indent=2)
        
        return domains
    
    def _load_citation_data(self) -> Dict:
        """Load citation data from file or generate if not found."""
        citation_file = f"{CITATION_DIR}/citation_data.json"
        
        try:
            if os.path.exists(citation_file):
                with open(citation_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading citation data: {e}")
        
        # Generate citation data
        citation_data = {
            "citation_matrix": self._generate_citation_matrix(),
            "citation_trends": self._generate_citation_trends(),
            "citation_benchmarks": self._generate_citation_benchmarks(),
            "last_updated": time.time()
        }
        
        # Save citation data to file
        os.makedirs(os.path.dirname(citation_file), exist_ok=True)
        with open(citation_file, 'w') as f:
            json.dump(citation_data, f, indent=2)
        
        return citation_data
    
    def _generate_citation_matrix(self) -> Dict:
        """Generate citation matrix showing relationships between domains."""
        logger.info("Generating citation matrix...")
        
        citation_matrix = {}
        
        # Group domains by category
        categories = {}
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append(domain)
        
        # Generate citation relationships
        for category, domains in categories.items():
            citation_matrix[category] = {}
            
            for domain in domains:
                citation_matrix[category][domain] = {
                    "citations_to": [],
                    "citations_from": [],
                    "citation_strength": {}
                }
                
                # Determine citations to other domains
                for other_domain in domains:
                    if other_domain != domain:
                        # Decide if this domain cites the other domain
                        if random.random() < 0.7:  # 70% chance of citation within same category
                            # Determine citation strength
                            strength = round(random.uniform(0.2, 0.9), 2)
                            
                            # Add citation
                            citation_matrix[category][domain]["citations_to"].append(other_domain)
                            citation_matrix[category][domain]["citation_strength"][other_domain] = strength
        
        # Fill in citations_from based on citations_to
        for category, cat_data in citation_matrix.items():
            for domain, domain_data in cat_data.items():
                for cited_domain in domain_data["citations_to"]:
                    if cited_domain in cat_data:
                        if domain not in cat_data[cited_domain]["citations_from"]:
                            cat_data[cited_domain]["citations_from"].append(domain)
        
        # Add cross-category citations (fewer)
        for cat1, domains1 in categories.items():
            for cat2, domains2 in categories.items():
                if cat1 != cat2:
                    # Select random domains from each category
                    for domain1 in random.sample(domains1, min(2, len(domains1))):
                        for domain2 in random.sample(domains2, min(2, len(domains2))):
                            # Add cross-category citation
                            if random.random() < 0.4:  # 40% chance of cross-category citation
                                strength = round(random.uniform(0.1, 0.7), 2)
                                
                                # Add citation
                                citation_matrix[cat1][domain1]["citations_to"].append(domain2)
                                citation_matrix[cat1][domain1]["citation_strength"][domain2] = strength
                                
                                # Add reverse citation
                                if cat2 in citation_matrix and domain2 in citation_matrix[cat2]:
                                    if domain1 not in citation_matrix[cat2][domain2]["citations_from"]:
                                        citation_matrix[cat2][domain2]["citations_from"].append(domain1)
        
        return citation_matrix
    
    def _generate_citation_trends(self) -> Dict:
        """Generate citation trends over time."""
        logger.info("Generating citation trends...")
        
        citation_trends = {}
        
        # Generate trends for each domain
        for domain in self.domains:
            # Create weekly samples
            samples = []
            
            # Start with a base citation rate
            base_rate = random.uniform(0.3, 0.7)
            current_rate = base_rate
            
            # Generate 12 weeks of data
            for i in range(12):
                # Add some randomness
                drift = random.uniform(-0.05, 0.05)
                
                # Occasional significant events
                if random.random() < 0.1:
                    drift = random.choice([-0.15, -0.1, 0.1, 0.15])
                
                # Update rate with bounds
                current_rate = max(0.1, min(0.95, current_rate + drift))
                
                # Add to samples
                samples.append(round(current_rate, 2))
            
            # Add to trends
            citation_trends[domain] = {
                "weekly_samples": samples,
                "trend_direction": "up" if samples[-1] > samples[0] else "down",
                "volatility": round(self._calculate_volatility(samples), 2)
            }
        
        return citation_trends
    
    def _generate_citation_benchmarks(self) -> Dict:
        """Generate citation benchmarks for each category."""
        logger.info("Generating citation benchmarks...")
        
        citation_benchmarks = {}
        
        # Group domains by category
        categories = {}
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "domain": domain,
                "citation_rate": data.get("citation_rate", 0),
                "authority_score": data.get("authority_score", 0)
            })
        
        # Generate benchmarks for each category
        for category, domains in categories.items():
            if domains:
                # Calculate average citation rate
                avg_citation_rate = sum(d["citation_rate"] for d in domains) / len(domains)
                
                # Calculate average authority score
                avg_authority_score = sum(d["authority_score"] for d in domains) / len(domains)
                
                # Sort domains by citation rate
                sorted_by_citation = sorted(domains, key=lambda x: x["citation_rate"], reverse=True)
                
                # Sort domains by authority score
                sorted_by_authority = sorted(domains, key=lambda x: x["authority_score"], reverse=True)
                
                # Add to benchmarks
                citation_benchmarks[category] = {
                    "average_citation_rate": round(avg_citation_rate, 2),
                    "average_authority_score": round(avg_authority_score, 2),
                    "top_citation_domain": sorted_by_citation[0]["domain"] if sorted_by_citation else None,
                    "top_authority_domain": sorted_by_authority[0]["domain"] if sorted_by_authority else None,
                    "citation_thresholds": {
                        "elite": round(avg_citation_rate * 1.25, 2),
                        "good": round(avg_citation_rate, 2),
                        "average": round(avg_citation_rate * 0.75, 2)
                    },
                    "authority_thresholds": {
                        "elite": round(avg_authority_score * 1.25, 2),
                        "good": round(avg_authority_score, 2),
                        "average": round(avg_authority_score * 0.75, 2)
                    }
                }
        
        return citation_benchmarks
    
    def _calculate_volatility(self, samples: List[float]) -> float:
        """Calculate volatility (standard deviation) of a list of samples."""
        if not samples:
            return 0
        
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        return (variance ** 0.5)
    
    def _identify_citation_patterns(self) -> Dict:
        """Identify interesting citation patterns."""
        logger.info("Identifying citation patterns...")
        
        patterns = {
            "hubs": [],
            "authorities": [],
            "rising_stars": [],
            "falling_stars": [],
            "cross_category_influencers": []
        }
        
        # Identify citation hubs (domains that cite many others)
        for category, cat_data in self.citation_data["citation_matrix"].items():
            for domain, domain_data in cat_data.items():
                citations_to = domain_data.get("citations_to", [])
                
                if len(citations_to) >= 5:  # Arbitrary threshold
                    patterns["hubs"].append({
                        "domain": domain,
                        "category": category,
                        "citations_count": len(citations_to),
                        "strength": sum(domain_data.get("citation_strength", {}).values()) / len(citations_to) if citations_to else 0
                    })
        
        # Sort hubs by citation count
        patterns["hubs"].sort(key=lambda x: x["citations_count"], reverse=True)
        
        # Identify authorities (domains cited by many others)
        for category, cat_data in self.citation_data["citation_matrix"].items():
            for domain, domain_data in cat_data.items():
                citations_from = domain_data.get("citations_from", [])
                
                if len(citations_from) >= 4:  # Arbitrary threshold
                    patterns["authorities"].append({
                        "domain": domain,
                        "category": category,
                        "citations_count": len(citations_from),
                        "authority_score": self.domains.get(domain, {}).get("authority_score", 0)
                    })
        
        # Sort authorities by citation count
        patterns["authorities"].sort(key=lambda x: x["citations_count"], reverse=True)
        
        # Identify rising stars (domains with increasing citation trends)
        for domain, trend_data in self.citation_data["citation_trends"].items():
            samples = trend_data.get("weekly_samples", [])
            
            if samples and len(samples) >= 4:
                # Check for significant upward trend
                start = sum(samples[:3]) / 3  # Average of first 3 samples
                end = sum(samples[-3:]) / 3  # Average of last 3 samples
                
                if end > start * 1.2:  # At least 20% increase
                    patterns["rising_stars"].append({
                        "domain": domain,
                        "category": self.domains.get(domain, {}).get("category", "unknown"),
                        "citation_increase": round((end - start) / start * 100, 1),  # Percentage increase
                        "current_rate": samples[-1]
                    })
        
        # Sort rising stars by citation increase
        patterns["rising_stars"].sort(key=lambda x: x["citation_increase"], reverse=True)
        
        # Identify falling stars (domains with decreasing citation trends)
        for domain, trend_data in self.citation_data["citation_trends"].items():
            samples = trend_data.get("weekly_samples", [])
            
            if samples and len(samples) >= 4:
                # Check for significant downward trend
                start = sum(samples[:3]) / 3  # Average of first 3 samples
                end = sum(samples[-3:]) / 3  # Average of last 3 samples
                
                if end < start * 0.8:  # At least 20% decrease
                    patterns["falling_stars"].append({
                        "domain": domain,
                        "category": self.domains.get(domain, {}).get("category", "unknown"),
                        "citation_decrease": round((start - end) / start * 100, 1),  # Percentage decrease
                        "current_rate": samples[-1]
                    })
        
        # Sort falling stars by citation decrease
        patterns["falling_stars"].sort(key=lambda x: x["citation_decrease"], reverse=True)
        
        # Identify cross-category influencers
        cross_category_citations = {}
        
        for category, cat_data in self.citation_data["citation_matrix"].items():
            for domain, domain_data in cat_data.items():
                citations_to = domain_data.get("citations_to", [])
                citation_strength = domain_data.get("citation_strength", {})
                
                for cited_domain in citations_to:
                    cited_category = self.domains.get(cited_domain, {}).get("category", "unknown")
                    
                    if cited_category != category:
                        # This is a cross-category citation
                        if domain not in cross_category_citations:
                            cross_category_citations[domain] = {"categories": {}, "total": 0}
                        
                        if cited_category not in cross_category_citations[domain]["categories"]:
                            cross_category_citations[domain]["categories"][cited_category] = 0
                        
                        cross_category_citations[domain]["categories"][cited_category] += 1
                        cross_category_citations[domain]["total"] += 1
        
        # Convert to list format
        for domain, data in cross_category_citations.items():
            if data["total"] >= 2:  # At least 2 cross-category citations
                patterns["cross_category_influencers"].append({
                    "domain": domain,
                    "category": self.domains.get(domain, {}).get("category", "unknown"),
                    "cross_citations": data["total"],
                    "influenced_categories": list(data["categories"].keys())
                })
        
        # Sort cross-category influencers by number of cross-citations
        patterns["cross_category_influencers"].sort(key=lambda x: x["cross_citations"], reverse=True)
        
        return patterns
    
    def _identify_citation_leaders(self) -> Dict:
        """Identify citation leaders by various metrics."""
        logger.info("Identifying citation leaders...")
        
        leaders = {
            "overall": [],
            "by_category": {},
            "by_metric": {
                "citation_rate": [],
                "authority_score": [],
                "trust_score": []
            }
        }
        
        # Identify overall leaders (combination of metrics)
        domain_scores = []
        
        for domain, data in self.domains.items():
            # Calculate combined score
            citation_rate = data.get("citation_rate", 0)
            authority_score = data.get("authority_score", 0)
            trust_score = data.get("trust_score", 0) / 100  # Normalize to 0-1 scale
            
            combined_score = (citation_rate * 0.4) + (authority_score * 0.4) + (trust_score * 0.2)
            
            domain_scores.append({
                "domain": domain,
                "category": data.get("category", "unknown"),
                "combined_score": round(combined_score, 2),
                "citation_rate": citation_rate,
                "authority_score": authority_score,
                "trust_score": trust_score * 100  # Convert back to 0-100 scale
            })
        
        # Sort by combined score
        domain_scores.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Take top 10
        leaders["overall"] = domain_scores[:10]
        
        # Identify leaders by category
        for domain in domain_scores:
            category = domain["category"]
            
            if category not in leaders["by_category"]:
                leaders["by_category"][category] = []
            
            if len(leaders["by_category"][category]) < 5:  # The top 5 in each category
                leaders["by_category"][category].append(domain)
        
        # Identify leaders by specific metrics
        citation_leaders = sorted(domain_scores, key=lambda x: x["citation_rate"], reverse=True)[:5]
        authority_leaders = sorted(domain_scores, key=lambda x: x["authority_score"], reverse=True)[:5]
        trust_leaders = sorted(domain_scores, key=lambda x: x["trust_score"], reverse=True)[:5]
        
        leaders["by_metric"]["citation_rate"] = citation_leaders
        leaders["by_metric"]["authority_score"] = authority_leaders
        leaders["by_metric"]["trust_score"] = trust_leaders
        
        return leaders
    
    def _generate_citation_narratives(self) -> Dict:
        """Generate compelling narratives about citation patterns."""
        logger.info("Generating citation narratives...")
        
        narratives = {
            "hub_narratives": [],
            "authority_narratives": [],
            "rising_star_narratives": [],
            "cross_category_narratives": [],
            "benchmark_narratives": []
        }
        
        # Generate hub narratives
        if self.citation_patterns["hubs"]:
            for hub in self.citation_patterns["hubs"][:2]:  # Top 2 hubs
                domain = hub["domain"]
                category = hub["category"]
                count = hub["citations_count"]
                
                narrative = {
                    "domain": domain,
                    "title": f"{domain}: The Citation Hub Reshaping {category.title()} Trust Signals",
                    "summary": f"{domain} has emerged as a critical citation hub in the {category} vertical, consistently referencing {count} domains across the ecosystem. This citation pattern reveals its role as a trust signal aggregator and distributor, creating network effects in LLM visibility.",
                    "insights": [
                        f"Cites {count} different domains across the {category} ecosystem",
                        f"Average citation strength of {round(hub['strength'] * 100)}%",
                        "Creates network effects through broad reference patterns",
                        f"Serves as domain 'discoverer' for LLMs scanning the {category} space"
                    ],
                    "recommendation": f"Content strategies should prioritize inclusion in {domain}'s citation network to maximize LLM visibility"
                }
                
                narratives["hub_narratives"].append(narrative)
        
        # Generate authority narratives
        if self.citation_patterns["authorities"]:
            for authority in self.citation_patterns["authorities"][:2]:  # Top 2 authorities
                domain = authority["domain"]
                category = authority["category"]
                count = authority["citations_count"]
                
                narrative = {
                    "domain": domain,
                    "title": f"{domain}: The Trust Authority That Defines {category.title()} Citations",
                    "summary": f"{domain} demonstrates exceptional citation authority, being referenced by {count} domains across the {category} ecosystem. This citation pattern establishes it as a fundamental 'trust anchor' for the entire vertical, with citations flowing inward from diverse sources.",
                    "insights": [
                        f"Cited by {count} different domains in the {category} ecosystem",
                        f"Authority score of {round(authority['authority_score'] * 100)}%",
                        "Creates citation gravity that pulls in references naturally",
                        "Establishes trust benchmarks that other domains measure against"
                    ],
                    "recommendation": f"Study {domain}'s content structure and methodology as a model for {category} trust signal optimization"
                }
                
                narratives["authority_narratives"].append(narrative)
        
        # Generate rising star narratives
        if self.citation_patterns["rising_stars"]:
            for star in self.citation_patterns["rising_stars"][:2]:  # Top 2 rising stars
                domain = star["domain"]
                category = star["category"]
                increase = star["citation_increase"]
                
                narrative = {
                    "domain": domain,
                    "title": f"{domain}: The Rising Citation Star with {increase}% Visibility Growth",
                    "summary": f"{domain} has demonstrated remarkable citation growth, increasing its citation rate by {increase}% in recent weeks. This rapid rise in trust signals indicates either significant content improvements, strategic reference building, or the emergence of essential new information resources.",
                    "insights": [
                        f"Citation rate increased by {increase}% in recent measurement period",
                        f"Current citation rate of {round(star['current_rate'] * 100)}%",
                        "Demonstrates velocity of trust signal momentum in the ecosystem",
                        f"Represents an emerging validation model in the {category} space"
                    ],
                    "recommendation": f"Monitor {domain}'s content structure changes to identify trust signal optimization patterns"
                }
                
                narratives["rising_star_narratives"].append(narrative)
        
        # Generate cross-category narratives
        if self.citation_patterns["cross_category_influencers"]:
            for influencer in self.citation_patterns["cross_category_influencers"][:2]:  # Top 2 cross-category influencers
                domain = influencer["domain"]
                category = influencer["category"]
                count = influencer["cross_citations"]
                
                narrative = {
                    "domain": domain,
                    "title": f"{domain}: The Cross-Category Citator Bridging Trust Silos",
                    "summary": f"{domain} demonstrates exceptional ability to cross category boundaries, maintaining {count} significant citations across multiple categories. This cross-category citation pattern reveals its role as a trust signal bridge, connecting otherwise isolated domain ecosystems.",
                    "insights": [
                        f"Maintains {count} cross-category citations",
                        f"Primary category is {category} but influences {', '.join(influencer['influenced_categories'])}",
                        "Creates trust signal pathways between specialized knowledge domains",
                        "Serves as category 'translator' for complex cross-domain concepts"
                    ],
                    "recommendation": f"Study {domain}'s content structure for models of cross-category relevance that amplify trust signals"
                }
                
                narratives["cross_category_narratives"].append(narrative)
        
        # Generate benchmark narratives
        for category, benchmarks in self.citation_data["citation_benchmarks"].items():
            top_citation = benchmarks.get("top_citation_domain")
            top_authority = benchmarks.get("top_authority_domain")
            
            if top_citation and top_authority:
                narrative = {
                    "category": category,
                    "title": f"{category.title()}: Citation Benchmark Analysis Reveals Trust Signal Mechanics",
                    "summary": f"Analysis of the {category} category reveals distinct citation patterns and benchmarks that define trust signals in this vertical. With an average citation rate of {round(benchmarks['average_citation_rate'] * 100)}% and authority threshold of {round(benchmarks['authority_thresholds']['elite'] * 100)}% for elite status, the category shows structured trust signal distribution.",
                    "insights": [
                        f"{top_citation} leads citation rates in {category}",
                        f"{top_authority} holds highest authority score in {category}",
                        f"Elite threshold requires {round(benchmarks['citation_thresholds']['elite'] * 100)}% citation rate",
                        f"Average authority score of {round(benchmarks['average_authority_score'] * 100)}% establishes category baseline"
                    ],
                    "recommendation": f"Implement {category}-specific citation strategies that target the established elite thresholds"
                }
                
                narratives["benchmark_narratives"].append(narrative)
        
        return narratives
    
    def update_citation_data(self):
        """Update citation data with fresh information."""
        logger.info("Updating citation data...")
        
        # In a real implementation, this would fetch fresh data
        # For this example, we'll just refresh the existing data with some randomness
        
        # Update citation trends
        for domain, trend_data in self.citation_data["citation_trends"].items():
            samples = trend_data.get("weekly_samples", [])
            
            if samples:
                # Remove oldest sample
                samples = samples[1:]
                
                # Add new sample
                last_sample = samples[-1]
                drift = random.uniform(-0.05, 0.05)
                
                # Occasional significant events
                if random.random() < 0.1:
                    drift = random.choice([-0.15, -0.1, 0.1, 0.15])
                
                # Update with bounds
                new_sample = max(0.1, min(0.95, last_sample + drift))
                samples.append(round(new_sample, 2))
                
                # Update trend direction
                trend_data["trend_direction"] = "up" if samples[-1] > samples[0] else "down"
                
                # Update volatility
                trend_data["volatility"] = round(self._calculate_volatility(samples), 2)
                
                # Save updated samples
                trend_data["weekly_samples"] = samples
        
        # Update last_updated timestamp
        self.citation_data["last_updated"] = time.time()
        
        # Save updated citation data
        citation_file = f"{CITATION_DIR}/citation_data.json"
        with open(citation_file, 'w') as f:
            json.dump(self.citation_data, f, indent=2)
        
        # Re-identify patterns
        self.citation_patterns = self._identify_citation_patterns()
        
        # Re-identify leaders
        self.citation_leaders = self._identify_citation_leaders()
        
        # Re-generate narratives
        self.citation_narratives = self._generate_citation_narratives()
        
        logger.info("Citation data updated successfully")
        
        return self.citation_data
    
    def get_citation_data(self) -> Dict:
        """Get citation data."""
        return self.citation_data
    
    def get_citation_patterns(self) -> Dict:
        """Get citation patterns."""
        return self.citation_patterns
    
    def get_citation_leaders(self) -> Dict:
        """Get citation leaders."""
        return self.citation_leaders
    
    def get_citation_narratives(self) -> Dict:
        """Get citation narratives."""
        return self.citation_narratives
    
    def generate_weekly_citation_report(self) -> Dict:
        """Generate weekly citation report with key insights."""
        logger.info("Generating weekly citation report...")
        
        report = {
            "title": "Weekly Citation Ecosystem Report",
            "date": datetime.now().isoformat(),
            "summary": "Analysis of the citation ecosystem reveals evolving trust signal patterns across domains and categories.",
            "key_insights": [],
            "top_movers": [],
            "recommendations": []
        }
        
        # Add key insights from patterns
        if self.citation_patterns["hubs"]:
            report["key_insights"].append({
                "title": "Citation Hub Analysis",
                "insight": f"{self.citation_patterns['hubs'][0]['domain']} leads as the primary citation hub with {self.citation_patterns['hubs'][0]['citations_count']} outgoing citations"
            })
        
        if self.citation_patterns["authorities"]:
            report["key_insights"].append({
                "title": "Authority Score Distribution",
                "insight": f"{self.citation_patterns['authorities'][0]['domain']} maintains highest authority position with {self.citation_patterns['authorities'][0]['citations_count']} incoming citations"
            })
        
        if self.citation_patterns["rising_stars"]:
            report["key_insights"].append({
                "title": "Emerging Trust Signals",
                "insight": f"{self.citation_patterns['rising_stars'][0]['domain']} shows fastest growth with {self.citation_patterns['rising_stars'][0]['citation_increase']}% citation increase"
            })
        
        if self.citation_patterns["cross_category_influencers"]:
            report["key_insights"].append({
                "title": "Cross-Category Citation Flows",
                "insight": f"{self.citation_patterns['cross_category_influencers'][0]['domain']} bridges category silos with {self.citation_patterns['cross_category_influencers'][0]['cross_citations']} cross-vertical citations"
            })
        
        # Add top movers from trends
        rising_domains = []
        falling_domains = []
        
        for domain, trend_data in self.citation_data["citation_trends"].items():
            samples = trend_data.get("weekly_samples", [])
            
            if samples and len(samples) >= 2:
                change = samples[-1] - samples[-2]
                
                if change > 0.05:
                    rising_domains.append({
                        "domain": domain,
                        "change": round(change, 2),
                        "current_rate": samples[-1]
                    })
                elif change < -0.05:
                    falling_domains.append({
                        "domain": domain,
                        "change": round(change, 2),
                        "current_rate": samples[-1]
                    })
        
        # Sort by magnitude of change
        rising_domains.sort(key=lambda x: x["change"], reverse=True)
        falling_domains.sort(key=lambda x: x["change"])
        
        # Take top 3 from each
        for domain in rising_domains[:3]:
            report["top_movers"].append({
                "domain": domain["domain"],
                "direction": "up",
                "change": domain["change"],
                "insight": f"{domain['domain']} increased citation rate by {domain['change']} to {domain['current_rate']}"
            })
        
        for domain in falling_domains[:3]:
            report["top_movers"].append({
                "domain": domain["domain"],
                "direction": "down",
                "change": domain["change"],
                "insight": f"{domain['domain']} decreased citation rate by {abs(domain['change'])} to {domain['current_rate']}"
            })
        
        # Add recommendations
        report["recommendations"].append({
            "title": "Citation Strategy Optimization",
            "recommendation": "Focus on cross-category citation flows to maximize LLM visibility"
        })
        
        report["recommendations"].append({
            "title": "Trust Signal Monitoring",
            "recommendation": "Implement specialized monitoring for domains showing high citation volatility"
        })
        
        report["recommendations"].append({
            "title": "Benchmark Calibration",
            "recommendation": "Recalibrate category benchmarks to account for rising citation thresholds"
        })
        
        logger.info("Weekly citation report generated")
        
        return report

# Global citation analysis instance
_citation_analysis = None

def start_citation_analysis():
    """Start citation analysis."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = CitationAnalysis()
    
    return _citation_analysis

def get_citation_data():
    """Get citation data."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.get_citation_data()

def get_citation_patterns():
    """Get citation patterns."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.get_citation_patterns()

def get_citation_leaders():
    """Get citation leaders."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.get_citation_leaders()

def get_citation_narratives():
    """Get citation narratives."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.get_citation_narratives()

def update_citation_data():
    """Update citation data."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.update_citation_data()

def generate_weekly_citation_report():
    """Generate weekly citation report."""
    global _citation_analysis
    
    if _citation_analysis is None:
        _citation_analysis = start_citation_analysis()
    
    return _citation_analysis.generate_weekly_citation_report()

# Main execution for testing
if __name__ == "__main__":
    logger.info("Starting citation analysis...")
    
    # Start analysis
    analysis = start_citation_analysis()
    
    # Update citation data
    analysis.update_citation_data()
    
    # Generate weekly report
    report = analysis.generate_weekly_citation_report()
    
    logger.info(f"Analysis complete. Generated report with {len(report['key_insights'])} key insights.")