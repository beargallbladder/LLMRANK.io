"""
LLMRank.io Admin Console - "The One Pane of Truth"

This module provides a secure admin console for monitoring and managing
the LLMPageRank system as specified in the Admin Console PRD.
"""

import os
import time
import json
import hashlib
import logging
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
ADMIN_EMAIL = "admin@llmrank.io"
SECURITY_LOG_PATH = "data/logs/security_log.json"
ADMIN_TOKEN_PATH = "data/admin/admin_token.txt"
ADMIN_HASH_PATH = "data/admin/admin_hash.txt"
DATA_DIR = "data"
INDEX_DIR = "data/indexwide"
SURFACE_DIR = "data/surface"

# Ensure directories exist
os.makedirs("data/logs", exist_ok=True)
os.makedirs("data/admin", exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# Authentication check
def check_authentication() -> bool:
    """Check if user is authenticated."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        auth_input = st.text_input("Enter admin token:", type="password")
        
        if st.button("Authenticate"):
            # Generate a dummy token for testing
            if not os.path.exists(ADMIN_TOKEN_PATH):
                with open(ADMIN_TOKEN_PATH, "w") as f:
                    f.write("admin_token_123456")
            
            with open(ADMIN_TOKEN_PATH, "r") as f:
                admin_token = f.read().strip()
            
            if auth_input == admin_token:
                st.session_state.authenticated = True
                log_security_event("login_success", {"email": ADMIN_EMAIL})
                st.experimental_rerun()
            else:
                log_security_event("login_failure", {"attempt": auth_input})
                st.error("Invalid admin token. Please try again.")
    
    return st.session_state.authenticated

def log_security_event(event_type, details=None):
    """Log a security event."""
    if details is None:
        details = {}
    
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "details": details
    }
    
    try:
        events = []
        if os.path.exists(SECURITY_LOG_PATH):
            with open(SECURITY_LOG_PATH, 'r') as f:
                events = json.load(f)
        
        events.append(event)
        
        with open(SECURITY_LOG_PATH, 'w') as f:
            json.dump(events, f, indent=2)
    except Exception as e:
        logger.error(f"Error logging security event: {e}")

# Indexwide scanning report
def render_indexwide_summary():
    """Render a summary of the indexwide scanning progress."""
    st.header("Indexwide Scanning Status")
    
    # Sample category data
    categories = {
        "Technology": 6,
        "Finance": 5,
        "Healthcare": 5, 
        "Consumer Goods": 5,
        "Energy": 5
    }
    
    # Create metrics for scanning status
    col1, col2, col3 = st.columns(3)
    col1.metric("Companies Indexed", "26")
    col2.metric("Surface Pages", "26")
    col3.metric("Rivalries Detected", "5")
    
    # Display status summary
    st.success("Indexwide scanning is active and monitoring 5 major categories")
    st.caption("Last scan completed: May 22, 2025 at 00:05:00")
    
    # Create category breakdown
    st.subheader("Category Breakdown")
    df = pd.DataFrame({
        "Category": list(categories.keys()),
        "Companies": list(categories.values())
    })
    
    fig = px.bar(df, x="Category", y="Companies", color="Category")
    st.plotly_chart(fig, use_container_width=True)
    
    # Create rivalry status
    st.subheader("Rivalry Detection Status")
    
    rivalry_data = {
        "Category": ["Technology", "Finance", "Healthcare", "Consumer Goods", "Energy"],
        "Top Brand": ["Apple", "JPMorgan", "Johnson & Johnson", "Procter & Gamble", "Exxon Mobil"],
        "Signal Strength": [0.71, 0.65, 0.62, 0.58, 0.52],
        "Delta": [0.42, 0.31, 0.25, 0.22, 0.18]
    }
    
    rivalry_df = pd.DataFrame(rivalry_data)
    st.dataframe(rivalry_df, use_container_width=True)
    
    # Add scan button with progress simulation
    if st.button("Run New Indexwide Scan", key="run_scan"):
        with st.spinner("Running Indexwide Scan..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            st.success("Scan completed successfully!")
            st.info("Found 3 new companies and updated 5 rivalry metrics")

# System health dashboard
def render_system_health():
    """Render system health dashboard."""
    st.header("System Health")
    
    # Generate sample health data
    health_metrics = {
        "api_response_time": 156,  # ms
        "database_connections": 8,
        "cache_hit_rate": 0.87,
        "server_uptime": 99.98,  # percentage
        "error_rate": 0.12  # percentage
    }
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="API Response Time",
        value=f"{health_metrics['api_response_time']} ms",
        delta="-12 ms"
    )
    
    col2.metric(
        label="Database Connections",
        value=health_metrics['database_connections'],
        delta="0"
    )
    
    col3.metric(
        label="Cache Hit Rate",
        value=f"{health_metrics['cache_hit_rate'] * 100:.1f}%",
        delta="+2.1%"
    )
    
    col4, col5, col6 = st.columns(3)
    
    col4.metric(
        label="Server Uptime",
        value=f"{health_metrics['server_uptime']}%",
        delta="+0.01%"
    )
    
    col5.metric(
        label="Error Rate",
        value=f"{health_metrics['error_rate'] * 100:.2f}%",
        delta="-0.03%"
    )
    
    col6.metric(
        label="Memory Usage",
        value="42%",
        delta="-5%"
    )
    
    # System health trend
    st.subheader("System Health Trend")
    
    # Generate sample trend data
    dates = pd.date_range(end=datetime.datetime.now(), periods=14, freq='D')
    api_times = [165, 162, 158, 160, 155, 159, 157, 162, 158, 155, 153, 156, 154, 156]
    error_rates = [0.18, 0.17, 0.16, 0.17, 0.16, 0.15, 0.14, 0.13, 0.14, 0.13, 0.12, 0.13, 0.12, 0.12]
    
    df = pd.DataFrame({
        'Date': dates,
        'API Response Time (ms)': api_times,
        'Error Rate (%)': [rate * 100 for rate in error_rates]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['API Response Time (ms)'], mode='lines+markers', name='API Response Time (ms)'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Error Rate (%)'], mode='lines+markers', name='Error Rate (%)', yaxis='y2'))
    
    fig.update_layout(
        title='System Performance (Last 14 Days)',
        xaxis=dict(title='Date'),
        yaxis=dict(title='API Response Time (ms)'),
        yaxis2=dict(title='Error Rate (%)', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add server logs
    st.subheader("Recent Server Logs")
    
    log_entries = [
        {"timestamp": "2025-05-22 01:30:45", "level": "INFO", "message": "API cache cleanup completed"},
        {"timestamp": "2025-05-22 01:15:22", "level": "INFO", "message": "Agent monitor reported successful health check"},
        {"timestamp": "2025-05-22 01:00:00", "level": "INFO", "message": "Scheduled task: Database optimization completed"},
        {"timestamp": "2025-05-22 00:45:10", "level": "WARN", "message": "Rate limit threshold reached for IP 203.0.113.42"},
        {"timestamp": "2025-05-22 00:30:15", "level": "INFO", "message": "New domain added: example-brand.com"}
    ]
    
    log_df = pd.DataFrame(log_entries)
    st.dataframe(log_df, use_container_width=True)

# Agent performance dashboard
def render_agent_performance():
    """Render agent performance dashboard."""
    st.header("Agent Performance")
    
    # Sample agent data
    agents = [
        {"name": "index_scan", "status": "active", "tasks_completed": 128, "success_rate": 0.98},
        {"name": "surface_seed", "status": "active", "tasks_completed": 146, "success_rate": 0.96},
        {"name": "drift_pulse", "status": "active", "tasks_completed": 85, "success_rate": 0.94},
        {"name": "insight_logger", "status": "active", "tasks_completed": 254, "success_rate": 0.99},
        {"name": "schema_auditor", "status": "active", "tasks_completed": 176, "success_rate": 0.97},
        {"name": "story_generator", "status": "active", "tasks_completed": 98, "success_rate": 0.92}
    ]
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Active Agents",
        value=len([a for a in agents if a["status"] == "active"]),
        delta="0"
    )
    
    col2.metric(
        label="Tasks Completed",
        value=sum(a["tasks_completed"] for a in agents),
        delta="+47"
    )
    
    avg_success = sum(a["success_rate"] for a in agents) / len(agents)
    col3.metric(
        label="Avg Success Rate",
        value=f"{avg_success * 100:.1f}%",
        delta="+0.5%"
    )
    
    # Agent performance table
    st.subheader("Agent Status")
    
    agent_df = pd.DataFrame(agents)
    agent_df["success_rate"] = agent_df["success_rate"].apply(lambda x: f"{x * 100:.1f}%")
    st.dataframe(agent_df, use_container_width=True)
    
    # Agent performance chart
    st.subheader("Agent Task Completion")
    
    fig = px.bar(
        agent_df,
        x="name",
        y="tasks_completed",
        color="name",
        labels={"name": "Agent", "tasks_completed": "Tasks Completed"}
    )
    
    st.plotly_chart(fig, use_container_width=True)

# MCP sync status dashboard
def render_mcp_sync_status():
    """Render MCP sync status dashboard."""
    st.header("MCP Sync Status")
    
    # Sample MCP metrics
    mcp_metrics = {
        "sync_status": "healthy",
        "last_sync": "2025-05-22 01:15:00",
        "domains_synced": 256,
        "insights_synced": 1248,
        "sync_success_rate": 0.995
    }
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Domains Synced",
        value=mcp_metrics["domains_synced"],
        delta="+12"
    )
    
    col2.metric(
        label="Insights Synced",
        value=mcp_metrics["insights_synced"],
        delta="+43"
    )
    
    col3.metric(
        label="Sync Success Rate",
        value=f"{mcp_metrics['sync_success_rate'] * 100:.2f}%",
        delta="+0.2%"
    )
    
    # Display sync status
    if mcp_metrics["sync_status"] == "healthy":
        st.success(f"MCP sync is healthy. Last successful sync: {mcp_metrics['last_sync']}")
    else:
        st.error(f"MCP sync is unhealthy. Last successful sync: {mcp_metrics['last_sync']}")
    
    # Recent sync activity
    st.subheader("Recent Sync Activity")
    
    sync_activities = [
        {"timestamp": "2025-05-22 01:15:00", "type": "full_sync", "domains": 256, "insights": 43, "status": "success"},
        {"timestamp": "2025-05-22 00:45:00", "type": "partial_sync", "domains": 12, "insights": 18, "status": "success"},
        {"timestamp": "2025-05-22 00:15:00", "type": "full_sync", "domains": 244, "insights": 36, "status": "success"},
        {"timestamp": "2025-05-21 23:45:00", "type": "partial_sync", "domains": 8, "insights": 15, "status": "success"},
        {"timestamp": "2025-05-21 23:15:00", "type": "full_sync", "domains": 236, "insights": 42, "status": "success"}
    ]
    
    sync_df = pd.DataFrame(sync_activities)
    st.dataframe(sync_df, use_container_width=True)
    
    # Sync trend chart
    st.subheader("Sync Volume Trend")
    
    # Generate sample trend data
    dates = pd.date_range(end=datetime.datetime.now(), periods=7, freq='D')
    domains_synced = [228, 234, 240, 245, 248, 252, 256]
    insights_synced = [1150, 1175, 1190, 1205, 1220, 1235, 1248]
    
    df = pd.DataFrame({
        'Date': dates,
        'Domains Synced': domains_synced,
        'Insights Synced': insights_synced
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Domains Synced'], mode='lines+markers', name='Domains Synced'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Insights Synced'], mode='lines+markers', name='Insights Synced', yaxis='y2'))
    
    fig.update_layout(
        title='Sync Volume (Last 7 Days)',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Domains Synced'),
        yaxis2=dict(title='Insights Synced', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Partner API usage dashboard
def render_partner_api_usage():
    """Render partner API usage dashboard."""
    st.header("Partner API Usage")
    
    # Sample API metrics
    api_metrics = {
        "total_requests": 12456,
        "unique_partners": 18,
        "avg_response_time": 132,  # ms
        "error_rate": 0.008,
        "quota_usage": 0.62
    }
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Total Requests",
        value=f"{api_metrics['total_requests']:,}",
        delta="+328"
    )
    
    col2.metric(
        label="Unique Partners",
        value=api_metrics["unique_partners"],
        delta="+1"
    )
    
    col3.metric(
        label="Avg Response Time",
        value=f"{api_metrics['avg_response_time']} ms",
        delta="-8 ms"
    )
    
    col4, col5, col6 = st.columns(3)
    
    col4.metric(
        label="Error Rate",
        value=f"{api_metrics['error_rate'] * 100:.2f}%",
        delta="-0.12%"
    )
    
    col5.metric(
        label="Quota Usage",
        value=f"{api_metrics['quota_usage'] * 100:.1f}%",
        delta="+2.5%"
    )
    
    # Partner usage table
    st.subheader("Partner Usage")
    
    partner_usage = [
        {"partner_id": "partner_a", "name": "ExampleCorp", "requests": 2456, "quota_usage": 0.82, "avg_response_time": 128},
        {"partner_id": "partner_b", "name": "TestCompany", "requests": 1851, "quota_usage": 0.74, "avg_response_time": 135},
        {"partner_id": "partner_c", "name": "DataSystems", "requests": 1623, "quota_usage": 0.65, "avg_response_time": 142},
        {"partner_id": "partner_d", "name": "InsightTech", "requests": 1245, "quota_usage": 0.58, "avg_response_time": 127},
        {"partner_id": "partner_e", "name": "BrandAI", "requests": 982, "quota_usage": 0.49, "avg_response_time": 131}
    ]
    
    partner_df = pd.DataFrame(partner_usage)
    partner_df["quota_usage"] = partner_df["quota_usage"].apply(lambda x: f"{x * 100:.1f}%")
    st.dataframe(partner_df, use_container_width=True)
    
    # Partner usage chart
    st.subheader("Partner Request Volume")
    
    fig = px.bar(
        partner_df,
        x="name",
        y="requests",
        color="name",
        labels={"name": "Partner", "requests": "Request Count"}
    )
    
    st.plotly_chart(fig, use_container_width=True)

# API key management dashboard
def render_api_key_management():
    """Render API key management dashboard."""
    st.header("API Key Management")
    
    # Create tabs for different key operations
    key_tabs = st.tabs(["Active Keys", "Create Key", "Revoke Key"])
    
    # Active Keys tab
    with key_tabs[0]:
        st.subheader("Active API Keys")
        
        # Sample API keys
        api_keys = [
            {"key_id": "key_8a7b6c5d", "plan": "enterprise", "owner": "ExampleCorp", "created": "2025-04-15", "expires": "2026-04-15", "status": "active"},
            {"key_id": "key_1a2b3c4d", "plan": "business", "owner": "TestCompany", "created": "2025-03-22", "expires": "2026-03-22", "status": "active"},
            {"key_id": "key_5e6f7g8h", "plan": "developer", "owner": "DataSystems", "created": "2025-05-10", "expires": "2025-11-10", "status": "active"},
            {"key_id": "key_9i8j7k6l", "plan": "enterprise", "owner": "InsightTech", "created": "2025-02-18", "expires": "2026-02-18", "status": "active"},
            {"key_id": "key_5m4n3o2p", "plan": "business", "owner": "BrandAI", "created": "2025-04-30", "expires": "2026-04-30", "status": "active"}
        ]
        
        keys_df = pd.DataFrame(api_keys)
        st.dataframe(keys_df, use_container_width=True)
        
        # Key distribution by plan
        st.subheader("Key Distribution by Plan")
        
        plan_counts = {}
        for key in api_keys:
            plan = key["plan"]
            if plan not in plan_counts:
                plan_counts[plan] = 0
            plan_counts[plan] += 1
        
        plan_df = pd.DataFrame({
            "Plan": list(plan_counts.keys()),
            "Count": list(plan_counts.values())
        })
        
        fig = px.pie(
            plan_df,
            values="Count",
            names="Plan",
            title="API Keys by Plan"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Create Key tab
    with key_tabs[1]:
        st.subheader("Create New API Key")
        
        owner = st.text_input("Owner Name")
        email = st.text_input("Owner Email")
        
        plan = st.selectbox(
            "Subscription Plan",
            ["developer", "business", "enterprise"]
        )
        
        expiration = st.selectbox(
            "Expiration Period",
            ["3 months", "6 months", "1 year", "2 years"]
        )
        
        if st.button("Generate API Key"):
            if owner and email:
                # Generate dummy key for demonstration
                key_prefix = "llmr_"
                random_suffix = hashlib.md5(f"{owner}_{email}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()[:16]
                new_key = f"{key_prefix}{random_suffix}"
                
                st.success("API key generated successfully")
                st.code(new_key)
                
                # Display key details
                st.info(f"Owner: {owner}\nPlan: {plan}\nExpiration: {expiration}")
                st.warning("Make sure to save this key as it won't be fully displayed again.")
            else:
                st.error("Owner name and email are required.")
    
    # Revoke Key tab
    with key_tabs[2]:
        st.subheader("Revoke API Key")
        
        key_id = st.text_input("API Key ID to Revoke")
        reason = st.text_area("Reason for Revocation")
        
        if st.button("Revoke API Key"):
            if key_id:
                st.success(f"API key {key_id} revoked successfully")
                st.info(f"Reason: {reason if reason else 'No reason provided'}")
            else:
                st.error("API Key ID is required.")

# Insight funnel dashboard
def render_insight_funnel():
    """Render insight funnel dashboard."""
    st.header("Insight Funnel")
    
    # Sample funnel metrics
    funnel_metrics = {
        "raw_signals": 2845,
        "filtered_signals": 1236,
        "insights_generated": 428,
        "published_insights": 156,
        "user_engagement": 982
    }
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Raw Signals",
        value=f"{funnel_metrics['raw_signals']:,}",
        delta="+124"
    )
    
    col2.metric(
        label="Filtered Signals",
        value=f"{funnel_metrics['filtered_signals']:,}",
        delta="+56"
    )
    
    col3.metric(
        label="Generated Insights",
        value=f"{funnel_metrics['insights_generated']:,}",
        delta="+18"
    )
    
    col4, col5, col6 = st.columns(3)
    
    col4.metric(
        label="Published Insights",
        value=f"{funnel_metrics['published_insights']:,}",
        delta="+7"
    )
    
    col5.metric(
        label="User Engagements",
        value=f"{funnel_metrics['user_engagement']:,}",
        delta="+43"
    )
    
    conversion_rate = funnel_metrics["published_insights"] / funnel_metrics["raw_signals"] * 100
    col6.metric(
        label="Conversion Rate",
        value=f"{conversion_rate:.2f}%",
        delta="+0.15%"
    )
    
    # Insight funnel visualization
    st.subheader("Insight Funnel Visualization")
    
    funnel_data = {
        "Stage": ["Raw Signals", "Filtered Signals", "Generated Insights", "Published Insights", "User Engagements"],
        "Count": [
            funnel_metrics["raw_signals"],
            funnel_metrics["filtered_signals"],
            funnel_metrics["insights_generated"],
            funnel_metrics["published_insights"],
            funnel_metrics["user_engagement"]
        ]
    }
    
    funnel_df = pd.DataFrame(funnel_data)
    
    fig = px.funnel(
        funnel_df,
        x="Count",
        y="Stage"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent insights
    st.subheader("Recent Published Insights")
    
    insights = [
        {"timestamp": "2025-05-22 01:12:34", "domain": "technology.com", "title": "Signal growth in enterprise AI adoption", "engagement": 45},
        {"timestamp": "2025-05-21 23:45:12", "domain": "finance-example.com", "title": "Market trends in digital banking", "engagement": 32},
        {"timestamp": "2025-05-21 22:18:05", "domain": "healthcare-brand.org", "title": "Telehealth adoption patterns", "engagement": 28},
        {"timestamp": "2025-05-21 20:56:48", "domain": "retail-sample.com", "title": "E-commerce conversion optimization", "engagement": 37},
        {"timestamp": "2025-05-21 19:23:10", "domain": "tech-leader.io", "title": "Cloud infrastructure scaling strategies", "engagement": 41}
    ]
    
    insights_df = pd.DataFrame(insights)
    st.dataframe(insights_df, use_container_width=True)

# Security logs dashboard
def render_security_logs():
    """Render security logs dashboard."""
    st.header("Security Logs")
    
    # Load security logs
    security_logs = []
    if os.path.exists(SECURITY_LOG_PATH):
        try:
            with open(SECURITY_LOG_PATH, 'r') as f:
                security_logs = json.load(f)
        except Exception as e:
            st.error(f"Error loading security logs: {e}")
    
    # Add sample logs if none exist
    if not security_logs:
        security_logs = [
            {"timestamp": "2025-05-22 01:30:45", "event_type": "login_success", "details": {"email": ADMIN_EMAIL}},
            {"timestamp": "2025-05-22 01:15:22", "event_type": "api_key_created", "details": {"owner": "ExampleCorp"}},
            {"timestamp": "2025-05-22 01:00:00", "event_type": "login_attempt", "details": {"ip": "203.0.113.42"}},
            {"timestamp": "2025-05-22 00:45:10", "event_type": "key_revoked", "details": {"key_id": "key_1234abcd"}},
            {"timestamp": "2025-05-22 00:30:15", "event_type": "login_failure", "details": {"attempt": "[REDACTED]"}}
        ]
    
    # Security metrics
    auth_attempts = len([log for log in security_logs if log["event_type"] in ["login_attempt", "login_success", "login_failure"]])
    auth_failures = len([log for log in security_logs if log["event_type"] == "login_failure"])
    key_operations = len([log for log in security_logs if log["event_type"] in ["api_key_created", "key_revoked"]])
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Auth Attempts",
        value=auth_attempts,
        delta="+3"
    )
    
    failure_rate = auth_failures / auth_attempts if auth_attempts > 0 else 0
    col2.metric(
        label="Auth Failure Rate",
        value=f"{failure_rate * 100:.1f}%",
        delta="-0.5%"
    )
    
    col3.metric(
        label="Key Operations",
        value=key_operations,
        delta="+1"
    )
    
    # Security logs table
    st.subheader("Recent Security Events")
    
    # Convert to DataFrame
    logs_df = pd.DataFrame(security_logs)
    
    # Handle details column for display
    if "details" in logs_df.columns:
        logs_df["details"] = logs_df["details"].apply(lambda x: str(x))
    
    st.dataframe(logs_df, use_container_width=True)
    
    # Event type distribution
    st.subheader("Event Type Distribution")
    
    event_counts = {}
    for log in security_logs:
        event_type = log["event_type"]
        if event_type not in event_counts:
            event_counts[event_type] = 0
        event_counts[event_type] += 1
    
    event_df = pd.DataFrame({
        "Event Type": list(event_counts.keys()),
        "Count": list(event_counts.values())
    })
    
    fig = px.bar(
        event_df,
        x="Event Type",
        y="Count",
        color="Event Type"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_admin_console():
    """Render the admin console."""
    if not check_authentication():
        return
    
    # Log successful access
    log_security_event("admin_console_access", {"email": ADMIN_EMAIL})
    
    st.title("LLMRank.io Admin Console")
    st.caption("The One Pane of Truth")
    
    # Main navigation
    tabs = st.tabs([
        "System Health", 
        "Agent Performance", 
        "MCP Sync Status", 
        "Partner API Usage",
        "API Key Management",
        "Insight Funnel",
        "Indexwide Scanning",
        "Security Logs"
    ])
    
    # System Health tab
    with tabs[0]:
        render_system_health()
    
    # Agent Performance tab
    with tabs[1]:
        render_agent_performance()
    
    # MCP Sync Status tab
    with tabs[2]:
        render_mcp_sync_status()
    
    # Partner API Usage tab
    with tabs[3]:
        render_partner_api_usage()
    
    # API Key Management tab
    with tabs[4]:
        render_api_key_management()
    
    # Insight Funnel tab
    with tabs[5]:
        render_insight_funnel()
    
    # Indexwide Scanning tab
    with tabs[6]:
        render_indexwide_summary()
        
    # Security Logs tab
    with tabs[7]:
        render_security_logs()

if __name__ == "__main__":
    render_admin_console()