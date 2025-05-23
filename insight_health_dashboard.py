"""
Insight Health Dashboard

This module provides a Streamlit dashboard to visualize the insight health
metrics and system status as specified in PRD21.
"""

import os
import json
import time
import logging
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Import from local modules
from insight_health_monitor import get_health_metrics, get_daily_digest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_insight_dashboard():
    """Render the insight health dashboard."""
    st.title("Insight Health Dashboard")
    st.subheader("Data & Insight First")
    
    try:
        # Get health metrics
        metrics = get_health_metrics()
        
        # Format last check time
        last_check = datetime.datetime.fromtimestamp(metrics.get("last_check", time.time()))
        st.caption(f"Last updated: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # System health overview
        st.header("System Health")
        render_system_health(metrics.get("system_health", {}))
        
        # Insight metrics
        st.header("Insight Metrics")
        render_insight_metrics(metrics.get("insight_metrics", {}))
        
        # Agent status
        st.header("Agent Status")
        render_agent_status(metrics.get("agents_status", {}))
        
        # Recent alerts
        st.header("Recent Alerts")
        render_alerts(metrics.get("recent_alerts", []))
        
        # Daily digest
        st.header("Daily Digest")
        render_daily_digest()
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")
        logger.error(f"Error rendering dashboard: {e}")

def render_system_health(system_health):
    """Render system health metrics."""
    cols = st.columns(len(system_health))
    
    for i, (component, data) in enumerate(system_health.items()):
        with cols[i]:
            status = data.get("status", "unknown")
            if status == "healthy":
                st.success(component)
            elif status == "warning":
                st.warning(component)
            elif status == "critical":
                st.error(component)
            else:
                st.info(component)
            
            last_heartbeat = data.get("last_heartbeat", 0)
            if last_heartbeat > 0:
                hb_time = datetime.datetime.fromtimestamp(last_heartbeat)
                st.caption(f"Last heartbeat: {hb_time.strftime('%H:%M:%S')}")
            else:
                st.caption("No heartbeat yet")

def render_insight_metrics(insight_metrics):
    """Render insight metrics."""
    # Create columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Insights", insight_metrics.get("total_insights", 0))
        
    with col2:
        st.metric("New Insights (24h)", insight_metrics.get("new_insights_24h", 0))
        
    with col3:
        if insight_metrics.get("stale_insights", False):
            st.warning("No new insights in 24h")
        else:
            st.success("Insights flowing")
    
    # Create metrics visualization
    metrics_data = {
        "Metric": ["Endpoint Diversity", "Payload Depth", "Partner Variability"],
        "Value": [
            insight_metrics.get("endpoint_diversity", 0),
            insight_metrics.get("payload_depth", 0) / 100,  # Normalize for display
            insight_metrics.get("partner_variability", 0)
        ]
    }
    
    df = pd.DataFrame(metrics_data)
    
    # Create a gauge chart for each metric
    for i, row in df.iterrows():
        metric_name = row["Metric"]
        value = min(1.0, row["Value"])  # Cap at 1.0 for gauge
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": metric_name},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 0.33], "color": "lightgray"},
                    {"range": [0.33, 0.67], "color": "gray"},
                    {"range": [0.67, 1], "color": "darkgray"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 0.5
                }
            }
        ))
        
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

def render_agent_status(agents_status):
    """Render agent status."""
    if not agents_status:
        st.info("No agent data available")
        return
    
    # Create DataFrame for agent status
    agent_data = []
    for name, status in agents_status.items():
        agent_data.append({
            "Agent": name,
            "Status": status.get("status", "unknown"),
            "Last Run": status.get("last_run", ""),
            "Last Success": status.get("last_success", ""),
            "Strata": status.get("strata", "unknown")
        })
    
    df = pd.DataFrame(agent_data)
    
    # Apply color highlighting based on status
    def highlight_status(val):
        if val == "active":
            return 'background-color: lightgreen'
        elif val == "inactive":
            return 'background-color: lightsalmon'
        return ''
    
    # Display DataFrame with highlighting
    st.dataframe(df.style.applymap(highlight_status, subset=['Status']))
    
    # Display agents by strata
    if "Strata" in df.columns:
        strata_counts = df["Strata"].value_counts().reset_index()
        strata_counts.columns = ["Strata", "Count"]
        
        fig = px.pie(strata_counts, values="Count", names="Strata", title="Agents by Strata")
        st.plotly_chart(fig, use_container_width=True)

def render_alerts(alerts):
    """Render recent alerts."""
    if not alerts:
        st.success("No recent alerts")
        return
    
    for alert in alerts:
        message = alert.get("message", "")
        level = alert.get("level", "info")
        date_str = alert.get("date", "")
        
        if level == "critical":
            st.error(message)
        elif level == "warning":
            st.warning(message)
        else:
            st.info(message)
        
        if date_str:
            st.caption(date_str)

def render_daily_digest():
    """Render daily digest."""
    try:
        digest = get_daily_digest()
        
        # Create columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Insight Quality")
            st.metric("Endpoint Diversity", digest.get("endpoint_diversity", 0))
            st.metric("Partner Variability", digest.get("partner_variability", 0))
            st.metric("New Insights", digest.get("new_insights_24h", 0))
        
        with col2:
            st.subheader("System Status")
            st.metric("Active Agents", digest.get("active_agents", 0))
            st.metric("Inactive Agents", digest.get("inactive_agents", 0))
            st.metric("Critical Alerts", digest.get("critical_alerts", 0))
            st.metric("Warning Alerts", digest.get("warning_alerts", 0))
        
        # Display system component status
        st.subheader("Component Status")
        system_status = digest.get("system_status", {})
        
        status_data = []
        for component, status in system_status.items():
            status_data.append({
                "Component": component,
                "Status": status
            })
        
        if status_data:
            status_df = pd.DataFrame(status_data)
            st.dataframe(status_df)
    except Exception as e:
        st.error(f"Error rendering daily digest: {e}")
        logger.error(f"Error rendering daily digest: {e}")

if __name__ == "__main__":
    render_insight_dashboard()