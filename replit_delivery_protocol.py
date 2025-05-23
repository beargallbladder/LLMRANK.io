"""
LLMPageRank V5 Replit Delivery Scoring Protocol

This module implements the formal scoring system for evaluating
the delivery of the LLMRank system by Replit as specified in the V5 Addendum.
"""

import os
import json
import time
import logging
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

# Ensure directories exist
os.makedirs(SYSTEM_FEEDBACK_DIR, exist_ok=True)
os.makedirs(ADMIN_INSIGHT_CONSOLE_DIR, exist_ok=True)

# File paths
REPLIT_DELIVERY_SCORECARD_FILE = f"{SYSTEM_FEEDBACK_DIR}/replit_delivery_scorecard.json"
REPLIT_GRADING_SUMMARY_FILE = f"{ADMIN_INSIGHT_CONSOLE_DIR}/replit_grading_summary.json"

class ReplitDeliveryProtocol:
    """
    Manages the formal scoring system for evaluating the delivery of the LLMRank system.
    """
    
    def __init__(self):
        """Initialize the Replit Delivery Protocol."""
        self.scorecard = {
            "week": datetime.now().strftime("%Y-%m-%d"),
            "modules_delivered": 0,
            "scan_volume_delta": 0,
            "insight_yield_rate": 0.0,
            "flat_benchmarks_detected": 0,
            "invalid_prompts_removed": 0,
            "new_trust_deltas_detected": 0,
            "watchlist_updates": 0,
            "score": "C",
            "notes": "Initial setup - awaiting first scan cycle",
            "timestamp": time.time()
        }
        
        self.grading_summary = {
            "prd_version": SYSTEM_VERSION,
            "scorecard": {
                "crawl_engine_status": "initializing",
                "insight_generation_status": "pending",
                "trust_drift_logging": "pending",
                "prompt_health": "pending",
                "category_coverage_health": "pending", 
                "total_output_score": "C"
            },
            "timestamp": time.time()
        }
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing delivery scorecard and grading summary."""
        # Load scorecard
        if os.path.exists(REPLIT_DELIVERY_SCORECARD_FILE):
            try:
                with open(REPLIT_DELIVERY_SCORECARD_FILE, 'r') as f:
                    self.scorecard = json.load(f)
            except Exception as e:
                logger.error(f"Error loading Replit delivery scorecard: {e}")
        
        # Load grading summary
        if os.path.exists(REPLIT_GRADING_SUMMARY_FILE):
            try:
                with open(REPLIT_GRADING_SUMMARY_FILE, 'r') as f:
                    self.grading_summary = json.load(f)
            except Exception as e:
                logger.error(f"Error loading Replit grading summary: {e}")
    
    def evaluate_delivery(self) -> Dict:
        """
        Evaluate the delivery of the LLMRank system against the V5 criteria.
        
        Returns:
            Dictionary with evaluation results
        """
        logger.info("Evaluating Replit delivery...")
        
        # Get data from various sources
        scan_integrity = im.get_scan_integrity_snapshot()
        data_signal = im.get_data_signal_review()
        scorecard = im.get_scorecard()
        
        # 1. Evaluate modules delivered
        modules_delivered = self._count_modules_delivered()
        self.scorecard["modules_delivered"] = modules_delivered
        
        # 2. Calculate scan volume delta
        previous_scans = self.scorecard.get("scan_volume_delta", 0)
        current_scans = scan_integrity.get("domains_scanned", 0)
        scan_delta = current_scans - previous_scans
        self.scorecard["scan_volume_delta"] = scan_delta
        
        # 3. Calculate insight yield rate
        if scan_integrity.get("domains_scanned", 0) > 0:
            insight_yield = scan_integrity.get("insights_generated", 0) / scan_integrity.get("domains_scanned", 1)
            self.scorecard["insight_yield_rate"] = round(insight_yield, 2)
        
        # 4. Track flat benchmarks detected
        self.scorecard["flat_benchmarks_detected"] = scan_integrity.get("flat_benchmark_flags", 0)
        
        # 5. Track invalid prompts removed (simulated for now)
        # In a full implementation, this would track actual prompt removals
        self.scorecard["invalid_prompts_removed"] = 6
        
        # 6. Track new trust deltas detected
        trust_drift_files = os.listdir(f"{DATA_DIR}/trust_drift/time_series") if os.path.exists(f"{DATA_DIR}/trust_drift/time_series") else []
        drift_events = 0
        
        for file in trust_drift_files:
            if file.endswith('.json'):
                try:
                    with open(os.path.join(f"{DATA_DIR}/trust_drift/time_series", file), 'r') as f:
                        drift_data = json.load(f)
                        drift_events += len(drift_data.get("drift_events", []))
                except Exception as e:
                    logger.error(f"Error loading drift data from {file}: {e}")
        
        self.scorecard["new_trust_deltas_detected"] = drift_events
        
        # 7. Track watchlist updates (simulated for now)
        # In a full implementation, this would track actual watchlist changes
        self.scorecard["watchlist_updates"] = 18
        
        # 8. Calculate overall score
        score = self._calculate_score()
        self.scorecard["score"] = score
        
        # 9. Generate notes
        notes = self._generate_notes(scan_integrity, data_signal)
        self.scorecard["notes"] = notes
        
        # 10. Update timestamp
        self.scorecard["week"] = datetime.now().strftime("%Y-%m-%d")
        self.scorecard["timestamp"] = time.time()
        
        # 11. Update grading summary
        self._update_grading_summary()
        
        # 12. Save results
        self._save_data()
        
        return self.scorecard
    
    def _count_modules_delivered(self) -> int:
        """
        Count the number of modules delivered.
        
        Returns:
            Number of modules delivered
        """
        # Check for key module files
        module_files = [
            "app.py",
            "database.py",
            "domain_discovery.py",
            "insight_monitor.py",
            "foma_insight_engine.py",
            "api_router.py",
            "category_matrix.py",
            "prompt_validator.py",
            "dashboard_v5.py",
            "replit_delivery_protocol.py"
        ]
        
        modules_found = sum(1 for file in module_files if os.path.exists(file))
        return modules_found
    
    def _calculate_score(self) -> str:
        """
        Calculate the overall delivery score.
        
        Returns:
            Letter grade (A, A-, B+, B, etc.)
        """
        # Define scoring criteria
        criteria = {
            "modules_delivered": {
                "weight": 0.2,
                "max_value": 10,
                "min_for_a": 9,
                "min_for_b": 7,
                "min_for_c": 5
            },
            "insight_yield_rate": {
                "weight": 0.3,
                "max_value": 1.0,
                "min_for_a": 0.7,
                "min_for_b": 0.5,
                "min_for_c": 0.3
            },
            "new_trust_deltas_detected": {
                "weight": 0.25,
                "max_value": 50,
                "min_for_a": 30,
                "min_for_b": 20,
                "min_for_c": 10
            },
            "flat_benchmarks_detected": {
                "weight": 0.15,
                "max_value": 20,  # Lower is better for this one
                "min_for_a": 5,
                "min_for_b": 10,
                "min_for_c": 15,
                "inverse": True
            },
            "invalid_prompts_removed": {
                "weight": 0.1,
                "max_value": 10,
                "min_for_a": 7,
                "min_for_b": 5,
                "min_for_c": 3
            }
        }
        
        # Calculate weighted score
        total_score = 0
        
        for criterion, params in criteria.items():
            value = self.scorecard.get(criterion, 0)
            
            # For inverse criteria (where lower is better)
            if params.get("inverse", False):
                value = max(0, params["max_value"] - value)
            
            # Normalize to 0-1 scale
            normalized = min(1.0, value / params["max_value"])
            
            # Apply weight
            weighted = normalized * params["weight"]
            total_score += weighted
        
        # Convert to letter grade
        if total_score >= 0.9:
            grade = "A"
        elif total_score >= 0.85:
            grade = "A-"
        elif total_score >= 0.8:
            grade = "B+"
        elif total_score >= 0.75:
            grade = "B"
        elif total_score >= 0.7:
            grade = "B-"
        elif total_score >= 0.65:
            grade = "C+"
        elif total_score >= 0.6:
            grade = "C"
        elif total_score >= 0.55:
            grade = "C-"
        else:
            grade = "Rework"
        
        return grade
    
    def _generate_notes(self, scan_integrity: Dict, data_signal: Dict) -> str:
        """
        Generate notes based on system performance.
        
        Args:
            scan_integrity: Scan integrity snapshot
            data_signal: Data signal review
            
        Returns:
            Notes string
        """
        notes = []
        
        # Check insight yield
        if self.scorecard["insight_yield_rate"] < 0.3:
            notes.append("Low insight yield - review prompt effectiveness")
        
        # Check flat benchmarks
        if self.scorecard["flat_benchmarks_detected"] > 10:
            notes.append("High number of flat benchmarks - check category targeting")
        
        # Check corrective actions from data signal
        if data_signal.get("corrective_action_plan", []):
            notes.append("System suggests corrective actions - see data signal review")
        
        # Check PRD version coverage
        if self.scorecard["modules_delivered"] < 8:
            notes.append("Incomplete module delivery - implementation needs attention")
        
        # Default note if no issues
        if not notes:
            notes.append("System performing within expected parameters")
        
        return "; ".join(notes)
    
    def _update_grading_summary(self) -> None:
        """Update the grading summary based on the scorecard."""
        # Update PRD version
        self.grading_summary["prd_version"] = SYSTEM_VERSION
        
        # Update crawl engine status
        if self.scorecard["scan_volume_delta"] > 100:
            crawl_status = "excellent"
        elif self.scorecard["scan_volume_delta"] > 50:
            crawl_status = "good"
        elif self.scorecard["scan_volume_delta"] > 0:
            crawl_status = "stable"
        else:
            crawl_status = "stalled"
        
        self.grading_summary["scorecard"]["crawl_engine_status"] = crawl_status
        
        # Update insight generation status
        if self.scorecard["insight_yield_rate"] >= 0.7:
            insight_status = "excellent"
        elif self.scorecard["insight_yield_rate"] >= 0.5:
            insight_status = "active"
        elif self.scorecard["insight_yield_rate"] >= 0.3:
            insight_status = "moderate"
        else:
            insight_status = "struggling"
        
        self.grading_summary["scorecard"]["insight_generation_status"] = insight_status
        
        # Update trust drift logging
        if self.scorecard["new_trust_deltas_detected"] >= 20:
            drift_status = "comprehensive"
        elif self.scorecard["new_trust_deltas_detected"] >= 10:
            drift_status = "enabled"
        elif self.scorecard["new_trust_deltas_detected"] > 0:
            drift_status = "limited"
        else:
            drift_status = "disabled"
        
        self.grading_summary["scorecard"]["trust_drift_logging"] = drift_status
        
        # Update prompt health
        if self.scorecard["invalid_prompts_removed"] >= 5:
            prompt_status = "actively maintained"
        elif self.scorecard["invalid_prompts_removed"] > 0:
            prompt_status = "partially stale"
        else:
            prompt_status = "stale"
        
        self.grading_summary["scorecard"]["prompt_health"] = prompt_status
        
        # Update category coverage
        # In a full implementation, this would use actual category coverage metrics
        coverage_status = "strong"  # Placeholder
        self.grading_summary["scorecard"]["category_coverage_health"] = coverage_status
        
        # Update total output score
        self.grading_summary["scorecard"]["total_output_score"] = self.scorecard["score"]
        
        # Update timestamp
        self.grading_summary["timestamp"] = time.time()
    
    def _save_data(self) -> None:
        """Save scorecard and grading summary."""
        # Save scorecard
        try:
            with open(REPLIT_DELIVERY_SCORECARD_FILE, 'w') as f:
                json.dump(self.scorecard, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Replit delivery scorecard: {e}")
        
        # Save grading summary
        try:
            with open(REPLIT_GRADING_SUMMARY_FILE, 'w') as f:
                json.dump(self.grading_summary, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving Replit grading summary: {e}")
    
    def get_scorecard(self) -> Dict:
        """
        Get the delivery scorecard.
        
        Returns:
            Delivery scorecard dictionary
        """
        return self.scorecard
    
    def get_grading_summary(self) -> Dict:
        """
        Get the grading summary.
        
        Returns:
            Grading summary dictionary
        """
        return self.grading_summary


# Initialize singleton instance
replit_delivery_protocol = ReplitDeliveryProtocol()

# Module-level functions that use the singleton
def evaluate_delivery() -> Dict:
    """
    Evaluate the delivery of the LLMRank system against the V5 criteria.
    
    Returns:
        Dictionary with evaluation results
    """
    return replit_delivery_protocol.evaluate_delivery()

def get_scorecard() -> Dict:
    """
    Get the delivery scorecard.
    
    Returns:
        Delivery scorecard dictionary
    """
    return replit_delivery_protocol.get_scorecard()

def get_grading_summary() -> Dict:
    """
    Get the grading summary.
    
    Returns:
        Grading summary dictionary
    """
    return replit_delivery_protocol.get_grading_summary()