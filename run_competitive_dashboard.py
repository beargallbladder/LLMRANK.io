"""
Competitive Memory Vulnerability Dashboard

This dashboard visualizes the memory vulnerability scores for competitive sectors,
showing which categories and brands are most at risk of being forgotten or misrepresented by LLMs.
It implements the loop-based monitoring approach to continuously track and update vulnerabilities.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import os

import competitive_sectors as cs

# Page configuration
st.set_page_config(
    page_title="Competitive Sectors Memory Dashboard",
    page_icon="🏆",
    layout="wide"
)

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
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        color: #4a5568;
    }
    .category-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a202c;
        margin-top: 1rem;
        margin-bottom: 1rem;
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
    .header-divider {
        height: 3px;
        background-color: #0066ff;
        margin-bottom: 2rem;
        width: 100px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the tracking data if not already done
if not os.path.exists(cs.CATEGORY_TRACKING_PATH):
    tracking_data = cs._initialize_tracking_data()
    with open(cs.CATEGORY_TRACKING_PATH, 'w') as f:
        json.dump(tracking_data, f, indent=2)

# Initialize session state for monitoring loop
if 'monitoring_loop_active' not in st.session_state:
    st.session_state.monitoring_loop_active = False
    
if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = datetime.now() - timedelta(hours=1)
    
if 'check_interval' not in st.session_state:
    st.session_state.check_interval = 30  # seconds, in real system would be much longer

# Header
st.markdown('<h1 class="title">Competitive Sectors Memory Vulnerability</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Loop-based monitoring of competitive categories at risk of memory drift</p>', unsafe_allow_html=True)
st.markdown('<div class="header-divider"></div>', unsafe_allow_html=True)

# Load data
competitive_categories = cs.load_competitive_categories()
vulnerability_factors = cs.load_vulnerability_factors()
high_risk_indicators = cs.load_high_risk_indicators()
tracking_data = cs.get_category_tracking_data()
check_cycle_stats = cs.get_check_cycle_stats()

# Check if we need to run a monitoring cycle (if active)
now = datetime.now()
if st.session_state.monitoring_loop_active:
    time_since_last_check = (now - st.session_state.last_check_time).total_seconds()
    if time_since_last_check >= st.session_state.check_interval:
        # Run check cycle
        cs.simulate_check_cycle()
        st.session_state.last_check_time = now
        
        # Reload data after check
        tracking_data = cs.get_category_tracking_data()
        check_cycle_stats = cs.get_check_cycle_stats()

# Top metrics
col1, col2, col3 = st.columns(3)

# Find highest risk category
highest_risk_categories = cs.get_highest_risk_categories(limit=1)
highest_risk_category = highest_risk_categories[0] if highest_risk_categories else {"name": "N/A", "memory_vulnerability": 0}

# Get all brands
all_brands = cs.get_brand_vulnerability_scores()
highest_risk_brand = all_brands[0] if all_brands else {"brand": "N/A", "vulnerability_score": 0}

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value high-risk">{highest_risk_category["memory_vulnerability"]:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Highest Category Risk Score</div>', unsafe_allow_html=True)
    st.markdown(f'<div>{highest_risk_category["name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value high-risk">{highest_risk_brand["vulnerability_score"]:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-label">Highest Brand Risk Score</div>', unsafe_allow_html=True)
    st.markdown(f'<div>{highest_risk_brand["brand"]} ({highest_risk_brand["category"]})</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Monitoring loop controls
    if st.session_state.monitoring_loop_active:
        status_color = "green"
        status_text = "Active"
    else:
        status_color = "red"
        status_text = "Inactive"
        
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {status_color}; margin-right: 10px;"></div>
        <div style="font-size: 1.2rem;">Monitoring Loop: <strong>{status_text}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Loop stats
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="font-size: 0.9rem; color: #4a5568;">Total checks: <strong>{check_cycle_stats.get('total_checks', 0)}</strong></div>
        <div style="font-size: 0.9rem; color: #4a5568;">Issues detected: <strong>{check_cycle_stats.get('total_issues_detected', 0)}</strong></div>
        <div style="font-size: 0.9rem; color: #4a5568;">Correction rate: <strong>{check_cycle_stats.get('correction_rate', 0):.2f}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    col3a, col3b = st.columns(2)
    with col3a:
        if st.button("▶️ Start Loop", key="start_loop", disabled=st.session_state.monitoring_loop_active):
            st.session_state.monitoring_loop_active = True
            st.rerun()
    
    with col3b:
        if st.button("⏹️ Stop Loop", key="stop_loop", disabled=not st.session_state.monitoring_loop_active):
            st.session_state.monitoring_loop_active = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Category Risk", "Brand Risk", "Monitoring Loop", "Risk Factors"])

# Category Risk tab
with tab1:
    st.subheader("Competitive Categories by Memory Vulnerability")
    
    # Create dataframe for category risk
    category_data = []
    for category in competitive_categories:
        # Get tracking metrics
        tracking_metrics = {}
        if category["name"] in tracking_data.get("categories", {}):
            tracking_metrics = tracking_data["categories"][category["name"]].get("tracking_metrics", {})
        
        category_data.append({
            "Category": category["name"],
            "Vulnerability Score": category.get("memory_vulnerability", 0),
            "Brands": ", ".join(category.get("brands", [])),
            "Key Attributes": ", ".join(category.get("key_attributes", [])),
            "Memory Miss Rate": tracking_metrics.get("memory_miss_rate", 0),
            "Hallucination Rate": tracking_metrics.get("hallucination_rate", 0),
            "Citation Rate": tracking_metrics.get("citation_rate", 0),
            "Accuracy Score": tracking_metrics.get("accuracy_score", 0)
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
    
    top5_categories = cs.get_highest_risk_categories(limit=5)
    
    # Display as cards
    cols = st.columns(5)
    for i, category in enumerate(top5_categories):
        with cols[i]:
            # Get tracking metrics
            tracking_metrics = {}
            if category["name"] in tracking_data.get("categories", {}):
                tracking_metrics = tracking_data["categories"][category["name"]].get("tracking_metrics", {})
            
            miss_rate = tracking_metrics.get("memory_miss_rate", 0)
            hallucination_rate = tracking_metrics.get("hallucination_rate", 0)
            
            # Card color based on vulnerability score
            card_bg_color = "rgba(229, 62, 62, 0.1)" if category["memory_vulnerability"] >= 0.8 else "rgba(237, 137, 54, 0.1)"
            
            st.markdown(f"""
            <div style="background-color: {card_bg_color}; padding: 15px; border-radius: 5px; height: 100%;">
                <h3 style="margin-top: 0; font-size: 1.1rem;">{category["name"]}</h3>
                <div style="font-size: 1.8rem; font-weight: bold; color: {'#e53e3e' if category['memory_vulnerability'] >= 0.8 else '#dd6b20'};">
                    {category["memory_vulnerability"]:.2f}
                </div>
                <div style="font-size: 0.8rem; margin-top: 10px;">
                    <div>Memory Miss: <strong>{miss_rate:.2f}</strong></div>
                    <div>Hallucination: <strong>{hallucination_rate:.2f}</strong></div>
                    <div>Brands: <strong>{len(category.get("brands", []))}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Category details
    st.subheader("Category Details")
    
    # Category selector
    selected_category_name = st.selectbox(
        "Select Category for Detailed Analysis",
        options=[category["name"] for category in competitive_categories]
    )
    
    # Get selected category
    selected_category = next((c for c in competitive_categories if c["name"] == selected_category_name), None)
    
    if selected_category:
        # Get tracking data for this category
        category_tracking = tracking_data.get("categories", {}).get(selected_category_name, {})
        tracking_metrics = category_tracking.get("tracking_metrics", {})
        check_history = category_tracking.get("check_history", [])
        
        col1, col2 = st.columns([2, 3])
        
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
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold;">Top Brands:</div>
                    <div>{", ".join(selected_category.get("brands", []))}</div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold;">Next Check Priority:</div>
                    <div>{category_tracking.get("next_check_priority", "medium").upper()}</div>
                </div>
                <div>
                    <div style="font-weight: bold;">Last Check:</div>
                    <div>{category_tracking.get("last_check", "Never")}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics descriptions
            metrics_descriptions = cs.get_metrics_descriptions()
            
            st.markdown("### Metrics Explained")
            
            for metric, description in metrics_descriptions.items():
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="font-weight: bold;">{metric.replace('_', ' ').title()}:</div>
                    <div style="font-size: 0.9rem;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Current metrics visualization
            st.markdown("### Current Tracking Metrics")
            
            # Create radar chart data
            radar_data = {
                "Metric": [
                    "Memory Miss Rate",
                    "Hallucination Rate",
                    "Citation Rate",
                    "Accuracy Score",
                    "Pickup Rate"
                ],
                "Value": [
                    tracking_metrics.get("memory_miss_rate", 0),
                    tracking_metrics.get("hallucination_rate", 0),
                    tracking_metrics.get("citation_rate", 0),
                    tracking_metrics.get("accuracy_score", 0),
                    tracking_metrics.get("pickup_rate", 0)
                ]
            }
            
            radar_df = pd.DataFrame(radar_data)
            
            fig = px.line_polar(
                radar_df, 
                r="Value", 
                theta="Metric", 
                line_close=True,
                range_r=[0, 1]
            )
            
            fig.update_traces(fill='toself')
            
            fig.update_layout(
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Check history
            if check_history:
                st.markdown("### Check History")
                
                # Create history dataframes
                history_dates = []
                memory_miss_values = []
                hallucination_values = []
                citation_values = []
                accuracy_values = []
                
                for check in check_history:
                    # Parse date from timestamp
                    check_date = check["timestamp"].split("T")[0]
                    
                    history_dates.append(check_date)
                    memory_miss_values.append(check["metrics"].get("memory_miss_rate", 0))
                    hallucination_values.append(check["metrics"].get("hallucination_rate", 0))
                    citation_values.append(check["metrics"].get("citation_rate", 0))
                    accuracy_values.append(check["metrics"].get("accuracy_score", 0))
                
                # Create dataframe
                history_df = pd.DataFrame({
                    "Date": history_dates,
                    "Memory Miss Rate": memory_miss_values,
                    "Hallucination Rate": hallucination_values,
                    "Citation Rate": citation_values,
                    "Accuracy Score": accuracy_values
                })
                
                # Create line chart
                fig = px.line(
                    history_df,
                    x="Date",
                    y=["Memory Miss Rate", "Hallucination Rate", "Citation Rate", "Accuracy Score"],
                    labels={"value": "Rate", "variable": "Metric"},
                    title="Metrics History"
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Rate",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)

# Brand Risk tab
with tab2:
    st.subheader("Top 20 Brands by Memory Vulnerability")
    
    # Get brand data
    brand_data = cs.get_brand_vulnerability_scores()
    
    # Convert to dataframe
    brand_df = pd.DataFrame([
        {
            "Brand": brand["brand"],
            "Category": brand["category"],
            "Vulnerability Score": brand["vulnerability_score"],
            "Memory Miss Rate": brand["metrics"].get("memory_miss_rate", 0) if "metrics" in brand else 0,
            "Citation Rate": brand["metrics"].get("citation_rate", 0) if "metrics" in brand else 0,
            "Hallucination Rate": brand["metrics"].get("hallucination_rate", 0) if "metrics" in brand else 0,
            "Accuracy Score": brand["metrics"].get("accuracy_score", 0) if "metrics" in brand else 0
        }
        for brand in brand_data
    ])
    
    # Top 20 brands
    top20_brands = brand_df.head(20)
    
    # Create bar chart
    fig = px.bar(
        top20_brands,
        x="Brand",
        y="Vulnerability Score",
        color="Category",
        hover_data=["Memory Miss Rate", "Hallucination Rate", "Citation Rate"],
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
            ),
            "Memory Miss Rate": st.column_config.ProgressColumn(
                "Memory Miss Rate",
                format="%.2f",
                min_value=0,
                max_value=1
            ),
            "Citation Rate": st.column_config.ProgressColumn(
                "Citation Rate",
                format="%.2f",
                min_value=0,
                max_value=1
            ),
            "Hallucination Rate": st.column_config.ProgressColumn(
                "Hallucination Rate",
                format="%.2f",
                min_value=0,
                max_value=1
            ),
            "Accuracy Score": st.column_config.ProgressColumn(
                "Accuracy Score",
                format="%.2f",
                min_value=0,
                max_value=1
            )
        }
    )
    
    # Brand detail
    st.subheader("Brand Detail")
    
    # Brand selector
    selected_brand = st.selectbox(
        "Select Brand for Detailed Analysis",
        options=sorted(brand_df["Brand"].unique())
    )
    
    # Get brand detail
    brand_detail = cs.get_brand_detail(selected_brand)
    
    if brand_detail:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Brand info
            category = brand_detail["category"]
            vulnerability_score = brand_detail["vulnerability_score"]
            metrics = brand_detail.get("metrics", {})
            
            # Find category details
            category_detail = next((c for c in competitive_categories if c["name"] == category), None)
            key_attributes = category_detail.get("key_attributes", []) if category_detail else []
            
            # Display brand card
            card_bg_color = "rgba(229, 62, 62, 0.1)" if vulnerability_score >= 0.8 else "rgba(237, 137, 54, 0.1)"
            
            st.markdown(f"""
            <div style="background-color: {card_bg_color}; padding: 20px; border-radius: 5px;">
                <h2 style="margin-top: 0;">{selected_brand}</h2>
                <div style="font-size: 1rem; color: #4a5568; margin-bottom: 15px;">Category: <strong>{category}</strong></div>
                <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 15px; color: {'#e53e3e' if vulnerability_score >= 0.8 else '#dd6b20'};">
                    {vulnerability_score:.2f}
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold;">Key Attributes:</div>
                    <div>{", ".join(key_attributes)}</div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold;">Key Metrics:</div>
                    <div>Memory Miss Rate: <strong>{metrics.get("memory_miss_rate", 0):.2f}</strong></div>
                    <div>Hallucination Rate: <strong>{metrics.get("hallucination_rate", 0):.2f}</strong></div>
                    <div>Citation Rate: <strong>{metrics.get("citation_rate", 0):.2f}</strong></div>
                    <div>Accuracy Score: <strong>{metrics.get("accuracy_score", 0):.2f}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Metrics visualization
            st.markdown("### Brand Memory Health Metrics")
            
            # Create gauge charts
            fig = go.Figure()
            
            # Memory miss gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics.get("memory_miss_rate", 0),
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
                        "value": 0.7
                    }
                },
                domain={"row": 0, "column": 0}
            ))
            
            # Hallucination gauge
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics.get("hallucination_rate", 0),
                title={"text": "Hallucination Rate"},
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
                domain={"row": 0, "column": 1}
            ))
            
            # Citation gauge (inverse - higher is better)
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics.get("citation_rate", 0),
                title={"text": "Citation Rate"},
                gauge={
                    "axis": {"range": [0, 1]},
                    "bar": {"color": "darkgreen"},
                    "steps": [
                        {"range": [0, 0.3], "color": "salmon"},
                        {"range": [0.3, 0.7], "color": "yellow"},
                        {"range": [0.7, 1], "color": "lightgreen"}
                    ],
                    "threshold": {
                        "line": {"color": "green", "width": 4},
                        "thickness": 0.75,
                        "value": 0.7
                    }
                },
                domain={"row": 1, "column": 0}
            ))
            
            # Accuracy gauge (inverse - higher is better)
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=metrics.get("accuracy_score", 0),
                title={"text": "Accuracy Score"},
                gauge={
                    "axis": {"range": [0, 1]},
                    "bar": {"color": "darkgreen"},
                    "steps": [
                        {"range": [0, 0.3], "color": "salmon"},
                        {"range": [0.3, 0.7], "color": "yellow"},
                        {"range": [0.7, 1], "color": "lightgreen"}
                    ],
                    "threshold": {
                        "line": {"color": "green", "width": 4},
                        "thickness": 0.75,
                        "value": 0.8
                    }
                },
                domain={"row": 1, "column": 1}
            ))
            
            fig.update_layout(
                grid={"rows": 2, "columns": 2, "pattern": "independent"},
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown("### Action Recommendations")
            
            # Generate recommendations based on metrics
            recommendations = []
            
            if metrics.get("memory_miss_rate", 0) > 0.4:
                recommendations.append("Strengthen memory signal with structured brand surface pages")
                
            if metrics.get("hallucination_rate", 0) > 0.3:
                recommendations.append("Create corrective brand facts schema to reduce hallucinations")
                
            if metrics.get("citation_rate", 0) < 0.6:
                recommendations.append("Enhance citation paths with authoritative structured data")
                
            if metrics.get("accuracy_score", 0) < 0.7:
                recommendations.append("Deploy fact verification Surface agents for this brand")
                
            if vulnerability_score > 0.8:
                recommendations.append("Prioritize for daily drift monitoring and correction")
                
            if not recommendations:
                recommendations.append("Maintain regular monitoring at current frequency")
            
            for i, recommendation in enumerate(recommendations):
                st.markdown(f"**{i+1}.** {recommendation}")

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
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### Monitoring Loop Status")
        
        # Simulate monitoring loop stats from check cycle stats
        full_scans = check_cycle_stats.get('total_checks', 0)
        focused_scans = full_scans * random.randint(3, 8)
        entities_discovered = random.randint(20, 60)
        risk_adjustments = check_cycle_stats.get('total_corrections_applied', 0)
        
        # Start/Stop buttons for monitoring (already have these in top card)
        # Using session state from the main controls
        
        # Status indicator
        status_color = "green" if st.session_state.monitoring_loop_active else "red"
        status_text = "Active" if st.session_state.monitoring_loop_active else "Inactive"
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {status_color}; margin-right: 10px;"></div>
            <div>Monitoring Status: <strong>{status_text}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Loop statistics
        st.markdown("""
        <div style="background-color: rgba(0, 100, 255, 0.1); padding: 15px; border-radius: 5px; margin-top: 15px;">
            <h4 style="margin-top: 0;">Monitoring Activity</h4>
            <table style="width: 100%;">
        """, unsafe_allow_html=True)
        
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
        
        # Check cycle interval settings
        st.markdown("### Monitoring Settings")
        
        # Adjust check interval with slider
        check_interval = st.slider(
            "Check Interval (seconds)",
            min_value=10,
            max_value=120,
            value=st.session_state.check_interval,
            step=10,
            help="How often to run the check cycle (in seconds). In a production system, this would be minutes or hours."
        )
        
        # Update session state if changed
        if check_interval != st.session_state.check_interval:
            st.session_state.check_interval = check_interval
        
        # Manual check button
        if st.button("Run Check Cycle Now"):
            cs.simulate_check_cycle()
            st.session_state.last_check_time = datetime.now()
            st.rerun()
    
    with col2:
        st.markdown("### Loop Visualization")
        
        # Create data for a mock monitoring timeline
        timeline_data = []
        current_time = datetime.now()
        
        # Create several days of activity
        for i in range(7):
            day_date = current_time - timedelta(days=6-i)
            # Full scans (1-2 per day)
            for _ in range(random.randint(1, 2)):
                scan_time = day_date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                )
                timeline_data.append({
                    "timestamp": scan_time,
                    "event_type": "Full Scan",
                    "details": f"Scanned all {len(competitive_categories)} categories"
                })
            
            # Focused scans (3-8 per day)
            for _ in range(random.randint(3, 8)):
                scan_time = day_date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                )
                category = random.choice(competitive_categories)["name"]
                timeline_data.append({
                    "timestamp": scan_time,
                    "event_type": "Focused Scan",
                    "details": f"Focused on {category}"
                })
            
            # Discoveries (0-3 per day)
            for _ in range(random.randint(0, 3)):
                scan_time = day_date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                )
                category = random.choice(competitive_categories)["name"]
                timeline_data.append({
                    "timestamp": scan_time,
                    "event_type": "Entity Discovery",
                    "details": f"New entity in {category}"
                })
            
            # Risk adjustments (1-4 per day)
            for _ in range(random.randint(1, 4)):
                scan_time = day_date.replace(
                    hour=random.randint(0, 23),
                    minute=random.randint(0, 59)
                )
                category = random.choice(competitive_categories)["name"]
                direction = random.choice(["increased", "decreased"])
                timeline_data.append({
                    "timestamp": scan_time,
                    "event_type": "Risk Adjustment",
                    "details": f"{category} risk {direction}"
                })
        
        # Sort by timestamp
        timeline_data.sort(key=lambda x: x["timestamp"])
        
        # Create dataframe
        timeline_df = pd.DataFrame(timeline_data)
        
        # Format timestamp
        timeline_df["formatted_time"] = timeline_df["timestamp"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
        
        # Add colors
        timeline_df["color"] = timeline_df["event_type"].apply(lambda x: 
            "#FF6347" if x == "Full Scan" else
            "#4682B4" if x == "Focused Scan" else
            "#32CD32" if x == "Entity Discovery" else
            "#FFD700"  # Risk Adjustment
        )
        
        # Create timeline visualization
        fig = px.scatter(
            timeline_df,
            x="formatted_time",
            y="event_type",
            color="event_type",
            hover_data=["details"],
            labels={"formatted_time": "Time", "event_type": "Activity Type"},
            title="7-Day Monitoring Activity Timeline"
        )
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Activity Type",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create coverage visualization
        st.markdown("### Coverage Expansion Over Time")
        
        # Create mock data for coverage expansion
        dates = []
        category_counts = []
        entity_counts = []
        
        # Start with base counts
        base_categories = 5
        base_entities = 25
        
        # Generate 30 days of expanding coverage
        for i in range(30):
            day_date = (current_time - timedelta(days=29-i)).strftime("%Y-%m-%d")
            dates.append(day_date)
            
            # Add categories and entities over time
            if i % 5 == 0:  # Every 5 days, add a new category
                base_categories += random.randint(0, 1)
            
            # Add entities each day
            base_entities += random.randint(0, 3)
            
            category_counts.append(base_categories)
            entity_counts.append(base_entities)
        
        # Create dataframe
        coverage_df = pd.DataFrame({
            "Date": dates,
            "Categories Monitored": category_counts,
            "Entities Tracked": entity_counts
        })
        
        # Create multi-line chart
        fig = px.line(
            coverage_df,
            x="Date",
            y=["Categories Monitored", "Entities Tracked"],
            labels={"value": "Count", "variable": "Metric"},
            title="Coverage Expansion Over 30 Days"
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Count",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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
    
    # Call to action
    st.markdown("""
    <div style="background-color: rgba(0, 102, 255, 0.1); padding: 20px; border-radius: 5px; margin-top: 30px; text-align: center;">
        <h3 style="margin-top: 0;">Ready to Activate Full Monitoring?</h3>
        <p>Click the Start Loop button to activate comprehensive memory vulnerability tracking across all competitive categories.</p>
    </div>
    """, unsafe_allow_html=True)

# Risk Factors tab
with tab4:
    st.subheader("Memory Vulnerability Risk Factors")
    
    # Display vulnerability factors
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Key Vulnerability Factors")
        
        for factor, description in vulnerability_factors.items():
            st.markdown(f"""
            <div style="margin-bottom: 20px;">
                <div style="font-weight: bold; font-size: 1.1rem; color: #e53e3e;">{factor.replace('_', ' ').title()}</div>
                <div>{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### High Risk Indicators")
        
        for indicator in high_risk_indicators:
            st.markdown(f"""
            <div style="background-color: rgba(229, 62, 62, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <div style="font-weight: bold;">{indicator}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Vulnerability matrix
    st.subheader("Category Vulnerability Matrix")
    
    # Create matrix data
    matrix_data = []
    
    for category in competitive_categories:
        # Get metrics for categories
        tracking_metrics = {}
        if category["name"] in tracking_data.get("categories", {}):
            tracking_metrics = tracking_data["categories"][category["name"]].get("tracking_metrics", {})
        
        # Create matrix entry
        matrix_data.append({
            "Category": category["name"],
            "Memory Vulnerability": category.get("memory_vulnerability", 0),
            "Brand Count": len(category.get("brands", [])),
            "Memory Miss Rate": tracking_metrics.get("memory_miss_rate", 0),
            "Hallucination Rate": tracking_metrics.get("hallucination_rate", 0)
        })
    
    # Create dataframe
    matrix_df = pd.DataFrame(matrix_data)
    
    # Create scatter plot
    fig = px.scatter(
        matrix_df,
        x="Memory Miss Rate",
        y="Hallucination Rate",
        size="Brand Count",
        color="Memory Vulnerability",
        color_continuous_scale="Reds",
        hover_name="Category",
        labels={
            "Memory Miss Rate": "Memory Miss Rate (higher = worse)",
            "Hallucination Rate": "Hallucination Rate (higher = worse)",
            "Memory Vulnerability": "Overall Vulnerability"
        },
        title="Memory Vulnerability Matrix"
    )
    
    fig.update_layout(
        xaxis_title="Memory Miss Rate",
        yaxis_title="Hallucination Rate",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add quadrant annotations
    st.markdown("""
    ### Vulnerability Quadrant Analysis
    
    <div style="display: flex; flex-wrap: wrap;">
        <div style="width: 50%; padding: 10px;">
            <div style="background-color: rgba(237, 137, 54, 0.1); padding: 15px; border-radius: 5px; height: 100%;">
                <h4 style="margin-top: 0;">High Miss / Low Hallucination</h4>
                <p>Categories in this quadrant are often overlooked by LLMs but when mentioned, information is generally accurate. The challenge is ensuring they're included in relevant responses.</p>
                <p><strong>Strategy:</strong> Increase visibility and citation paths</p>
            </div>
        </div>
        <div style="width: 50%; padding: 10px;">
            <div style="background-color: rgba(229, 62, 62, 0.1); padding: 15px; border-radius: 5px; height: 100%;">
                <h4 style="margin-top: 0;">High Miss / High Hallucination</h4>
                <p>The most vulnerable categories - they're both forgotten AND misrepresented when mentioned. Requires immediate and comprehensive intervention.</p>
                <p><strong>Strategy:</strong> Full Surface deployment with corrective schemas and continuous monitoring</p>
            </div>
        </div>
        <div style="width: 50%; padding: 10px;">
            <div style="background-color: rgba(56, 161, 105, 0.1); padding: 15px; border-radius: 5px; height: 100%;">
                <h4 style="margin-top: 0;">Low Miss / Low Hallucination</h4>
                <p>The healthiest categories - they're consistently remembered and accurately represented. Maintain current status with periodic monitoring.</p>
                <p><strong>Strategy:</strong> Maintain integrity with lower-frequency monitoring</p>
            </div>
        </div>
        <div style="width: 50%; padding: 10px;">
            <div style="background-color: rgba(66, 153, 225, 0.1); padding: 15px; border-radius: 5px; height: 100%;">
                <h4 style="margin-top: 0;">Low Miss / High Hallucination</h4>
                <p>Categories that are frequently mentioned but with inaccurate information. Focus on correcting rather than increasing visibility.</p>
                <p><strong>Strategy:</strong> Deploy fact correction surfaces and structured data</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Initialize monitoring if this is the first run
if not os.path.exists(cs.CATEGORY_TRACKING_PATH):
    cs.get_category_tracking_data()