"""
Runtime Health Dashboard for LLMPageRank V10

This module implements the Runtime Health Dashboard for LLMPageRank V10,
visualizing system health, agent performance, and operational metrics.
"""

import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Constants
DATA_DIR = "data"
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_DIR = f"{DATA_DIR}/admin_insight_console"
AGENT_LOGS_DIR = "agents/logs"

def load_system_health():
    """Load system health data from file."""
    system_health_file = f"{ADMIN_INSIGHT_DIR}/system_health.json"
    
    try:
        if os.path.exists(system_health_file):
            with open(system_health_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading system health: {e}")
    
    # Return empty dict if file not found or error
    return {}

def load_agent_registry():
    """Load agent registry from file."""
    agent_registry_file = "agents/registry.json"
    
    try:
        if os.path.exists(agent_registry_file):
            with open(agent_registry_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading agent registry: {e}")
    
    # Return empty dict if file not found or error
    return {"agents": []}

def load_dispatcher_logs():
    """Load dispatcher logs from file."""
    dispatcher_log_file = f"{SYSTEM_FEEDBACK_DIR}/dispatcher_log.json"
    
    try:
        if os.path.exists(dispatcher_log_file):
            with open(dispatcher_log_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading dispatcher logs: {e}")
    
    # Return empty list if file not found or error
    return []

def load_integration_logs():
    """Load integration test logs from file."""
    integration_log_file = f"{SYSTEM_FEEDBACK_DIR}/integration_status_log.json"
    
    try:
        if os.path.exists(integration_log_file):
            with open(integration_log_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading integration logs: {e}")
    
    # Return empty list if file not found or error
    return []

def load_self_reports():
    """Load agent self-reports from file."""
    self_report_file = f"{SYSTEM_FEEDBACK_DIR}/agent_self_report.json"
    
    try:
        if os.path.exists(self_report_file):
            with open(self_report_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading self-reports: {e}")
    
    # Return empty list if file not found or error
    return []

def format_timestamp(timestamp):
    """Format timestamp for display."""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"

def create_health_gauge(value, title, min_val=0, max_val=100, threshold_good=80, threshold_warn=50):
    """Create a gauge chart for health metrics."""
    # Determine color based on thresholds
    if value >= threshold_good:
        color = "green"
    elif value >= threshold_warn:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, threshold_warn], 'color': 'rgba(255, 0, 0, 0.3)'},
                {'range': [threshold_warn, threshold_good], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [threshold_good, max_val], 'color': 'rgba(0, 128, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold_good
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_agent_status_chart(agents):
    """Create a pie chart showing agent status distribution."""
    # Count statuses
    status_counts = {"active": 0, "dormant": 0, "disabled": 0}
    
    for agent in agents:
        status = agent.get("status", "").lower()
        if status in status_counts:
            status_counts[status] += 1
    
    # Create dataframe
    df = pd.DataFrame({
        "Status": list(status_counts.keys()),
        "Count": list(status_counts.values())
    })
    
    # Create pie chart
    fig = px.pie(
        df, 
        values="Count", 
        names="Status", 
        color="Status",
        color_discrete_map={
            "active": "green",
            "dormant": "orange",
            "disabled": "red"
        },
        title="Agent Status Distribution"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_agent_strata_chart(agents):
    """Create a bar chart showing agent strata distribution."""
    # Count strata
    strata_counts = {"Gold": 0, "Silver": 0, "Rust": 0}
    
    for agent in agents:
        strata = agent.get("runtime_strata", "").title()
        if strata in strata_counts:
            strata_counts[strata] += 1
    
    # Create dataframe
    df = pd.DataFrame({
        "Strata": list(strata_counts.keys()),
        "Count": list(strata_counts.values())
    })
    
    # Create bar chart
    fig = px.bar(
        df, 
        x="Strata", 
        y="Count", 
        color="Strata",
        color_discrete_map={
            "Gold": "gold",
            "Silver": "silver",
            "Rust": "firebrick"
        },
        title="Agent Strata Distribution"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_cookie_distribution_chart(agents):
    """Create a bar chart showing cookie distribution among agents."""
    # Extract agent names and cookies
    agent_names = []
    cookies = []
    
    for agent in agents:
        agent_name = agent.get("agent_name", "Unknown")
        if len(agent_name) > 15:
            agent_name = agent_name[:12] + "..."
        
        agent_names.append(agent_name)
        cookies.append(agent.get("cookies_last_7d", 0))
    
    # Create dataframe
    df = pd.DataFrame({
        "Agent": agent_names,
        "Cookies": cookies
    })
    
    # Sort by cookies descending
    df = df.sort_values("Cookies", ascending=False)
    
    # Create bar chart
    fig = px.bar(
        df, 
        x="Agent", 
        y="Cookies", 
        color="Cookies",
        color_continuous_scale=["firebrick", "orange", "gold"],
        title="Cookie Distribution (Last 7 Days)"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-45
    )
    
    return fig

def create_integration_test_chart(logs):
    """Create a line chart showing integration test results over time."""
    # Extract timestamps and results
    timestamps = []
    pass_rates = []
    
    # Group logs by hour
    hour_results = {}
    
    for log in logs:
        timestamp = log.get("timestamp", 0)
        result = 1 if log.get("result", "") == "pass" else 0
        
        # Round to nearest hour
        hour = int(timestamp / 3600) * 3600
        
        if hour not in hour_results:
            hour_results[hour] = {"total": 0, "passes": 0}
        
        hour_results[hour]["total"] += 1
        hour_results[hour]["passes"] += result
    
    # Calculate pass rates
    for hour, results in sorted(hour_results.items()):
        if results["total"] > 0:
            pass_rate = (results["passes"] / results["total"]) * 100
        else:
            pass_rate = 0
        
        timestamps.append(datetime.fromtimestamp(hour))
        pass_rates.append(pass_rate)
    
    # Create dataframe
    df = pd.DataFrame({
        "Time": timestamps,
        "Pass Rate (%)": pass_rates
    })
    
    # Create line chart
    fig = px.line(
        df,
        x="Time",
        y="Pass Rate (%)",
        markers=True,
        title="Integration Test Pass Rate"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 105])
    )
    
    return fig

def create_dispatcher_events_chart(logs):
    """Create a bar chart showing dispatcher events over time."""
    # Extract events and counts
    events = {}
    
    for log in logs:
        event = log.get("event", "unknown")
        
        if event not in events:
            events[event] = 0
        
        events[event] += 1
    
    # Create dataframe
    df = pd.DataFrame({
        "Event": list(events.keys()),
        "Count": list(events.values())
    })
    
    # Create bar chart
    fig = px.bar(
        df,
        x="Event",
        y="Count",
        color="Event",
        title="Dispatcher Events"
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def render_runtime_health_dashboard():
    """Render the runtime health dashboard."""
    # Load data
    system_health = load_system_health()
    registry = load_agent_registry()
    dispatch_logs = load_dispatcher_logs()
    integration_logs = load_integration_logs()
    self_reports = load_self_reports()
    
    agents = registry.get("agents", [])
    
    # Page title
    st.title("LLMPageRank V10 Runtime Health Monitor")
    
    # System status overview
    st.markdown("## System Status Overview")
    st.markdown("Real-time health monitoring of the LLMPageRank V10 autonomous agent system")
    
    # Last updated timestamp
    last_updated = system_health.get("last_updated", 0)
    last_updated_str = format_timestamp(last_updated)
    
    # Calculate time since last update
    current_time = time.time()
    time_since_update = current_time - last_updated
    
    if time_since_update < 60:
        update_status = f"🟢 Updated {int(time_since_update)} seconds ago"
    elif time_since_update < 300:
        update_status = f"🟡 Updated {int(time_since_update / 60)} minutes ago"
    else:
        update_status = f"🔴 Last update was {int(time_since_update / 60)} minutes ago"
    
    st.markdown(f"**Status:** {update_status}")
    
    # Health gauges
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Dispatcher success rate gauge
        dispatcher_rate = system_health.get("dispatcher_success_rate", 0)
        st.plotly_chart(create_health_gauge(
            dispatcher_rate, 
            "Dispatcher Success Rate (%)"
        ), use_container_width=True)
    
    with col2:
        # Integration test pass rate gauge
        integration_rate = system_health.get("integration_test_pass_rate", 0)
        st.plotly_chart(create_health_gauge(
            integration_rate, 
            "Integration Test Pass Rate (%)"
        ), use_container_width=True)
    
    with col3:
        # Agent health rate gauge
        active_agents = system_health.get("active_agents", 0)
        total_agents = active_agents + system_health.get("dormant_agents", 0)
        
        if total_agents > 0:
            agent_health_rate = (active_agents / total_agents) * 100
        else:
            agent_health_rate = 0
        
        st.plotly_chart(create_health_gauge(
            agent_health_rate, 
            "Agent Health Rate (%)"
        ), use_container_width=True)
    
    # Agent status and performance
    st.markdown("## Agent Status and Performance")
    st.markdown("Current status and performance metrics for all system agents")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Agent status pie chart
        st.plotly_chart(create_agent_status_chart(agents), use_container_width=True)
    
    with col2:
        # Agent strata bar chart
        st.plotly_chart(create_agent_strata_chart(agents), use_container_width=True)
    
    # Cookie distribution
    st.plotly_chart(create_cookie_distribution_chart(agents), use_container_width=True)
    
    # System metrics over time
    st.markdown("## System Metrics Over Time")
    st.markdown("Trends in system performance and health over time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Integration test chart
        st.plotly_chart(create_integration_test_chart(integration_logs), use_container_width=True)
    
    with col2:
        # Dispatcher events chart
        st.plotly_chart(create_dispatcher_events_chart(dispatch_logs), use_container_width=True)
    
    # Agent details
    st.markdown("## Agent Details")
    
    # Convert agents to DataFrame for display
    agent_data = []
    
    for agent in agents:
        last_run = agent.get("last_run", "")
        # Try to parse ISO format
        try:
            if last_run:
                last_run_dt = datetime.fromisoformat(last_run.rstrip("Z"))
                last_run_str = last_run_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_run_str = "Never"
        except:
            last_run_str = last_run
        
        agent_data.append({
            "Agent": agent.get("agent_name", "Unknown"),
            "Status": agent.get("status", "Unknown"),
            "Strata": agent.get("runtime_strata", "Unknown"),
            "Cookies (7d)": agent.get("cookies_last_7d", 0),
            "Last Run": last_run_str
        })
    
    # Create DataFrame
    agent_df = pd.DataFrame(agent_data)
    
    # Display agent table
    st.dataframe(agent_df)
    
    # Self-reports section
    if self_reports:
        st.markdown("## Agent Self-Reports")
        st.markdown("Latest self-assessment reports from system agents")
        
        # Convert self-reports to DataFrame
        report_data = []
        
        for report in self_reports:
            report_data.append({
                "Agent": report.get("agent", "Unknown"),
                "Cycle": report.get("cycle", "Unknown"),
                "Cookies Awarded": report.get("cookies_awarded", 0),
                "Clarity Average": report.get("clarity_avg", 0),
                "Impact Average": report.get("impact_avg", 0),
                "Status": report.get("status", "Unknown"),
                "Reset Plan": "Yes" if report.get("reset_plan_triggered", False) else "No"
            })
        
        # Create DataFrame
        report_df = pd.DataFrame(report_data)
        
        # Display report table
        st.dataframe(report_df)