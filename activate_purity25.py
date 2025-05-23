"""
PRD-25: LLM Model Enrichment & Signal Divergence Indexing (Purity25)

This script activates the Purity25 functionality with model comparison,
gap detection, and signal rarity profiling.
"""

import os
import json
import logging
from datetime import datetime

# Import agents
from agents import model_comparator, gap_detector, signal_rarity_profiler
import llm_clients

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_model_comparisons(prompts_list):
    """
    Run model comparisons for a list of prompts.
    
    Args:
        prompts_list: List of dictionaries with prompt and category keys
    """
    logger.info(f"Running model comparisons for {len(prompts_list)} prompts")
    
    # Initialize multi-model client
    client = llm_clients.MultiModelClient(use_real_models=False)  # Use mock clients for demo
    
    results = []
    
    for prompt_data in prompts_list:
        prompt = prompt_data["prompt"]
        category = prompt_data["category"]
        prompt_id = f"purity25_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Processing prompt: {prompt}")
        
        # Get responses from all models
        model_responses = client.get_all_model_responses(prompt)
        
        # Run model comparator
        divergence_metrics = model_comparator.calculate_model_disagreement(
            model_responses=model_responses,
            category=category
        )
        
        # Run gap detector
        blindspot_metrics = gap_detector.detect_model_blindspots(
            prompt_id=prompt_id,
            prompt_text=prompt,
            category=category,
            model_responses=model_responses
        )
        
        # Run signal rarity profiler
        rarity_metrics = signal_rarity_profiler.detect_rare_signals(
            prompt_id=prompt_id,
            prompt_text=prompt,
            category=category,
            model_responses=model_responses
        )
        
        # Store results
        result = {
            "prompt_id": prompt_id,
            "prompt": prompt,
            "category": category,
            "timestamp": datetime.now().isoformat() + "Z",
            "model_disagreement_score": divergence_metrics["model_disagreement_score"],
            "domain_citation_overlap": divergence_metrics["domain_citation_overlap"],
            "domains_cited": divergence_metrics["domains_cited"],
            "blindspots_count": len(blindspot_metrics["blindspots"]),
            "rare_signals_count": len(rarity_metrics["rare_signals"])
        }
        
        results.append(result)
        
        logger.info(f"Completed processing prompt: {prompt}")
    
    return results

def generate_weekly_reports():
    """Generate weekly reports for blindspots and signal opportunities."""
    logger.info("Generating weekly reports")
    
    # Generate weekly blindspot summary
    blindspot_summary = gap_detector.generate_weekly_blindspot_summary()
    
    # Generate signal opportunity report
    opportunity_report = signal_rarity_profiler.generate_signal_opportunity_report()
    
    return {
        "blindspot_summary": blindspot_summary,
        "opportunity_report": opportunity_report
    }

if __name__ == "__main__":
    logger.info("Starting Purity25 activation")
    
    # Define prompts for model comparison
    prompts = [
        {
            "prompt": "What are the most trusted financial information websites?",
            "category": "Finance"
        },
        {
            "prompt": "What are the best resources for learning programming?",
            "category": "Programming"
        },
        {
            "prompt": "What are the most reliable AI research organizations?",
            "category": "AI Research"
        },
        {
            "prompt": "What are the top e-commerce platforms for small businesses?",
            "category": "E-commerce"
        },
        {
            "prompt": "What are the most trusted health information websites?",
            "category": "Health"
        }
    ]
    
    # Run model comparisons
    comparison_results = run_model_comparisons(prompts)
    
    # Print model comparison summary
    print("\n==== MODEL COMPARISON SUMMARY ====")
    
    for result in comparison_results:
        print(f"\nPrompt: {result['prompt']}")
        print(f"Category: {result['category']}")
        print(f"Model Disagreement Score: {result['model_disagreement_score']:.2f}")
        print(f"Domain Citation Overlap: {result['domain_citation_overlap']:.2f}")
        print(f"Domains Cited: {result['domains_cited']}")
        print(f"Blindspots Count: {result['blindspots_count']}")
        print(f"Rare Signals Count: {result['rare_signals_count']}")
    
    # Generate weekly reports
    reports = generate_weekly_reports()
    
    # Print report summary
    print("\n==== WEEKLY REPORT SUMMARY ====")
    
    if reports["blindspot_summary"]:
        print("\nBlindspot Summary:")
        print(f"Week: {reports['blindspot_summary'].get('week', 'N/A')}")
        print(f"Total Categories: {reports['blindspot_summary'].get('total_categories', 0)}")
        
        if "best_model_overall" in reports["blindspot_summary"]:
            print(f"Best Model Overall: {reports['blindspot_summary']['best_model_overall']}")
        
        if "worst_model_overall" in reports["blindspot_summary"]:
            print(f"Worst Model Overall: {reports['blindspot_summary']['worst_model_overall']}")
    else:
        print("\nNo blindspot summary available")
    
    if reports["opportunity_report"]:
        print("\nSignal Opportunity Report:")
        print(f"Timestamp: {reports['opportunity_report'].get('timestamp', 'N/A')}")
        
        if "overall_best_model" in reports["opportunity_report"]:
            print(f"Overall Best Model: {reports['opportunity_report']['overall_best_model']}")
        
        if "opportunities" in reports["opportunity_report"]:
            print(f"Top Opportunities: {len(reports['opportunity_report']['opportunities'])}")
            
            for i, opportunity in enumerate(reports["opportunity_report"]["opportunities"][:3], 1):
                print(f"\n  Opportunity {i}:")
                print(f"  Category: {opportunity.get('category', 'N/A')}")
                print(f"  Model: {opportunity.get('model', 'N/A')}")
                print(f"  Unique Domains: {', '.join(opportunity.get('unique_domains', []))}")
    else:
        print("\nNo opportunity report available")
    
    print("\n=================================")
    
    logger.info("Purity25 activation completed")