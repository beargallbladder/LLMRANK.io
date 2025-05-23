"""
LLMPageRank V3 Prompt Validator

This module handles prompt validation, QA intensity scoring, and problem detection for the V3 system.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
import numpy as np

# Import from project modules
from config import DATA_DIR, CATEGORIES, PROMPT_VERSION

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PROMPTS_DIR = f"{DATA_DIR}/prompts"
INVALID_PROMPTS_FILE = f"{DATA_DIR}/invalid_prompts.json"
QA_INTENSITY_DIR = f"{DATA_DIR}/qa_intensity"

# Create directories if they don't exist
os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(QA_INTENSITY_DIR, exist_ok=True)

class PromptValidator:
    """Validates prompts and tracks QA intensity for LLMPageRank V3."""
    
    def __init__(self):
        """Initialize the prompt validator."""
        self.invalid_prompts = []
        self.prompt_history = {}
        self.qa_intensity_scores = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing prompt validation data."""
        # Load invalid prompts
        if os.path.exists(INVALID_PROMPTS_FILE):
            try:
                with open(INVALID_PROMPTS_FILE, 'r') as f:
                    self.invalid_prompts = json.load(f)
            except Exception as e:
                logger.error(f"Error loading invalid prompts: {e}")
                self.invalid_prompts = []
        
        # Load prompt history
        for category in CATEGORIES:
            prompts_file = os.path.join(PROMPTS_DIR, f"{category}_prompts.json")
            
            if os.path.exists(prompts_file):
                try:
                    with open(prompts_file, 'r') as f:
                        self.prompt_history[category] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading prompts for {category}: {e}")
                    self.prompt_history[category] = []
        
        # Load QA intensity scores
        for category in CATEGORIES:
            qa_file = os.path.join(QA_INTENSITY_DIR, f"{category}_qa.json")
            
            if os.path.exists(qa_file):
                try:
                    with open(qa_file, 'r') as f:
                        self.qa_intensity_scores[category] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading QA scores for {category}: {e}")
                    self.qa_intensity_scores[category] = {}
    
    def validate_prompt(self, prompt: Dict) -> Dict:
        """
        Validate a prompt and return validation results.
        
        Args:
            prompt: Dictionary containing prompt information
        
        Returns:
            Dictionary with validation results
        """
        # Extract prompt data
        prompt_id = prompt.get("prompt_id", "")
        prompt_text = prompt.get("prompt_text", "")
        category = prompt.get("category", "")
        prompt_type = prompt.get("prompt_type", "")
        
        if not prompt_id or not prompt_text or not category:
            return {
                "valid": False,
                "prompt_id": prompt_id,
                "reason": "Missing required fields (prompt_id, prompt_text, or category)",
                "qa_intensity": 1.0,  # High intensity needed due to missing data
                "timestamp": time.time()
            }
        
        # Check category validity
        if category not in CATEGORIES:
            return {
                "valid": False,
                "prompt_id": prompt_id,
                "reason": f"Invalid category: {category}",
                "qa_intensity": 0.8,  # High intensity for category issues
                "timestamp": time.time()
            }
        
        # Length checks
        if len(prompt_text) < 10:
            return {
                "valid": False,
                "prompt_id": prompt_id,
                "reason": "Prompt text too short (< 10 chars)",
                "qa_intensity": 0.7,
                "timestamp": time.time()
            }
        
        if len(prompt_text) > 500:
            return {
                "valid": False,
                "prompt_id": prompt_id,
                "reason": "Prompt text too long (> 500 chars)",
                "qa_intensity": 0.6,
                "timestamp": time.time()
            }
        
        # Check for prompt duplication
        if category in self.prompt_history:
            for existing_prompt in self.prompt_history[category]:
                if existing_prompt.get("prompt_id") != prompt_id and \
                   existing_prompt.get("prompt_text") == prompt_text:
                    return {
                        "valid": False,
                        "prompt_id": prompt_id,
                        "reason": f"Duplicate prompt text (same as prompt_id: {existing_prompt.get('prompt_id')})",
                        "qa_intensity": 0.5,
                        "timestamp": time.time()
                    }
        
        # Check for prompt problems
        problems = self._check_prompt_problems(prompt_text)
        
        if problems:
            return {
                "valid": False,
                "prompt_id": prompt_id,
                "reason": f"Prompt problems: {', '.join(problems)}",
                "qa_intensity": 0.7,
                "timestamp": time.time()
            }
        
        # Calculate QA intensity
        qa_intensity = self._calculate_qa_intensity(prompt)
        
        # Valid prompt
        return {
            "valid": True,
            "prompt_id": prompt_id,
            "qa_intensity": qa_intensity,
            "timestamp": time.time()
        }
    
    def _check_prompt_problems(self, prompt_text: str) -> List[str]:
        """
        Check for common prompt problems.
        
        Args:
            prompt_text: Prompt text to check
        
        Returns:
            List of problem descriptions
        """
        problems = []
        
        # Check for leading/trailing whitespace
        if prompt_text.strip() != prompt_text:
            problems.append("Contains leading/trailing whitespace")
        
        # Check for common issues
        if "?" not in prompt_text and prompt_text.endswith("."):
            problems.append("Not a question (missing question mark)")
        
        if "{{" in prompt_text or "}}" in prompt_text:
            problems.append("Contains template placeholders")
        
        if "$" in prompt_text or "{$" in prompt_text:
            problems.append("Contains unresolved variables")
        
        # Common placeholder checks
        placeholders = ["[DOMAIN]", "[CATEGORY]", "[DATE]", "[COMPANY]", "[NAME]"]
        for placeholder in placeholders:
            if placeholder in prompt_text:
                problems.append(f"Contains unresolved placeholder: {placeholder}")
        
        return problems
    
    def _calculate_qa_intensity(self, prompt: Dict) -> float:
        """
        Calculate QA intensity score for a prompt (0-1 scale).
        Higher value = more testing needed due to risks.
        
        Args:
            prompt: Prompt dictionary
        
        Returns:
            QA intensity score (0-1)
        """
        # Base factors
        category = prompt.get("category", "")
        prompt_type = prompt.get("prompt_type", "")
        prompt_text = prompt.get("prompt_text", "")
        
        # Start with default intensity
        intensity = 0.5
        
        # Factor 1: Historical volatility
        if category in self.qa_intensity_scores:
            # Get historical issues rate for this category
            category_scores = self.qa_intensity_scores[category]
            issue_rate = category_scores.get("issue_rate", 0.5)
            
            # Adjust based on historical issues
            intensity += (issue_rate - 0.5) * 0.2
        
        # Factor 2: Prompt complexity
        # Simple measure: length and special characters
        complexity = min(1.0, len(prompt_text) / 300)  # Normalize to 0-1
        special_chars = sum(1 for c in prompt_text if not c.isalnum() and not c.isspace())
        special_char_ratio = min(1.0, special_chars / len(prompt_text) * 10)
        
        complexity_factor = (complexity * 0.3 + special_char_ratio * 0.7)
        intensity += (complexity_factor - 0.5) * 0.2
        
        # Factor 3: Domain sensitivity
        sensitive_categories = ["finance", "healthcare", "legal"]
        if category in sensitive_categories:
            intensity += 0.1
        
        # Factor 4: Model disagreement history
        if category in self.qa_intensity_scores:
            disagreement_rate = self.qa_intensity_scores[category].get("model_disagreement", 0.3)
            intensity += disagreement_rate * 0.2
        
        # Ensure intensity is in 0-1 range
        intensity = max(0.1, min(1.0, intensity))
        
        return intensity
    
    def record_invalid_prompt(self, prompt_id: str, prompt_text: str, reason: str, 
                             category: str = "", qa_intensity: float = 0.7) -> None:
        """
        Record an invalid prompt for tracking.
        
        Args:
            prompt_id: Prompt identifier
            prompt_text: Prompt text
            reason: Reason for invalidity
            category: Prompt category
            qa_intensity: QA intensity score
        """
        # Create invalid prompt record
        invalid_prompt = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "category": category,
            "reason": reason,
            "qa_intensity": qa_intensity,
            "timestamp": time.time()
        }
        
        # Add to invalid prompts list
        self.invalid_prompts.append(invalid_prompt)
        
        # Save to file
        self._save_invalid_prompts()
        
        # Update QA intensity for category
        if category:
            self._update_qa_intensity(category, valid=False)
    
    def record_valid_prompt(self, prompt: Dict) -> None:
        """
        Record a valid prompt in the appropriate category.
        
        Args:
            prompt: Prompt dictionary
        """
        category = prompt.get("category", "")
        
        if not category or category not in CATEGORIES:
            logger.error(f"Invalid category for prompt: {prompt}")
            return
        
        # Ensure category exists in prompt history
        if category not in self.prompt_history:
            self.prompt_history[category] = []
        
        # Check if prompt already exists
        for i, existing_prompt in enumerate(self.prompt_history[category]):
            if existing_prompt.get("prompt_id") == prompt.get("prompt_id"):
                # Update existing prompt
                self.prompt_history[category][i] = prompt
                break
        else:
            # Add new prompt
            self.prompt_history[category].append(prompt)
        
        # Save to file
        self._save_prompts(category)
        
        # Update QA intensity for category
        self._update_qa_intensity(category, valid=True)
    
    def _save_invalid_prompts(self) -> None:
        """Save invalid prompts to file."""
        try:
            with open(INVALID_PROMPTS_FILE, 'w') as f:
                json.dump(self.invalid_prompts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving invalid prompts: {e}")
    
    def _save_prompts(self, category: str) -> None:
        """
        Save prompts for a category to file.
        
        Args:
            category: Category name
        """
        if category not in self.prompt_history:
            return
        
        prompts_file = os.path.join(PROMPTS_DIR, f"{category}_prompts.json")
        
        try:
            with open(prompts_file, 'w') as f:
                json.dump(self.prompt_history[category], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving prompts for {category}: {e}")
    
    def _update_qa_intensity(self, category: str, valid: bool) -> None:
        """
        Update QA intensity scores for a category based on validation result.
        
        Args:
            category: Category name
            valid: Whether the prompt was valid
        """
        # Ensure category exists in QA intensity scores
        if category not in self.qa_intensity_scores:
            self.qa_intensity_scores[category] = {
                "total_prompts": 0,
                "invalid_prompts": 0,
                "issue_rate": 0.5,
                "model_disagreement": 0.3,
                "last_updated": time.time()
            }
        
        # Update counts
        self.qa_intensity_scores[category]["total_prompts"] += 1
        
        if not valid:
            self.qa_intensity_scores[category]["invalid_prompts"] += 1
        
        # Calculate issue rate
        total = self.qa_intensity_scores[category]["total_prompts"]
        invalid = self.qa_intensity_scores[category]["invalid_prompts"]
        
        if total > 0:
            self.qa_intensity_scores[category]["issue_rate"] = invalid / total
        
        # Update timestamp
        self.qa_intensity_scores[category]["last_updated"] = time.time()
        
        # Save to file
        qa_file = os.path.join(QA_INTENSITY_DIR, f"{category}_qa.json")
        
        try:
            with open(qa_file, 'w') as f:
                json.dump(self.qa_intensity_scores[category], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving QA scores for {category}: {e}")
    
    def get_qa_intensity_for_domain(self, domain: str, category: str) -> float:
        """
        Get QA intensity score for a domain based on its category.
        
        Args:
            domain: Domain name
            category: Domain category
        
        Returns:
            QA intensity score (0-1)
        """
        # Get category QA intensity
        if category in self.qa_intensity_scores:
            base_intensity = self.qa_intensity_scores[category].get("issue_rate", 0.5)
        else:
            base_intensity = 0.5
        
        # Adjust based on domain factors
        # This is a placeholder for domain-specific adjustments
        # In a real implementation, analyze the domain's history, complexity, etc.
        adjusted_intensity = base_intensity
        
        return adjusted_intensity
    
    def get_invalid_prompts(self) -> List[Dict]:
        """
        Get list of invalid prompts.
        
        Returns:
            List of invalid prompt dictionaries
        """
        return self.invalid_prompts


# Initialize singleton instance
prompt_validator = PromptValidator()

# Module-level functions that use the singleton
def validate_prompt(prompt: Dict) -> Dict:
    """
    Validate a prompt and return validation results.
    
    Args:
        prompt: Dictionary containing prompt information
    
    Returns:
        Dictionary with validation results
    """
    return prompt_validator.validate_prompt(prompt)

def record_invalid_prompt(prompt_id: str, prompt_text: str, reason: str, 
                         category: str = "", qa_intensity: float = 0.7) -> None:
    """
    Record an invalid prompt for tracking.
    
    Args:
        prompt_id: Prompt identifier
        prompt_text: Prompt text
        reason: Reason for invalidity
        category: Prompt category
        qa_intensity: QA intensity score
    """
    prompt_validator.record_invalid_prompt(prompt_id, prompt_text, reason, category, qa_intensity)

def record_valid_prompt(prompt: Dict) -> None:
    """
    Record a valid prompt in the appropriate category.
    
    Args:
        prompt: Prompt dictionary
    """
    prompt_validator.record_valid_prompt(prompt)

def get_qa_intensity_for_domain(domain: str, category: str) -> float:
    """
    Get QA intensity score for a domain based on its category.
    
    Args:
        domain: Domain name
        category: Domain category
    
    Returns:
        QA intensity score (0-1)
    """
    return prompt_validator.get_qa_intensity_for_domain(domain, category)

def get_invalid_prompts() -> List[Dict]:
    """
    Get list of invalid prompts.
    
    Returns:
        List of invalid prompt dictionaries
    """
    return prompt_validator.get_invalid_prompts()