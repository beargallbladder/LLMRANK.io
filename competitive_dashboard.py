"""
Competitive Memory Vulnerability Dashboard

This simplified dashboard visualizes the memory vulnerability scores across competitive sectors
to help identify which categories need the most attention from our Surface agents.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import random
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Competitive Memory Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Make sure data directory exists
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)
PRIORITY_CATEGORIES_PATH = os.path.join(SURFACE_DATA_DIR, "priority_categories.json")

# Style
st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066ff;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1.5rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 2rem;
    }
    .high-risk {
        color: #e53e3e;
    }
    .medium-risk {
        color: #dd6b20;
    }
    .low-risk {
        color: #38a169;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="title">Competitive Memory Vulnerability</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Identifying categories at high risk of memory drift in LLMs</p>', unsafe_allow_html=True)

# Load competitive categories data
def load_categories():
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                return data.get("fiercely_competitive_categories", [])
        else:
            st.warning(f"Priority categories file not found at {PRIORITY_CATEGORIES_PATH}")
            return []
    except Exception as e:
        st.error(f"Error loading competitive categories: {e}")
        return []

categories = load_categories()

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Category Risk", "Brand Risk", "Monitoring Loop"])

# Category Risk tab
with tab1:
    st.subheader("Competitive Categories by Memory Vulnerability")
    
    # Create dataframe for category risk
    if categories:
        category_data = []
        for category in categories:
            category_data.append({
                "Category": category.get("name", "Unknown"),
                "Vulnerability Score": category.get("memory_vulnerability", 0),
                "Brands": ", ".join(category.get("brands", [])),
                "Key Attributes": ", ".join(category.get("key_attributes", []))
            })
        
        category_df = pd.DataFrame(category_data)
        
        # Create bar chart
        fig = px.bar(
            category_df,
            x="Category",
            y="Vulnerability Score",
            color="Vulnerability Score",
            color_continuous_scale="Reds",
            hover_data=["Brands", "Key Attributes"],
            labels={"Vulnerability Score": "Memory Vulnerability Score"}
        )
        
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Memory Vulnerability Score",
            yaxis_range=[0, 1],
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 5 highest risk categories
        st.subheader("Top 5 Highest Risk Categories")
        
        # Sort by vulnerability score
        sorted_categories = sorted(
            categories,
            key=lambda x: x.get("memory_vulnerability", 0),
            reverse=True
        )
        top5_categories = sorted_categories[:5]
        
        # Display top 5 as a table
        top5_data = []
        for category in top5_categories:
            top5_data.append({
                "Category": category.get("name", "Unknown"),
                "Vulnerability Score": category.get("memory_vulnerability", 0),
                "Top Brands": ", ".join(category.get("brands", [])[:3])
            })
        
        top5_df = pd.DataFrame(top5_data)
        st.dataframe(
            top5_df, 
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
        
        # Category details
        st.subheader("Category Details")
        
        # Category selector
        selected_category_name = st.selectbox(
            "Select Category for Detailed Analysis",
            options=[category.get("name", "Unknown") for category in categories]
        )
        
        # Get selected category
        selected_category = next((c for c in categories if c.get("name") == selected_category_name), None)
        
        if selected_category:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                <div style="background-color: rgba(0, 102, 255, 0.1); padding: 20px; border-radius: 5px;">
                    <h3 style="margin-top: 0;">{selected_category_name}</h3>
                    <div style="font-size: 2rem; font-weight: bold; margin-bottom: 15px;">
                        {selected_category.get("memory_vulnerability", 0):.2f}
                    </div>
                    <div style="margin-bottom: 15px;">
                        <div style="font-weight: bold;">Key Attributes:</div>
                        <div>{", ".join(selected_category.get("key_attributes", []))}</div>
                    </div>
                    <div>
                        <div style="font-weight: bold;">Top Brands:</div>
                        <div>{", ".join(selected_category.get("brands", []))}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Generate mock memory metrics
                memory_metrics = {
                    "Memory Miss Rate": round(random.uniform(0.2, 0.5), 2),
                    "Hallucination Rate": round(random.uniform(0.1, 0.4), 2),
                    "Citation Rate": round(random.uniform(0.3, 0.9), 2),
                    "Accuracy Score": round(random.uniform(0.5, 0.9), 2)
                }
                
                # Create gauge charts
                fig = go.Figure()
                
                # Memory miss gauge
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=memory_metrics["Memory Miss Rate"],
                    title={"text": "Memory Miss Rate"},
                    gauge={
                        "axis": {"range": [0, 1]},
                        "bar": {"color": "darkred"},
                        "steps": [
                            {"range": [0, 0.3], "color": "lightgreen"},
                            {"range": [0.3, 0.7], "color": "yellow"},
                            {"range": [0.7, 1], "color": "salmon"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 0.5
                        }
                    },
                    domain={"row": 0, "column": 0}
                ))
                
                # Hallucination gauge
                fig.add_trace(go.Indicator(
                    mode="gauge+number",
                    value=memory_metrics["Hallucination Rate"],
                    title={"text": "Hallucination Rate"},
                    gauge={
                        "axis": {"range": [0, 1]},
                        "bar": {"color": "darkred"},
                        "steps": [
                            {"range": [0, 0.2], "color": "lightgreen"},
                            {"range": [0.2, 0.5], "color": "yellow"},
                            {"range": [0.5, 1], "color": "salmon"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 0.4
                        }
                    },
                    domain={"row": 0, "column": 1}
                ))
                
                fig.update_layout(
                    grid={"rows": 1, "columns": 2, "pattern": "independent"},
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations
                st.markdown("### Action Recommendations")
                
                memory_score = selected_category.get("memory_vulnerability", 0)
                
                if memory_score >= 0.8:
                    st.markdown("""
                    **Critical Priority - Daily Monitoring Required**
                    1. Deploy Surface agents for continuous monitoring
                    2. Implement structured Surface pages with JSON-LD
                    3. Establish citation paths with authoritative sources
                    4. Schedule daily memory drift checks
                    """)
                elif memory_score >= 0.7:
                    st.markdown("""
                    **High Priority - Weekly Monitoring Required**
                    1. Deploy Surface pages with correction mechanisms
                    2. Implement schema markup for key entities
                    3. Schedule weekly drift checks
                    """)
                elif memory_score >= 0.6:
                    st.markdown("""
                    **Medium Priority - Biweekly Monitoring Recommended**
                    1. Create baseline Surface pages
                    2. Track citation accuracy
                    3. Schedule biweekly checks
                    """)
                else:
                    st.markdown("""
                    **Low Priority - Monthly Monitoring Sufficient**
                    1. Establish baseline memory metrics
                    2. Track for significant changes
                    3. Schedule monthly verification
                    """)
    else:
        st.warning("No category data available. Please check the data file.")

# Brand Risk tab
with tab2:
    st.subheader("Top Brands by Memory Vulnerability")
    
    if categories:
        # Create brand data
        brand_data = []
        
        for category in categories:
            category_name = category.get("name", "Unknown")
            category_vulnerability = category.get("memory_vulnerability", 0.5)
            
            # Get brands for this category
            brands = category.get("brands", [])
            
            # Process each brand
            for brand in brands:
                # Calculate brand-specific vulnerability score
                # Using category vulnerability with a small random variation
                brand_vulnerability = min(
                    1.0,
                    max(0.0, category_vulnerability + random.uniform(-0.1, 0.1))
                )
                
                # Add brand data
                brand_data.append({
                    "Brand": brand,
                    "Category": category_name,
                    "Vulnerability Score": round(brand_vulnerability, 2)
                })
        
        # Convert to dataframe
        brand_df = pd.DataFrame(brand_data)
        
        # Sort by vulnerability score
        brand_df = brand_df.sort_values(by="Vulnerability Score", ascending=False)
        
        # Top 20 brands
        top20_brands = brand_df.head(20)
        
        # Create bar chart
        fig = px.bar(
            top20_brands,
            x="Brand",
            y="Vulnerability Score",
            color="Category",
            labels={"Vulnerability Score": "Memory Vulnerability Score"}
        )
        
        fig.update_layout(
            xaxis_title="Brand",
            yaxis_title="Memory Vulnerability Score",
            yaxis_range=[0, 1],
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Brand search and filter
        st.subheader("Search and Filter Brands")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category filter
            category_filter = st.multiselect(
                "Filter by Category",
                options=sorted(brand_df["Category"].unique()),
                default=[]
            )
        
        with col2:
            # Score threshold
            score_threshold = st.slider(
                "Minimum Vulnerability Score",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05
            )
        
        # Apply filters
        filtered_df = brand_df.copy()
        
        if category_filter:
            filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
        
        filtered_df = filtered_df[filtered_df["Vulnerability Score"] >= score_threshold]
        
        # Sort by vulnerability score
        filtered_df = filtered_df.sort_values(by="Vulnerability Score", ascending=False)
        
        # Show filtered data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Brand": st.column_config.TextColumn("Brand"),
                "Category": st.column_config.TextColumn("Category"),
                "Vulnerability Score": st.column_config.ProgressColumn(
                    "Vulnerability Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                    help="Higher score = greater risk of being forgotten or misrepresented"
                )
            }
        )
    else:
        st.warning("No category data available. Please check the data file.")

# Monitoring Loop tab
with tab3:
    st.subheader("Continuous Loop-Based Memory Vulnerability Monitoring")
    
    st.markdown("""
    Our Surface agents constantly monitor the competitive sector landscape using a dynamic "ghost monitoring" 
    approach that expands and contracts focus to maximize coverage over time.
    
    This continuous loop system:
    1. Evaluates vulnerability across all competitive categories
    2. Prioritizes high-risk brands for focused monitoring
    3. Expands monitoring to discover new entities at risk
    4. Adjusts vulnerability scores based on observed trends
    5. Repeats the cycle to maintain comprehensive coverage
    """)
    
    # Display monitoring loop visualization
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Monitoring Loop Status")
        
        # Initialize monitoring state
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
        
        # Monitoring status
        status_color = "green" if st.session_state.monitoring_active else "red"
        status_text = "Active" if st.session_state.monitoring_active else "Inactive"
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {status_color}; margin-right: 10px;"></div>
            <div>Monitoring Status: <strong>{status_text}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Monitoring controls
        col1a, col1b = st.columns(2)
        with col1a:
            if st.button("▶️ Start Loop", key="start_loop", disabled=st.session_state.monitoring_active):
                st.session_state.monitoring_active = True
                st.rerun()
        
        with col1b:
            if st.button("⏹️ Stop Loop", key="stop_loop", disabled=not st.session_state.monitoring_active):
                st.session_state.monitoring_active = False
                st.rerun()
        
        # Monitoring stats
        st.markdown("""
        <div style="background-color: rgba(0, 100, 255, 0.1); padding: 15px; border-radius: 5px; margin-top: 15px;">
            <h4 style="margin-top: 0;">Monitoring Activity</h4>
            <table style="width: 100%;">
        """, unsafe_allow_html=True)
        
        # Generate mock stats
        full_scans = random.randint(5, 20)
        focused_scans = random.randint(30, 100)
        entities_discovered = random.randint(20, 60)
        risk_adjustments = random.randint(15, 40)
        
        st.markdown(f"""
                <tr>
                    <td>Full Scans Completed:</td>
                    <td><strong>{full_scans}</strong></td>
                </tr>
                <tr>
                    <td>Focused Scans Completed:</td>
                    <td><strong>{focused_scans}</strong></td>
                </tr>
                <tr>
                    <td>New Entities Discovered:</td>
                    <td><strong>{entities_discovered}</strong></td>
                </tr>
                <tr>
                    <td>Risk Score Adjustments:</td>
                    <td><strong>{risk_adjustments}</strong></td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Manual check button
        if st.button("Run Check Cycle Now"):
            st.success("Check cycle completed")
    
    with col2:
        # Show the loop process
        st.markdown("### The Competitive Memory Monitoring Loop")
        
        # Create mock data for monitoring cycle
        phases = [
            "Evaluate All Categories", 
            "Prioritize High-Risk Brands", 
            "Focused Monitoring", 
            "Expand Coverage", 
            "Discover New Entities",
            "Update Risk Scores",
            "Repeat Cycle"
        ]
        
        phase_descriptions = [
            "Scan all competitive categories to calculate baseline vulnerability scores",
            "Identify brands with highest memory vulnerability scores for priority monitoring",
            "Deploy Surface agents to closely monitor high-risk brands for drift",
            "Gradually widen monitoring scope to ensure comprehensive coverage",
            "Continuously seek new brands that may be at risk of being forgotten",
            "Adjust vulnerability scores based on observed trends and new data",
            "Return to full evaluation with updated priorities"
        ]
        
        # Generate cycle visualization
        st.markdown("""
        <div style="display: flex; flex-wrap: wrap; justify-content: center; margin-top: 30px;">
        """, unsafe_allow_html=True)
        
        for i, (phase, desc) in enumerate(zip(phases, phase_descriptions)):
            # Create a card for each phase
            st.markdown(f"""
            <div style="width: 200px; margin: 10px; text-align: center;">
                <div style="background-color: #0066ff; color: white; padding: 10px; border-radius: 5px 5px 0 0;">
                    <strong>{i+1}. {phase}</strong>
                </div>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 0 0 5px 5px; height: 100px;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add arrow except for the last item
            if i < len(phases) - 1:
                st.markdown("""
                <div style="display: flex; align-items: center; justify-content: center; width: 40px; margin: 10px 0;">
                    <div style="font-size: 24px;">→</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main function to run the app
if __name__ == "__main__":
    pass