"""
PRD-24.2: Insight Integrity, Scoring & Story-Driven Signal System

Insight Monitor
--------------
This module integrates the insight system with the existing LLMPageRank infrastructure.
"""

import os
import json
import logging
import time
import threading
import schedule
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import from project modules
import insight_schema
from agents import insight_logger, schema_auditor, story_generator
import runtime_monitor
import database
import category_matrix

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
running = False
scheduler_thread = None

def process_trust_signal_changes(domain_data: List[Dict]) -> List[Dict]:
    """
    Process trust signal changes and create insights.
    
    Args:
        domain_data: List of domain data dictionaries with trust signal changes
        
    Returns:
        List of created insights
    """
    logger.info(f"Processing trust signal changes for {len(domain_data)} domains")
    
    # Initialize category matrix if needed
    cat_matrix = category_matrix.CategoryMatrix()
    
    # Process each domain
    insights = []
    
    for data in domain_data:
        domain = data.get("domain", "")
        trust_delta = data.get("trust_delta", 0.0)
        score = data.get("score", 0.0)
        
        # Skip domains with minimal change
        if abs(trust_delta) < 0.5:
            continue
        
        # Get category for domain
        category = cat_matrix.get_domain_category(domain)
        if not category:
            category = "Uncategorized"
        
        # Get model disagreement data
        model_disagreement = data.get("model_disagreement", 0.0)
        if model_disagreement is None:
            model_disagreement = 0.0
        
        # Get volatility data
        volatility = data.get("volatility", 0.0)
        if volatility is None:
            volatility = 0.0
        
        # Calculate rarity within category
        category_domains = cat_matrix.get_category_domains(category)
        if category_domains and len(category_domains) > 1:
            # Get trust deltas for all domains in category
            category_deltas = []
            for cat_domain in category_domains:
                for d in domain_data:
                    if d.get("domain") == cat_domain:
                        category_deltas.append(abs(d.get("trust_delta", 0.0)))
                        break
            
            if category_deltas:
                avg_delta = sum(category_deltas) / len(category_deltas)
                if avg_delta > 0:
                    rarity = abs(trust_delta) / avg_delta
                else:
                    rarity = 1.0
            else:
                rarity = 1.0
        else:
            rarity = 1.0
        
        # Create insight
        insight = insight_logger.process_domain_movement(
            domain=domain,
            category=category,
            trust_delta=trust_delta,
            model_disagreement=model_disagreement,
            volatility=volatility,
            rarity=rarity,
            prompt_id=data.get("prompt_id", "unknown"),
            source_model=data.get("source_model", "unknown"),
            additional_data={
                "original_score": score,
                "previous_score": score - trust_delta,
                "source_data": data.get("source", "monitoring")
            }
        )
        
        insights.append(insight)
    
    logger.info(f"Created {len(insights)} insights")
    return insights

def check_runtime_health() -> Dict:
    """
    Check runtime health and create insights for anomalies.
    
    Returns:
        Health report dictionary
    """
    logger.info("Checking runtime health for insights")
    
    # Get runtime health data
    health_data = runtime_monitor.get_system_health()
    
    # Process health anomalies
    anomalies = []
    
    for agent_id, agent_health in health_data.get("agent_health", {}).items():
        if agent_health.get("status") != "healthy":
            anomalies.append({
                "type": "agent_health",
                "agent_id": agent_id,
                "status": agent_health.get("status"),
                "last_success": agent_health.get("last_success_time"),
                "failures": agent_health.get("consecutive_failures")
            })
    
    for metric, metric_data in health_data.get("system_metrics", {}).items():
        if metric_data.get("status") != "normal":
            anomalies.append({
                "type": "system_metric",
                "metric": metric,
                "status": metric_data.get("status"),
                "current_value": metric_data.get("current_value"),
                "threshold": metric_data.get("threshold")
            })
    
    # Log anomalies
    if anomalies:
        logger.warning(f"Found {len(anomalies)} runtime health anomalies")
        
        # TODO: Create insights for significant health anomalies
    
    return {
        "checked_at": datetime.now().isoformat() + "Z",
        "anomalies_count": len(anomalies),
        "anomalies": anomalies
    }

def run_daily_story_generation():
    """Run daily story generation tasks."""
    logger.info("Running daily story generation")
    
    # Generate weekly summary
    weekly_summary = story_generator.generate_weekly_summary()
    
    # Generate hot stories
    hot_stories = story_generator.generate_hot_stories()
    
    # Generate trend anomalies
    trend_anomalies = story_generator.generate_trend_anomalies()
    
    logger.info("Daily story generation completed")
    
    return {
        "weekly_summary_length": len(weekly_summary),
        "hot_stories_count": len(hot_stories.get("categories", {})),
        "trend_anomalies_count": len(trend_anomalies)
    }

def run_daily_schema_audit():
    """Run daily schema audit."""
    logger.info("Running daily schema audit")
    
    # Run schema audit
    audit_report = schema_auditor.run_scheduled_audit()
    
    logger.info(f"Daily schema audit completed: {audit_report.get('valid_insights')} valid, {audit_report.get('invalid_insights')} invalid")
    
    return audit_report

def scheduler_loop():
    """Run the scheduler loop."""
    global running
    
    while running:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def start_scheduled_tasks():
    """Start scheduled tasks."""
    global running, scheduler_thread
    
    if running:
        logger.warning("Scheduled tasks already running")
        return False
    
    logger.info("Starting scheduled insight system tasks")
    
    # Schedule daily story generation at 2 AM
    schedule.every().day.at("02:00").do(run_daily_story_generation)
    
    # Schedule daily schema audit at 1 AM
    schedule.every().day.at("01:00").do(run_daily_schema_audit)
    
    # Schedule runtime health check every 3 hours
    schedule.every(3).hours.do(check_runtime_health)
    
    # Start scheduler thread
    running = True
    scheduler_thread = threading.Thread(target=scheduler_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Scheduled insight system tasks started")
    
    return True

def stop_scheduled_tasks():
    """Stop scheduled tasks."""
    global running, scheduler_thread
    
    if not running:
        logger.warning("Scheduled tasks not running")
        return False
    
    logger.info("Stopping scheduled insight system tasks")
    
    # Stop scheduler thread
    running = False
    
    if scheduler_thread:
        scheduler_thread.join(timeout=5)
    
    # Clear schedule
    schedule.clear()
    
    logger.info("Scheduled insight system tasks stopped")
    
    return True

def process_recent_domain_data() -> List[Dict]:
    """
    Process recent domain data from the database.
    
    Returns:
        List of created insights
    """
    logger.info("Processing recent domain data from database")
    
    # Get recent domain data from database
    try:
        conn = database.get_conn()
        cursor = conn.cursor()
        
        # Get domains with recent trust signal changes
        query = """
        SELECT d.domain, d.trust_score, d.previous_score, d.model_disagreement, d.volatility, d.prompt_id, d.source_model
        FROM domains d
        WHERE d.trust_score IS NOT NULL AND d.previous_score IS NOT NULL AND ABS(d.trust_score - d.previous_score) > 0.5
        ORDER BY ABS(d.trust_score - d.previous_score) DESC
        LIMIT 100
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Transform query results to domain data format
        domain_data = []
        for row in results:
            domain, trust_score, previous_score, model_disagreement, volatility, prompt_id, source_model = row
            
            trust_delta = trust_score - previous_score
            
            domain_data.append({
                "domain": domain,
                "score": trust_score,
                "trust_delta": trust_delta,
                "model_disagreement": model_disagreement,
                "volatility": volatility,
                "prompt_id": prompt_id or "unknown",
                "source_model": source_model or "unknown",
                "source": "database"
            })
        
        cursor.close()
        conn.close()
        
        logger.info(f"Retrieved {len(domain_data)} domains with recent trust signal changes")
        
        # Process domain data
        insights = process_trust_signal_changes(domain_data)
        
        return insights
    except Exception as e:
        logger.error(f"Error processing recent domain data: {e}")
        return []

def initialize_insight_system() -> bool:
    """
    Initialize the insight system.
    
    Returns:
        Success flag
    """
    logger.info("Initializing insight integrity system")
    
    # Create data directories
    os.makedirs(insight_schema.DATA_DIR, exist_ok=True)
    os.makedirs(insight_schema.INSIGHTS_DIR, exist_ok=True)
    os.makedirs(insight_schema.LOGS_DIR, exist_ok=True)
    os.makedirs(insight_schema.STORIES_DIR, exist_ok=True)
    
    # Create agent log directories
    os.makedirs("agents/logs", exist_ok=True)
    os.makedirs("agents/logs/insight_logger.agent", exist_ok=True)
    os.makedirs("agents/logs/schema_auditor.agent", exist_ok=True)
    os.makedirs("agents/logs/story_generator.agent", exist_ok=True)
    
    # Start scheduled tasks
    success = start_scheduled_tasks()
    
    # Process recent domain data
    insights = process_recent_domain_data()
    
    logger.info(f"Insight integrity system initialized: {len(insights)} initial insights created")
    
    return success

def main():
    """Main function."""
    initialize_insight_system()

if __name__ == "__main__":
    main()