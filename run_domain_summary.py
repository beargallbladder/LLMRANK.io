#!/usr/bin/env python3
"""
Run Domain Summary - Shows the competitive domain intelligence on the admin console

This script provides a Streamlit interface for the admin console to display
the ruthless competitive domain intelligence summaries.
"""

import streamlit as st
import json
import os
import pandas as pd
import time
import domain_aggregator as da

def main():
    """Main function to render the admin console for competitive domain intelligence."""
    st.set_page_config(
        page_title="LLMPageRank - Competitive Domain Intelligence",
        page_icon="📊",
        layout="wide"
    )
    
    # Add CSS to make it look more dashboard-like
    st.markdown("""
        <style>
        .main {
            background-color: #f5f7f9;
        }
        .stMetric {
            background-color: white;
            border-radius: 5px;
            padding: 15px 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .stMetric label {
            color: #555;
        }
        .stMetric [data-testid="stMetricValue"] {
            font-size: 24px;
            font-weight: bold;
            color: #192841;
        }
        h1, h2, h3 {
            color: #192841;
        }
        .story-card {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .story-title {
            font-weight: bold;
            color: #192841;
        }
        .story-sector {
            font-size: 14px;
            color: #555;
        }
        .story-participants {
            margin-top: 10px;
        }
        .participant-chip {
            background-color: #e1e8f0;
            padding: 3px 8px;
            border-radius: 12px;
            margin-right: 5px;
            font-size: 12px;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Competitive Domain Intelligence")
    st.subheader("Ruthlessly tracking visibility and competitive dynamics")
    
    # Add refresh button
    if st.button("Refresh Data"):
        with st.spinner("Aggregating domain intelligence..."):
            summary = da.main()
            st.success("Domain intelligence refreshed!")
            time.sleep(1)
    
    # Load summary if it exists
    summary_path = os.path.join("data/summaries", "domains_summary.json")
    if not os.path.exists(summary_path):
        summary = da.main()
    else:
        with open(summary_path, 'r') as f:
            summary = json.load(f)
    
    # Display top-level metrics in a dashboard style
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Unique Domains", summary["total_domains"])
    col2.metric("Industry Sectors", summary["total_sectors"])
    col3.metric("Categories", summary["total_categories"]) 
    col4.metric("Market Segments", summary["total_segments"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Competitive Stories", summary["total_stories"])
    with col2:
        st.metric("Avg Competitors Per Story", summary["avg_participants_per_story"])
    
    # Display top influencers as a bar chart
    st.subheader("Cross-Sector Influencers")
    influencers = summary["top_cross_sector_influencers"]
    influencer_df = pd.DataFrame({
        "Domain": list(influencers.keys()),
        "Stories": list(influencers.values())
    })
    influencer_df = influencer_df.sort_values("Stories", ascending=False)
    
    st.bar_chart(influencer_df.set_index("Domain"))
    
    # Display high potential stories in a grid layout
    st.subheader("Highest Potential Competitive Stories")
    story_cols = st.columns(2)
    
    for i, story in enumerate(summary["highest_potential_stories"]):
        col = story_cols[i % 2]
        with col:
            st.markdown(f"""
            <div class="story-card">
                <div class="story-title">{story['title']}</div>
                <div class="story-sector">{story['sector'].replace('_', ' ').title()} / {story['category'].replace('_', ' ').title()}</div>
                <div class="story-participants">
                    {''.join([f'<span class="participant-chip">{p}</span>' for p in story['participants']])}
                </div>
                <div style="margin-top: 10px;">
                    <div style="height: 5px; background-color: #e1e8f0; border-radius: 2px;">
                        <div style="height: 5px; width: {int(story['visibility_potential'] * 100)}%; background-color: #4CAF50; border-radius: 2px;"></div>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">
                        Visibility: {story['visibility_potential']} | Intensity: {round(story['competitive_intensity'], 2)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Display last updated timestamp
    st.caption(f"Last Updated: {summary['updated_at']}")
    
    # Add an explanation of what the dashboard shows
    with st.expander("About This Dashboard"):
        st.markdown("""
        ### Competitive Domain Intelligence Dashboard
        
        This dashboard provides a ruthless view of competitive dynamics across industries tracked by LLMPageRank:
        
        - **Unique Domains**: Total number of companies and organizations being tracked
        - **Industry Sectors**: Major industry classifications in our dataset
        - **Categories & Segments**: Hierarchical organization of the competitive landscape
        - **Cross-Sector Influencers**: Companies that appear in multiple competitive stories across different sectors
        - **Highest Potential Stories**: Competitive narratives with the highest visibility potential and competitive intensity
        
        The system identifies emerging competitive trends by analyzing visibility patterns, citation relationships, 
        and market dynamics across thousands of data points.
        """)

if __name__ == "__main__":
    main()