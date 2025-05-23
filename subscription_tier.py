"""
Subscription Tier System

This module implements a tier-based subscription system that controls access
to various features of the Sentinel loop system.

Tiers:
- Free: Limited access to basic features
- Pro: Access to intermediate features with manual control
- Growth: Extended features but no auto-publishing
- Enterprise: Full access with autonomous execution
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tier definitions
TIERS = {
    "free": {
        "name": "Free",
        "description": "Basic access to MISS score and limited features",
        "features": {
            "weekly_miss_score": True,
            "model_presence_tracker": True,
            "score_drift_alerts": True,
            "detection_step": True,
            "drafting_step": False,
            "publishing_step": False,
            "validation_step": False,
            "feedback_step": False,
            "signal_audit": False,
            "insight_preview": False,
            "human_override": False,
            "purity_score": False,
            "multi_domain": False,
            "competitive_benchmarking": False,
            "ab_testing": False,
            "feedback_analysis": False,
            "auto_publishing": False,
            "signal_triggers": False,
            "model_prioritization": False,
            "api_export": False,
            "custom_policies": False
        },
        "limits": {
            "domains": 1,
            "models": 1,
            "categories": 3,
            "history_weeks": 4,
            "alerts_per_week": 1
        }
    },
    "pro": {
        "name": "Pro",
        "description": "Professional access with manual publishing control",
        "features": {
            "weekly_miss_score": True,
            "model_presence_tracker": True,
            "score_drift_alerts": True,
            "detection_step": True,
            "drafting_step": True,
            "publishing_step": True,  # Manual only
            "validation_step": False,
            "feedback_step": False,
            "signal_audit": True,
            "insight_preview": True,
            "human_override": True,
            "purity_score": True,
            "multi_domain": False,
            "competitive_benchmarking": False,
            "ab_testing": False,
            "feedback_analysis": False,
            "auto_publishing": False,
            "signal_triggers": False,
            "model_prioritization": False,
            "api_export": False,
            "custom_policies": False
        },
        "limits": {
            "domains": 3,
            "models": 2,
            "categories": 5,
            "history_weeks": 12,
            "alerts_per_week": 5
        }
    },
    "growth": {
        "name": "Growth",
        "description": "Advanced features with multi-domain support and full loop except auto-publishing",
        "features": {
            "weekly_miss_score": True,
            "model_presence_tracker": True,
            "score_drift_alerts": True,
            "detection_step": True,
            "drafting_step": True,
            "publishing_step": True,  # Manual only
            "validation_step": True,
            "feedback_step": True,
            "signal_audit": True,
            "insight_preview": True,
            "human_override": True,
            "purity_score": True,
            "multi_domain": True,
            "competitive_benchmarking": True,
            "ab_testing": True,
            "feedback_analysis": True,
            "auto_publishing": False,
            "signal_triggers": False,
            "model_prioritization": False,
            "api_export": False,
            "custom_policies": False
        },
        "limits": {
            "domains": 10,
            "models": 3,
            "categories": 10,
            "history_weeks": 26,
            "alerts_per_week": 20
        }
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Full access with autonomous agent execution and custom policies",
        "features": {
            "weekly_miss_score": True,
            "model_presence_tracker": True,
            "score_drift_alerts": True,
            "detection_step": True,
            "drafting_step": True,
            "publishing_step": True,
            "validation_step": True,
            "feedback_step": True,
            "signal_audit": True,
            "insight_preview": True,
            "human_override": True,
            "purity_score": True,
            "multi_domain": True,
            "competitive_benchmarking": True,
            "ab_testing": True,
            "feedback_analysis": True,
            "auto_publishing": True,
            "signal_triggers": True,
            "model_prioritization": True,
            "api_export": True,
            "custom_policies": True
        },
        "limits": {
            "domains": float('inf'),  # Unlimited
            "models": float('inf'),   # Unlimited
            "categories": float('inf'),  # Unlimited
            "history_weeks": 52,  # Full year
            "alerts_per_week": float('inf')  # Unlimited
        }
    }
}

class SubscriptionTierManager:
    """
    Manages access to features based on subscription tier.
    """
    
    def __init__(self):
        """Initialize the subscription tier manager."""
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """
        Load user data from file.
        
        Returns:
            Dictionary with user data
        """
        users_path = "data/subscription/users.json"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs("data/subscription", exist_ok=True)
            
            if os.path.exists(users_path):
                with open(users_path, "r") as f:
                    return json.load(f)
            else:
                # Initialize with default admin user
                return {
                    "users": {
                        "admin": {
                            "user_id": "admin",
                            "name": "Administrator",
                            "email": "admin@llmrank.io",
                            "tier": "enterprise",
                            "created_at": datetime.now().isoformat(),
                            "domains": ["example.com"],
                            "api_key": "sk_admin_key"
                        }
                    }
                }
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            return {"users": {}}
    
    def _save_users(self) -> None:
        """Save user data to file."""
        users_path = "data/subscription/users.json"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs("data/subscription", exist_ok=True)
            
            with open(users_path, "w") as f:
                json.dump(self.users, f, indent=2)
                
            logger.info("User data saved successfully")
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user data by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data dictionary or None if not found
        """
        return self.users.get("users", {}).get(user_id)
    
    def get_user_by_api_key(self, api_key: str) -> Optional[Dict]:
        """
        Get user data by API key.
        
        Args:
            api_key: API key
            
        Returns:
            User data dictionary or None if not found
        """
        for user_id, user_data in self.users.get("users", {}).items():
            if user_data.get("api_key") == api_key:
                return user_data
        return None
    
    def create_user(self, name: str, email: str, tier: str = "free") -> Dict:
        """
        Create a new user.
        
        Args:
            name: User name
            email: User email
            tier: Subscription tier (default: free)
            
        Returns:
            New user data
        """
        # Validate tier
        if tier not in TIERS:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Generate user ID from email
        user_id = email.split("@")[0].lower().replace(".", "_")
        
        # Check if user already exists
        if user_id in self.users.get("users", {}):
            raise ValueError(f"User already exists: {user_id}")
        
        # Generate API key
        import hashlib
        import time
        import random
        api_key = f"sk_{hashlib.sha256(f'{email}{time.time()}{random.random()}'.encode()).hexdigest()[:24]}"
        
        # Create user
        user_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "tier": tier,
            "created_at": datetime.now().isoformat(),
            "domains": [],
            "api_key": api_key
        }
        
        # Add to users
        if "users" not in self.users:
            self.users["users"] = {}
        
        self.users["users"][user_id] = user_data
        
        # Save users
        self._save_users()
        
        return user_data
    
    def update_user_tier(self, user_id: str, tier: str) -> Dict:
        """
        Update a user's subscription tier.
        
        Args:
            user_id: User ID
            tier: New subscription tier
            
        Returns:
            Updated user data
        """
        # Validate tier
        if tier not in TIERS:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Check if user exists
        if user_id not in self.users.get("users", {}):
            raise ValueError(f"User not found: {user_id}")
        
        # Update tier
        self.users["users"][user_id]["tier"] = tier
        
        # Save users
        self._save_users()
        
        return self.users["users"][user_id]
    
    def add_user_domain(self, user_id: str, domain: str) -> Dict:
        """
        Add a domain to a user's account.
        
        Args:
            user_id: User ID
            domain: Domain name
            
        Returns:
            Updated user data
        """
        # Check if user exists
        if user_id not in self.users.get("users", {}):
            raise ValueError(f"User not found: {user_id}")
        
        # Get user data
        user_data = self.users["users"][user_id]
        
        # Check domain limit
        tier_data = TIERS[user_data["tier"]]
        max_domains = tier_data["limits"]["domains"]
        
        if max_domains != float('inf') and len(user_data.get("domains", [])) >= max_domains:
            raise ValueError(f"Domain limit reached for tier {tier_data['name']}")
        
        # Add domain if not already added
        if "domains" not in user_data:
            user_data["domains"] = []
        
        if domain not in user_data["domains"]:
            user_data["domains"].append(domain)
        
        # Save users
        self._save_users()
        
        return user_data
    
    def remove_user_domain(self, user_id: str, domain: str) -> Dict:
        """
        Remove a domain from a user's account.
        
        Args:
            user_id: User ID
            domain: Domain name
            
        Returns:
            Updated user data
        """
        # Check if user exists
        if user_id not in self.users.get("users", {}):
            raise ValueError(f"User not found: {user_id}")
        
        # Get user data
        user_data = self.users["users"][user_id]
        
        # Remove domain if present
        if "domains" in user_data and domain in user_data["domains"]:
            user_data["domains"].remove(domain)
        
        # Save users
        self._save_users()
        
        return user_data
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """
        Check if a user has access to a feature.
        
        Args:
            user_id: User ID
            feature: Feature name
            
        Returns:
            True if user has access, False otherwise
        """
        # Check if user exists
        user_data = self.get_user(user_id)
        if not user_data:
            return False
        
        # Get tier data
        tier = user_data["tier"]
        tier_data = TIERS.get(tier)
        
        if not tier_data:
            return False
        
        # Check feature access
        return tier_data["features"].get(feature, False)
    
    def get_tier_features(self, tier: str) -> Dict:
        """
        Get feature access for a tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            Dictionary with feature access information
        """
        return TIERS.get(tier, {}).get("features", {})
    
    def get_tier_limits(self, tier: str) -> Dict:
        """
        Get usage limits for a tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            Dictionary with usage limits
        """
        return TIERS.get(tier, {}).get("limits", {})
    
    def get_user_feature_access(self, user_id: str) -> Dict:
        """
        Get feature access for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with feature access information
        """
        # Check if user exists
        user_data = self.get_user(user_id)
        if not user_data:
            return {}
        
        # Get tier data
        tier = user_data["tier"]
        return self.get_tier_features(tier)
    
    def get_user_limits(self, user_id: str) -> Dict:
        """
        Get usage limits for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with usage limits
        """
        # Check if user exists
        user_data = self.get_user(user_id)
        if not user_data:
            return {}
        
        # Get tier data
        tier = user_data["tier"]
        return self.get_tier_limits(tier)
    
    def get_upgrade_recommendations(self, user_id: str) -> List[Dict]:
        """
        Get upgrade recommendations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendation dictionaries
        """
        # Check if user exists
        user_data = self.get_user(user_id)
        if not user_data:
            return []
        
        # Get current tier
        current_tier = user_data["tier"]
        
        # Find next tier
        tier_order = ["free", "pro", "growth", "enterprise"]
        current_index = tier_order.index(current_tier)
        
        # If already at top tier, no recommendations
        if current_index == len(tier_order) - 1:
            return []
        
        recommendations = []
        
        # Add recommendations for next tier
        next_tier = tier_order[current_index + 1]
        next_tier_data = TIERS[next_tier]
        
        # Compare features
        current_features = TIERS[current_tier]["features"]
        next_features = next_tier_data["features"]
        
        # Find new features
        new_features = []
        for feature, access in next_features.items():
            if access and not current_features.get(feature, False):
                # Convert feature_name to display name
                display_name = feature.replace("_", " ").title()
                new_features.append(display_name)
        
        if new_features:
            recommendations.append({
                "tier": next_tier,
                "name": next_tier_data["name"],
                "description": next_tier_data["description"],
                "new_features": new_features,
                "message": f"Upgrade to {next_tier_data['name']} to unlock {len(new_features)} new features"
            })
        
        # Check for domain limit recommendations
        current_domains = len(user_data.get("domains", []))
        max_domains = TIERS[current_tier]["limits"]["domains"]
        
        if max_domains != float('inf') and current_domains >= max_domains * 0.8:
            # Close to domain limit
            next_max_domains = TIERS[next_tier]["limits"]["domains"]
            domain_message = (
                f"You're using {current_domains}/{max_domains} domains. "
                f"Upgrade to {next_tier_data['name']} to track up to {next_max_domains} domains."
            )
            
            # Add domain recommendation if not already added
            if not recommendations:
                recommendations.append({
                    "tier": next_tier,
                    "name": next_tier_data["name"],
                    "description": next_tier_data["description"],
                    "new_features": new_features,
                    "message": domain_message
                })
            else:
                recommendations[0]["message"] += f" {domain_message}"
        
        return recommendations

# Singleton instance
_tier_manager = None

def get_manager() -> SubscriptionTierManager:
    """
    Get the singleton instance of the subscription tier manager.
    
    Returns:
        Subscription tier manager instance
    """
    global _tier_manager
    
    if _tier_manager is None:
        _tier_manager = SubscriptionTierManager()
    
    return _tier_manager

def get_user(user_id: str) -> Optional[Dict]:
    """
    Get user data by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User data dictionary or None if not found
    """
    return get_manager().get_user(user_id)

def get_user_by_api_key(api_key: str) -> Optional[Dict]:
    """
    Get user data by API key.
    
    Args:
        api_key: API key
        
    Returns:
        User data dictionary or None if not found
    """
    return get_manager().get_user_by_api_key(api_key)

def create_user(name: str, email: str, tier: str = "free") -> Dict:
    """
    Create a new user.
    
    Args:
        name: User name
        email: User email
        tier: Subscription tier (default: free)
        
    Returns:
        New user data
    """
    return get_manager().create_user(name, email, tier)

def update_user_tier(user_id: str, tier: str) -> Dict:
    """
    Update a user's subscription tier.
    
    Args:
        user_id: User ID
        tier: New subscription tier
        
    Returns:
        Updated user data
    """
    return get_manager().update_user_tier(user_id, tier)

def add_user_domain(user_id: str, domain: str) -> Dict:
    """
    Add a domain to a user's account.
    
    Args:
        user_id: User ID
        domain: Domain name
        
    Returns:
        Updated user data
    """
    return get_manager().add_user_domain(user_id, domain)

def remove_user_domain(user_id: str, domain: str) -> Dict:
    """
    Remove a domain from a user's account.
    
    Args:
        user_id: User ID
        domain: Domain name
        
    Returns:
        Updated user data
    """
    return get_manager().remove_user_domain(user_id, domain)

def check_feature_access(user_id: str, feature: str) -> bool:
    """
    Check if a user has access to a feature.
    
    Args:
        user_id: User ID
        feature: Feature name
        
    Returns:
        True if user has access, False otherwise
    """
    return get_manager().check_feature_access(user_id, feature)

def get_tier_features(tier: str) -> Dict:
    """
    Get feature access for a tier.
    
    Args:
        tier: Subscription tier
        
    Returns:
        Dictionary with feature access information
    """
    return get_manager().get_tier_features(tier)

def get_tier_limits(tier: str) -> Dict:
    """
    Get usage limits for a tier.
    
    Args:
        tier: Subscription tier
        
    Returns:
        Dictionary with usage limits
    """
    return get_manager().get_tier_limits(tier)

def get_user_feature_access(user_id: str) -> Dict:
    """
    Get feature access for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with feature access information
    """
    return get_manager().get_user_feature_access(user_id)

def get_user_limits(user_id: str) -> Dict:
    """
    Get usage limits for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with usage limits
    """
    return get_manager().get_user_limits(user_id)

def get_upgrade_recommendations(user_id: str) -> List[Dict]:
    """
    Get upgrade recommendations for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of recommendation dictionaries
    """
    return get_manager().get_upgrade_recommendations(user_id)

if __name__ == "__main__":
    # Test subscription tier system
    
    # Create a test user
    try:
        user = create_user("Test User", "test@example.com", "free")
        print(f"Created user: {user['user_id']} with tier {user['tier']}")
    except ValueError as e:
        print(f"User already exists: {e}")
        user = get_manager().get_user("test")
    
    # Add a domain
    domain = "example.com"
    try:
        user = add_user_domain(user["user_id"], domain)
        print(f"Added domain {domain} to user {user['user_id']}")
    except ValueError as e:
        print(f"Error adding domain: {e}")
    
    # Check feature access
    features_to_check = [
        "weekly_miss_score",
        "signal_audit",
        "multi_domain",
        "auto_publishing"
    ]
    
    print(f"\nFeature access for tier {user['tier']}:")
    for feature in features_to_check:
        access = check_feature_access(user["user_id"], feature)
        print(f"  {feature}: {'✓' if access else '✗'}")
    
    # Get upgrade recommendations
    recommendations = get_upgrade_recommendations(user["user_id"])
    
    if recommendations:
        print(f"\nUpgrade recommendations:")
        for rec in recommendations:
            print(f"  Upgrade to {rec['name']}: {rec['message']}")
            if "new_features" in rec and rec["new_features"]:
                print(f"    New features: {', '.join(rec['new_features'])}")
    else:
        print("\nNo upgrade recommendations available.")