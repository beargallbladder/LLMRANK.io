"""
Comprehensive Competitive Intelligence Data Schema
For tracking decay, drift, and competitive positioning over time
"""

from datetime import datetime
import json

def get_comprehensive_domain_schema():
    """
    Complete data schema for competitive intelligence tracking
    """
    return {
        # === CORE IDENTITY ===
        "domain": "microsoft.com",
        "display_name": "Microsoft",
        "industry": "Technology",
        "category": "Enterprise Software",
        "tier": "Fortune 100",
        
        # === TEMPORAL TRACKING ===
        "collection_timestamp": 1737573600,  # Unix timestamp
        "last_updated": "2025-05-22T16:00:00Z",
        "data_version": "v2.1",
        "collection_session_id": "blitz_20250522_001",
        
        # === COMPETITIVE POSITION PILLARS ===
        "competitive_metrics": {
            "overall_score": 0.87,
            "market_position": "leader",
            "visibility_rank": 2,
            "mention_frequency": 156,
            "authority_score": 0.92,
            "trust_signal": 0.88,
            "competitive_advantage": ["AI integration", "Enterprise reach", "Cloud dominance"]
        },
        
        # === DECAY/DRIFT TRACKING ===
        "drift_indicators": {
            "sentiment_drift": -0.02,  # Negative = declining sentiment
            "quality_drift": +0.05,   # Positive = improving quality
            "position_drift": 0.00,   # No change in competitive position
            "visibility_drift": -0.01, # Slight decline in visibility
            "decay_rate": 0.003,      # Rate of quality loss per day
            "stability_score": 0.94   # How stable the metrics are
        },
        
        # === MEMORY PERSISTENCE ===
        "memory_metrics": {
            "llm_recall_frequency": 0.78,     # How often LLMs mention this brand
            "context_persistence": 0.85,      # How well context is maintained
            "citation_strength": 0.72,        # How strongly cited in responses
            "prompt_responsiveness": 0.89,     # Response to direct prompts
            "indirect_mentions": 47,           # Mentions without direct prompting
            "memory_decay_rate": 0.002         # Rate of memory loss
        },
        
        # === CONTENT ANALYSIS ===
        "content_quality": {
            "depth_score": 0.84,
            "accuracy_score": 0.91,
            "relevance_score": 0.88,
            "uniqueness_score": 0.76,
            "engagement_potential": 0.82,
            "actionability_score": 0.79
        },
        
        # === COMPETITIVE INTELLIGENCE ===
        "competitive_analysis": {
            "top_competitors": ["Google", "Amazon", "Apple"],
            "competitive_gaps": ["Consumer hardware", "Mobile ecosystems"],
            "strengths": ["Enterprise software", "Cloud services", "AI tools"],
            "threats": ["Antitrust concerns", "Open source alternatives"],
            "opportunities": ["AI revolution", "Hybrid work trends"]
        },
        
        # === CITATION & AUTHORITY ===
        "authority_metrics": {
            "citation_count": 28,
            "authoritative_sources": ["TechCrunch", "Forbes", "WSJ"],
            "expert_mentions": 12,
            "academic_citations": 5,
            "news_coverage_score": 0.86,
            "thought_leadership_score": 0.81
        },
        
        # === ENGAGEMENT SIGNALS ===
        "engagement_data": {
            "user_click_rate": 0.067,
            "time_on_content": 145,  # seconds
            "share_rate": 0.034,
            "conversion_indicators": 0.028,
            "bounce_rate": 0.32,
            "engagement_trend": "stable"
        },
        
        # === VULNERABILITY TRACKING ===
        "vulnerability_indicators": {
            "reputation_risk": 0.15,
            "negative_sentiment_growth": 0.02,
            "competitor_gain_rate": 0.008,
            "market_share_pressure": 0.12,
            "regulatory_exposure": 0.25
        },
        
        # === HISTORICAL TRACKING ===
        "historical_snapshots": [
            {
                "timestamp": 1737487200,
                "overall_score": 0.85,
                "position_rank": 2,
                "sentiment": 0.82
            },
            {
                "timestamp": 1737573600,
                "overall_score": 0.87,
                "position_rank": 2,
                "sentiment": 0.80
            }
        ],
        
        # === MCP NEGOTIATION FIELDS ===
        "mcp_metadata": {
            "tier_classification": "premium",     # For content tiering
            "access_level": "full",              # Full vs limited data access
            "conversion_priority": "high",        # Conversion funnel priority
            "engagement_threshold": 0.75,         # Minimum engagement for display
            "data_freshness": "real_time",        # How fresh this data is
            "api_endpoints": ["insights", "trends", "competitors"]
        },
        
        # === SOURCE & VALIDATION ===
        "data_sources": {
            "primary_scrape": "https://microsoft.com",
            "news_sources": ["Reuters", "Bloomberg", "TechCrunch"],
            "social_signals": ["Twitter", "LinkedIn", "Reddit"],
            "analyst_reports": ["Gartner", "Forrester"],
            "llm_models_tested": ["GPT-4", "Claude", "Gemini"],
            "validation_score": 0.94
        },
        
        # === SYSTEM METADATA ===
        "system_metadata": {
            "agent_id": "blitz_agent_007",
            "collection_method": "continuous_blitz",
            "processing_time": 3.4,  # seconds
            "quality_validation": "passed",
            "brutal_enforcement": True,
            "version_control": "git_sha_abc123"
        }
    }

def validate_schema_completeness(domain_data):
    """
    Validate that domain data has all required competitive tracking pillars
    """
    required_pillars = [
        "competitive_metrics",
        "drift_indicators", 
        "memory_metrics",
        "authority_metrics",
        "vulnerability_indicators",
        "mcp_metadata"
    ]
    
    missing_pillars = []
    for pillar in required_pillars:
        if pillar not in domain_data:
            missing_pillars.append(pillar)
    
    return {
        "complete": len(missing_pillars) == 0,
        "missing_pillars": missing_pillars,
        "coverage_score": (len(required_pillars) - len(missing_pillars)) / len(required_pillars)
    }

def map_to_mcp_fields(domain_data):
    """
    Map comprehensive domain data to MCP client negotiation fields
    """
    return {
        # Core fields for MCP API
        "domain": domain_data["domain"],
        "score": domain_data["competitive_metrics"]["overall_score"],
        "tier": domain_data["mcp_metadata"]["tier_classification"],
        "access": domain_data["mcp_metadata"]["access_level"],
        
        # Engagement signals
        "engagement": domain_data["engagement_data"]["user_click_rate"],
        "conversion_priority": domain_data["mcp_metadata"]["conversion_priority"],
        
        # Competitive intelligence
        "position": domain_data["competitive_metrics"]["market_position"],
        "authority": domain_data["authority_metrics"]["citation_count"],
        "stability": domain_data["drift_indicators"]["stability_score"],
        
        # Memory persistence
        "recall": domain_data["memory_metrics"]["llm_recall_frequency"],
        "persistence": domain_data["memory_metrics"]["context_persistence"],
        
        # Risk indicators
        "vulnerability": domain_data["vulnerability_indicators"]["reputation_risk"],
        "decay_rate": domain_data["drift_indicators"]["decay_rate"]
    }

if __name__ == "__main__":
    # Example usage
    schema = get_comprehensive_domain_schema()
    print("📊 COMPREHENSIVE COMPETITIVE INTELLIGENCE SCHEMA")
    print("=" * 60)
    print(json.dumps(schema, indent=2)[:1000] + "...")
    
    validation = validate_schema_completeness(schema)
    print(f"\n✅ Schema Coverage: {validation['coverage_score']:.1%}")
    
    mcp_fields = map_to_mcp_fields(schema)
    print(f"\n🔗 MCP Negotiation Fields:")
    for key, value in mcp_fields.items():
        print(f"  {key}: {value}")