"""
Domain Growth Projector
Calculates when LLMPageRank will reach 10,000 domains based on current
engagement-driven agent performance and brutal quality enforcement.
"""

import os
import json
import datetime
import math
from typing import Dict, List, Tuple

def analyze_current_domain_data():
    """Analyze current domain performance to project growth."""
    
    # Count current domains
    results_dir = "data/results"
    current_domains = 0
    domain_performance = {}
    
    if os.path.exists(results_dir):
        domains = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
        current_domains = len(domains)
        
        # Analyze each domain's engagement potential
        for domain in domains:
            domain_path = os.path.join(results_dir, domain)
            result_files = [f for f in os.listdir(domain_path) if f.endswith('.json')]
            
            # Calculate domain quality score based on result frequency
            domain_performance[domain] = {
                "results_count": len(result_files),
                "last_updated": max([f.split('_')[1] + f.split('_')[2].replace('.json', '') 
                                   for f in result_files]) if result_files else "unknown",
                "engagement_potential": min(len(result_files) * 0.1, 1.0)  # Cap at 1.0
            }
    
    return current_domains, domain_performance

def calculate_growth_scenarios():
    """Calculate different growth scenarios based on agent performance."""
    
    current_domains, domain_performance = analyze_current_domain_data()
    target_domains = 10000
    domains_needed = target_domains - current_domains
    
    # Engagement-driven growth scenarios
    scenarios = {
        "brutal_quality": {
            "description": "High-quality engagement-driven growth",
            "daily_rate": 15,  # 15 high-quality domains per day
            "quality_filter": 0.85,  # 85% of domains survive brutal filter
            "agent_efficiency": 0.9,  # 90% agent efficiency with brutal enforcement
            "engagement_multiplier": 1.5  # Engagement warfare engine boost
        },
        "moderate_expansion": {
            "description": "Balanced growth with quality control",
            "daily_rate": 25,  # 25 domains per day
            "quality_filter": 0.7,  # 70% survive
            "agent_efficiency": 0.75,
            "engagement_multiplier": 1.2
        },
        "aggressive_scale": {
            "description": "Rapid expansion with engagement validation",
            "daily_rate": 50,  # 50 domains per day
            "quality_filter": 0.6,  # 60% survive brutal filter
            "agent_efficiency": 0.65,
            "engagement_multiplier": 1.0
        }
    }
    
    projections = {}
    
    for scenario_name, params in scenarios.items():
        # Calculate effective daily growth rate
        effective_daily_rate = (
            params["daily_rate"] * 
            params["quality_filter"] * 
            params["agent_efficiency"] * 
            params["engagement_multiplier"]
        )
        
        # Calculate days to reach target
        days_to_target = math.ceil(domains_needed / effective_daily_rate)
        
        # Calculate target date
        target_date = datetime.date.today() + datetime.timedelta(days=days_to_target)
        
        projections[scenario_name] = {
            **params,
            "effective_daily_rate": round(effective_daily_rate, 1),
            "days_to_target": days_to_target,
            "target_date": target_date.strftime("%Y-%m-%d"),
            "weeks_to_target": round(days_to_target / 7, 1),
            "months_to_target": round(days_to_target / 30, 1)
        }
    
    return current_domains, target_domains, projections

def analyze_engagement_impact():
    """Analyze how engagement warfare engine affects growth speed."""
    
    engagement_factors = {
        "click_rate_optimization": {
            "impact": "15% faster domain validation",
            "multiplier": 1.15
        },
        "retention_feedback_loop": {
            "impact": "20% better agent quality",
            "multiplier": 1.20
        },
        "real_time_pattern_detection": {
            "impact": "25% faster bad domain elimination", 
            "multiplier": 1.25
        },
        "brutal_agent_evolution": {
            "impact": "30% improvement in insight quality",
            "multiplier": 1.30
        }
    }
    
    # Calculate cumulative engagement warfare boost
    total_multiplier = 1.0
    for factor in engagement_factors.values():
        total_multiplier *= factor["multiplier"]
    
    return engagement_factors, total_multiplier

def generate_growth_report():
    """Generate comprehensive growth projection report."""
    
    current_domains, target_domains, projections = calculate_growth_scenarios()
    engagement_factors, engagement_boost = analyze_engagement_impact()
    
    report = {
        "current_status": {
            "current_domains": current_domains,
            "target_domains": target_domains,
            "domains_needed": target_domains - current_domains,
            "completion_percentage": round((current_domains / target_domains) * 100, 2)
        },
        "growth_projections": projections,
        "engagement_warfare_impact": {
            "factors": engagement_factors,
            "total_boost": round(engagement_boost, 2),
            "description": "Engagement Warfare Engine provides cumulative growth acceleration"
        },
        "recommended_strategy": None,
        "key_milestones": []
    }
    
    # Determine recommended strategy
    brutal_quality = projections["brutal_quality"]
    if brutal_quality["months_to_target"] <= 12:
        report["recommended_strategy"] = {
            "strategy": "brutal_quality",
            "reason": "Achieves 10K domains in under 12 months with highest quality",
            "timeline": f"{brutal_quality['months_to_target']} months",
            "date": brutal_quality["target_date"]
        }
    else:
        moderate = projections["moderate_expansion"]
        report["recommended_strategy"] = {
            "strategy": "moderate_expansion", 
            "reason": "Balanced approach for sustainable growth",
            "timeline": f"{moderate['months_to_target']} months",
            "date": moderate["target_date"]
        }
    
    # Generate key milestones
    recommended = report["recommended_strategy"]["strategy"]
    daily_rate = projections[recommended]["effective_daily_rate"]
    
    milestones = [1000, 2500, 5000, 7500, 10000]
    for milestone in milestones:
        if milestone > current_domains:
            domains_to_milestone = milestone - current_domains
            days_to_milestone = math.ceil(domains_to_milestone / daily_rate)
            milestone_date = datetime.date.today() + datetime.timedelta(days=days_to_milestone)
            
            report["key_milestones"].append({
                "domains": milestone,
                "days_from_now": days_to_milestone,
                "date": milestone_date.strftime("%Y-%m-%d"),
                "months_from_now": round(days_to_milestone / 30, 1)
            })
    
    return report

def print_growth_analysis():
    """Print formatted growth analysis."""
    
    report = generate_growth_report()
    
    print("🚀 DOMAIN GROWTH PROJECTION TO 10,000 DOMAINS 🚀")
    print("=" * 60)
    
    # Current status
    status = report["current_status"]
    print(f"\n📊 CURRENT STATUS:")
    print(f"   Current Domains: {status['current_domains']:,}")
    print(f"   Target Domains: {status['target_domains']:,}")
    print(f"   Domains Needed: {status['domains_needed']:,}")
    print(f"   Progress: {status['completion_percentage']}%")
    
    # Recommended strategy
    strategy = report["recommended_strategy"]
    print(f"\n🎯 RECOMMENDED STRATEGY: {strategy['strategy'].upper()}")
    print(f"   Timeline: {strategy['timeline']}")
    print(f"   Target Date: {strategy['date']}")
    print(f"   Reason: {strategy['reason']}")
    
    # Growth scenarios
    print(f"\n📈 GROWTH SCENARIOS:")
    for name, proj in report["growth_projections"].items():
        print(f"   {name.upper()}:")
        print(f"     • {proj['effective_daily_rate']} domains/day")
        print(f"     • {proj['months_to_target']} months to 10K")
        print(f"     • Target: {proj['target_date']}")
        print(f"     • {proj['description']}")
    
    # Engagement warfare impact
    print(f"\n⚔️ ENGAGEMENT WARFARE BOOST:")
    engagement = report["engagement_warfare_impact"]
    print(f"   Total Acceleration: {engagement['total_boost']}x")
    for factor_name, factor_data in engagement["factors"].items():
        print(f"     • {factor_name}: {factor_data['impact']}")
    
    # Key milestones
    print(f"\n🏁 KEY MILESTONES:")
    for milestone in report["key_milestones"]:
        print(f"   {milestone['domains']:,} domains: {milestone['date']} ({milestone['months_from_now']} months)")
    
    print("\n" + "=" * 60)
    print("💀 WITH BRUTAL AGENT QUALITY ENFORCEMENT ACTIVE 💀")
    print("🔥 ENGAGEMENT WARFARE ENGINE OPERATIONAL 🔥")

if __name__ == "__main__":
    print_growth_analysis()