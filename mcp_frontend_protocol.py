"""
MCP Frontend Communication Protocol
Codename: "Crystal Clear Control"

This module implements the MCP interface that explicitly controls what data
the frontend (www.llmpagerank.com) receives and how it should be presented.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import requests
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentTier(Enum):
    """Content access tiers."""
    FREE_TEASER = "free_teaser"
    FREE_FULL = "free_full" 
    PAID_PREVIEW = "paid_preview"
    PAID_FULL = "paid_full"
    PREMIUM_EXCLUSIVE = "premium_exclusive"

class EngagementAction(Enum):
    """Actions users can take."""
    VIEW = "view"
    CLICK = "click"
    SHARE = "share"
    CONVERT = "convert"
    UPGRADE = "upgrade"
    RETURN = "return"

@dataclass
class FrontendInstruction:
    """Instructions for how frontend should display content."""
    content_id: str
    tier: ContentTier
    display_mode: str  # "teaser", "full", "gated", "upgrade_prompt"
    engagement_hooks: List[str]  # Specific elements to track
    conversion_trigger: Optional[str]  # When to show upgrade
    time_gate: Optional[int]  # Seconds before revealing more
    next_action: Optional[str]  # What to do after engagement

class MCPFrontendController:
    """
    Controls all communication between MCP backend and frontend.
    Ensures backend determines engagement strategy, not frontend.
    """
    
    def __init__(self):
        """Initialize the MCP Frontend Controller."""
        self.frontend_url = "https://www.llmpagerank.com/api"
        self.engagement_data = {}
        self.conversion_rules = self._load_conversion_rules()
        self.teaser_strategies = self._load_teaser_strategies()
        
        logger.info("🎯 MCP Frontend Controller initialized - Backend controls engagement")
        
    def _load_conversion_rules(self) -> Dict:
        """Load conversion rules that determine when to gate content."""
        return {
            "free_user_limits": {
                "insights_per_day": 5,
                "domains_per_search": 3,
                "detail_level": "basic"
            },
            "conversion_triggers": {
                "view_count": 3,  # Show upgrade after 3 views
                "time_on_page": 60,  # Show upgrade after 1 minute
                "repeat_visits": 2,  # Show upgrade on 2nd visit
                "high_quality_insight": 0.8  # Immediately gate insights > 0.8 quality
            },
            "teaser_lengths": {
                "low_quality": 100,  # Characters for low quality insights
                "medium_quality": 50,  # Shorter teasers for better content
                "high_quality": 30   # Minimal teasers for premium content
            }
        }
        
    def _load_teaser_strategies(self) -> Dict:
        """Load strategies for how to create engaging teasers."""
        return {
            "hooks": {
                "trust_spike": "🚀 {domain} is experiencing a major trust surge...",
                "trust_drop": "⚠️ {domain} trust signals are showing concerning patterns...",
                "competitive_shift": "🔥 Major competitive shift detected in {category}...",
                "model_disagreement": "🤔 AI models disagree about {domain}...",
                "breakthrough": "💡 Breakthrough insight discovered for {domain}..."
            },
            "call_to_actions": {
                "upgrade": "Unlock the full analysis →",
                "register": "Sign up for complete insights →",
                "premium": "Get premium competitive intelligence →"
            }
        }
        
    def prepare_frontend_payload(self, user_profile: Dict, requested_data: Dict) -> Dict:
        """
        Prepare data payload for frontend with explicit engagement controls.
        
        Args:
            user_profile: User's subscription status, engagement history
            requested_data: What the frontend is requesting
            
        Returns:
            Structured payload with engagement instructions
        """
        user_tier = user_profile.get("tier", "free")
        engagement_history = user_profile.get("engagement_history", {})
        
        payload = {
            "timestamp": time.time(),
            "user_controls": self._determine_user_controls(user_profile),
            "content_instructions": [],
            "engagement_tracking": {},
            "conversion_strategy": {}
        }
        
        # Process each requested insight/domain
        for item in requested_data.get("items", []):
            instruction = self._create_content_instruction(item, user_profile, engagement_history)
            payload["content_instructions"].append(instruction.__dict__)
            
        # Add engagement tracking requirements
        payload["engagement_tracking"] = self._create_engagement_tracking(user_profile)
        
        # Add conversion strategy
        payload["conversion_strategy"] = self._create_conversion_strategy(user_profile, engagement_history)
        
        return payload
        
    def _determine_user_controls(self, user_profile: Dict) -> Dict:
        """Determine what controls the user should see."""
        tier = user_profile.get("tier", "free")
        
        controls = {
            "search_limit": 3 if tier == "free" else 100,
            "daily_insights": 5 if tier == "free" else 1000,
            "export_enabled": tier in ["premium", "enterprise"],
            "real_time_alerts": tier in ["premium", "enterprise"],
            "competitive_analysis": tier != "free",
            "historical_data": tier in ["premium", "enterprise"]
        }
        
        return controls
        
    def _create_content_instruction(self, item: Dict, user_profile: Dict, engagement_history: Dict) -> FrontendInstruction:
        """Create specific instruction for how to display content."""
        content_id = item.get("id")
        quality_score = item.get("quality_score", 0.0)
        content_type = item.get("type", "insight")
        
        user_tier = user_profile.get("tier", "free")
        view_count = engagement_history.get(content_id, {}).get("views", 0)
        
        # Determine content tier based on quality and user status
        if user_tier == "enterprise":
            tier = ContentTier.PREMIUM_EXCLUSIVE
            display_mode = "full"
        elif user_tier == "premium":
            tier = ContentTier.PAID_FULL if quality_score > 0.7 else ContentTier.PAID_PREVIEW
            display_mode = "full" if quality_score <= 0.8 else "full"
        elif user_tier == "basic":
            if quality_score > 0.8:
                tier = ContentTier.PAID_PREVIEW
                display_mode = "teaser"
            else:
                tier = ContentTier.FREE_FULL
                display_mode = "full"
        else:  # free user
            if quality_score > 0.7:
                tier = ContentTier.FREE_TEASER
                display_mode = "teaser"
            else:
                tier = ContentTier.FREE_FULL
                display_mode = "full" if view_count < 3 else "gated"
                
        # Determine engagement hooks
        engagement_hooks = ["view_time", "scroll_depth"]
        if tier in [ContentTier.FREE_TEASER, ContentTier.PAID_PREVIEW]:
            engagement_hooks.extend(["upgrade_click", "cta_interaction"])
            
        # Determine conversion trigger
        conversion_trigger = None
        if user_tier == "free" and quality_score > 0.8:
            conversion_trigger = "immediate"
        elif user_tier == "free" and view_count >= 2:
            conversion_trigger = "soft_prompt"
        elif user_tier == "basic" and quality_score > 0.9:
            conversion_trigger = "premium_upgrade"
            
        # Time gate for premium content
        time_gate = None
        if tier == ContentTier.FREE_TEASER and quality_score > 0.8:
            time_gate = 30  # 30 seconds before showing upgrade prompt
            
        return FrontendInstruction(
            content_id=content_id,
            tier=tier,
            display_mode=display_mode,
            engagement_hooks=engagement_hooks,
            conversion_trigger=conversion_trigger,
            time_gate=time_gate,
            next_action=self._determine_next_action(tier, user_tier, view_count)
        )
        
    def _determine_next_action(self, content_tier: ContentTier, user_tier: str, view_count: int) -> Optional[str]:
        """Determine what action frontend should prompt next."""
        if user_tier == "free":
            if content_tier in [ContentTier.FREE_TEASER, ContentTier.PAID_PREVIEW]:
                return "prompt_upgrade"
            elif view_count >= 3:
                return "registration_wall"
        elif user_tier == "basic":
            if content_tier == ContentTier.PREMIUM_EXCLUSIVE:
                return "premium_upgrade"
                
        return "continue_browsing"
        
    def _create_engagement_tracking(self, user_profile: Dict) -> Dict:
        """Create engagement tracking requirements for frontend."""
        user_tier = user_profile.get("tier", "free")
        
        tracking = {
            "required_events": ["page_view", "content_view", "scroll_depth"],
            "conversion_events": ["upgrade_click", "registration_start", "payment_start"],
            "feedback_loop": True,
            "real_time_sync": user_tier in ["premium", "enterprise"]
        }
        
        # Add specific tracking for free users to optimize conversion
        if user_tier == "free":
            tracking["required_events"].extend([
                "teaser_engagement",
                "upgrade_prompt_view", 
                "upgrade_prompt_dismiss",
                "content_frustration"  # When user tries to access gated content
            ])
            
        return tracking
        
    def _create_conversion_strategy(self, user_profile: Dict, engagement_history: Dict) -> Dict:
        """Create conversion strategy for this specific user."""
        user_tier = user_profile.get("tier", "free")
        total_visits = len(engagement_history)
        
        strategy = {
            "primary_goal": "retention" if user_tier != "free" else "conversion",
            "messaging": {},
            "timing": {},
            "incentives": {}
        }
        
        if user_tier == "free":
            if total_visits == 1:
                strategy["messaging"]["primary"] = "Discover competitive intelligence that matters"
                strategy["timing"]["first_prompt"] = 60  # seconds
                strategy["incentives"]["trial"] = "7_day_premium_trial"
            elif total_visits >= 3:
                strategy["messaging"]["primary"] = "You're clearly finding value - unlock everything"
                strategy["timing"]["aggressive"] = True
                strategy["incentives"]["discount"] = "20_percent_off_first_month"
        elif user_tier == "basic":
            strategy["messaging"]["primary"] = "Get deeper competitive insights with Premium"
            strategy["incentives"]["upgrade"] = "premium_features_trial"
            
        return strategy
        
    def send_to_frontend(self, payload: Dict) -> bool:
        """
        Send engagement-controlled payload to frontend.
        
        Args:
            payload: Frontend instructions and data
            
        Returns:
            Success flag
        """
        try:
            # In a real implementation, this would POST to frontend API
            endpoint = f"{self.frontend_url}/mcp/instructions"
            
            # For now, log the payload structure
            logger.info(f"📤 Sending MCP instructions to frontend:")
            logger.info(f"   User controls: {len(payload['user_controls'])} settings")
            logger.info(f"   Content instructions: {len(payload['content_instructions'])} items")
            logger.info(f"   Engagement tracking: {len(payload['engagement_tracking'])} events")
            logger.info(f"   Conversion strategy: {payload['conversion_strategy']['primary_goal']}")
            
            # Simulate API call
            # response = requests.post(endpoint, json=payload, timeout=5)
            # return response.status_code == 200
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send instructions to frontend: {e}")
            return False
            
    def process_frontend_feedback(self, feedback: Dict) -> Dict:
        """
        Process engagement feedback from frontend to improve strategy.
        
        Args:
            feedback: Engagement and conversion data from frontend
            
        Returns:
            Updated strategy recommendations
        """
        user_id = feedback.get("user_id")
        events = feedback.get("events", [])
        conversions = feedback.get("conversions", [])
        
        # Analyze engagement patterns
        engagement_analysis = self._analyze_engagement_patterns(events)
        
        # Update conversion rules based on what's working
        rule_updates = self._update_conversion_rules(engagement_analysis, conversions)
        
        # Generate strategy adjustments
        strategy_updates = {
            "user_id": user_id,
            "engagement_score": engagement_analysis["score"],
            "conversion_likelihood": engagement_analysis["conversion_likelihood"],
            "recommended_adjustments": rule_updates,
            "next_session_strategy": self._plan_next_session(engagement_analysis)
        }
        
        logger.info(f"📊 Processed frontend feedback for user {user_id}")
        logger.info(f"   Engagement score: {engagement_analysis['score']:.2f}")
        logger.info(f"   Conversion likelihood: {engagement_analysis['conversion_likelihood']:.2f}")
        
        return strategy_updates
        
    def _analyze_engagement_patterns(self, events: List[Dict]) -> Dict:
        """Analyze user engagement patterns from frontend events."""
        total_time = sum(event.get("duration", 0) for event in events)
        content_views = len([e for e in events if e.get("type") == "content_view"])
        upgrade_interactions = len([e for e in events if "upgrade" in e.get("type", "")])
        
        # Calculate engagement score
        engagement_score = min(1.0, (total_time / 300) * 0.4 + (content_views / 10) * 0.6)
        
        # Calculate conversion likelihood  
        conversion_likelihood = min(1.0, upgrade_interactions * 0.3 + engagement_score * 0.7)
        
        return {
            "score": engagement_score,
            "conversion_likelihood": conversion_likelihood,
            "total_time": total_time,
            "content_views": content_views,
            "upgrade_interactions": upgrade_interactions
        }
        
    def _update_conversion_rules(self, engagement_analysis: Dict, conversions: List[Dict]) -> Dict:
        """Update conversion rules based on what's working."""
        updates = {}
        
        # If high engagement but no conversion, adjust timing
        if engagement_analysis["score"] > 0.7 and engagement_analysis["conversion_likelihood"] < 0.3:
            updates["timing"] = "delay_prompts"
            
        # If quick conversions, be more aggressive
        if any(c.get("time_to_convert", 1000) < 60 for c in conversions):
            updates["strategy"] = "immediate_value_proposition"
            
        return updates
        
    def _plan_next_session(self, engagement_analysis: Dict) -> Dict:
        """Plan strategy for user's next session."""
        if engagement_analysis["conversion_likelihood"] > 0.7:
            return {
                "approach": "direct_conversion",
                "message": "personalized_value_prop",
                "timing": "immediate"
            }
        elif engagement_analysis["score"] > 0.5:
            return {
                "approach": "nurture_engagement", 
                "message": "educational_content",
                "timing": "gradual"
            }
        else:
            return {
                "approach": "re_engagement",
                "message": "hook_content",
                "timing": "attention_grabbing"
            }
            
    def create_teaser_content(self, full_insight: Dict, user_profile: Dict) -> Dict:
        """
        Create engaging teaser version of content based on user profile.
        
        Args:
            full_insight: Complete insight data
            user_profile: User subscription and engagement data
            
        Returns:
            Teaser version with engagement hooks
        """
        quality_score = full_insight.get("quality_score", 0.0)
        content_type = full_insight.get("type", "insight")
        domain = full_insight.get("domain", "")
        category = full_insight.get("category", "")
        
        # Determine teaser length based on quality
        if quality_score > 0.8:
            max_chars = self.conversion_rules["teaser_lengths"]["high_quality"]
        elif quality_score > 0.6:
            max_chars = self.conversion_rules["teaser_lengths"]["medium_quality"]
        else:
            max_chars = self.conversion_rules["teaser_lengths"]["low_quality"]
            
        # Create engaging hook
        hook_template = self.teaser_strategies["hooks"].get(content_type, "📊 New insight detected for {domain}...")
        hook = hook_template.format(domain=domain, category=category)
        
        # Truncate content strategically (at sentence boundary if possible)
        full_content = full_insight.get("content", "")
        if len(full_content) <= max_chars:
            teaser_content = full_content
        else:
            # Find last sentence boundary within limit
            truncated = full_content[:max_chars]
            last_sentence = truncated.rfind('.')
            if last_sentence > max_chars * 0.7:  # If we can keep most content
                teaser_content = full_content[:last_sentence + 1]
            else:
                teaser_content = truncated + "..."
                
        # Add call to action
        user_tier = user_profile.get("tier", "free")
        if user_tier == "free":
            cta = self.teaser_strategies["call_to_actions"]["register"]
        elif user_tier == "basic":
            cta = self.teaser_strategies["call_to_actions"]["premium"]
        else:
            cta = self.teaser_strategies["call_to_actions"]["upgrade"]
            
        return {
            "id": full_insight.get("id"),
            "hook": hook,
            "teaser_content": teaser_content,
            "call_to_action": cta,
            "unlock_trigger": "user_action",  # What unlocks full content
            "engagement_elements": ["hover_preview", "click_expand", "share_prompt"],
            "conversion_prompt": f"This is a {quality_score:.0%} quality insight. {cta}",
            "full_available": user_tier in ["premium", "enterprise"] or quality_score < 0.7
        }

# Global controller instance
mcp_frontend_controller = MCPFrontendController()

# Convenience functions for integration
def prepare_user_payload(user_profile: Dict, requested_data: Dict) -> Dict:
    """Prepare frontend payload for specific user."""
    return mcp_frontend_controller.prepare_frontend_payload(user_profile, requested_data)

def send_frontend_instructions(payload: Dict) -> bool:
    """Send instructions to frontend."""
    return mcp_frontend_controller.send_to_frontend(payload)

def process_engagement_feedback(feedback: Dict) -> Dict:
    """Process engagement feedback from frontend."""
    return mcp_frontend_controller.process_frontend_feedback(feedback)

def create_engaging_teaser(full_insight: Dict, user_profile: Dict) -> Dict:
    """Create engaging teaser for insight."""
    return mcp_frontend_controller.create_teaser_content(full_insight, user_profile)

if __name__ == "__main__":
    # Test the MCP Frontend Controller
    controller = MCPFrontendController()
    
    # Test user profiles
    free_user = {
        "user_id": "test_free",
        "tier": "free",
        "engagement_history": {}
    }
    
    premium_user = {
        "user_id": "test_premium", 
        "tier": "premium",
        "engagement_history": {"insight_123": {"views": 5}}
    }
    
    # Test data request
    requested_data = {
        "items": [
            {
                "id": "insight_123",
                "quality_score": 0.92,
                "type": "competitive_shift",
                "domain": "openai.com",
                "category": "ai",
                "content": "OpenAI is experiencing a significant trust surge in enterprise AI adoption..."
            }
        ]
    }
    
    # Test payload creation
    free_payload = controller.prepare_frontend_payload(free_user, requested_data)
    premium_payload = controller.prepare_frontend_payload(premium_user, requested_data)
    
    print("🎯 MCP Frontend Controller Test Results:")
    print(f"Free user payload: {len(free_payload['content_instructions'])} instructions")
    print(f"Premium user payload: {len(premium_payload['content_instructions'])} instructions")
    
    # Test teaser creation
    full_insight = requested_data["items"][0]
    teaser = controller.create_teaser_content(full_insight, free_user)
    print(f"Teaser created: {teaser['hook']}")
    print(f"CTA: {teaser['call_to_action']}")