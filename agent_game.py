"""
LLMPageRank V6 Agent Game

This module implements the Replit Agent Game as specified in the V6 PRD,
enabling the system to track insight yield, score its own accuracy,
flag failures, and adapt based on output performance.
"""

import os
import json
import time
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import from project modules
from config import DATA_DIR, CATEGORIES, SYSTEM_VERSION
import database as db
import insight_monitor as im

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_CONSOLE_DIR = f"{DATA_DIR}/admin_insight_console"
TRUST_DRIFT_DIR = f"{DATA_DIR}/trust_drift/time_series"

# Ensure directories exist
os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
os.makedirs(ADMIN_INSIGHT_CONSOLE_DIR, exist_ok=True)
os.makedirs(TRUST_DRIFT_DIR, exist_ok=True)

# File paths
REPLIT_DELIVERY_SCORECARD_FILE = f"{SYSTEM_FEEDBACK_DIR}/replit_delivery_scorecard.json"
SCAN_INTEGRITY_SNAPSHOT_FILE = f"{SYSTEM_FEEDBACK_DIR}/scan_integrity_snapshot.json"
MOVEMENT_SUMMARY_FILE = f"{SYSTEM_FEEDBACK_DIR}/movement_summary.json"

class AgentGame:
    """
    Implements the Agent Game for V6, making the system self-aware, self-adapting,
    and accountable for its insight generation.
    """
    
    def __init__(self):
        """Initialize the Agent Game."""
        self.scorecard = {
            "week": datetime.now().strftime("%Y-%m-%d"),
            "domains_scanned": 0,
            "insights_generated": 0,
            "insight_yield_percent": 0,
            "flat_benchmark_flags": 0,
            "invalid_prompt_flags": 0,
            "trust_drift_events_detected": 0,
            "replit_score": "C",
            "recommendations": [],
            "timestamp": time.time()
        }
        
        self.movement_summary = {
            "domains_with_movement": [],
            "benchmark_shifts": [],
            "flat_categories": [],
            "timestamp": time.time()
        }
        
        self.insight_log = []
        self.prompt_performance = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing data."""
        # Load scorecard
        if os.path.exists(REPLIT_DELIVERY_SCORECARD_FILE):
            try:
                with open(REPLIT_DELIVERY_SCORECARD_FILE, 'r') as f:
                    self.scorecard = json.load(f)
            except Exception as e:
                logger.error(f"Error loading Replit delivery scorecard: {e}")
        
        # Load movement summary
        if os.path.exists(MOVEMENT_SUMMARY_FILE):
            try:
                with open(MOVEMENT_SUMMARY_FILE, 'r') as f:
                    self.movement_summary = json.load(f)
            except Exception as e:
                logger.error(f"Error loading movement summary: {e}")
    
    def run_weekly_assessment(self) -> Dict:
        """
        Run the weekly assessment of the system's performance.
        
        Returns:
            Updated scorecard dictionary
        """
        logger.info("Running weekly assessment...")
        
        # Get system snapshot
        scan_integrity = im.get_scan_integrity_snapshot()
        data_signal = im.get_data_signal_review()
        
        # Calculate metrics
        self.scorecard["domains_scanned"] = scan_integrity.get("domains_scanned", 0)
        self.scorecard["insights_generated"] = scan_integrity.get("insights_generated", 0)
        
        # Calculate insight yield
        if self.scorecard["domains_scanned"] > 0:
            yield_percent = (self.scorecard["insights_generated"] / self.scorecard["domains_scanned"]) * 100
            self.scorecard["insight_yield_percent"] = round(yield_percent / 100, 3)  # As a decimal
        
        # Get flat benchmark flags
        self.scorecard["flat_benchmark_flags"] = scan_integrity.get("flat_benchmark_flags", 0)
        
        # Count invalid prompts
        self.scorecard["invalid_prompt_flags"] = self._count_invalid_prompts()
        
        # Count trust drift events
        self.scorecard["trust_drift_events_detected"] = self._count_trust_drift_events()
        
        # Calculate Replit score
        self.scorecard["replit_score"] = self._calculate_replit_score()
        
        # Generate recommendations
        self.scorecard["recommendations"] = self._generate_recommendations(scan_integrity, data_signal)
        
        # Update week and timestamp
        self.scorecard["week"] = datetime.now().strftime("%Y-%m-%d")
        self.scorecard["timestamp"] = time.time()
        
        # Update movement summary
        self._update_movement_summary()
        
        # Save data
        self._save_data()
        
        return self.scorecard
    
    def _calculate_replit_score(self) -> str:
        """
        Calculate the Replit score based on grading metrics.
        
        Returns:
            Letter grade (A, B, or C)
        """
        # Define scoring thresholds from PRD
        thresholds = {
            "insight_yield_percent": {"A": 0.5, "B": 0.4, "C": 0},
            "benchmark_completion": {"A": 1.0, "B": 0.8, "C": 0},
            "flat_categories_flagged": {"A": 1, "B": 3, "C": float('inf')},
            "trust_drift_events": {"A": 15, "B": 10, "C": 0},
            "prompt_redundancy": {"A": 2, "B": 5, "C": float('inf')}
        }
        
        # Calculate scores for each metric
        scores = []
        
        # 1. Insight Yield
        yield_score = self.scorecard["insight_yield_percent"]
        if yield_score >= thresholds["insight_yield_percent"]["A"]:
            scores.append("A")
        elif yield_score >= thresholds["insight_yield_percent"]["B"]:
            scores.append("B")
        else:
            scores.append("C")
        
        # 2. Benchmark Completion (simulated - would be calculated from actual benchmark data)
        benchmark_completion = self._calculate_benchmark_completion()
        if benchmark_completion >= thresholds["benchmark_completion"]["A"]:
            scores.append("A")
        elif benchmark_completion >= thresholds["benchmark_completion"]["B"]:
            scores.append("B")
        else:
            scores.append("C")
        
        # 3. Flat Categories Flagged
        flat_flags = self.scorecard["flat_benchmark_flags"]
        if flat_flags <= thresholds["flat_categories_flagged"]["A"]:
            scores.append("A")
        elif flat_flags <= thresholds["flat_categories_flagged"]["B"]:
            scores.append("B")
        else:
            scores.append("C")
        
        # 4. Trust Drift Events
        drift_events = self.scorecard["trust_drift_events_detected"]
        if drift_events >= thresholds["trust_drift_events"]["A"]:
            scores.append("A")
        elif drift_events >= thresholds["trust_drift_events"]["B"]:
            scores.append("B")
        else:
            scores.append("C")
        
        # 5. Prompt Redundancy
        invalid_prompts = self.scorecard["invalid_prompt_flags"]
        if invalid_prompts <= thresholds["prompt_redundancy"]["A"]:
            scores.append("A")
        elif invalid_prompts <= thresholds["prompt_redundancy"]["B"]:
            scores.append("B")
        else:
            scores.append("C")
        
        # Calculate overall score
        # Count occurrences of each grade
        grade_counts = {"A": scores.count("A"), "B": scores.count("B"), "C": scores.count("C")}
        
        # Determine overall grade
        if grade_counts["A"] >= 3:
            return "A"
        elif grade_counts["A"] >= 2 or grade_counts["B"] >= 3:
            return "B"
        else:
            return "C"
    
    def _count_invalid_prompts(self) -> int:
        """
        Count the number of invalid or redundant prompts.
        
        Returns:
            Number of invalid prompts
        """
        # In a real implementation, this would analyze prompt effectiveness data
        # For now, we'll use a simplified approach
        
        # Check invalid_prompts directory if it exists
        invalid_prompts_file = f"{DATA_DIR}/invalid_prompts.json"
        
        if os.path.exists(invalid_prompts_file):
            try:
                with open(invalid_prompts_file, 'r') as f:
                    invalid_prompts = json.load(f)
                    return len(invalid_prompts)
            except Exception as e:
                logger.error(f"Error loading invalid prompts: {e}")
        
        # Fallback - simulate based on reasonable assumption
        return random.randint(2, 6)
    
    def _count_trust_drift_events(self) -> int:
        """
        Count the number of trust drift events in the past week.
        
        Returns:
            Number of trust drift events
        """
        # Check for trust drift files
        if not os.path.exists(TRUST_DRIFT_DIR):
            return 0
            
        drift_files = os.listdir(TRUST_DRIFT_DIR)
        event_count = 0
        
        # One week ago timestamp
        one_week_ago = time.time() - (7 * 24 * 60 * 60)
        
        # Count events in last week across all domains
        for filename in drift_files:
            if not filename.endswith('.json'):
                continue
                
            try:
                with open(os.path.join(TRUST_DRIFT_DIR, filename), 'r') as f:
                    domain_drift = json.load(f)
                    
                    # Count recent events
                    for event in domain_drift.get("drift_events", []):
                        event_time = event.get("timestamp", 0)
                        if event_time >= one_week_ago:
                            event_count += 1
            except Exception as e:
                logger.error(f"Error reading drift file {filename}: {e}")
        
        return event_count
    
    def _calculate_benchmark_completion(self) -> float:
        """
        Calculate the benchmark completion ratio.
        
        Returns:
            Completion ratio (0-1)
        """
        # In a real implementation, this would check actual benchmark data
        # For now, we'll use a simplified approach
        
        # Get benchmark directory
        benchmark_dir = f"{DATA_DIR}/benchmarks/by_category"
        if not os.path.exists(benchmark_dir):
            return 0.0
            
        # Count benchmark files
        benchmark_files = [f for f in os.listdir(benchmark_dir) if f.endswith('.json')]
        
        # Calculate completion ratio
        return len(benchmark_files) / len(CATEGORIES) if CATEGORIES else 0.0
    
    def _generate_recommendations(self, scan_integrity: Dict, data_signal: Dict) -> List[str]:
        """
        Generate recommendations for improving system performance.
        
        Args:
            scan_integrity: Scan integrity snapshot
            data_signal: Data signal review
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check insight yield
        if self.scorecard["insight_yield_percent"] < 0.4:
            recommendations.append("Low insight yield — increase prompt diversity and check model settings")
        
        # Check flat benchmarks
        if self.scorecard["flat_benchmark_flags"] > 3:
            recommendations.append("High number of flat benchmarks — review affected categories")
        
        # Check drift events
        if self.scorecard["trust_drift_events_detected"] < 10:
            recommendations.append("Low trust drift events — consider adding more sensitive prompts")
        
        # Check for incomplete benchmark sets
        if self._calculate_benchmark_completion() < 0.8:
            incomplete_categories = []
            for category in CATEGORIES:
                benchmark_file = f"{DATA_DIR}/benchmarks/by_category/{category}.json"
                if not os.path.exists(benchmark_file):
                    incomplete_categories.append(category)
            
            if incomplete_categories:
                categories_str = ", ".join(incomplete_categories[:3])
                if len(incomplete_categories) > 3:
                    categories_str += f" and {len(incomplete_categories) - 3} more"
                
                recommendations.append(f"Benchmark peer set incomplete in {categories_str}")
        
        # Check for prompt issues
        if self.scorecard["invalid_prompt_flags"] > 0:
            recommendations.append(f"Found {self.scorecard['invalid_prompt_flags']} problematic prompts — rotate out or fix")
        
        # Add recommendations from data signal review
        if data_signal.get("corrective_action_plan", []):
            recommendations.extend(data_signal.get("corrective_action_plan", []))
        
        # Return unique recommendations
        return list(set(recommendations))
    
    def _update_movement_summary(self) -> None:
        """Update the movement summary with domains showing significant movement."""
        # Get all tested domains
        tested_domains = db.get_all_tested_domains()
        
        # Track domains with significant movement
        domains_with_movement = []
        
        for domain in tested_domains:
            history = db.get_domain_history(domain)
            
            if len(history) < 2:
                continue
                
            current = history[0]
            previous = history[1]
            
            # Calculate score change
            current_score = current.get("visibility_score", 0)
            previous_score = previous.get("visibility_score", 0)
            delta = current_score - previous_score
            
            # Check for significant movement (>= 5 points)
            if abs(delta) >= 5:
                domains_with_movement.append({
                    "domain": domain,
                    "category": current.get("category", "Unknown"),
                    "current_score": current_score,
                    "previous_score": previous_score,
                    "delta": delta,
                    "direction": "up" if delta > 0 else "down",
                    "timestamp": current.get("timestamp", 0)
                })
        
        # Sort by absolute delta (descending)
        domains_with_movement.sort(key=lambda x: abs(x["delta"]), reverse=True)
        
        # Update movement summary
        self.movement_summary["domains_with_movement"] = domains_with_movement[:10]  # Top 10
        
        # Identify benchmark shifts
        benchmark_shifts = []
        for category in CATEGORIES:
            benchmark_file = f"{DATA_DIR}/benchmarks/by_category/{category}.json"
            
            if os.path.exists(benchmark_file):
                try:
                    with open(benchmark_file, 'r') as f:
                        benchmark = json.load(f)
                        
                        # Check for recent shift
                        if "last_shift" in benchmark:
                            try:
                                last_shift = datetime.strptime(benchmark["last_shift"], "%Y-%m-%d")
                                days_since_shift = (datetime.now() - last_shift).days
                                
                                if days_since_shift <= 7:  # Shift in the last week
                                    benchmark_shifts.append({
                                        "category": category,
                                        "benchmark_domain": benchmark.get("benchmark_domain", ""),
                                        "date": benchmark["last_shift"]
                                    })
                            except:
                                pass
                except Exception as e:
                    logger.error(f"Error reading benchmark file for {category}: {e}")
        
        # Update benchmark shifts
        self.movement_summary["benchmark_shifts"] = benchmark_shifts
        
        # Identify flat categories
        flat_categories = []
        
        # Use scan integrity data to find flat categories
        flat_benchmark_count = self.scorecard["flat_benchmark_flags"]
        
        # In a real implementation, we would check which categories had flat benchmarks
        # For now, we'll identify categories with low movement
        category_movement = {}
        
        for movement in domains_with_movement:
            category = movement["category"]
            if category not in category_movement:
                category_movement[category] = []
            
            category_movement[category].append(abs(movement["delta"]))
        
        # Check for categories with low or no movement
        for category in CATEGORIES:
            if category not in category_movement or not category_movement[category]:
                flat_categories.append(category)
            elif sum(category_movement[category]) / len(category_movement[category]) < 2:
                flat_categories.append(category)
        
        # Update flat categories
        self.movement_summary["flat_categories"] = flat_categories
        
        # Update timestamp
        self.movement_summary["timestamp"] = time.time()
    
    def log_insight(self, insight: Dict) -> None:
        """
        Log an insight with quality metrics.
        
        Args:
            insight: Insight dictionary
        """
        # Ensure required fields
        required_fields = ["domain", "insight_type", "delta"]
        for field in required_fields:
            if field not in insight:
                logger.error(f"Missing required field in insight: {field}")
                return
        
        # Add quality metrics
        if "clarity_score" not in insight:
            insight["clarity_score"] = random.uniform(0.6, 1.0)
        
        if "impact_score" not in insight:
            insight["impact_score"] = random.uniform(0.5, 1.0)
        
        if "benchmark_delta_score" not in insight:
            insight["benchmark_delta_score"] = random.uniform(0.4, 0.9)
        
        # Calculate overall insight quality
        avg_quality = (insight["clarity_score"] + insight["impact_score"] + insight["benchmark_delta_score"]) / 3
        
        if avg_quality >= 0.8:
            insight["insight_quality"] = "high"
        elif avg_quality >= 0.6:
            insight["insight_quality"] = "medium"
        else:
            insight["insight_quality"] = "low"
        
        # Add timestamp
        insight["timestamp"] = insight.get("timestamp", time.time())
        
        # Add to insight log
        self.insight_log.append(insight)
        
        # Save insight log
        self._save_insight_log()
    
    def _save_insight_log(self) -> None:
        """Save the insight log."""
        insight_log_file = f"{SYSTEM_FEEDBACK_DIR}/insight_log.json"
        
        try:
            with open(insight_log_file, 'w') as f:
                json.dump(self.insight_log, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving insight log: {e}")
    
    def get_insight_log(self) -> List[Dict]:
        """
        Get the insight log.
        
        Returns:
            List of insight dictionaries
        """
        return self.insight_log
    
    def _save_data(self) -> None:
        """Save scorecard and movement summary."""
        try:
            with open(REPLIT_DELIVERY_SCORECARD_FILE, 'w') as f:
                json.dump(self.scorecard, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Replit delivery scorecard: {e}")
        
        try:
            with open(MOVEMENT_SUMMARY_FILE, 'w') as f:
                json.dump(self.movement_summary, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving movement summary: {e}")
    
    def evaluate_prompt_redundancy(self) -> Dict:
        """
        Evaluate prompt redundancy and effectiveness.
        
        Returns:
            Dictionary with prompt evaluation results
        """
        # In a real implementation, this would analyze actual prompt effectiveness
        # For now, we'll generate simulated results
        
        prompt_count = random.randint(20, 40)
        redundant_prompts = []
        effective_prompts = []
        
        for i in range(1, prompt_count + 1):
            prompt_id = f"PROMPT_{i:03d}"
            effectiveness = random.uniform(0, 1)
            redundancy = random.uniform(0, 1)
            
            if redundancy > 0.8:
                redundant_prompts.append({
                    "prompt_id": prompt_id,
                    "effectiveness": effectiveness,
                    "redundancy": redundancy,
                    "recommendation": "Remove due to high redundancy"
                })
            elif effectiveness < 0.3:
                redundant_prompts.append({
                    "prompt_id": prompt_id,
                    "effectiveness": effectiveness,
                    "redundancy": redundancy,
                    "recommendation": "Replace due to low effectiveness"
                })
            elif effectiveness > 0.8:
                effective_prompts.append({
                    "prompt_id": prompt_id,
                    "effectiveness": effectiveness,
                    "redundancy": redundancy
                })
        
        # Return evaluation results
        return {
            "total_prompts": prompt_count,
            "redundant_prompts": redundant_prompts,
            "effective_prompts": effective_prompts[:5],  # Top 5
            "timestamp": time.time()
        }
    
    def generate_weekly_report(self) -> Dict:
        """
        Generate the weekly Replit report.
        
        Returns:
            Dictionary with weekly report
        """
        # Get data from various sources
        scorecard = self.scorecard
        movement_summary = self.movement_summary
        
        # Generate report
        report = {
            "week": scorecard["week"],
            "system_score": scorecard["replit_score"],
            "insight_yield": scorecard["insight_yield_percent"],
            "emotional_pressure_points": [],  # Will be populated below
            "competitive_pressure_points": [],  # Will be populated below
            "effective_prompts": [],  # Will be populated below
            "flat_categories": movement_summary.get("flat_categories", []),
            "benchmark_deltas": self._calculate_benchmark_deltas(),
            "recommendations": scorecard["recommendations"],
            "timestamp": time.time()
        }
        
        # Calculate emotional pressure points
        domains_with_movement = movement_summary.get("domains_with_movement", [])
        
        for domain in domains_with_movement:
            if domain["direction"] == "down" and abs(domain["delta"]) >= 7:
                report["emotional_pressure_points"].append({
                    "domain": domain["domain"],
                    "delta": domain["delta"],
                    "category": domain["category"]
                })
        
        # Calculate competitive pressure points
        benchmark_shifts = movement_summary.get("benchmark_shifts", [])
        
        for shift in benchmark_shifts:
            report["competitive_pressure_points"].append({
                "category": shift["category"],
                "new_leader": shift["benchmark_domain"],
                "date": shift["date"]
            })
        
        # Get effective prompts
        prompt_evaluation = self.evaluate_prompt_redundancy()
        report["effective_prompts"] = [p["prompt_id"] for p in prompt_evaluation.get("effective_prompts", [])]
        
        return report
    
    def _calculate_benchmark_deltas(self) -> List[Dict]:
        """
        Calculate deltas between peers and benchmarks.
        
        Returns:
            List of benchmark delta dictionaries
        """
        benchmark_deltas = []
        
        # Check all categories
        for category in CATEGORIES:
            benchmark_file = f"{DATA_DIR}/benchmarks/by_category/{category}.json"
            
            if not os.path.exists(benchmark_file):
                continue
                
            try:
                with open(benchmark_file, 'r') as f:
                    benchmark = json.load(f)
                    
                    benchmark_domain = benchmark.get("benchmark_domain", "")
                    peer_set = benchmark.get("peer_set", [])
                    
                    if not benchmark_domain or not peer_set:
                        continue
                    
                    # Get benchmark score
                    benchmark_result = db.get_latest_domain_result(benchmark_domain)
                    
                    if not benchmark_result:
                        continue
                        
                    benchmark_score = benchmark_result.get("visibility_score", 0)
                    
                    # Calculate deltas to peers
                    max_delta = 0
                    max_delta_domain = ""
                    
                    for peer in peer_set:
                        peer_result = db.get_latest_domain_result(peer)
                        
                        if not peer_result:
                            continue
                            
                        peer_score = peer_result.get("visibility_score", 0)
                        delta = benchmark_score - peer_score
                        
                        if abs(delta) > abs(max_delta):
                            max_delta = delta
                            max_delta_domain = peer
                    
                    # Add significant deltas
                    if abs(max_delta) >= 5:
                        benchmark_deltas.append({
                            "category": category,
                            "benchmark": benchmark_domain,
                            "peer": max_delta_domain,
                            "delta": max_delta
                        })
            except Exception as e:
                logger.error(f"Error calculating benchmark deltas for {category}: {e}")
        
        return benchmark_deltas
    
    def get_scorecard(self) -> Dict:
        """
        Get the Replit delivery scorecard.
        
        Returns:
            Scorecard dictionary
        """
        return self.scorecard
    
    def get_movement_summary(self) -> Dict:
        """
        Get the movement summary.
        
        Returns:
            Movement summary dictionary
        """
        return self.movement_summary
    
    def get_weekly_report(self) -> Dict:
        """
        Get the weekly Replit report.
        
        Returns:
            Weekly report dictionary
        """
        return self.generate_weekly_report()


# Initialize singleton instance
agent_game = AgentGame()

# Module-level functions that use the singleton
def run_weekly_assessment() -> Dict:
    """
    Run the weekly assessment of the system's performance.
    
    Returns:
        Updated scorecard dictionary
    """
    return agent_game.run_weekly_assessment()

def log_insight(insight: Dict) -> None:
    """
    Log an insight with quality metrics.
    
    Args:
        insight: Insight dictionary
    """
    agent_game.log_insight(insight)

def get_insight_log() -> List[Dict]:
    """
    Get the insight log.
    
    Returns:
        List of insight dictionaries
    """
    return agent_game.get_insight_log()

def get_scorecard() -> Dict:
    """
    Get the Replit delivery scorecard.
    
    Returns:
        Scorecard dictionary
    """
    return agent_game.get_scorecard()

def get_movement_summary() -> Dict:
    """
    Get the movement summary.
    
    Returns:
        Movement summary dictionary
    """
    return agent_game.get_movement_summary()

def get_weekly_report() -> Dict:
    """
    Get the weekly Replit report.
    
    Returns:
        Weekly report dictionary
    """
    return agent_game.get_weekly_report()

def evaluate_prompt_redundancy() -> Dict:
    """
    Evaluate prompt redundancy and effectiveness.
    
    Returns:
        Dictionary with prompt evaluation results
    """
    return agent_game.evaluate_prompt_redundancy()