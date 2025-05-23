"""
Database V2 Module

Enhanced database functions for LLMPageRank V2 that implement the
V2 Master Directive requirements.
"""

import os
import json
import time
import logging
import psycopg2
import psycopg2.extras
from datetime import datetime, date
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import get_db_connection
from config import VERSION_INFO, SYSTEM_VERSION, PROMPT_VERSION

def save_time_series_data(domain: str, llmrank: int, delta: float, status: str, 
                         models: List[str], triggering_prompts: List[str]) -> bool:
    """
    Save time-series data for longitudinal tracking.
    
    Args:
        domain: Domain name
        llmrank: Current LLMRank score
        delta: Change from previous measurement
        status: Status label (e.g., "Trust Rising")
        models: List of models used in testing
        triggering_prompts: List of prompts that triggered citations
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today = date.today()
        
        # Check if entry for today already exists
        cursor.execute(
            "SELECT id FROM domain_time_series WHERE domain = %s AND date = %s",
            (domain, today)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            cursor.execute(
                """
                UPDATE domain_time_series 
                SET llmrank = %s, delta = %s, status = %s, models = %s, triggering_prompts = %s
                WHERE domain = %s AND date = %s
                """,
                (
                    llmrank, 
                    delta, 
                    status, 
                    json.dumps(models),
                    json.dumps(triggering_prompts),
                    domain,
                    today
                )
            )
        else:
            # Insert new entry
            cursor.execute(
                """
                INSERT INTO domain_time_series
                (domain, date, llmrank, delta, status, models, triggering_prompts)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    domain,
                    today,
                    llmrank,
                    delta,
                    status,
                    json.dumps(models),
                    json.dumps(triggering_prompts)
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Saved time-series data for domain {domain}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving time-series data for {domain}: {e}")
        return False

def get_domain_time_series(domain: str, limit: int = 90) -> List[Dict]:
    """
    Get time-series data for a domain.
    
    Args:
        domain: Domain name
        limit: Maximum number of days to return
        
    Returns:
        List of time-series entries for the domain
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT * FROM domain_time_series
            WHERE domain = %s
            ORDER BY date DESC
            LIMIT %s
            """,
            (domain, limit)
        )
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return list(results)
        
    except Exception as e:
        logger.error(f"Error getting time-series data for {domain}: {e}")
        return []

def save_opportunity_target(domain: str, category: str, opportunity_score: float,
                           customer_likelihood: int, structure_score: float,
                           visibility_score: float, delta: float, 
                           has_ads: bool, has_schema: bool, has_seo_stack: bool) -> bool:
    """
    Save an opportunity target.
    
    Args:
        domain: Domain name
        category: Domain category
        opportunity_score: Calculated opportunity score
        customer_likelihood: Customer likelihood score
        structure_score: Structure/SEO score
        visibility_score: LLM visibility score
        delta: Recent change in visibility
        has_ads: Whether domain has ads
        has_schema: Whether domain has schema markup
        has_seo_stack: Whether domain has SEO tools
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute(
            "SELECT id FROM domain_opportunities WHERE domain = %s",
            (domain,)
        )
        existing = cursor.fetchone()
        
        current_time = time.time()
        
        if existing:
            # Update existing entry
            cursor.execute(
                """
                UPDATE domain_opportunities
                SET category = %s, opportunity_score = %s, customer_likelihood = %s,
                    structure_score = %s, visibility_score = %s, delta = %s,
                    has_ads = %s, has_schema = %s, has_seo_stack = %s, last_updated = %s
                WHERE domain = %s
                """,
                (
                    category, opportunity_score, customer_likelihood,
                    structure_score, visibility_score, delta,
                    has_ads, has_schema, has_seo_stack, current_time,
                    domain
                )
            )
        else:
            # Insert new entry
            cursor.execute(
                """
                INSERT INTO domain_opportunities
                (domain, category, opportunity_score, customer_likelihood, structure_score,
                 visibility_score, delta, has_ads, has_schema, has_seo_stack, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    domain, category, opportunity_score, customer_likelihood,
                    structure_score, visibility_score, delta,
                    has_ads, has_schema, has_seo_stack, current_time
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Saved opportunity target for domain {domain}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving opportunity target for {domain}: {e}")
        return False

def get_opportunity_targets(min_score: float = 0, limit: int = 100) -> List[Dict]:
    """
    Get opportunity targets sorted by opportunity score.
    
    Args:
        min_score: Minimum opportunity score to include
        limit: Maximum number of targets to return
        
    Returns:
        List of opportunity target entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT * FROM domain_opportunities
            WHERE opportunity_score >= %s
            ORDER BY opportunity_score DESC
            LIMIT %s
            """,
            (min_score, limit)
        )
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return list(results)
        
    except Exception as e:
        logger.error(f"Error getting opportunity targets: {e}")
        return []

def save_prompt_performance(prompt_id: str, category: str, intent: str,
                          citation_frequency: float, model_coverage: float,
                          clarity_score: float, total_runs: int, 
                          successful_citations: int) -> bool:
    """
    Save prompt performance metrics.
    
    Args:
        prompt_id: Unique prompt ID
        category: Domain category
        intent: Prompt intent (informational, transactional, decision_support)
        citation_frequency: Frequency of citations
        model_coverage: Proportion of models that cite with this prompt
        clarity_score: Clarity score (0-1)
        total_runs: Total number of times prompt was used
        successful_citations: Number of successful citations
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if entry already exists
        cursor.execute(
            "SELECT id FROM prompt_performance_metrics WHERE prompt_id = %s",
            (prompt_id,)
        )
        existing = cursor.fetchone()
        
        current_time = time.time()
        
        if existing:
            # Update existing entry
            cursor.execute(
                """
                UPDATE prompt_performance_metrics
                SET category = %s, intent = %s, citation_frequency = %s,
                    model_coverage = %s, clarity_score = %s, total_runs = %s,
                    successful_citations = %s, last_updated = %s
                WHERE prompt_id = %s
                """,
                (
                    category, intent, citation_frequency,
                    model_coverage, clarity_score, total_runs,
                    successful_citations, current_time,
                    prompt_id
                )
            )
        else:
            # Insert new entry
            cursor.execute(
                """
                INSERT INTO prompt_performance_metrics
                (prompt_id, category, intent, citation_frequency, model_coverage,
                 clarity_score, total_runs, successful_citations, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    prompt_id, category, intent, citation_frequency,
                    model_coverage, clarity_score, total_runs,
                    successful_citations, current_time
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Saved performance metrics for prompt {prompt_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving prompt performance for {prompt_id}: {e}")
        return False

def get_top_performing_prompts(limit: int = 10) -> List[Dict]:
    """
    Get top performing prompts sorted by citation frequency.
    
    Args:
        limit: Maximum number of prompts to return
        
    Returns:
        List of prompt performance entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT * FROM prompt_performance_metrics
            ORDER BY citation_frequency DESC
            LIMIT %s
            """,
            (limit,)
        )
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return list(results)
        
    except Exception as e:
        logger.error(f"Error getting top performing prompts: {e}")
        return []

def save_enhanced_trends(trends_data: Dict) -> bool:
    """
    Save enhanced trends data with version information.
    
    Args:
        trends_data: Dictionary with trends data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add version information
        enhanced_data = trends_data.copy()
        enhanced_data["version"] = PROMPT_VERSION
        enhanced_data["system_version"] = SYSTEM_VERSION
        
        cursor.execute(
            """
            INSERT INTO trends
            (last_updated, top_domains, movers, invisible_sites, category_stats, version, system_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                time.time(),
                json.dumps(enhanced_data.get("top_domains", [])),
                json.dumps(enhanced_data.get("movers", [])),
                json.dumps(enhanced_data.get("invisible_sites", [])),
                json.dumps(enhanced_data.get("category_stats", {})),
                enhanced_data.get("version"),
                enhanced_data.get("system_version")
            )
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Saved enhanced trends data")
        return True
        
    except Exception as e:
        logger.error(f"Error saving enhanced trends data: {e}")
        return False

def get_enhanced_trends() -> Dict:
    """
    Get the latest enhanced trends data with version information.
    
    Returns:
        Dictionary with trends data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT * FROM trends
            ORDER BY last_updated DESC
            LIMIT 1
            """
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            # Convert to more usable format
            trends_data = {
                "last_updated": result["last_updated"],
                "top_domains": result["top_domains"],
                "movers": result["movers"],
                "invisible_sites": result["invisible_sites"],
                "category_stats": result["category_stats"],
                "version": result["version"],
                "system_version": result["system_version"]
            }
            return trends_data
        else:
            # Return empty data structure
            return {
                "last_updated": time.time(),
                "top_domains": [],
                "movers": [],
                "invisible_sites": [],
                "category_stats": {},
                "version": PROMPT_VERSION,
                "system_version": SYSTEM_VERSION
            }
        
    except Exception as e:
        logger.error(f"Error getting enhanced trends data: {e}")
        return {
            "last_updated": time.time(),
            "top_domains": [],
            "movers": [],
            "invisible_sites": [],
            "category_stats": {},
            "version": PROMPT_VERSION,
            "system_version": SYSTEM_VERSION
        }

def update_domain_customer_likelihood(domain: str, customer_likelihood: int) -> bool:
    """
    Update the customer likelihood score for a domain.
    
    Args:
        domain: Domain name
        customer_likelihood: Customer likelihood score (0-100)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE domains
            SET customer_likelihood = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE domain = %s
            """,
            (customer_likelihood, domain)
        )
        
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        if affected > 0:
            logger.info(f"Updated customer likelihood for domain {domain}")
            return True
        else:
            logger.warning(f"Domain {domain} not found for customer likelihood update")
            return False
        
    except Exception as e:
        logger.error(f"Error updating customer likelihood for {domain}: {e}")
        return False