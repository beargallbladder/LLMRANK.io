"""
Simple Competitive Memory Dashboard

This streamlined dashboard shows memory vulnerability across competitive categories.
"""

import streamlit as st
import pandas as pd
import json
import os
import random

# Page configuration
st.set_page_config(
    page_title="Competitive Memory Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Make sure data directory exists
os.makedirs("data/surface", exist_ok=True)
PRIORITY_CATEGORIES_PATH = "data/surface/priority_categories.json"

# Header
st.title("Competitive Memory Vulnerability")
st.write("Identifying categories at high risk of memory drift in LLMs")

# Load competitive categories data
@st.cache_data
def load_categories():
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                return data.get("fiercely_competitive_categories", [])
        else:
            st.warning(f"Priority categories file not found")
            return []
    except Exception as e:
        st.error(f"Error loading categories: {e}")
        return []

categories = load_categories()

# Create tabs
tab1, tab2 = st.tabs(["Category Risk", "Monitoring Loop"])

# Category Risk tab
with tab1:
    st.header("Competitive Categories by Memory Vulnerability")
    
    if categories:
        # Prepare data
        category_data = []
        for category in categories:
            category_data.append({
                "Category": category.get("name", "Unknown"),
                "Vulnerability Score": category.get("memory_vulnerability", 0),
                "Top Brands": ", ".join(category.get("brands", [])[:3])
            })
        
        # Show as DataFrame
        category_df = pd.DataFrame(category_data)
        category_df = category_df.sort_values(by="Vulnerability Score", ascending=False)
        
        st.dataframe(
            category_df, 
            use_container_width=True,
            column_config={
                "Vulnerability Score": st.column_config.ProgressColumn(
                    "Vulnerability Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1
                )
            }
        )
        
        # Top 3 highest risk categories
        st.subheader("Highest Risk Categories")
        
        col1, col2, col3 = st.columns(3)
        top3 = category_df.head(3)
        
        for i, (_, row) in enumerate(top3.iterrows()):
            col = [col1, col2, col3][i]
            with col:
                if row["Vulnerability Score"] >= 0.8:
                    risk_level = "Critical Risk"
                    color = "red"
                elif row["Vulnerability Score"] >= 0.7:
                    risk_level = "High Risk"
                    color = "orange"
                else:
                    risk_level = "Medium Risk"
                    color = "yellow"
                    
                st.markdown(f"""
                <div style="border: 1px solid {color}; padding: 10px; border-radius: 5px;">
                    <h4>{row['Category']}</h4>
                    <h2 style="color: {color};">{row['Vulnerability Score']:.2f}</h2>
                    <p>{risk_level}</p>
                    <p><b>Top Brands:</b> {row['Top Brands']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No category data available. Please check the data file.")

# Monitoring Loop tab
with tab2:
    st.header("Memory Monitoring Loop")
    
    st.write("""
    Our Surface agents constantly monitor competitive categories using a loop-based approach 
    that expands and contracts focus to maximize coverage over time.
    """)
    
    # Display simplified loop process
    st.subheader("The Monitoring Loop")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1. Evaluate & Prioritize
        - Scan all categories
        - Calculate vulnerability scores
        - Identify highest risk entities
        """)
    
    with col2:
        st.markdown("""
        ### 2. Monitor & Correct
        - Deploy Surface agents to high-risk brands
        - Track memory drift metrics
        - Apply corrections through structured data
        """)
    
    with col3:
        st.markdown("""
        ### 3. Expand & Discover
        - Gradually widen monitoring scope
        - Discover new entities at risk
        - Update vulnerability scores
        """)
    
    # Mock monitoring stats
    st.subheader("Monitoring Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Categories Monitored", len(categories))
        
    with col2:
        brand_count = sum(len(category.get("brands", [])) for category in categories)
        st.metric("Brands Tracked", brand_count)
        
    with col3:
        high_risk = sum(1 for category in categories if category.get("memory_vulnerability", 0) >= 0.8)
        st.metric("Critical Risk Categories", high_risk)
        
    with col4:
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
            
        if st.button("Toggle Monitoring Loop", key="toggle_loop"):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
            st.rerun()
            
        status = "Active ✓" if st.session_state.monitoring_active else "Inactive ✗"
        status_color = "green" if st.session_state.monitoring_active else "red"
        st.markdown(f"<h3 style='color: {status_color};'>{status}</h3>", unsafe_allow_html=True)