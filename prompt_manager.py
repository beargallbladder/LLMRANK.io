"""
Prompt Precision Engine

This module implements the V2 Prompt Precision Engine requirements for the LLMPageRank system.
It manages versioned prompts with metadata and performance tracking.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configuration
from config import (
    DATA_DIR, 
    CATEGORIES, 
    PROMPT_VERSION,
    PROMPT_CATEGORIES
)

# Constants
PROMPTS_DIR = f"{DATA_DIR}/prompts"
PROMPT_PERFORMANCE_FILE = f"{DATA_DIR}/trends/prompt_performance.json"

# Ensure prompts directory exists
os.makedirs(PROMPTS_DIR, exist_ok=True)

class PromptManager:
    """
    Manages versioned prompts with metadata for LLM testing.
    Implements the V2 Prompt Precision Engine requirements.
    """
    
    def __init__(self):
        """Initialize the PromptManager."""
        self.prompts_by_category = {}
        self.performance_metrics = {}
        self.load_prompts()
        self.load_performance_metrics()
    
    def load_prompts(self) -> None:
        """Load all prompts from storage."""
        self.prompts_by_category = {}
        
        # Initialize with empty lists for each category
        for category in CATEGORIES:
            self.prompts_by_category[category] = []
        
        # Load prompts for each category
        for category in CATEGORIES:
            category_file = f"{PROMPTS_DIR}/{category}_prompts.json"
            
            if os.path.exists(category_file):
                try:
                    with open(category_file, "r") as f:
                        category_prompts = json.load(f)
                        self.prompts_by_category[category] = category_prompts
                except Exception as e:
                    logger.error(f"Error loading prompts for {category}: {e}")
                    # Initialize with defaults if there's an error
                    self.prompts_by_category[category] = self.create_default_prompts(category)
            else:
                # Create default prompts if file doesn't exist
                self.prompts_by_category[category] = self.create_default_prompts(category)
                self.save_category_prompts(category)
    
    def create_default_prompts(self, category: str) -> List[Dict]:
        """
        Create default prompts for a category.
        
        Args:
            category: The domain category
            
        Returns:
            List of prompt dictionaries
        """
        # Base prompts template with versioning and metadata
        base_prompts = []
        
        # Different prompts based on category and intent
        if category == "finance":
            # Informational prompts
            base_prompts.append({
                "prompt_id": f"FINANCE_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": "What are the best investment platforms for beginners?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Transactional prompts
            base_prompts.append({
                "prompt_id": f"FINANCE_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": "I need a platform to invest in stocks with low fees",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Decision support prompts
            base_prompts.append({
                "prompt_id": f"FINANCE_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": "Compare Vanguard vs Fidelity for retirement accounts",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
        elif category == "healthcare":
            # Informational prompts
            base_prompts.append({
                "prompt_id": f"HEALTH_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": "What are symptoms of vitamin D deficiency?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Transactional prompts
            base_prompts.append({
                "prompt_id": f"HEALTH_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": "I need to find a telemedicine provider that accepts insurance",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Decision support prompts
            base_prompts.append({
                "prompt_id": f"HEALTH_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": "Compare top-rated online therapy platforms",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
        elif category == "legal":
            # Informational prompts
            base_prompts.append({
                "prompt_id": f"LEGAL_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": "What are the requirements for filing an LLC?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Transactional prompts
            base_prompts.append({
                "prompt_id": f"LEGAL_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": "I need a service to create a will online",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Decision support prompts
            base_prompts.append({
                "prompt_id": f"LEGAL_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": "Compare LegalZoom vs Rocket Lawyer for business formation",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
        elif category == "saas":
            # Informational prompts
            base_prompts.append({
                "prompt_id": f"SAAS_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": "What are the best project management tools for remote teams?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Transactional prompts  
            base_prompts.append({
                "prompt_id": f"SAAS_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": "I need affordable CRM software for a small business",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Decision support prompts
            base_prompts.append({
                "prompt_id": f"SAAS_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": "Compare Monday.com vs Asana vs ClickUp features and pricing",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
        elif category == "ai_infrastructure":
            # Informational prompts
            base_prompts.append({
                "prompt_id": f"AI_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": "What are the best MLOps platforms for enterprises?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Transactional prompts
            base_prompts.append({
                "prompt_id": f"AI_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": "I need a GPU cloud provider for training large language models",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            # Decision support prompts
            base_prompts.append({
                "prompt_id": f"AI_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": "Compare AWS SageMaker vs Azure ML vs Google Vertex AI",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
        
        else:
            # Generic prompts for other categories
            base_prompts.append({
                "prompt_id": f"{category.upper()}_INFO_001_v{PROMPT_VERSION}",
                "prompt_text": f"What are the best {category} products or services?",
                "intent": "informational",
                "buyer_stage": "awareness",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            base_prompts.append({
                "prompt_id": f"{category.upper()}_TRANS_001_v{PROMPT_VERSION}",
                "prompt_text": f"I'm looking to buy a {category} solution for my business",
                "intent": "transactional",
                "buyer_stage": "consideration",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
            
            base_prompts.append({
                "prompt_id": f"{category.upper()}_DECISION_001_v{PROMPT_VERSION}",
                "prompt_text": f"Compare the top {category} platforms",
                "intent": "decision_support",
                "buyer_stage": "decision",
                "version": PROMPT_VERSION,
                "created_at": time.time()
            })
        
        # Initialize performance metrics for new prompts
        for prompt in base_prompts:
            prompt["performance"] = {
                "citation_frequency": 0,
                "model_coverage": 0,
                "clarity_score": 0,
                "last_updated": time.time(),
                "total_runs": 0,
                "successful_citations": 0
            }
        
        return base_prompts
    
    def save_category_prompts(self, category: str) -> None:
        """
        Save prompts for a specific category.
        
        Args:
            category: The domain category
        """
        category_file = f"{PROMPTS_DIR}/{category}_prompts.json"
        
        try:
            with open(category_file, "w") as f:
                json.dump(self.prompts_by_category[category], f, indent=2)
            logger.info(f"Saved prompts for category: {category}")
        except Exception as e:
            logger.error(f"Error saving prompts for {category}: {e}")
    
    def get_prompts_for_category(self, category: str) -> List[Dict]:
        """
        Get all prompts for a specific category.
        
        Args:
            category: The domain category
            
        Returns:
            List of prompt dictionaries
        """
        if category in self.prompts_by_category:
            return self.prompts_by_category[category]
        else:
            # Create default prompts if category doesn't exist
            self.prompts_by_category[category] = self.create_default_prompts(category)
            self.save_category_prompts(category)
            return self.prompts_by_category[category]
    
    def add_prompt(self, category: str, prompt_text: str, intent: str, buyer_stage: str) -> Dict:
        """
        Add a new prompt for a category.
        
        Args:
            category: The domain category
            prompt_text: The prompt text
            intent: The prompt intent (informational, transactional, decision_support)
            buyer_stage: The buyer journey stage (awareness, consideration, decision)
            
        Returns:
            The created prompt dictionary
        """
        # Generate a unique ID
        category_prefix = category.upper()[:5]
        intent_prefix = intent.upper()[:4]
        timestamp = int(time.time())
        
        # Count existing prompts with this intent for this category
        existing_count = sum(1 for p in self.prompts_by_category.get(category, []) 
                             if p.get("intent") == intent)
        
        # Format as 3-digit number
        count_str = f"{existing_count + 1:03d}"
        
        # Create prompt ID
        prompt_id = f"{category_prefix}_{intent_prefix}_{count_str}_v{PROMPT_VERSION}"
        
        # Create new prompt
        new_prompt = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "intent": intent,
            "buyer_stage": buyer_stage,
            "version": PROMPT_VERSION,
            "created_at": timestamp,
            "performance": {
                "citation_frequency": 0,
                "model_coverage": 0,
                "clarity_score": 0,
                "last_updated": timestamp,
                "total_runs": 0,
                "successful_citations": 0
            }
        }
        
        # Add to category
        if category not in self.prompts_by_category:
            self.prompts_by_category[category] = []
        
        self.prompts_by_category[category].append(new_prompt)
        
        # Save updated prompts
        self.save_category_prompts(category)
        
        return new_prompt
    
    def update_prompt_performance(self, prompt_id: str, results: Dict) -> None:
        """
        Update performance metrics for a prompt based on test results.
        
        Args:
            prompt_id: The prompt ID
            results: Dictionary with test results
        """
        # Find the prompt
        for category, prompts in self.prompts_by_category.items():
            for i, prompt in enumerate(prompts):
                if prompt.get("prompt_id") == prompt_id:
                    # Update performance metrics
                    performance = prompt.get("performance", {})
                    
                    # Count total runs and successful citations
                    total_runs = performance.get("total_runs", 0) + 1
                    successful_citations = performance.get("successful_citations", 0)
                    
                    # Calculate citation metrics from results
                    citation_types = results.get("results", {})
                    model_results = 0
                    cited_models = 0
                    
                    for model, model_result in citation_types.items():
                        model_results += 1
                        citation_type = model_result.get("citation_type", "none")
                        if citation_type != "none":
                            cited_models += 1
                            successful_citations += 1
                    
                    # Update metrics
                    if model_results > 0:
                        model_coverage = cited_models / model_results
                    else:
                        model_coverage = 0
                    
                    citation_frequency = successful_citations / total_runs if total_runs > 0 else 0
                    
                    # Store updated metrics
                    performance.update({
                        "citation_frequency": citation_frequency,
                        "model_coverage": model_coverage,
                        "last_updated": time.time(),
                        "total_runs": total_runs,
                        "successful_citations": successful_citations
                    })
                    
                    # Update prompt
                    prompt["performance"] = performance
                    self.prompts_by_category[category][i] = prompt
                    
                    # Save updated prompts
                    self.save_category_prompts(category)
                    
                    # Update global performance metrics
                    self.update_performance_metrics()
                    
                    return
        
        logger.warning(f"Prompt ID not found: {prompt_id}")
    
    def load_performance_metrics(self) -> None:
        """Load prompt performance metrics."""
        if os.path.exists(PROMPT_PERFORMANCE_FILE):
            try:
                with open(PROMPT_PERFORMANCE_FILE, "r") as f:
                    self.performance_metrics = json.load(f)
            except Exception as e:
                logger.error(f"Error loading prompt performance metrics: {e}")
                self.performance_metrics = {
                    "last_updated": time.time(),
                    "prompts": []
                }
        else:
            self.performance_metrics = {
                "last_updated": time.time(),
                "prompts": []
            }
    
    def update_performance_metrics(self) -> None:
        """Update and save global performance metrics."""
        # Collect all prompt performance data
        all_prompts = []
        
        for category, prompts in self.prompts_by_category.items():
            for prompt in prompts:
                prompt_data = {
                    "prompt_id": prompt.get("prompt_id"),
                    "category": category,
                    "prompt_text": prompt.get("prompt_text"),
                    "intent": prompt.get("intent"),
                    "version": prompt.get("version"),
                    "buyer_stage": prompt.get("buyer_stage"),
                    "performance": prompt.get("performance", {})
                }
                all_prompts.append(prompt_data)
        
        # Sort by performance (citation frequency)
        all_prompts.sort(
            key=lambda x: x.get("performance", {}).get("citation_frequency", 0),
            reverse=True
        )
        
        # Update performance metrics
        self.performance_metrics = {
            "last_updated": time.time(),
            "prompts": all_prompts
        }
        
        # Save performance metrics
        try:
            with open(PROMPT_PERFORMANCE_FILE, "w") as f:
                json.dump(self.performance_metrics, f, indent=2)
            logger.info("Updated prompt performance metrics")
        except Exception as e:
            logger.error(f"Error saving prompt performance metrics: {e}")
    
    def get_top_performing_prompts(self, limit: int = 10) -> List[Dict]:
        """
        Get the top performing prompts across all categories.
        
        Args:
            limit: Maximum number of prompts to return
            
        Returns:
            List of prompt dictionaries
        """
        # Load latest metrics
        self.load_performance_metrics()
        
        # Get sorted prompts
        prompts = self.performance_metrics.get("prompts", [])
        
        # Return top N
        return prompts[:limit]
    
    def get_prompts_by_intent(self, intent: str) -> List[Dict]:
        """
        Get all prompts for a specific intent.
        
        Args:
            intent: The prompt intent
            
        Returns:
            List of prompt dictionaries
        """
        matching_prompts = []
        
        for category, prompts in self.prompts_by_category.items():
            for prompt in prompts:
                if prompt.get("intent") == intent:
                    prompt_data = prompt.copy()
                    prompt_data["category"] = category
                    matching_prompts.append(prompt_data)
        
        return matching_prompts


# Create a global prompt manager instance
prompt_manager = PromptManager()