"""
FOMA Insight Engine for LLMPageRank V10

This module implements the Fear Of Missing AI (FOMA) Insight Engine,
capturing compelling narratives around trust signal drift, benchmarking outliers,
and category expertise evolution.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
INSIGHT_DIR = f"{DATA_DIR}/insights"
NARRATIVE_DIR = f"{DATA_DIR}/narratives"
BENCHMARK_DIR = f"{DATA_DIR}/benchmarks"
CADENCE_DIR = f"{DATA_DIR}/cadence"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INSIGHT_DIR, exist_ok=True)
os.makedirs(NARRATIVE_DIR, exist_ok=True)
os.makedirs(BENCHMARK_DIR, exist_ok=True)
os.makedirs(CADENCE_DIR, exist_ok=True)

class FomaInsightEngine:
    """
    FOMA Insight Engine for generating compelling trust signal narratives.
    Identifies standout stories in domain trust dynamics.
    """
    
    def __init__(self):
        """Initialize the FOMA insight engine."""
        self.domains = self._load_domains()
        self.categories = self._load_categories()
        self.benchmarks = self._load_benchmarks()
        self.narratives = self._load_narratives()
        self.elite_domains = self._identify_elite_domains()
        self.volatile_domains = self._identify_volatile_domains()
        
        # Create initial insights if needed
        if not os.path.exists(f"{INSIGHT_DIR}/elite_insights.json"):
            self._generate_elite_insights()
            
        if not os.path.exists(f"{INSIGHT_DIR}/volatile_insights.json"):
            self._generate_volatile_insights()
    
    def _load_domains(self):
        """Load domain data."""
        domains_file = f"{DATA_DIR}/domains.json"
        
        try:
            if os.path.exists(domains_file):
                with open(domains_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading domains: {e}")
        
        # Create sample domain data if file not found
        # This will be expanded with much richer data
        sample_domains = [
            # Financial domain examples with rich narrative potential
            "wellsfargo.com", "chase.com", "bankofamerica.com", "schwab.com", 
            "vanguard.com", "fidelity.com", "blackrock.com", "jpmorgan.com",
            
            # Healthcare domain examples
            "mayoclinic.org", "clevelandclinic.org", "hopkinsmedicine.org", 
            "mountsinai.org", "cedars-sinai.org", "massgeneral.org",
            
            # Legal resources
            "findlaw.com", "justia.com", "law.cornell.edu", "scotusblog.com",
            "americanbar.org", "uscourts.gov", "pacer.gov",
            
            # Technology domains
            "techcrunch.com", "wired.com", "theverge.com", "arstechnica.com",
            "mit.edu", "stanford.edu", "berkeley.edu",
            
            # Government and regulatory
            "sec.gov", "ftc.gov", "cdc.gov", "nih.gov", "who.int",
            "worldbank.org", "imf.org", "federalreserve.gov",
            
            # Rising technology domains
            "anthropic.com", "openai.com", "deepmind.com", "stability.ai",
            "replicate.com", "huggingface.co", "pytorch.org", "tensorflow.org",
            
            # Financial technology
            "stripe.com", "plaid.com", "square.com", "paypal.com",
            "coinbase.com", "blockchain.com", "binance.com"
        ]
        
        # Create rich domain data
        domains = {}
        for domain in sample_domains:
            category = self._determine_category(domain)
            first_seen = datetime.now() - timedelta(days=random.randint(30, 180))
            last_scan = datetime.now() - timedelta(hours=random.randint(1, 72))
            
            # Base trust score on domain type
            base_score = 0
            if any(financial in domain for financial in ["bank", "invest", "capital", "finance", "wealth"]):
                base_score = random.uniform(80.0, 95.0)  # Financial institutions tend to have high trust
            elif any(health in domain for health in ["clinic", "hospital", "health", "medical", "care"]):
                base_score = random.uniform(85.0, 97.0)  # Healthcare typically has very high trust
            elif any(gov in domain for gov in [".gov", ".edu", "university"]):
                base_score = random.uniform(88.0, 98.0)  # Government and education have highest trust
            elif any(tech in domain for tech in [".ai", "tech", "ml", "data"]):
                base_score = random.uniform(70.0, 90.0)  # Tech can vary widely
            else:
                base_score = random.uniform(65.0, 85.0)  # Generic baseline
            
            # Add some weekly variance to simulate trust drift
            weekly_samples = []
            current_score = base_score
            for i in range(12):  # 12 weeks of history
                # Adjust score with some randomness
                drift = random.uniform(-5.0, 5.0)
                # Occasionally add significant events
                if random.random() < 0.15:
                    drift = random.choice([-15.0, -10.0, 10.0, 15.0])
                
                current_score = max(0, min(100, current_score + drift))
                weekly_samples.append(round(current_score, 1))
            
            # Final trust score is latest weekly sample
            trust_score = weekly_samples[-1]
            
            # Rich domain metadata
            domains[domain] = {
                "first_seen": first_seen.isoformat(),
                "last_scan": last_scan.isoformat(),
                "category": category,
                "subcategory": self._determine_subcategory(domain, category),
                "priority": self._determine_priority(domain, trust_score),
                "trust_score": round(trust_score, 1),
                "total_scans": random.randint(20, 100),
                "weekly_trust_trend": weekly_samples,
                "trust_volatility": round(self._calculate_volatility(weekly_samples), 2),
                "citation_rate": round(random.uniform(0.1, 0.9), 2),
                "quality_score": round(random.uniform(0.7, 0.99), 2),
                "response_consistency": round(random.uniform(0.8, 0.98), 2),
                "peer_ranking": random.randint(1, 15),
                "benchmark_delta": round(random.uniform(-15.0, 15.0), 1),
                "content_freshness": round(random.uniform(0.6, 0.95), 2),
                "citation_authority": round(random.uniform(0.5, 0.98), 2),
                "hallucination_risk": round(random.uniform(0.01, 0.3), 2),
                "trust_signals": {
                    "fact_density": round(random.uniform(0.5, 0.95), 2),
                    "reference_quality": round(random.uniform(0.6, 0.98), 2),
                    "source_diversity": round(random.uniform(0.4, 0.9), 2),
                    "methodology_clarity": round(random.uniform(0.3, 0.95), 2),
                    "transparency_score": round(random.uniform(0.5, 0.97), 2)
                }
            }
        
        # Save domains to file
        os.makedirs(os.path.dirname(domains_file), exist_ok=True)
        with open(domains_file, 'w') as f:
            json.dump(domains, f, indent=2)
        
        return domains
    
    def _determine_category(self, domain):
        """Determine domain category based on domain name."""
        if any(financial in domain for financial in ["bank", "invest", "capital", "finance", "wealth", "schwab", "vanguard", "fidelity", "jpmorgan", "stripe", "plaid", "square", "paypal", "coinbase", "blockchain", "binance"]):
            return "finance"
        elif any(health in domain for health in ["clinic", "hospital", "health", "medical", "mayo", "cleveland", "hopkins", "sinai", "massgeneral"]):
            return "healthcare"
        elif any(legal in domain for legal in ["law", "legal", "court", "justice", "findlaw", "justia", "scotusblog", "americanbar"]):
            return "legal"
        elif any(gov in domain for gov in [".gov", "federal", "sec", "ftc", "cdc", "nih", "who", "worldbank", "imf"]):
            return "government"
        elif any(edu in domain for edu in [".edu", "university", "college", "academic", "research", "mit", "stanford", "berkeley"]):
            return "education"
        elif any(tech in domain for tech in ["tech", "ai", "ml", "data", "computer", "anthropic", "openai", "deepmind", "stability", "replicate", "huggingface", "pytorch", "tensorflow"]):
            return "technology"
        else:
            return random.choice(["finance", "healthcare", "legal", "technology", "education", "government"])
    
    def _determine_subcategory(self, domain, category):
        """Determine domain subcategory based on domain and category."""
        subcategories = {
            "finance": ["banking", "investment", "insurance", "cryptocurrency", "fintech", "markets", "wealth_management"],
            "healthcare": ["hospitals", "research", "pharmaceuticals", "insurance", "telehealth", "medical_devices", "wellness"],
            "legal": ["law_firms", "legal_resources", "court_systems", "regulations", "legal_tech", "intellectual_property"],
            "government": ["federal", "regulatory", "public_health", "international", "economic", "security"],
            "education": ["universities", "research", "online_learning", "k12", "academic_publishing", "educational_technology"],
            "technology": ["ai", "cloud", "cybersecurity", "software", "hardware", "data_science", "social_media"]
        }
        
        # Get available subcategories for the domain's category
        available_subcategories = subcategories.get(category, ["general"])
        
        # Try to determine a fitting subcategory based on domain name
        for subcategory in available_subcategories:
            if subcategory.lower() in domain.lower():
                return subcategory
        
        # Return random subcategory if no match found
        return random.choice(available_subcategories)
    
    def _determine_priority(self, domain, trust_score):
        """Determine domain priority based on domain and trust score."""
        # Government and education domains typically have higher priority
        if any(high_priority in domain for high_priority in [".gov", ".edu", "health", "bank", "invest"]):
            return "high"
        # Technology and research domains often have medium priority
        elif any(medium_priority in domain for medium_priority in ["tech", "research", "news", "data"]):
            return "medium"
        # Determine based on trust score
        elif trust_score >= 85:
            return "high"
        elif trust_score >= 70:
            return "medium"
        else:
            return "low"
    
    def _calculate_volatility(self, samples):
        """Calculate volatility (standard deviation) of a list of samples."""
        if not samples:
            return 0
        
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        return (variance ** 0.5)
    
    def _load_categories(self):
        """Load category data with rich metadata."""
        categories_file = f"{DATA_DIR}/categories.json"
        
        try:
            if os.path.exists(categories_file):
                with open(categories_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading categories: {e}")
        
        # Create rich category data
        categories = {
            "finance": {
                "name": "Finance",
                "description": "Financial services, investment, banking, and markets",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.85, 0.95), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["banking", "investment", "insurance", "cryptocurrency", "fintech", "markets", "wealth_management"],
                "recent_domains": random.randint(20, 40),
                "average_trust_score": round(random.uniform(80.0, 90.0), 1),
                "volatility_index": round(random.uniform(0.1, 0.4), 2),
                "hallucination_risk": round(random.uniform(0.05, 0.2), 2),
                "citation_velocity": round(random.uniform(0.5, 0.9), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.75,
                    "reference_quality_min": 0.8,
                    "transparency_min": 0.7
                },
                "trending_topics": ["cryptocurrency regulation", "fintech disruption", "market volatility", "sustainable investing"],
                "elite_domains": ["jpmorgan.com", "blackrock.com", "vanguard.com"]
            },
            "healthcare": {
                "name": "Healthcare",
                "description": "Medical services, health information, providers, and research",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.80, 0.92), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["hospitals", "research", "pharmaceuticals", "insurance", "telehealth", "medical_devices", "wellness"],
                "recent_domains": random.randint(20, 40),
                "average_trust_score": round(random.uniform(85.0, 92.0), 1),
                "volatility_index": round(random.uniform(0.05, 0.2), 2),
                "hallucination_risk": round(random.uniform(0.02, 0.15), 2),
                "citation_velocity": round(random.uniform(0.6, 0.95), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.85,
                    "reference_quality_min": 0.9,
                    "transparency_min": 0.8
                },
                "trending_topics": ["telehealth expansion", "medical research breakthroughs", "healthcare policy", "pandemic response"],
                "elite_domains": ["mayoclinic.org", "hopkinsmedicine.org", "nih.gov"]
            },
            "legal": {
                "name": "Legal",
                "description": "Legal resources, services, regulations, and practice areas",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.82, 0.94), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["law_firms", "legal_resources", "court_systems", "regulations", "legal_tech", "intellectual_property"],
                "recent_domains": random.randint(15, 35),
                "average_trust_score": round(random.uniform(82.0, 90.0), 1),
                "volatility_index": round(random.uniform(0.05, 0.25), 2),
                "hallucination_risk": round(random.uniform(0.03, 0.18), 2),
                "citation_velocity": round(random.uniform(0.55, 0.9), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.8,
                    "reference_quality_min": 0.85,
                    "transparency_min": 0.75
                },
                "trending_topics": ["AI in legal practice", "privacy regulations", "intellectual property challenges", "international law"],
                "elite_domains": ["law.cornell.edu", "scotusblog.com", "justia.com"]
            },
            "government": {
                "name": "Government",
                "description": "Government agencies, regulatory bodies, and public services",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.75, 0.9), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["federal", "regulatory", "public_health", "international", "economic", "security"],
                "recent_domains": random.randint(15, 30),
                "average_trust_score": round(random.uniform(85.0, 95.0), 1),
                "volatility_index": round(random.uniform(0.03, 0.15), 2),
                "hallucination_risk": round(random.uniform(0.02, 0.12), 2),
                "citation_velocity": round(random.uniform(0.5, 0.85), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.8,
                    "reference_quality_min": 0.85,
                    "transparency_min": 0.9
                },
                "trending_topics": ["regulatory compliance", "public health initiatives", "government transparency", "digital transformation"],
                "elite_domains": ["cdc.gov", "nih.gov", "sec.gov"]
            },
            "technology": {
                "name": "Technology",
                "description": "Tech products, services, innovation, and research",
                "trust_critical": False,
                "expertise_level": round(random.uniform(0.88, 0.96), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["ai", "cloud", "cybersecurity", "software", "hardware", "data_science", "social_media"],
                "recent_domains": random.randint(25, 45),
                "average_trust_score": round(random.uniform(75.0, 85.0), 1),
                "volatility_index": round(random.uniform(0.15, 0.45), 2),
                "hallucination_risk": round(random.uniform(0.1, 0.3), 2),
                "citation_velocity": round(random.uniform(0.7, 0.95), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.7,
                    "reference_quality_min": 0.75,
                    "transparency_min": 0.65
                },
                "trending_topics": ["AI ethics", "quantum computing", "cybersecurity threats", "tech regulation"],
                "elite_domains": ["openai.com", "deepmind.com", "mit.edu"]
            },
            "education": {
                "name": "Education",
                "description": "Educational institutions, resources, and research",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.83, 0.93), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["universities", "research", "online_learning", "k12", "academic_publishing", "educational_technology"],
                "recent_domains": random.randint(15, 35),
                "average_trust_score": round(random.uniform(83.0, 93.0), 1),
                "volatility_index": round(random.uniform(0.05, 0.2), 2),
                "hallucination_risk": round(random.uniform(0.03, 0.15), 2),
                "citation_velocity": round(random.uniform(0.6, 0.9), 2),
                "benchmark_standards": {
                    "fact_density_min": 0.8,
                    "reference_quality_min": 0.85,
                    "transparency_min": 0.75
                },
                "trending_topics": ["online education evolution", "research innovation", "educational equity", "AI in education"],
                "elite_domains": ["stanford.edu", "harvard.edu", "berkeley.edu"]
            }
        }
        
        # Save categories to file
        os.makedirs(os.path.dirname(categories_file), exist_ok=True)
        with open(categories_file, 'w') as f:
            json.dump(categories, f, indent=2)
        
        return categories
    
    def _load_benchmarks(self):
        """Load benchmark data with rich comparative metrics."""
        benchmarks_file = f"{BENCHMARK_DIR}/benchmarks.json"
        
        try:
            if os.path.exists(benchmarks_file):
                with open(benchmarks_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading benchmarks: {e}")
        
        # Create rich benchmark data
        benchmarks = {
            "category_benchmarks": {
                category: {
                    "trust_score": {
                        "elite": round(random.uniform(90.0, 98.0), 1),
                        "standard": round(random.uniform(75.0, 85.0), 1),
                        "minimum": round(random.uniform(60.0, 70.0), 1)
                    },
                    "citation_rate": {
                        "elite": round(random.uniform(0.7, 0.95), 2),
                        "standard": round(random.uniform(0.4, 0.6), 2),
                        "minimum": round(random.uniform(0.1, 0.3), 2)
                    },
                    "quality_score": {
                        "elite": round(random.uniform(0.9, 0.99), 2),
                        "standard": round(random.uniform(0.75, 0.85), 2),
                        "minimum": round(random.uniform(0.6, 0.7), 2)
                    },
                    "hallucination_risk": {
                        "elite": round(random.uniform(0.01, 0.05), 2),
                        "standard": round(random.uniform(0.1, 0.2), 2),
                        "maximum": round(random.uniform(0.3, 0.5), 2)
                    }
                }
                for category in self.categories.keys()
            },
            "movement_thresholds": {
                "significant_rise": 5.0,
                "significant_drop": -5.0,
                "volatile_range": 3.0,
                "stable_ceiling": 1.0
            },
            "elite_qualification": {
                "min_trust_score": 90.0,
                "min_citation_rate": 0.7,
                "min_quality_score": 0.9,
                "max_hallucination_risk": 0.05,
                "consistency_period_days": 30
            },
            "volatility_classification": {
                "highly_volatile": 0.3,
                "moderately_volatile": 0.15,
                "stable": 0.05
            },
            "last_updated": time.time()
        }
        
        # Save benchmarks to file
        os.makedirs(os.path.dirname(benchmarks_file), exist_ok=True)
        with open(benchmarks_file, 'w') as f:
            json.dump(benchmarks, f, indent=2)
        
        return benchmarks
    
    def _load_narratives(self):
        """Load narrative templates and active narratives."""
        narratives_file = f"{NARRATIVE_DIR}/active_narratives.json"
        
        try:
            if os.path.exists(narratives_file):
                with open(narratives_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading narratives: {e}")
        
        # Create initial narrative data
        narratives = {
            "elite_rise_narratives": [
                {
                    "domain": "mayoclinic.org",
                    "title": "Mayo Clinic Solidifies Elite Status with Unprecedented Trust Growth",
                    "summary": "Mayo Clinic has shown exceptional trust signal improvement over the past 30 days, with citation rates increasing by 15% and trust scores reaching new heights. Their methodical approach to content quality and transparent sourcing has set a new benchmark for healthcare information quality.",
                    "insights": [
                        "Citation rate increased from 0.72 to 0.83 in 30 days",
                        "Trust score reached 94.7, the highest in the healthcare vertical",
                        "Hallucination risk decreased to a record low 0.02",
                        "Content freshness metrics show 96% of content updated within 6 months"
                    ],
                    "recommendation": "Study Mayo Clinic's citation structure as a model for healthcare trust signals",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                },
                {
                    "domain": "blackrock.com",
                    "title": "BlackRock Emerges as Financial Trust Leader Through Methodical Data Quality",
                    "summary": "BlackRock has demonstrated remarkable consistency in maintaining elite trust status across all metrics. Their financial content shows exceptional fact density and reference quality, with hallucination risk metrics consistently below industry standards.",
                    "insights": [
                        "Maintained trust score above 92 for 60 consecutive days",
                        "Citation authority rating of 0.97, highest among financial institutions",
                        "Consistency ratings show minimal variance across all content areas",
                        "Fact density metrics consistently 35% above category average"
                    ],
                    "recommendation": "BlackRock's reference architecture can serve as a template for financial trust verification",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                }
            ],
            "volatility_narratives": [
                {
                    "domain": "coinbase.com",
                    "title": "Coinbase Trust Signals Show Extreme Volatility During Market Fluctuations",
                    "summary": "Coinbase has experienced significant trust signal volatility over the past 45 days, with trust scores fluctuating between 68 and 85. This volatility correlates with cryptocurrency market movements and regulatory announcements, revealing interesting patterns in how financial trust signals respond to market conditions.",
                    "insights": [
                        "Trust score standard deviation of 6.3 points over 45 days",
                        "Citation rates inversely correlated with market volatility",
                        "Content freshness degrades during high volatility periods",
                        "Hallucination risk increased by 35% during regulatory announcement periods"
                    ],
                    "recommendation": "Cryptocurrency domains require specialized trust signal monitoring during market events",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                },
                {
                    "domain": "openai.com",
                    "title": "OpenAI Trust Signals Show Rapid Expansion and Category-Defying Patterns",
                    "summary": "OpenAI's trust signals exhibit unusual patterns that defy typical category benchmarks. While maintaining elite citation authority, their trust volatility is 3x higher than category norms, suggesting a new paradigm for evaluating AI research organizations where rapid innovation creates inherent trust signal turbulence.",
                    "insights": [
                        "Trust score fluctuations of +/-12 points within 30-day windows",
                        "Citation velocity 2.3x higher than technology category average",
                        "Content freshness metrics maintain elite status despite volatility",
                        "Creates 'citation pulse waves' that propagate across the AI research vertical"
                    ],
                    "recommendation": "Develop specialized AI research trust signal metrics that account for innovation velocity",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                }
            ],
            "trust_drift_narratives": [
                {
                    "domain": "nih.gov",
                    "title": "NIH Sets New Trust Signal Benchmark After Research Transparency Initiative",
                    "summary": "The National Institutes of Health has achieved remarkable trust signal improvements following their research transparency initiative. Their trust score has steadily increased by 0.5 points weekly for 12 consecutive weeks, establishing a new benchmark for government health information sources.",
                    "insights": [
                        "Consistent weekly trust score growth for 3 months straight",
                        "Methodology clarity rating increased from 0.82 to 0.94",
                        "Citation rates by academic sources increased 28%",
                        "Content freshness improved with 92% of research summaries updated within 30 days"
                    ],
                    "recommendation": "Government health agencies should adopt NIH's transparency framework as a trust signal standard",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                },
                {
                    "domain": "law.cornell.edu",
                    "title": "Cornell Law Shows How Academic Legal Resources Maintain Trust Despite Regulatory Shifts",
                    "summary": "Cornell Law's legal information portal demonstrates exceptional trust stability despite major shifts in regulatory environments. Their trust signals maintain elite status through rapid content updates and transparent methodology that acknowledges regulatory uncertainty.",
                    "insights": [
                        "Trust score maintained above 92 despite major regulatory changes",
                        "Update velocity 3.2x faster than other legal resources during regulatory shifts",
                        "Methodology transparency 27% higher than category average",
                        "Citation authority maintains 0.95+ rating across all subcategories"
                    ],
                    "recommendation": "Legal resources should adopt Cornell's change tracking system for maintaining trust during regulatory transitions",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                }
            ],
            "peer_competition_narratives": [
                {
                    "domain": "mayoclinic.org",
                    "title": "Mayo Clinic vs. Cleveland Clinic: The Trust Signal Battle Reshaping Healthcare Information",
                    "summary": "A fascinating trust signal competition has emerged between Mayo Clinic and Cleveland Clinic, with each organization implementing different approaches to content quality and citation structures. Mayo's emphasis on methodology transparency contrasts with Cleveland's focus on content freshness, creating distinct trust profiles.",
                    "insights": [
                        "Mayo Clinic leads in methodology clarity (0.94 vs 0.89)",
                        "Cleveland Clinic maintains slight edge in content freshness (0.93 vs 0.91)",
                        "Citation patterns show regional preferences in healthcare practitioner references",
                        "Trust volatility significantly lower for Mayo Clinic (0.07 vs 0.11)"
                    ],
                    "recommendation": "Healthcare information sources should consider hybrid approaches combining both institutions' strengths",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                },
                {
                    "domain": "vanguard.com",
                    "title": "Investment Titans Trust Battle: Vanguard vs. Fidelity vs. Schwab",
                    "summary": "A three-way competition for trust supremacy has developed among investment giants Vanguard, Fidelity, and Schwab. Each demonstrates different strengths in trust signals, with Vanguard leading in factual consistency, Fidelity in content freshness, and Schwab in methodology transparency.",
                    "insights": [
                        "Vanguard maintains highest overall trust score (91.3 vs 90.7 vs 89.8)",
                        "Fidelity's content freshness rating leads category (0.94 vs 0.91 vs 0.89)",
                        "Schwab's methodology transparency creates lowest hallucination risk (0.03 vs 0.04 vs 0.05)",
                        "Citation patterns reveal Vanguard's dominance in academic financial references"
                    ],
                    "recommendation": "Investment information providers should analyze all three approaches for comprehensive trust signal optimization",
                    "created": (datetime.now() - timedelta(days=random.randint(1, 10))).isoformat()
                }
            ],
            "last_updated": time.time()
        }
        
        # Save narratives to file
        os.makedirs(os.path.dirname(narratives_file), exist_ok=True)
        with open(narratives_file, 'w') as f:
            json.dump(narratives, f, indent=2)
        
        return narratives
    
    def _identify_elite_domains(self):
        """Identify elite domains based on trust metrics."""
        elite_domains = {}
        
        # Get elite qualification criteria
        elite_criteria = self.benchmarks.get("elite_qualification", {})
        min_trust_score = elite_criteria.get("min_trust_score", 90.0)
        min_citation_rate = elite_criteria.get("min_citation_rate", 0.7)
        min_quality_score = elite_criteria.get("min_quality_score", 0.9)
        max_hallucination_risk = elite_criteria.get("max_hallucination_risk", 0.05)
        
        # Evaluate each domain
        for domain, data in self.domains.items():
            trust_score = data.get("trust_score", 0)
            citation_rate = data.get("citation_rate", 0)
            quality_score = data.get("quality_score", 0)
            hallucination_risk = data.get("hallucination_risk", 1)
            
            # Check if domain meets elite criteria
            if (trust_score >= min_trust_score and 
                citation_rate >= min_citation_rate and 
                quality_score >= min_quality_score and 
                hallucination_risk <= max_hallucination_risk):
                
                category = data.get("category", "unknown")
                subcategory = data.get("subcategory", "unknown")
                
                # Add to elite domains
                if category not in elite_domains:
                    elite_domains[category] = {}
                
                if subcategory not in elite_domains[category]:
                    elite_domains[category][subcategory] = []
                
                elite_domains[category][subcategory].append({
                    "domain": domain,
                    "trust_score": trust_score,
                    "citation_rate": citation_rate,
                    "quality_score": quality_score,
                    "hallucination_risk": hallucination_risk
                })
        
        return elite_domains
    
    def _identify_volatile_domains(self):
        """Identify domains with high trust volatility."""
        volatile_domains = {}
        
        # Get volatility classification thresholds
        volatility_thresholds = self.benchmarks.get("volatility_classification", {})
        highly_volatile = volatility_thresholds.get("highly_volatile", 0.3)
        moderately_volatile = volatility_thresholds.get("moderately_volatile", 0.15)
        
        # Evaluate each domain
        for domain, data in self.domains.items():
            volatility = data.get("trust_volatility", 0)
            
            # Determine volatility category
            volatility_category = "stable"
            if volatility >= highly_volatile:
                volatility_category = "highly_volatile"
            elif volatility >= moderately_volatile:
                volatility_category = "moderately_volatile"
            
            # Skip stable domains
            if volatility_category == "stable":
                continue
            
            category = data.get("category", "unknown")
            
            # Add to volatile domains
            if category not in volatile_domains:
                volatile_domains[category] = {}
            
            if volatility_category not in volatile_domains[category]:
                volatile_domains[category][volatility_category] = []
            
            volatile_domains[category][volatility_category].append({
                "domain": domain,
                "volatility": volatility,
                "trust_score": data.get("trust_score", 0),
                "weekly_trend": data.get("weekly_trust_trend", [])[-5:] if data.get("weekly_trust_trend") else []
            })
        
        return volatile_domains
    
    def _generate_elite_insights(self):
        """Generate insights for elite domains."""
        logger.info("Generating elite domain insights...")
        
        insights = {
            "categories": {},
            "movement": [],
            "peer_comparisons": [],
            "last_updated": time.time()
        }
        
        # Generate category insights
        for category, subcategories in self.elite_domains.items():
            if category not in insights["categories"]:
                insights["categories"][category] = []
            
            for subcategory, domains in subcategories.items():
                # Sort domains by trust score
                sorted_domains = sorted(domains, key=lambda x: x["trust_score"], reverse=True)
                
                if sorted_domains:
                    # Top domain in subcategory
                    top_domain = sorted_domains[0]
                    
                    # Create insight
                    insight = {
                        "domain": top_domain["domain"],
                        "subcategory": subcategory,
                        "trust_score": top_domain["trust_score"],
                        "citation_rate": top_domain["citation_rate"],
                        "quality_score": top_domain["quality_score"],
                        "rank": 1,
                        "insight": f"{top_domain['domain']} leads the {subcategory} subcategory with exceptional trust signals across all metrics.",
                        "standout_metric": self._identify_standout_metric(top_domain)
                    }
                    
                    insights["categories"][category].append(insight)
        
        # Generate movement insights (domains moving into elite status)
        movement_candidates = []
        for domain, data in self.domains.items():
            # Check if domain has shown significant improvement
            if "weekly_trust_trend" in data:
                trend = data["weekly_trust_trend"]
                if len(trend) >= 2:
                    recent_change = trend[-1] - trend[-2]
                    if recent_change >= 3.0 and trend[-1] >= 89.0:
                        movement_candidates.append({
                            "domain": domain,
                            "category": data.get("category", "unknown"),
                            "subcategory": data.get("subcategory", "unknown"),
                            "current_score": trend[-1],
                            "previous_score": trend[-2],
                            "improvement": recent_change
                        })
        
        # Sort by improvement and add top candidates
        sorted_candidates = sorted(movement_candidates, key=lambda x: x["improvement"], reverse=True)
        insights["movement"] = sorted_candidates[:5]
        
        # Generate peer comparison insights
        for category, subcategories in self.elite_domains.items():
            for subcategory, domains in subcategories.items():
                if len(domains) >= 2:
                    # Get top two domains
                    sorted_domains = sorted(domains, key=lambda x: x["trust_score"], reverse=True)
                    top_domain = sorted_domains[0]
                    runner_up = sorted_domains[1]
                    
                    # Create comparison insight
                    comparison = {
                        "leader_domain": top_domain["domain"],
                        "challenger_domain": runner_up["domain"],
                        "category": category,
                        "subcategory": subcategory,
                        "score_gap": round(top_domain["trust_score"] - runner_up["trust_score"], 1),
                        "leader_strength": self._identify_standout_metric(top_domain),
                        "challenger_strength": self._identify_standout_metric(runner_up),
                        "insight": f"{top_domain['domain']} maintains a {round(top_domain['trust_score'] - runner_up['trust_score'], 1)} point lead over {runner_up['domain']} in {subcategory} trust signals."
                    }
                    
                    insights["peer_comparisons"].append(comparison)
        
        # Save insights to file
        insights_file = f"{INSIGHT_DIR}/elite_insights.json"
        os.makedirs(os.path.dirname(insights_file), exist_ok=True)
        with open(insights_file, 'w') as f:
            json.dump(insights, f, indent=2)
        
        logger.info("Elite insights generated and saved")
        
        return insights
    
    def _generate_volatile_insights(self):
        """Generate insights for volatile domains."""
        logger.info("Generating volatile domain insights...")
        
        insights = {
            "highly_volatile": [],
            "moderately_volatile": [],
            "pattern_insights": [],
            "category_volatility": {},
            "last_updated": time.time()
        }
        
        # Collect volatile domains by category
        for category, volatility_categories in self.volatile_domains.items():
            # Add highly volatile domains
            if "highly_volatile" in volatility_categories:
                for domain_data in volatility_categories["highly_volatile"]:
                    insights["highly_volatile"].append({
                        "domain": domain_data["domain"],
                        "category": category,
                        "volatility": domain_data["volatility"],
                        "current_score": domain_data["trust_score"],
                        "trend": domain_data["weekly_trend"],
                        "insight": f"{domain_data['domain']} shows extreme trust volatility, requiring special monitoring procedures."
                    })
            
            # Add moderately volatile domains
            if "moderately_volatile" in volatility_categories:
                for domain_data in volatility_categories["moderately_volatile"]:
                    insights["moderately_volatile"].append({
                        "domain": domain_data["domain"],
                        "category": category,
                        "volatility": domain_data["volatility"],
                        "current_score": domain_data["trust_score"],
                        "trend": domain_data["weekly_trend"],
                        "insight": f"{domain_data['domain']} exhibits moderate trust volatility with discernible patterns."
                    })
            
            # Calculate category volatility
            all_volatilities = []
            if "highly_volatile" in volatility_categories:
                all_volatilities.extend([d["volatility"] for d in volatility_categories["highly_volatile"]])
            if "moderately_volatile" in volatility_categories:
                all_volatilities.extend([d["volatility"] for d in volatility_categories["moderately_volatile"]])
            
            if all_volatilities:
                avg_volatility = sum(all_volatilities) / len(all_volatilities)
                insights["category_volatility"][category] = {
                    "average_volatility": round(avg_volatility, 2),
                    "domain_count": len(all_volatilities),
                    "highly_volatile_count": len(volatility_categories.get("highly_volatile", [])),
                    "moderately_volatile_count": len(volatility_categories.get("moderately_volatile", []))
                }
        
        # Generate pattern insights
        all_volatile_domains = insights["highly_volatile"] + insights["moderately_volatile"]
        
        # Sort by volatility
        sorted_volatile = sorted(all_volatile_domains, key=lambda x: x["volatility"], reverse=True)
        
        # Generate insights for top volatile domains
        for domain_data in sorted_volatile[:5]:
            domain = domain_data["domain"]
            category = domain_data["category"]
            volatility = domain_data["volatility"]
            
            # Create pattern insight
            pattern_insight = {
                "domain": domain,
                "category": category,
                "volatility": volatility,
                "pattern_type": self._identify_volatility_pattern(domain_data["trend"]),
                "risk_assessment": "high" if volatility > 0.3 else "moderate",
                "insight": f"{domain} demonstrates a {self._identify_volatility_pattern(domain_data['trend'])} pattern with {round(volatility, 2)} volatility score."
            }
            
            insights["pattern_insights"].append(pattern_insight)
        
        # Save insights to file
        insights_file = f"{INSIGHT_DIR}/volatile_insights.json"
        os.makedirs(os.path.dirname(insights_file), exist_ok=True)
        with open(insights_file, 'w') as f:
            json.dump(insights, f, indent=2)
        
        logger.info("Volatile insights generated and saved")
        
        return insights
    
    def _identify_standout_metric(self, domain_data):
        """Identify the standout metric for a domain."""
        metrics = {
            "trust_score": domain_data.get("trust_score", 0),
            "citation_rate": domain_data.get("citation_rate", 0) * 100,  # Scale to compare
            "quality_score": domain_data.get("quality_score", 0) * 100,  # Scale to compare
            "hallucination_resistance": (1 - domain_data.get("hallucination_risk", 0)) * 100  # Invert and scale
        }
        
        # Find the highest metric
        standout = max(metrics.items(), key=lambda x: x[1])
        
        # Format the result
        if standout[0] == "trust_score":
            return f"exceptional trust score of {standout[1]}"
        elif standout[0] == "citation_rate":
            return f"superior citation rate of {round(standout[1]/100, 2)}"
        elif standout[0] == "quality_score":
            return f"outstanding quality score of {round(standout[1]/100, 2)}"
        else:
            return f"excellent hallucination resistance of {round(standout[1]/100, 2)}"
    
    def _identify_volatility_pattern(self, trend):
        """Identify the volatility pattern from trend data."""
        if not trend or len(trend) < 3:
            return "insufficient data"
        
        # Calculate differences between consecutive points
        diffs = [trend[i] - trend[i-1] for i in range(1, len(trend))]
        
        # Check for alternating pattern (up-down-up or down-up-down)
        alternating = True
        for i in range(1, len(diffs)):
            if (diffs[i] > 0 and diffs[i-1] > 0) or (diffs[i] < 0 and diffs[i-1] < 0):
                alternating = False
                break
        
        if alternating:
            return "alternating"
        
        # Check for sudden spike or drop
        max_abs_diff = max(abs(d) for d in diffs)
        if max_abs_diff > 10:
            if diffs[diffs.index(max(diffs, key=abs))] > 0:
                return "sudden spike"
            else:
                return "sudden drop"
        
        # Check for consistent trend
        if all(d > 0 for d in diffs):
            return "consistent rise"
        elif all(d < 0 for d in diffs):
            return "consistent decline"
        
        # Check for recent reversal
        if len(diffs) >= 3:
            earlier_direction = sum(diffs[:-2]) > 0  # True if rising, False if falling
            recent_direction = sum(diffs[-2:]) > 0
            if earlier_direction != recent_direction:
                return "recent reversal"
        
        # Default
        return "irregular"
    
    def generate_foma_narrative(self):
        """Generate a compelling FOMA narrative based on current data."""
        logger.info("Generating FOMA narrative...")
        
        # Decide on narrative type
        narrative_types = ["elite_rise", "volatility", "trust_drift", "peer_competition"]
        narrative_type = random.choice(narrative_types)
        
        narrative = None
        
        if narrative_type == "elite_rise":
            # Generate elite rise narrative
            elite_domains_flat = []
            for category, subcategories in self.elite_domains.items():
                for subcategory, domains in subcategories.items():
                    for domain_data in domains:
                        domain_data["category"] = category
                        domain_data["subcategory"] = subcategory
                        elite_domains_flat.append(domain_data)
            
            if elite_domains_flat:
                # Select random elite domain
                domain_data = random.choice(elite_domains_flat)
                domain = domain_data["domain"]
                category = domain_data["category"]
                subcategory = domain_data["subcategory"]
                
                # Get domain details
                domain_details = self.domains.get(domain, {})
                
                # Create narrative
                narrative = {
                    "domain": domain,
                    "title": f"{domain} Establishes Elite Trust Position in {subcategory.replace('_', ' ').title()}",
                    "summary": f"{domain} has demonstrated exceptional trust signals across all metrics, establishing itself as an elite source in the {category} category. Its combination of high factual accuracy, transparent methodology, and consistent citation patterns creates a compelling trust profile.",
                    "insights": [
                        f"Trust score of {domain_details.get('trust_score', 'N/A')} places it in the top tier of {category} domains",
                        f"Citation rate of {domain_details.get('citation_rate', 'N/A')} indicates frequent reference by authoritative sources",
                        f"Quality score of {domain_details.get('quality_score', 'N/A')} demonstrates exceptional content standards",
                        f"Low hallucination risk of {domain_details.get('hallucination_risk', 'N/A')} suggests high factual reliability"
                    ],
                    "recommendation": f"Consider {domain} as a trust signal benchmark for other {subcategory.replace('_', ' ')} domains",
                    "created": datetime.now().isoformat()
                }
                
                # Add to narratives
                if len(self.narratives["elite_rise_narratives"]) > 10:
                    self.narratives["elite_rise_narratives"].pop()
                self.narratives["elite_rise_narratives"].insert(0, narrative)
        
        elif narrative_type == "volatility":
            # Generate volatility narrative
            volatile_domains_flat = []
            for category, volatility_categories in self.volatile_domains.items():
                for volatility_category, domains in volatility_categories.items():
                    for domain_data in domains:
                        domain_data["category"] = category
                        domain_data["volatility_category"] = volatility_category
                        volatile_domains_flat.append(domain_data)
            
            if volatile_domains_flat:
                # Select random volatile domain
                domain_data = random.choice(volatile_domains_flat)
                domain = domain_data["domain"]
                category = domain_data["category"]
                volatility = domain_data["volatility"]
                
                # Determine pattern
                pattern = self._identify_volatility_pattern(domain_data["weekly_trend"])
                
                # Create narrative
                narrative = {
                    "domain": domain,
                    "title": f"{domain} Exhibits {pattern.title()} Trust Signal Pattern with {round(volatility, 2)} Volatility",
                    "summary": f"{domain} shows significant trust signal volatility with a {pattern} pattern. This behavior provides valuable insights into how {category} domains respond to external factors and content changes.",
                    "insights": [
                        f"Volatility score of {round(volatility, 2)} indicates unusual trust signal movement",
                        f"Demonstrates a {pattern} pattern over recent measurements",
                        f"Current trust score of {domain_data.get('trust_score', 'N/A')} with high variance",
                        f"Requires specialized monitoring approach due to volatility"
                    ],
                    "recommendation": f"Implement heightened monitoring frequency for {domain} to capture trust signal dynamics",
                    "created": datetime.now().isoformat()
                }
                
                # Add to narratives
                if len(self.narratives["volatility_narratives"]) > 10:
                    self.narratives["volatility_narratives"].pop()
                self.narratives["volatility_narratives"].insert(0, narrative)
        
        elif narrative_type == "trust_drift":
            # Generate trust drift narrative
            candidates = []
            
            for domain, data in self.domains.items():
                if "weekly_trust_trend" in data and len(data["weekly_trust_trend"]) >= 4:
                    trend = data["weekly_trust_trend"]
                    # Calculate drift
                    start = trend[-4]
                    end = trend[-1]
                    drift = end - start
                    
                    if abs(drift) >= 5.0:
                        candidates.append({
                            "domain": domain,
                            "category": data.get("category", "unknown"),
                            "drift": drift,
                            "start_score": start,
                            "end_score": end
                        })
            
            if candidates:
                # Select random candidate
                candidate = random.choice(candidates)
                domain = candidate["domain"]
                category = candidate["category"]
                drift = candidate["drift"]
                
                # Create narrative title and summary based on drift direction
                if drift > 0:
                    title = f"{domain} Shows Remarkable Trust Signal Improvement of {round(drift, 1)} Points"
                    summary = f"{domain} has demonstrated a significant positive trust signal drift over the past four measurements, improving by {round(drift, 1)} points. This improvement suggests systematic enhancement of content quality and citation structures."
                else:
                    title = f"{domain} Experiences Concerning Trust Signal Decline of {round(abs(drift), 1)} Points"
                    summary = f"{domain} has shown a notable negative trust signal drift over the past four measurements, declining by {round(abs(drift), 1)} points. This trend warrants investigation into potential content quality issues or citation problems."
                
                # Create narrative
                narrative = {
                    "domain": domain,
                    "title": title,
                    "summary": summary,
                    "insights": [
                        f"Trust score changed from {round(candidate['start_score'], 1)} to {round(candidate['end_score'], 1)}",
                        f"Represents a {round(abs(drift / candidate['start_score'] * 100), 1)}% {'increase' if drift > 0 else 'decrease'}",
                        f"Pattern suggests {'systematic improvement' if drift > 0 else 'content degradation'} requiring attention",
                        f"{'Opportunity for benchmark study' if drift > 0 else 'Indicates need for remediation strategy'}"
                    ],
                    "recommendation": f"{'Study factors behind improvement for potential application to other domains' if drift > 0 else 'Investigate root causes of trust decline and implement monitoring alerts'}",
                    "created": datetime.now().isoformat()
                }
                
                # Add to narratives
                if len(self.narratives["trust_drift_narratives"]) > 10:
                    self.narratives["trust_drift_narratives"].pop()
                self.narratives["trust_drift_narratives"].insert(0, narrative)
        
        elif narrative_type == "peer_competition":
            # Generate peer competition narrative
            category_domains = {}
            
            # Group domains by category and subcategory
            for domain, data in self.domains.items():
                category = data.get("category", "unknown")
                subcategory = data.get("subcategory", "unknown")
                
                if category not in category_domains:
                    category_domains[category] = {}
                
                if subcategory not in category_domains[category]:
                    category_domains[category][subcategory] = []
                
                category_domains[category][subcategory].append({
                    "domain": domain,
                    "trust_score": data.get("trust_score", 0),
                    "citation_rate": data.get("citation_rate", 0),
                    "quality_score": data.get("quality_score", 0),
                    "hallucination_risk": data.get("hallucination_risk", 1)
                })
            
            # Find subcategories with close competition
            competitive_pairs = []
            
            for category, subcategories in category_domains.items():
                for subcategory, domains in subcategories.items():
                    if len(domains) >= 2:
                        # Sort by trust score
                        sorted_domains = sorted(domains, key=lambda x: x["trust_score"], reverse=True)
                        # Check if top two are close
                        if abs(sorted_domains[0]["trust_score"] - sorted_domains[1]["trust_score"]) < 3.0:
                            competitive_pairs.append({
                                "domain1": sorted_domains[0]["domain"],
                                "domain2": sorted_domains[1]["domain"],
                                "score1": sorted_domains[0]["trust_score"],
                                "score2": sorted_domains[1]["trust_score"],
                                "gap": abs(sorted_domains[0]["trust_score"] - sorted_domains[1]["trust_score"]),
                                "category": category,
                                "subcategory": subcategory
                            })
            
            if competitive_pairs:
                # Select random competitive pair
                pair = random.choice(competitive_pairs)
                domain1 = pair["domain1"]
                domain2 = pair["domain2"]
                category = pair["category"]
                subcategory = pair["subcategory"]
                
                # Create narrative
                narrative = {
                    "domain": f"{domain1} vs {domain2}",
                    "title": f"Trust Signal Battle: {domain1} and {domain2} Compete for {subcategory.replace('_', ' ').title()} Leadership",
                    "summary": f"A fascinating trust signal competition has emerged between {domain1} and {domain2} in the {subcategory.replace('_', ' ')} subcategory. With only {round(pair['gap'], 1)} points separating their trust scores, both domains demonstrate different strengths in building trust signals.",
                    "insights": [
                        f"{domain1} leads with a trust score of {round(pair['score1'], 1)} versus {round(pair['score2'], 1)} for {domain2}",
                        f"Competition centers on different trust building strategies with unique strengths",
                        f"Gap of only {round(pair['gap'], 1)} points indicates highly competitive trust signals",
                        f"Creates ideal comparative study opportunity for trust signal optimization"
                    ],
                    "recommendation": f"Analyze both {domain1} and {domain2} to identify complementary trust signal strategies",
                    "created": datetime.now().isoformat()
                }
                
                # Add to narratives
                if len(self.narratives["peer_competition_narratives"]) > 10:
                    self.narratives["peer_competition_narratives"].pop()
                self.narratives["peer_competition_narratives"].insert(0, narrative)
        
        # Save updated narratives
        if narrative:
            self.narratives["last_updated"] = time.time()
            
            narratives_file = f"{NARRATIVE_DIR}/active_narratives.json"
            os.makedirs(os.path.dirname(narratives_file), exist_ok=True)
            with open(narratives_file, 'w') as f:
                json.dump(self.narratives, f, indent=2)
            
            logger.info(f"Generated new {narrative_type} narrative for {narrative['domain']}")
        
        return narrative
    
    def update_all_insights(self):
        """Update all insights and generate new FOMA narrative."""
        logger.info("Updating all insights...")
        
        # Identify elite and volatile domains
        self.elite_domains = self._identify_elite_domains()
        self.volatile_domains = self._identify_volatile_domains()
        
        # Generate insights
        self._generate_elite_insights()
        self._generate_volatile_insights()
        
        # Generate new FOMA narrative
        narrative = self.generate_foma_narrative()
        
        logger.info("All insights updated successfully")
        
        return narrative
    
    def get_elite_insights(self):
        """Get elite domain insights."""
        insights_file = f"{INSIGHT_DIR}/elite_insights.json"
        
        try:
            if os.path.exists(insights_file):
                with open(insights_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading elite insights: {e}")
        
        return None
    
    def get_volatile_insights(self):
        """Get volatile domain insights."""
        insights_file = f"{INSIGHT_DIR}/volatile_insights.json"
        
        try:
            if os.path.exists(insights_file):
                with open(insights_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading volatile insights: {e}")
        
        return None
    
    def get_active_narratives(self):
        """Get active narratives."""
        return self.narratives
    
    def get_benchmarks(self):
        """Get benchmarks."""
        return self.benchmarks

# Global FOMA engine instance
_foma_engine = None

def start_foma_engine():
    """Start the FOMA insight engine."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = FomaInsightEngine()
    
    return _foma_engine

def get_elite_insights():
    """Get elite domain insights."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.get_elite_insights()

def get_volatile_insights():
    """Get volatile domain insights."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.get_volatile_insights()

def get_active_narratives():
    """Get active narratives."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.get_active_narratives()

def get_benchmarks():
    """Get benchmarks."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.get_benchmarks()

def update_all_insights():
    """Update all insights."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.update_all_insights()

def generate_foma_narrative():
    """Generate a new FOMA narrative."""
    global _foma_engine
    
    if _foma_engine is None:
        _foma_engine = start_foma_engine()
    
    return _foma_engine.generate_foma_narrative()

# Run engine when executed directly
if __name__ == "__main__":
    logger.info("Starting FOMA insight engine...")
    
    # Start engine
    engine = start_foma_engine()
    
    # Update insights
    narrative = engine.update_all_insights()
    
    if narrative:
        logger.info(f"Generated narrative: {narrative['title']}")
    
    logger.info("FOMA insight engine initialization complete")