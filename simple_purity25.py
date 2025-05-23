"""
PRD-25: LLM Model Enrichment & Signal Divergence Indexing (Purity25) - Simple Version

This script implements a simplified version of the Purity25 functionality to simulate
model comparison, gap detection, and signal rarity profiling without external dependencies.
"""

import os
import json
import logging
import random
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory for storing output data
DATA_DIR = "data/purity25_output"
os.makedirs(DATA_DIR, exist_ok=True)

class SimpleLLMClient:
    """Simple mock LLM client for testing."""
    
    def __init__(self, model_name):
        """Initialize the client."""
        self.model_name = model_name
        
        # Define citation patterns for each model
        self.citation_patterns = {
            "gpt-4": ["example.com", "ai-research.org", "techblog.io", "gpt4-exclusive.com"],
            "claude": ["example.com", "datascience.net", "ai-research.org", "claude-exclusive.net"],
            "mixtral": ["example.com", "machinelearning.dev", "devops.co", "mixtral-exclusive.io"],
            "gemini": ["example.com", "ai-research.org", "cybersecurity.io", "gemini-exclusive.org"],
            "cohere": ["example.com", "ai-research.org", "knowledge-base.io", "cohere-exclusive.com"],
            "llama-3": ["example.com", "open-source.org", "research-papers.net", "llama-exclusive.ai"],
            "perplexity": ["example.com", "ai-research.org", "real-time-data.io", "perplexity-exclusive.co"],
            "claude-3-opus": ["example.com", "advanced-research.org", "deep-insights.ai", "opus-exclusive.org"]
        }
        
        # Define category-specific domains
        self.category_domains = {
            "AI Research": ["arxiv.org", "openai.com", "anthropic.com", "huggingface.co", "deepmind.com"],
            "Finance": ["bloomberg.com", "wsj.com", "ft.com", "cnbc.com", "forbes.com"],
            "Programming": ["github.com", "stackoverflow.com", "dev.to", "medium.com", "freecodecamp.org"],
            "E-commerce": ["shopify.com", "amazon.com", "ebay.com", "etsy.com", "woocommerce.com"],
            "Health": ["who.int", "nih.gov", "mayoclinic.org", "webmd.com", "healthline.com"]
        }
    
    def get_citations(self, prompt, category):
        """Get simulated citations for a prompt."""
        # Get base citations for this model
        citations = list(self.citation_patterns.get(self.model_name, ["example.com"]))
        
        # Add category-specific domains
        category_specific = self.category_domains.get(category, [])
        
        # Randomly select some category-specific domains
        selected_count = random.randint(1, min(3, len(category_specific)))
        selected_domains = random.sample(category_specific, selected_count)
        
        # Add to citations
        citations.extend(selected_domains)
        
        # Sometimes skip some citations to create model disagreement
        if random.random() < 0.3:
            skip_count = random.randint(1, len(citations) // 2)
            for _ in range(skip_count):
                if citations:
                    citations.pop(random.randrange(len(citations)))
        
        return citations

class MultiModelClient:
    """Client for interacting with multiple LLM models."""
    
    def __init__(self):
        """Initialize the multi-model client."""
        # Initialize individual clients
        self.clients = {
            "gpt-4": SimpleLLMClient("gpt-4"),
            "claude": SimpleLLMClient("claude"),
            "mixtral": SimpleLLMClient("mixtral"),
            "gemini": SimpleLLMClient("gemini"),
            "cohere": SimpleLLMClient("cohere"),
            "llama-3": SimpleLLMClient("llama-3"),
            "perplexity": SimpleLLMClient("perplexity"),
            "claude-3-opus": SimpleLLMClient("claude-3-opus")
        }
    
    def get_all_model_responses(self, prompt, category):
        """Get responses from all models."""
        responses = {}
        
        for model_name, client in self.clients.items():
            responses[model_name] = client.get_citations(prompt, category)
        
        return responses

class ModelComparator:
    """Model comparator agent."""
    
    def calculate_model_disagreement(self, model_responses, category):
        """Calculate model disagreement metrics."""
        # Get all unique domains
        all_domains = set()
        for domains in model_responses.values():
            all_domains.update(domains)
        
        total_domains = len(all_domains)
        
        if total_domains == 0:
            return {
                "model_disagreement_score": 0.0,
                "domain_citation_overlap": 0.0,
                "domains_cited": 0,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate jaccard distances
        models = list(model_responses.keys())
        distances = []
        
        for i in range(len(models)):
            for j in range(i+1, len(models)):
                model_a = models[i]
                model_b = models[j]
                
                set_a = set(model_responses[model_a])
                set_b = set(model_responses[model_b])
                
                union = len(set_a.union(set_b))
                intersection = len(set_a.intersection(set_b))
                
                if union > 0:
                    distance = 1.0 - (intersection / union)
                else:
                    distance = 0.0
                
                distances.append(distance)
        
        # Calculate average distance
        disagreement_score = sum(distances) / len(distances) if distances else 0.0
        
        # Calculate domain citation overlap
        overlap_ratios = []
        for model, domains in model_responses.items():
            if not domains:
                continue
                
            domains_set = set(domains)
            for other_model, other_domains in model_responses.items():
                if other_model != model and other_domains:
                    other_domains_set = set(other_domains)
                    intersection = len(domains_set.intersection(other_domains_set))
                    overlap_ratio = intersection / len(domains_set)
                    overlap_ratios.append(overlap_ratio)
        
        average_overlap = sum(overlap_ratios) / len(overlap_ratios) if overlap_ratios else 0.0
        
        return {
            "model_disagreement_score": round(disagreement_score, 3),
            "domain_citation_overlap": round(average_overlap, 3),
            "domains_cited": total_domains,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

class GapDetector:
    """Gap detector agent."""
    
    def detect_model_blindspots(self, prompt_id, prompt_text, category, model_responses):
        """Detect model blindspots."""
        # Get all unique domains
        all_domains = set()
        for domains in model_responses.values():
            all_domains.update(domains)
        
        # Find which models missed which domains
        blindspots = {}
        
        for domain in all_domains:
            missing_models = []
            
            for model, domains in model_responses.items():
                if domain not in domains:
                    missing_models.append(model)
            
            if missing_models:
                blindspots[domain] = missing_models
        
        # Calculate metrics
        total_blindspots = sum(len(models) for models in blindspots.values())
        total_possible = len(all_domains) * len(model_responses)
        
        blindspot_ratio = total_blindspots / total_possible if total_possible > 0 else 0.0
        
        return {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "blindspots": blindspots,
            "metrics": {
                "total_blindspots": total_blindspots,
                "total_possible_citations": total_possible,
                "blindspot_ratio": round(blindspot_ratio, 3),
                "domains_with_blindspots": len(blindspots),
                "total_domains": len(all_domains)
            }
        }

class SignalRarityProfiler:
    """Signal rarity profiler agent."""
    
    def detect_rare_signals(self, prompt_id, prompt_text, category, model_responses):
        """Detect rare signals."""
        # Count how many models cite each domain
        domain_citations = {}
        
        for model, domains in model_responses.items():
            for domain in domains:
                if domain not in domain_citations:
                    domain_citations[domain] = {
                        "count": 0,
                        "models": []
                    }
                
                domain_citations[domain]["count"] += 1
                domain_citations[domain]["models"].append(model)
        
        # Find domains cited by only one model
        rare_signals = {}
        
        for domain, citation_data in domain_citations.items():
            if citation_data["count"] == 1:
                model = citation_data["models"][0]
                
                if model not in rare_signals:
                    rare_signals[model] = []
                
                rare_signals[model].append(domain)
        
        # Calculate metrics
        total_domains = len(domain_citations)
        total_rare_signals = sum(len(domains) for domains in rare_signals.values())
        
        rarity_ratio = total_rare_signals / total_domains if total_domains > 0 else 0.0
        
        return {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "rare_signals": rare_signals,
            "metrics": {
                "total_rare_signals": total_rare_signals,
                "total_domains": total_domains,
                "rarity_ratio": round(rarity_ratio, 3),
                "models_with_rare_signals": len(rare_signals)
            }
        }

def run_model_comparisons(prompts_list):
    """Run model comparisons for a list of prompts."""
    logger.info(f"Running model comparisons for {len(prompts_list)} prompts")
    
    # Initialize clients and agents
    client = MultiModelClient()
    comparator = ModelComparator()
    gap_detector = GapDetector()
    rarity_profiler = SignalRarityProfiler()
    
    results = []
    
    for prompt_data in prompts_list:
        prompt = prompt_data["prompt"]
        category = prompt_data["category"]
        prompt_id = f"purity25_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Processing prompt: {prompt}")
        
        # Get responses from all models
        model_responses = client.get_all_model_responses(prompt, category)
        
        # Run model comparator
        divergence_metrics = comparator.calculate_model_disagreement(
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
        rarity_metrics = rarity_profiler.detect_rare_signals(
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
            "timestamp": datetime.now().isoformat(),
            "model_disagreement_score": divergence_metrics["model_disagreement_score"],
            "domain_citation_overlap": divergence_metrics["domain_citation_overlap"],
            "domains_cited": divergence_metrics["domains_cited"],
            "blindspots_count": len(blindspot_metrics["blindspots"]),
            "rare_signals_count": len(rarity_metrics["rare_signals"]),
            "model_responses": model_responses
        }
        
        results.append(result)
        
        # Save individual results
        save_result(result, prompt_id)
        save_blindspot_data(blindspot_metrics, prompt_id)
        save_rarity_data(rarity_metrics, prompt_id)
        
        logger.info(f"Completed processing prompt: {prompt}")
    
    return results

def save_result(result, prompt_id):
    """Save result to file."""
    filename = f"{DATA_DIR}/comparison_{prompt_id}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Saved result to {filename}")

def save_blindspot_data(data, prompt_id):
    """Save blindspot data to file."""
    filename = f"{DATA_DIR}/blindspots_{prompt_id}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved blindspot data to {filename}")

def save_rarity_data(data, prompt_id):
    """Save rarity data to file."""
    filename = f"{DATA_DIR}/rarity_{prompt_id}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved rarity data to {filename}")

def generate_weekly_digest(results):
    """Generate a weekly digest from results."""
    logger.info("Generating weekly digest")
    
    # Calculate aggregated metrics
    categories = {}
    models = {
        "gpt-4": {"rare_signals": 0, "blindspots": 0},
        "claude": {"rare_signals": 0, "blindspots": 0},
        "mixtral": {"rare_signals": 0, "blindspots": 0},
        "gemini": {"rare_signals": 0, "blindspots": 0},
        "cohere": {"rare_signals": 0, "blindspots": 0},
        "llama-3": {"rare_signals": 0, "blindspots": 0},
        "perplexity": {"rare_signals": 0, "blindspots": 0},
        "claude-3-opus": {"rare_signals": 0, "blindspots": 0}
    }
    
    # Process all results
    for result in results:
        category = result["category"]
        
        if category not in categories:
            categories[category] = {
                "prompts": 0,
                "avg_disagreement": 0.0,
                "total_domains_cited": 0,
                "rare_signals": 0,
                "blindspots": 0
            }
        
        categories[category]["prompts"] += 1
        categories[category]["avg_disagreement"] += result["model_disagreement_score"]
        categories[category]["total_domains_cited"] += result["domains_cited"]
        categories[category]["rare_signals"] += result["rare_signals_count"]
        categories[category]["blindspots"] += result["blindspots_count"]
        
        # Process model-specific data
        for model, domains in result["model_responses"].items():
            # Count how many domains this model missed
            missed_count = sum(1 for other_model_domains in result["model_responses"].values() 
                              for domain in other_model_domains if domain not in domains)
            
            models[model]["blindspots"] += missed_count
            
            # Count rare signals (domains only this model cited)
            rare_count = sum(1 for domain in domains if sum(1 for other_model, other_domains 
                                                           in result["model_responses"].items() 
                                                           if model != other_model and domain in other_domains) == 0)
            
            models[model]["rare_signals"] += rare_count
    
    # Calculate averages
    for category, stats in categories.items():
        if stats["prompts"] > 0:
            stats["avg_disagreement"] /= stats["prompts"]
    
    # Find best and worst models
    best_rare_signal_model = max(models.items(), key=lambda x: x[1]["rare_signals"])[0]
    worst_blindspot_model = max(models.items(), key=lambda x: x[1]["blindspots"])[0]
    
    # Create digest
    digest = {
        "timestamp": datetime.now().isoformat(),
        "total_prompts_analyzed": len(results),
        "total_categories": len(categories),
        "category_stats": categories,
        "model_stats": models,
        "best_rare_signal_model": best_rare_signal_model,
        "worst_blindspot_model": worst_blindspot_model
    }
    
    # Save digest
    filename = f"{DATA_DIR}/weekly_digest.json"
    
    with open(filename, 'w') as f:
        json.dump(digest, f, indent=2)
    
    logger.info(f"Saved weekly digest to {filename}")
    
    return digest

if __name__ == "__main__":
    logger.info("Starting Simple Purity25 Implementation")
    
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
    
    # Generate and print weekly digest
    digest = generate_weekly_digest(comparison_results)
    
    print("\n==== WEEKLY DIGEST ====")
    print(f"Total Prompts Analyzed: {digest['total_prompts_analyzed']}")
    print(f"Total Categories: {digest['total_categories']}")
    print(f"Best Rare Signal Model: {digest['best_rare_signal_model']}")
    print(f"Worst Blindspot Model: {digest['worst_blindspot_model']}")
    
    print("\nCategory Stats:")
    for category, stats in digest['category_stats'].items():
        print(f"  {category}:")
        print(f"    Prompts: {stats['prompts']}")
        print(f"    Avg Disagreement: {stats['avg_disagreement']:.2f}")
        print(f"    Total Domains Cited: {stats['total_domains_cited']}")
        print(f"    Rare Signals: {stats['rare_signals']}")
        print(f"    Blindspots: {stats['blindspots']}")
    
    print("\n=========================")
    
    logger.info("Simple Purity25 Implementation Completed")
    print("\nData has been saved to the data/purity25_output directory.")