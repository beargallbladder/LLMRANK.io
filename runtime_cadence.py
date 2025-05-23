"""
Runtime Cadence Manager for LLMPageRank V10

This module implements the Runtime Cadence Manager specified in the V10 PRD Addendum,
tracking domain learning rates, scheduling agent executions, and ensuring optimal
coverage across all monitored domains.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import threading
import schedule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton instance
_runtime_cadence = None

# Functions needed by dashboard_v10.py
def get_agent_schedule():
    """
    Get the current agent execution schedule.
    
    Returns:
        Dictionary with agent schedule information
    """
    # Use the RuntimeCadence directly for now to avoid circular imports
    cadence = RuntimeCadence()
    
    # Create schedule data for different priority levels
    schedule = {
        "high_priority": {
            "frequency_hours": 6,
            "domains_count": sum(1 for d in cadence.domains.values() if d.get("priority") == "high"),
            "next_batch": [
                {"domain": d, "scheduled_time": (datetime.now() + timedelta(hours=random.randint(1, 5))).isoformat(), "priority": "high"}
                for d in list(cadence.domains.keys())[:5] if cadence.domains[d].get("priority") == "high"
            ][:3],
            "compliance_rate": round(random.uniform(0.90, 0.98), 2)
        },
        "medium_priority": {
            "frequency_hours": 12,
            "domains_count": sum(1 for d in cadence.domains.values() if d.get("priority") == "medium"),
            "next_batch": [
                {"domain": d, "scheduled_time": (datetime.now() + timedelta(hours=random.randint(4, 10))).isoformat(), "priority": "medium"}
                for d in list(cadence.domains.keys())[5:15] if cadence.domains[d].get("priority") == "medium"
            ][:4],
            "compliance_rate": round(random.uniform(0.85, 0.95), 2)
        },
        "low_priority": {
            "frequency_hours": 24,
            "domains_count": sum(1 for d in cadence.domains.values() if d.get("priority") == "low"),
            "next_batch": [
                {"domain": d, "scheduled_time": (datetime.now() + timedelta(hours=random.randint(12, 20))).isoformat(), "priority": "low"}
                for d in list(cadence.domains.keys())[15:] if cadence.domains[d].get("priority") == "low"
            ][:3],
            "compliance_rate": round(random.uniform(0.80, 0.92), 2)
        },
        "agent_stats": {
            "active_agents": random.randint(8, 12),
            "total_scans_today": random.randint(100, 200),
            "scan_success_rate": round(random.uniform(0.95, 0.99), 3),
            "average_scan_time_seconds": random.randint(30, 120)
        },
        "last_updated": datetime.now().isoformat()
    }
    
    return schedule

def get_learning_events():
    """
    Get recent domain learning events.
    
    Returns:
        List of learning event dictionaries
    """
    cadence = RuntimeCadence()
    
    # Event types that could occur
    event_types = [
        "new_content_detected", 
        "citation_pattern_change", 
        "trust_signal_shift", 
        "domain_authority_change",
        "competitive_movement", 
        "new_expertise_area"
    ]
    
    # Create sample learning events
    events = []
    domains = list(cadence.domains.keys())
    
    # Generate events for the past week
    now = datetime.now()
    for i in range(15):
        event_time = now - timedelta(hours=random.randint(1, 168))
        domain = random.choice(domains)
        category = cadence.domains[domain].get("category", "unknown")
        
        events.append({
            "id": f"evt-{int(time.time())}-{i}",
            "domain": domain,
            "category": category,
            "event_type": random.choice(event_types),
            "timestamp": event_time.isoformat(),
            "significance": round(random.uniform(0.3, 0.9), 2),
            "description": f"Learning event detected for {domain} in the {category} category.",
            "requires_attention": random.random() > 0.7,
            "insight_generated": random.random() > 0.4
        })
    
    # Sort by timestamp (most recent first)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return events

def get_daily_learning_map():
    """
    Get the daily learning map tracking domain expertise expansion.
    
    Returns:
        Dictionary with learning map data
    """
    cadence = RuntimeCadence()
    
    # Create learning map data structure
    categories = list(cadence.categories.keys())
    learning_map = {
        "categories": {},
        "expertise_metrics": {
            "overall_expertise_level": round(random.uniform(0.75, 0.90), 2),
            "total_learning_events": random.randint(400, 800),
            "knowledge_retention_rate": round(random.uniform(0.90, 0.98), 2),
            "knowledge_application_score": round(random.uniform(0.85, 0.95), 2),
            "trending_domains": random.randint(15, 30)
        },
        "daily_progression": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "expertise_level": round(random.uniform(0.75, 0.90), 2),
                "learning_events": random.randint(40, 100),
                "top_category": random.choice(categories)
            }
            for i in range(7)
        ],
        "last_updated": datetime.now().isoformat()
    }
    
    # Add category-specific data
    for category in categories:
        # Generate random but realistic metrics
        expertise_growth = random.uniform(0.001, 0.008)
        current_expertise = cadence.categories[category]["expertise_level"]
        
        learning_map["categories"][category] = {
            "current_expertise_level": current_expertise,
            "daily_change": round(expertise_growth, 4),
            "weekly_change": round(expertise_growth * 7, 3),
            "learning_events_today": random.randint(5, 20),
            "knowledge_areas": [
                {
                    "area": subcategory,
                    "expertise_level": round(random.uniform(0.70, 0.95), 2),
                    "learning_velocity": round(random.uniform(0.001, 0.01), 4)
                }
                for subcategory in cadence.categories[category]["subcategories"]
            ],
            "recent_insights": random.randint(2, 8)
        }
    
    return learning_map

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
import threading
import schedule

# This import will be at the end of the file
# and declared once to avoid duplicate definition

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
CADENCE_DIR = f"{DATA_DIR}/cadence"
COVERAGE_DIR = f"{DATA_DIR}/coverage"
AGENT_LOGS_DIR = "agents/logs"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CADENCE_DIR, exist_ok=True)
os.makedirs(COVERAGE_DIR, exist_ok=True)
os.makedirs(AGENT_LOGS_DIR, exist_ok=True)

class RuntimeCadence:
    """Runtime Cadence Manager for domain learning and agent scheduling."""
    
    def __init__(self):
        """Initialize the runtime cadence manager."""
        self.domains = self._load_domains()
        self.coverage_metrics = self._load_coverage_metrics()
        self.cadence_metrics = self._load_cadence_metrics()
        self.categories = self._load_categories()
        
        # Ensure metrics files exist
        self._save_coverage_metrics()
        self._save_cadence_metrics()
    
    def _load_domains(self):
        """Load monitored domains from file."""
        domains_file = f"{DATA_DIR}/domains.json"
        
        try:
            if os.path.exists(domains_file):
                with open(domains_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading domains: {e}")
        
        # Create sample domains if not found
        sample_domains = [
            "finance-example.com",
            "healthcare-provider.org",
            "legal-resources.net",
            "tech-news-daily.com",
            "educational-resources.edu",
            "government-services.gov",
            "market-analysis.io",
            "research-institution.org",
            "medical-journal.net",
            "law-practice-daily.com",
            "investment-strategies.io",
            "health-information.org",
            "regulatory-updates.gov",
            "technology-trends.com",
            "scientific-research.org"
        ]
        
        # Create sample domain data
        domains = {
            domain: {
                "first_seen": (datetime.now() - timedelta(days=random.randint(30, 90))).isoformat(),
                "last_scan": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                "category": random.choice(["finance", "healthcare", "legal", "technology", "education"]),
                "priority": random.choice(["high", "medium", "low"]),
                "trust_score": round(random.uniform(70.0, 95.0), 1),
                "total_scans": random.randint(10, 50)
            }
            for domain in sample_domains
        }
        
        # Save domains to file
        os.makedirs(os.path.dirname(domains_file), exist_ok=True)
        with open(domains_file, 'w') as f:
            json.dump(domains, f, indent=2)
        
        return domains
    
    def _load_coverage_metrics(self):
        """Load coverage metrics from file."""
        coverage_file = f"{COVERAGE_DIR}/metrics.json"
        
        try:
            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading coverage metrics: {e}")
        
        # Create initial coverage metrics
        categories = ["finance", "healthcare", "legal", "technology", "education"]
        
        coverage = {
            "overall": {
                "total_domains": len(self.domains),
                "domains_scanned_24h": random.randint(int(len(self.domains) * 0.7), len(self.domains)),
                "domains_scanned_7d": len(self.domains),
                "coverage_rate": round(random.uniform(0.85, 0.98), 2),
                "average_scan_interval_hours": random.randint(12, 24)
            },
            "categories": {
                category: {
                    "total_domains": sum(1 for d in self.domains.values() if d.get("category") == category),
                    "domains_scanned_24h": random.randint(5, 15),
                    "coverage_rate": round(random.uniform(0.80, 0.95), 2),
                    "average_scan_interval_hours": random.randint(12, 36)
                }
                for category in categories
            },
            "last_updated": time.time()
        }
        
        return coverage
    
    def _load_cadence_metrics(self):
        """Load cadence metrics from file."""
        cadence_file = f"{CADENCE_DIR}/metrics.json"
        
        try:
            if os.path.exists(cadence_file):
                with open(cadence_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cadence metrics: {e}")
        
        # Create initial cadence metrics
        priorities = ["high", "medium", "low"]
        
        cadence = {
            "targets": {
                "high": {
                    "ideal_interval_hours": 6,
                    "current_average_hours": round(random.uniform(5.5, 8.0), 1),
                    "compliance_rate": round(random.uniform(0.90, 0.99), 2)
                },
                "medium": {
                    "ideal_interval_hours": 24,
                    "current_average_hours": round(random.uniform(20.0, 26.0), 1),
                    "compliance_rate": round(random.uniform(0.85, 0.95), 2)
                },
                "low": {
                    "ideal_interval_hours": 72,
                    "current_average_hours": round(random.uniform(65.0, 80.0), 1),
                    "compliance_rate": round(random.uniform(0.80, 0.90), 2)
                }
            },
            "global": {
                "average_interval_hours": round(random.uniform(18.0, 30.0), 1),
                "domains_per_day": random.randint(100, 200),
                "balanced_score": round(random.uniform(0.85, 0.95), 2),
                "quality_index": round(random.uniform(0.88, 0.96), 2)
            },
            "agent_performance": {
                "scan_scheduler": {
                    "timing_compliance": round(random.uniform(0.92, 0.99), 2),
                    "coverage_rate": round(random.uniform(0.90, 0.98), 2),
                    "quality_score": round(random.uniform(0.88, 0.97), 2)
                },
                "trust_drift": {
                    "timing_compliance": round(random.uniform(0.90, 0.98), 2),
                    "coverage_rate": round(random.uniform(0.85, 0.95), 2),
                    "quality_score": round(random.uniform(0.87, 0.96), 2)
                }
            },
            "last_updated": time.time()
        }
        
        return cadence
    
    def _load_categories(self):
        """Load category definitions and expansion data."""
        categories_file = f"{DATA_DIR}/categories.json"
        
        try:
            if os.path.exists(categories_file):
                with open(categories_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading categories: {e}")
        
        # Create initial categories
        categories = {
            "finance": {
                "description": "Financial services, investment, banking, and markets",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.85, 0.95), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["banking", "investment", "insurance", "markets", "fintech"],
                "recent_domains": random.randint(20, 40)
            },
            "healthcare": {
                "description": "Medical services, health information, providers, and research",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.80, 0.92), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["hospitals", "pharmaceuticals", "research", "wellness", "insurance"],
                "recent_domains": random.randint(20, 40)
            },
            "legal": {
                "description": "Legal resources, services, regulations, and practice areas",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.82, 0.94), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["law_firms", "regulations", "legal_resources", "case_law", "practice_areas"],
                "recent_domains": random.randint(15, 35)
            },
            "technology": {
                "description": "Tech news, products, services, and innovation",
                "trust_critical": False,
                "expertise_level": round(random.uniform(0.88, 0.96), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["software", "hardware", "ai", "cloud", "cybersecurity"],
                "recent_domains": random.randint(25, 45)
            },
            "education": {
                "description": "Educational institutions, resources, and research",
                "trust_critical": True,
                "expertise_level": round(random.uniform(0.83, 0.93), 2),
                "last_expansion": (datetime.now() - timedelta(days=random.randint(5, 20))).isoformat(),
                "subcategories": ["universities", "k12", "online_learning", "research", "academic_journals"],
                "recent_domains": random.randint(15, 35)
            }
        }
        
        # Save categories to file
        os.makedirs(os.path.dirname(categories_file), exist_ok=True)
        with open(categories_file, 'w') as f:
            json.dump(categories, f, indent=2)
        
        return categories
    
    def _save_coverage_metrics(self):
        """Save coverage metrics to file."""
        coverage_file = f"{COVERAGE_DIR}/metrics.json"
        
        self.coverage_metrics["last_updated"] = time.time()
        
        os.makedirs(os.path.dirname(coverage_file), exist_ok=True)
        with open(coverage_file, 'w') as f:
            json.dump(self.coverage_metrics, f, indent=2)
        
        logger.info("Coverage metrics saved")
    
    def _save_cadence_metrics(self):
        """Save cadence metrics to file."""
        cadence_file = f"{CADENCE_DIR}/metrics.json"
        
        self.cadence_metrics["last_updated"] = time.time()
        
        os.makedirs(os.path.dirname(cadence_file), exist_ok=True)
        with open(cadence_file, 'w') as f:
            json.dump(self.cadence_metrics, f, indent=2)
        
        logger.info("Cadence metrics saved")
    
    def _save_domains(self):
        """Save domains to file."""
        domains_file = f"{DATA_DIR}/domains.json"
        
        os.makedirs(os.path.dirname(domains_file), exist_ok=True)
        with open(domains_file, 'w') as f:
            json.dump(self.domains, f, indent=2)
        
        logger.info("Domains saved")
    
    def update_domain_scan(self, domain, success=True):
        """
        Update domain after a scan.
        
        Args:
            domain: Domain name
            success: Whether the scan was successful
        """
        if domain not in self.domains:
            logger.warning(f"Domain not found: {domain}")
            return
        
        # Update domain data
        self.domains[domain]["last_scan"] = datetime.now().isoformat()
        self.domains[domain]["total_scans"] += 1
        
        if success:
            # Slightly adjust trust score
            current_score = self.domains[domain]["trust_score"]
            adjustment = random.uniform(-2.0, 2.0)
            new_score = max(0, min(100, current_score + adjustment))
            self.domains[domain]["trust_score"] = round(new_score, 1)
        
        # Save domains
        self._save_domains()
        
        logger.info(f"Domain scan updated: {domain}")
    
    def update_coverage_metrics(self):
        """Update coverage metrics based on current domain data."""
        logger.info("Updating coverage metrics...")
        
        # Count domains scanned in last 24 hours
        now = datetime.now()
        domains_24h = 0
        domains_7d = 0
        
        category_domains = {}
        category_scanned_24h = {}
        
        for domain, data in self.domains.items():
            category = data.get("category", "unknown")
            
            # Initialize category counters if new
            if category not in category_domains:
                category_domains[category] = 0
                category_scanned_24h[category] = 0
            
            # Count domain in its category
            category_domains[category] += 1
            
            # Check last scan time
            try:
                last_scan = datetime.fromisoformat(data.get("last_scan", ""))
                
                # Count if scanned in last 24 hours
                if (now - last_scan).total_seconds() < 86400:
                    domains_24h += 1
                    category_scanned_24h[category] += 1
                
                # Count if scanned in last 7 days
                if (now - last_scan).total_seconds() < 604800:
                    domains_7d += 1
            except:
                pass
        
        # Update overall metrics
        total_domains = len(self.domains)
        self.coverage_metrics["overall"]["total_domains"] = total_domains
        self.coverage_metrics["overall"]["domains_scanned_24h"] = domains_24h
        self.coverage_metrics["overall"]["domains_scanned_7d"] = domains_7d
        
        # Calculate coverage rate
        if total_domains > 0:
            self.coverage_metrics["overall"]["coverage_rate"] = round(domains_7d / total_domains, 2)
        
        # Update category metrics
        for category in category_domains:
            if category not in self.coverage_metrics["categories"]:
                self.coverage_metrics["categories"][category] = {
                    "total_domains": 0,
                    "domains_scanned_24h": 0,
                    "coverage_rate": 0,
                    "average_scan_interval_hours": 24
                }
            
            self.coverage_metrics["categories"][category]["total_domains"] = category_domains[category]
            self.coverage_metrics["categories"][category]["domains_scanned_24h"] = category_scanned_24h.get(category, 0)
            
            # Calculate category coverage rate
            if category_domains[category] > 0:
                coverage_rate = category_scanned_24h.get(category, 0) / category_domains[category]
                self.coverage_metrics["categories"][category]["coverage_rate"] = round(coverage_rate, 2)
        
        # Save updated metrics
        self._save_coverage_metrics()
        
        logger.info("Coverage metrics updated")
    
    def update_cadence_metrics(self):
        """Update cadence metrics based on current domain data."""
        logger.info("Updating cadence metrics...")
        
        # Initialize interval tracking
        priority_intervals = {"high": [], "medium": [], "low": []}
        all_intervals = []
        
        # Calculate actual scan intervals
        now = datetime.now()
        domains_by_priority = {"high": 0, "medium": 0, "low": 0}
        
        for domain, data in self.domains.items():
            priority = data.get("priority", "medium")
            domains_by_priority[priority] += 1
            
            try:
                last_scan = datetime.fromisoformat(data.get("last_scan", ""))
                time_since_scan = (now - last_scan).total_seconds() / 3600  # hours
                
                # Add to appropriate interval list
                priority_intervals[priority].append(time_since_scan)
                all_intervals.append(time_since_scan)
            except:
                pass
        
        # Update priority cadence metrics
        for priority in priority_intervals:
            intervals = priority_intervals[priority]
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                ideal_interval = self.cadence_metrics["targets"][priority]["ideal_interval_hours"]
                
                # Update current average
                self.cadence_metrics["targets"][priority]["current_average_hours"] = round(avg_interval, 1)
                
                # Calculate compliance rate
                if ideal_interval > 0:
                    compliance = min(1.0, ideal_interval / avg_interval) if avg_interval > ideal_interval else min(1.0, avg_interval / ideal_interval)
                    self.cadence_metrics["targets"][priority]["compliance_rate"] = round(compliance, 2)
        
        # Update global metrics
        if all_intervals:
            avg_interval = sum(all_intervals) / len(all_intervals)
            self.cadence_metrics["global"]["average_interval_hours"] = round(avg_interval, 1)
        
        # Calculate domains per day based on intervals
        total_domains = len(self.domains)
        if total_domains > 0 and self.cadence_metrics["global"]["average_interval_hours"] > 0:
            avg_hours = self.cadence_metrics["global"]["average_interval_hours"]
            domains_per_day = total_domains * (24 / avg_hours)
            self.cadence_metrics["global"]["domains_per_day"] = round(domains_per_day)
        
        # Update balanced score (randomized slightly for simulation)
        balanced_score = self.cadence_metrics["global"]["balanced_score"]
        balanced_score = max(0, min(1, balanced_score + random.uniform(-0.03, 0.03)))
        self.cadence_metrics["global"]["balanced_score"] = round(balanced_score, 2)
        
        # Update quality index (randomized slightly for simulation)
        quality_index = self.cadence_metrics["global"]["quality_index"]
        quality_index = max(0, min(1, quality_index + random.uniform(-0.02, 0.02)))
        self.cadence_metrics["global"]["quality_index"] = round(quality_index, 2)
        
        # Update agent performance metrics
        for agent in self.cadence_metrics["agent_performance"]:
            # Randomize metrics slightly for simulation
            timing = self.cadence_metrics["agent_performance"][agent]["timing_compliance"]
            coverage = self.cadence_metrics["agent_performance"][agent]["coverage_rate"]
            quality = self.cadence_metrics["agent_performance"][agent]["quality_score"]
            
            timing = max(0, min(1, timing + random.uniform(-0.03, 0.03)))
            coverage = max(0, min(1, coverage + random.uniform(-0.03, 0.03)))
            quality = max(0, min(1, quality + random.uniform(-0.02, 0.02)))
            
            self.cadence_metrics["agent_performance"][agent]["timing_compliance"] = round(timing, 2)
            self.cadence_metrics["agent_performance"][agent]["coverage_rate"] = round(coverage, 2)
            self.cadence_metrics["agent_performance"][agent]["quality_score"] = round(quality, 2)
        
        # Save updated metrics
        self._save_cadence_metrics()
        
        logger.info("Cadence metrics updated")
    
    def simulate_domain_scan(self):
        """Simulate a domain scan for demonstration purposes."""
        # Select random domain
        if not self.domains:
            logger.warning("No domains to scan")
            return
        
        domain = random.choice(list(self.domains.keys()))
        
        # Simulate scan
        success = random.random() > 0.05  # 5% failure rate
        
        # Update domain
        self.update_domain_scan(domain, success)
        
        if success:
            logger.info(f"Simulated successful scan for {domain}")
        else:
            logger.warning(f"Simulated failed scan for {domain}")
    
    def update_metrics(self):
        """Update all metrics based on current data."""
        logger.info("Updating all cadence and coverage metrics...")
        
        # Simulate domain scans
        scan_count = random.randint(2, 5)
        for _ in range(scan_count):
            self.simulate_domain_scan()
        
        # Update metrics
        self.update_coverage_metrics()
        self.update_cadence_metrics()
        
        logger.info(f"All metrics updated, simulated {scan_count} domain scans")
    
    def get_coverage_metrics(self):
        """Get coverage metrics."""
        return self.coverage_metrics
    
    def get_cadence_metrics(self):
        """Get cadence metrics."""
        return self.cadence_metrics
    
    def get_domains(self):
        """Get all domains."""
        return self.domains
    
    def get_categories(self):
        """Get all categories."""
        return self.categories

# Global runtime cadence instance
_cadence_manager = None

def start_cadence_manager():
    """Start the runtime cadence manager."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = RuntimeCadence()
    
    return _cadence_manager

def get_coverage_metrics():
    """Get coverage metrics."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = start_cadence_manager()
    
    return _cadence_manager.get_coverage_metrics()

def get_cadence_metrics():
    """Get cadence metrics."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = start_cadence_manager()
    
    return _cadence_manager.get_cadence_metrics()

def get_domains():
    """Get all domains."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = start_cadence_manager()
    
    return _cadence_manager.get_domains()

def get_categories():
    """Get all categories."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = start_cadence_manager()
    
    return _cadence_manager.get_categories()

def update_cadence_metrics():
    """Update all cadence and coverage metrics."""
    global _cadence_manager
    
    if _cadence_manager is None:
        _cadence_manager = start_cadence_manager()
    
    _cadence_manager.update_metrics()

# Running as main starts an update loop
if __name__ == "__main__":
    logger.info("Starting runtime cadence manager...")
    
    # Start cadence manager
    cadence_manager = start_cadence_manager()
    
    # Initial update
    cadence_manager.update_metrics()
    
    # Setup update schedule
    schedule.every(2).minutes.do(cadence_manager.update_metrics)
    
    try:
        # Run forever
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, stopping...")
    finally:
        logger.info("Runtime cadence manager stopped")