"""
Initialize the Insight Integrity System with demo data.

This script creates the necessary directories and adds sample insights
to demonstrate the PRD-24.2 Insight Integrity System.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import random

# Import from project modules
import insight_schema
from agents import story_generator, schema_auditor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_demo_insights():
    """Generate demo insights for testing."""
    # Sample domains and categories
    domains = [
        "example.com", "ai-research.org", "techblog.io", "datascience.net",
        "machinelearning.dev", "devops.co", "cloudcomputing.tech",
        "cybersecurity.io", "artificialintelligence.org", "deeplearning.ai"
    ]
    
    categories = [
        "AI Collaboration", "Technical Documentation", "Education", 
        "Research", "Software Development", "DevOps", "Cloud Services",
        "Cybersecurity", "Machine Learning", "Data Science"
    ]
    
    # Generate demo insights
    demo_insights = []
    
    for i in range(20):
        domain_idx = i % len(domains)
        category_idx = i % len(categories)
        
        trust_delta = (i % 10) - 5  # Range from -5 to 4
        model_disagreement = (i % 5) / 2  # Range from 0 to 2
        volatility = (i % 4) / 2  # Range from 0 to 1.5
        rarity = (i % 6) / 3  # Range from 0 to 1.67
        
        # Process domain movement
        insight = insight_schema.create_insight(
            domain=domains[domain_idx],
            category=categories[category_idx],
            insight_type=insight_schema.INSIGHT_TYPES[i % len(insight_schema.INSIGHT_TYPES)],
            trust_delta=trust_delta,
            prompt_id=f"p_{i:05d}",
            source_model="gpt-4",
            agent_id="demo_generator",
            score=insight_schema.calculate_insight_score(
                trust_delta=trust_delta,
                model_disagreement=model_disagreement,
                volatility=volatility,
                rarity=rarity
            ),
            heat_index=insight_schema.determine_heat_index(
                insight_schema.calculate_insight_score(
                    trust_delta=trust_delta,
                    model_disagreement=model_disagreement,
                    volatility=volatility,
                    rarity=rarity
                )
            )
        )
        
        # Save insight
        insight_schema.save_insight(insight)
        demo_insights.append(insight)
    
    logger.info(f"Generated {len(demo_insights)} demo insights")
    return demo_insights

def initialize_system():
    """Initialize the Insight Integrity System."""
    logger.info("Initializing Insight Integrity System")
    
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
    
    # Generate demo insights
    insights = generate_demo_insights()
    
    # Generate weekly summary
    logger.info("Generating weekly summary")
    summary = story_generator.generate_weekly_summary()
    
    # Generate hot stories
    logger.info("Generating hot stories")
    hot_stories = story_generator.generate_hot_stories()
    
    # Generate trend anomalies
    logger.info("Generating trend anomalies")
    anomalies = story_generator.generate_trend_anomalies()
    
    # Run schema audit
    logger.info("Running schema audit")
    audit_report = schema_auditor.run_scheduled_audit()
    
    logger.info("Insight Integrity System initialized successfully")
    return True

def main():
    """Main function."""
    initialize_system()

if __name__ == "__main__":
    main()