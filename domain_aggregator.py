#!/usr/bin/env python3
"""
Domain Aggregator - Ruthlessly collects and summarizes competitive stories from expanded domain datasets

This script scans the expanded domain files, aggregates the competitive landscape data, and 
generates summaries for the admin console. It ensures all stories and metrics are properly
stored and displayed.
"""

import os
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
EXPANDED_DOMAINS_DIR = "data/expanded_domains"
SUMMARY_OUTPUT_DIR = "data/summaries"
STORIES_OUTPUT_DIR = "data/stories"

os.makedirs(SUMMARY_OUTPUT_DIR, exist_ok=True)
os.makedirs(STORIES_OUTPUT_DIR, exist_ok=True)

def load_sector_data() -> Dict[str, Any]:
    """Load all sector data from expanded domains directory."""
    sectors_data = {}
    
    for filename in os.listdir(EXPANDED_DOMAINS_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(EXPANDED_DOMAINS_DIR, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    sector_name = filename.replace(".json", "")
                    sectors_data[sector_name] = data
                    logger.info(f"Loaded sector data from {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
    
    return sectors_data

def count_domains(sectors_data: Dict[str, Any]) -> int:
    """Count total unique domains across all sectors."""
    all_domains = set()
    
    for sector_name, sector_data in sectors_data.items():
        for category_name, category_data in sector_data.items():
            for segment_name, segment_data in category_data.items():
                # Add domains from top players
                all_domains.update(segment_data.get("top_players", []))
                # Add domains from mid tier
                all_domains.update(segment_data.get("mid_tier", []))
                # Add domains from emerging disruptors
                all_domains.update(segment_data.get("emerging_disruptors", []))
    
    return len(all_domains)

def extract_all_stories(sectors_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all competitive stories across sectors."""
    all_stories = []
    
    for sector_name, sector_data in sectors_data.items():
        for category_name, category_data in sector_data.items():
            for segment_name, segment_data in category_data.items():
                stories = segment_data.get("competitive_stories", [])
                for story in stories:
                    story_with_context = story.copy()
                    story_with_context["sector"] = sector_name
                    story_with_context["category"] = category_name
                    story_with_context["segment"] = segment_name
                    # Add a unique ID based on title and context
                    story_id = f"{sector_name}_{category_name}_{segment_name}_{story['title']}".replace(" ", "_").lower()
                    story_with_context["id"] = story_id
                    # Add timestamp
                    story_with_context["updated_at"] = datetime.now().isoformat()
                    # Add metrics for ruthless tracking
                    story_with_context["engagement_score"] = 0
                    story_with_context["visibility_potential"] = calculate_visibility_potential(story["participants"])
                    story_with_context["competitive_intensity"] = len(story["participants"]) / 5  # Normalize to 0-1
                    
                    all_stories.append(story_with_context)
    
    return all_stories

def calculate_visibility_potential(domains: List[str]) -> float:
    """Calculate visibility potential based on domain prominence."""
    # In a real implementation, this would check actual visibility data
    # For now, use a simple heuristic based on domain name length
    # Shorter domain names tend to be more established/valuable
    avg_length = sum(len(domain) for domain in domains) / len(domains)
    # Invert and normalize to 0-1 scale (shorter = higher potential)
    potential = max(0, min(1, 1 - (avg_length - 5) / 15))
    return round(potential, 2)

def generate_summaries(sectors_data: Dict[str, Any], all_stories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for admin console."""
    total_domains = count_domains(sectors_data)
    total_sectors = len(sectors_data)
    
    # Count categories and segments
    categories_count = 0
    segments_count = 0
    for sector_data in sectors_data.values():
        categories_count += len(sector_data)
        for category_data in sector_data.values():
            segments_count += len(category_data)
    
    # Story statistics
    total_stories = len(all_stories)
    avg_participants_per_story = sum(len(story["participants"]) for story in all_stories) / max(1, total_stories)
    
    # Companies that appear in multiple stories (cross-sector influencers)
    company_appearances = {}
    for story in all_stories:
        for participant in story["participants"]:
            if participant in company_appearances:
                company_appearances[participant] += 1
            else:
                company_appearances[participant] = 1
    
    cross_sector_influencers = {
        domain: count for domain, count in company_appearances.items() 
        if count > 1
    }
    
    top_influencers = sorted(
        cross_sector_influencers.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    # Generate a high-level summary
    summary = {
        "total_domains": total_domains,
        "total_sectors": total_sectors,
        "total_categories": categories_count,
        "total_segments": segments_count,
        "total_stories": total_stories,
        "avg_participants_per_story": round(avg_participants_per_story, 2),
        "top_cross_sector_influencers": dict(top_influencers),
        "updated_at": datetime.now().isoformat(),
        "highest_potential_stories": get_highest_potential_stories(all_stories)
    }
    
    return summary

def get_highest_potential_stories(all_stories: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Get stories with highest visibility potential."""
    sorted_stories = sorted(
        all_stories,
        key=lambda x: x["visibility_potential"] * x["competitive_intensity"],
        reverse=True
    )
    
    return [
        {
            "id": story["id"],
            "title": story["title"],
            "sector": story["sector"],
            "category": story["category"],
            "segment": story["segment"],
            "participants": story["participants"],
            "visibility_potential": story["visibility_potential"],
            "competitive_intensity": story["competitive_intensity"]
        }
        for story in sorted_stories[:limit]
    ]

def save_results(summary: Dict[str, Any], all_stories: List[Dict[str, Any]]) -> None:
    """Save summary and stories to output files."""
    # Save summary
    summary_path = os.path.join(SUMMARY_OUTPUT_DIR, "domains_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved summary to {summary_path}")
    
    # Save all stories
    stories_path = os.path.join(STORIES_OUTPUT_DIR, "competitive_stories.json")
    with open(stories_path, 'w') as f:
        json.dump(all_stories, f, indent=2)
    logger.info(f"Saved stories to {stories_path}")
    
    # Save individual high-potential stories for quick access
    high_potential_stories = summary["highest_potential_stories"]
    for idx, story in enumerate(high_potential_stories):
        story_id = story["id"]
        story_path = os.path.join(STORIES_OUTPUT_DIR, f"high_potential_{idx+1}_{story_id}.json")
        with open(story_path, 'w') as f:
            json.dump(story, f, indent=2)

def print_ruthless_summary(summary: Dict[str, Any]) -> None:
    """Print ruthless summary to console."""
    print("\n" + "="*80)
    print("LLMPAGERANK COMPETITIVE DOMAIN INTELLIGENCE - RUTHLESS SUMMARY")
    print("="*80)
    print(f"Total Unique Domains: {summary['total_domains']}")
    print(f"Industry Sectors: {summary['total_sectors']}")
    print(f"Categories: {summary['total_categories']}")
    print(f"Market Segments: {summary['total_segments']}")
    print(f"Competitive Stories: {summary['total_stories']}")
    print(f"Average Competitors Per Story: {summary['avg_participants_per_story']}")
    
    print("\nTOP CROSS-SECTOR INFLUENCERS:")
    for domain, count in summary['top_cross_sector_influencers'].items():
        print(f"  {domain}: {count} competitive stories")
    
    print("\nHIGHEST POTENTIAL COMPETITIVE STORIES:")
    for idx, story in enumerate(summary['highest_potential_stories']):
        print(f"  {idx+1}. {story['title']} ({story['sector']}/{story['category']})")
        print(f"     Participants: {', '.join(story['participants'])}")
        print(f"     Visibility Potential: {story['visibility_potential']} | Competitive Intensity: {round(story['competitive_intensity'], 2)}")
    
    print("\nLast Updated: " + summary['updated_at'])
    print("="*80)
    print("DATA RUTHLESSLY AGGREGATED BY LLMPAGERANK COMPETITIVE INTELLIGENCE")
    print("="*80 + "\n")

def main():
    """Main function to run the domain aggregator."""
    logger.info("Starting domain aggregator")
    
    # Load sector data
    sectors_data = load_sector_data()
    
    # Extract all stories
    all_stories = extract_all_stories(sectors_data)
    
    # Generate summaries
    summary = generate_summaries(sectors_data, all_stories)
    
    # Save results
    save_results(summary, all_stories)
    
    # Print ruthless summary
    print_ruthless_summary(summary)
    
    logger.info("Domain aggregation complete")
    return summary

def render_admin_summary():
    """Render admin summary for Streamlit dashboard."""
    st.title("LLMPageRank Competitive Domain Intelligence")
    
    # Load summary if it exists
    summary_path = os.path.join(SUMMARY_OUTPUT_DIR, "domains_summary.json")
    if not os.path.exists(summary_path):
        summary = main()  # Generate if it doesn't exist
    else:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
    
    # Display top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Unique Domains", summary["total_domains"])
    col2.metric("Industry Sectors", summary["total_sectors"])
    col3.metric("Categories", summary["total_categories"]) 
    col4.metric("Competitive Stories", summary["total_stories"])
    
    # Display top influencers
    st.subheader("Cross-Sector Influence Leaders")
    influencers = summary["top_cross_sector_influencers"]
    influencer_data = [{"Domain": domain, "Competitive Stories": count} for domain, count in influencers.items()]
    st.dataframe(influencer_data)
    
    # Display high potential stories
    st.subheader("Highest Potential Competitive Stories")
    for story in summary["highest_potential_stories"]:
        with st.expander(f"{story['title']} ({story['sector']}/{story['category']})"):
            st.write(f"**Segment:** {story['segment']}")
            st.write(f"**Participants:** {', '.join(story['participants'])}")
            st.progress(story['visibility_potential'])
            st.caption(f"Visibility Potential: {story['visibility_potential']} | Competitive Intensity: {round(story['competitive_intensity'], 2)}")
    
    st.caption(f"Last Updated: {summary['updated_at']}")

if __name__ == "__main__":
    main()