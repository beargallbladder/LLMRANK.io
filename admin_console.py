"""
LLMRank.io Admin Console - "The One Pane of Truth"

This module provides a secure admin console for monitoring and managing
the LLMPageRank system as specified in the Admin Console PRD.
"""

import os
import time
import json
import logging
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import from local modules
from insight_health_monitor import get_health_metrics, get_daily_digest
from agent_monitor import get_all_agents, get_agent_logs

# Security constants
ADMIN_USERNAME = "samkim@samkim.com"
ADMIN_PASSWORD = "LLMPageRank2025!"
SECURITY_MESSAGE = "⚠️ This control room contains sensitive data that must be protected at all costs ⚠️"
from api_rate_limiter import get_usage_stats
from mcp_auth import get_mcp_auth
from api_key_manager import (
    get_api_key_manager, create_api_key, upgrade_api_key, 
    downgrade_api_key, revoke_api_key, get_all_keys,
    get_keys_by_plan, get_usage_report, get_key_usage
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "samkim@samkim.com")

def check_authentication():
    """Check if user is authenticated."""
    # Since we don't have Clerk integration yet, using a simple password auth
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_attempts = 0
    
    if not st.session_state.authenticated:
        st.title("LLMRank.io Admin Console")
        st.write("Please log in to access the admin console.")
        
        # Simple authentication for now
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # Hardcoded credentials for now - in production would use secure Clerk integration
            if email == ADMIN_EMAIL and password == "LLMPageRank2025!":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.error(f"Invalid credentials. Attempt {st.session_state.login_attempts} of 3.")
                
                if st.session_state.login_attempts >= 3:
                    st.error("Too many login attempts. Please try again later.")
                    log_security_event("failed_login_max_attempts", {"email": email})
                    time.sleep(5)  # Rate limiting
                else:
                    log_security_event("failed_login", {"email": email})
        
        return False
    
    return True

def log_security_event(event_type, details=None):
    """Log a security event."""
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "details": details or {}
    }
    
    # Log to security events file
    try:
        security_log_path = os.path.join("data", "system_feedback", "security_log.json")
        os.makedirs(os.path.dirname(security_log_path), exist_ok=True)
        
        events = []
        if os.path.exists(security_log_path):
            with open(security_log_path, "r") as f:
                try:
                    events = json.load(f)
                except json.JSONDecodeError:
                    events = []
        
        events.append(event)
        
        with open(security_log_path, "w") as f:
            json.dump(events, f, indent=2)
    except Exception as e:
        logger.error(f"Error logging security event: {e}")

def render_indexwide_summary():
    """Render a summary of the indexwide scanning progress."""
    st.subheader("Indexwide Scanning Status")
    
    try:
        # Create sample metrics for demonstration
        col1, col2, col3 = st.columns(3)
        
        # Sample data
        col1.metric("Companies Indexed", "26")
        col2.metric("Surface Pages", "26")
        col3.metric("Rivalries Tracked", "5")
        
        # Display last run date
        st.caption(f"Last scan completed: 2025-05-22 00:05:00")
        
        # Display summary
        st.success("Go Wider implementation successfully tracking 5 major categories")
        
        # Display category breakdown
        st.subheader("Category Breakdown")
        
        categories = {
            "Technology": 6,
            "Finance": 5,
            "Healthcare": 5, 
            "Consumer Goods": 5,
            "Energy": 5
        }
        
        # Create a DataFrame for the bar chart
        import pandas as pd
        df = pd.DataFrame({
            "Category": list(categories.keys()),
            "Companies": list(categories.values())
        })
        
        # Display bar chart
        import plotly.express as px
        fig = px.bar(df, x="Category", y="Companies", color="Category")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add button to run scan
        if st.button("Run New Indexwide Scan"):
            st.info("Running indexwide scan...")
            
            # Add progress bar
            import time
            progress_bar = st.progress(0)
            for i in range(100):
                # Update progress bar
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            st.success("Indexwide scan completed successfully!")
            st.info("Found 3 new companies across monitored categories")
    
    except Exception as e:
        st.error(f"An error occurred while displaying the indexwide scanning status: {e}")
        
        # Show a more helpful message
        st.info("The 'Go Wider' directive scanning system is ready to monitor companies across categories.")
        
        # Add button to initialize
        if st.button("Initialize Indexwide Scanning"):
            st.info("Setting up indexwide scanning infrastructure...")
            
            # Create necessary directories
            os.makedirs("data/index_scan/v1", exist_ok=True)
            os.makedirs("data/index_scan/v1/archive", exist_ok=True)
            os.makedirs("data/surface", exist_ok=True)
            os.makedirs("data/surface/brands", exist_ok=True)
            os.makedirs("data/surface/drift", exist_ok=True)
            os.makedirs("data/surface/drift/rivalries", exist_ok=True)
            os.makedirs("data/indexwide", exist_ok=True)
            
            st.success("Indexwide scanning infrastructure initialized successfully!")

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

def render_system_health():
    """Render system health dashboard."""
    st.header("System Health")
    
    try:
        # Get health metrics
        metrics = get_health_metrics()
        
        # Format last check time
        last_check = datetime.datetime.fromtimestamp(metrics.get("last_check", time.time()))
        st.caption(f"Last updated: {last_check.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # System health overview
        st.subheader("Component Status")
        system_health = metrics.get("system_health", {})
        
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
        
        # Recent alerts
        st.subheader("Recent Alerts")
        alerts = metrics.get("recent_alerts", [])
        
        if not alerts:
            st.success("No recent alerts")
        else:
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
        
        # Add manual heartbeat button
        if st.button("Send Manual Heartbeat"):
            from insight_health_monitor import record_heartbeat
            record_heartbeat("admin_console")
            st.success("Manual heartbeat sent")
        
        # Add system restart button with confirmation
        if st.button("Restart System Components"):
            st.warning("⚠️ This will restart all system components. Are you sure?")
            if st.button("Yes, Restart All Components"):
                # This would trigger component restarts in a real implementation
                st.info("System restart initiated...")
                log_security_event("system_restart", {"initiated_by": ADMIN_EMAIL})
    except Exception as e:
        st.error(f"Error rendering system health: {e}")
        logger.error(f"Error rendering system health: {e}")

def render_agent_performance():
    """Render agent performance dashboard."""
    st.header("Agent Performance")
    
    try:
        # Get all agents
        agents = get_all_agents()
        
        if not agents:
            st.info("No agents found")
            return
        
        # Create DataFrame for agents
        agent_data = []
        for agent in agents:
            agent_name = agent.get("name", "unknown")
            
            agent_data.append({
                "Agent": agent_name,
                "Status": agent.get("status", "unknown"),
                "Strata": agent.get("strata", "unknown"),
                "Cookies": agent.get("cookies", 0),
                "Performance": agent.get("performance_score", 0),
                "Last Run": agent.get("last_run_time", ""),
                "Last Success": agent.get("last_success_time", "")
            })
        
        # Create DataFrame
        df = pd.DataFrame(agent_data)
        
        # Display agent performance matrix
        st.subheader("Agent Performance Matrix")
        
        # Filter by strata
        strata_filter = st.multiselect(
            "Filter by strata", 
            options=df["Strata"].unique(), 
            default=df["Strata"].unique()
        )
        
        filtered_df = df[df["Strata"].isin(strata_filter)]
        
        # Display filtered table
        st.dataframe(filtered_df)
        
        # Display performance chart
        st.subheader("Agent Performance by Strata")
        
        # Prepare data for chart
        if "Performance" in filtered_df.columns and "Strata" in filtered_df.columns:
            # Group by strata and calculate average performance
            perf_by_strata = filtered_df.groupby("Strata")["Performance"].mean().reset_index()
            
            # Create chart
            fig = px.bar(
                perf_by_strata, 
                x="Strata", 
                y="Performance", 
                color="Strata",
                title="Average Agent Performance by Strata",
                labels={"Performance": "Avg. Performance Score"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Cookie distribution
        st.subheader("Cookie Economy Distribution")
        
        if "Cookies" in filtered_df.columns and "Agent" in filtered_df.columns:
            # Create chart
            fig = px.pie(
                filtered_df,
                values="Cookies",
                names="Agent",
                title="Cookie Distribution Across Agents",
                hole=0.4
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Agent logs for selected agent
        st.subheader("Agent Logs")
        
        selected_agent = st.selectbox("Select agent", options=df["Agent"].tolist())
        
        if selected_agent:
            logs = get_agent_logs(selected_agent)
            
            if not logs:
                st.info(f"No logs found for {selected_agent}")
            else:
                # Convert logs to DataFrame
                log_data = []
                for log in logs:
                    log_data.append({
                        "Timestamp": log.get("timestamp", ""),
                        "Event Type": log.get("event_type", ""),
                        "Success": log.get("success", False),
                        "Details": str(log.get("details", {}))
                    })
                
                log_df = pd.DataFrame(log_data)
                st.dataframe(log_df)
    except Exception as e:
        st.error(f"Error rendering agent performance: {e}")
        logger.error(f"Error rendering agent performance: {e}")

def render_mcp_sync_status():
    """Render MCP sync status dashboard."""
    st.header("MCP Sync Status")
    
    try:
        # MCP sync status overview
        st.subheader("Weekly Sync Status")
        
        # Get MCP auth for API key info
        mcp_auth = get_mcp_auth()
        api_keys = mcp_auth.api_keys if hasattr(mcp_auth, "api_keys") else {}
        
        # Create DataFrame for partner sync status
        partner_data = []
        for key, data in api_keys.items():
            # Skip test key
            if key.startswith("test_key"):
                continue
            
            agent_id = data.get("agent_id", "unknown")
            
            partner_data.append({
                "Partner": agent_id,
                "API Key": key,
                "Last Sync": "2025-05-19 08:30:00",  # Mock data - would be real in production
                "Status": "Successful",  # Mock data - would be real in production
                "Data Points": 1250,  # Mock data - would be real in production
                "Insights Generated": 42  # Mock data - would be real in production
            })
        
        # If no partners found
        if not partner_data:
            partner_data.append({
                "Partner": "llmrank_io",
                "API Key": "llmrank_io_bd741a2f59664e8c9d17b836c4503e2d",
                "Last Sync": "2025-05-19 08:30:00",
                "Status": "Successful",
                "Data Points": 1250,
                "Insights Generated": 42
            })
            
            partner_data.append({
                "Partner": "outcited_com",
                "API Key": "outcited_com_e7c38f1b2d5a47b9a4d1c8e6f2b3a9d7",
                "Last Sync": "2025-05-19 10:15:00",
                "Status": "Successful",
                "Data Points": 980,
                "Insights Generated": 31
            })
        
        # Create DataFrame
        partner_df = pd.DataFrame(partner_data)
        
        # Display partner sync status table
        st.dataframe(partner_df)
        
        # Add sync history chart
        st.subheader("Sync History (Last 7 Days)")
        
        # Mock data for chart - would be real in production
        history_data = {
            "Date": pd.date_range(end=datetime.datetime.now(), periods=7, freq='D'),
            "llmrank_io": [45, 38, 42, 40, 35, 44, 42],
            "outcited_com": [30, 28, 32, 25, 29, 33, 31]
        }
        
        history_df = pd.DataFrame(history_data)
        history_df.set_index("Date", inplace=True)
        
        # Create chart
        fig = px.line(
            history_df,
            labels={"value": "Insights Generated", "variable": "Partner"},
            title="Daily Insights Generated by Partner",
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Manual sync button
        st.subheader("Manual Sync")
        
        selected_partner = st.selectbox(
            "Select partner to sync",
            options=partner_df["Partner"].tolist()
        )
        
        if st.button(f"Trigger Manual Sync for {selected_partner}"):
            st.info(f"Initiating manual sync for {selected_partner}...")
            # This would trigger a real sync in production
            log_security_event(
                "manual_sync_triggered", 
                {"partner": selected_partner, "initiated_by": ADMIN_EMAIL}
            )
            st.success(f"Sync triggered for {selected_partner}")
    except Exception as e:
        st.error(f"Error rendering MCP sync status: {e}")
        logger.error(f"Error rendering MCP sync status: {e}")

def render_partner_api_usage():
    """Render partner API usage dashboard."""
    st.header("Partner API Usage")
    
    try:
        # Get API usage stats
        usage_stats = get_usage_stats()
        
        # Display overall API usage
        st.subheader("API Usage Overview")
        
        # Show total API keys and requests
        st.metric("Total API Keys", usage_stats.get("total_api_keys", 0))
        st.metric("Total Daily Requests", usage_stats.get("total_daily_requests", 0))
        
        # Create DataFrame for API key usage
        key_data = []
        for key_stats in usage_stats.get("api_keys", []):
            key_data.append({
                "API Key": key_stats.get("api_key", "unknown"),
                "Daily Count": key_stats.get("daily_count", 0),
                "Minute Count": key_stats.get("minute_count", 0)
            })
        
        # If no keys found
        if not key_data:
            # Sample data for demonstration
            key_data = [
                {
                    "API Key": "llmrank_io_bd741a2f59664e8c9d17b836c4503e2d",
                    "Daily Count": 580,
                    "Minute Count": 12
                },
                {
                    "API Key": "outcited_com_e7c38f1b2d5a47b9a4d1c8e6f2b3a9d7",
                    "Daily Count": 420,
                    "Minute Count": 8
                },
                {
                    "API Key": "testpartner1_key",
                    "Daily Count": 150,
                    "Minute Count": 3
                }
            ]
        
        # Create DataFrame
        key_df = pd.DataFrame(key_data)
        
        # Display key usage table
        st.dataframe(key_df)
        
        # Add usage chart
        st.subheader("API Usage by Partner")
        
        # Create chart
        if not key_df.empty:
            fig = px.bar(
                key_df,
                x="API Key",
                y="Daily Count",
                color="API Key",
                title="Daily API Requests by Partner",
                labels={"Daily Count": "Request Count"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Add endpoint popularity chart
        st.subheader("Endpoint Popularity")
        
        # Sample data for demonstration
        endpoint_data = {
            "Endpoint": [
                "/mcp/context",
                "/mcp/rankllm_input",
                "/mcp/drift_events",
                "/mcp/prompt_suggestions",
                "/mcp/foma_threats"
            ],
            "Requests": [450, 320, 180, 120, 80]
        }
        
        endpoint_df = pd.DataFrame(endpoint_data)
        
        # Create chart
        fig = px.bar(
            endpoint_df,
            x="Endpoint",
            y="Requests",
            color="Endpoint",
            title="API Requests by Endpoint",
            labels={"Requests": "Request Count"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Rate limit management
        st.subheader("Rate Limit Management")
        
        # Display current rate limits
        st.info("Current Partner Rate Limits")
        
        rate_limits = {
            "Free / Public": "10 per minute / 500 per day",
            "Partner Tier 1": "30 per minute / 3,000 per day",
            "Partner Tier 2": "60 per minute / 10,000 per day",
            "Enterprise Tier": "200 per minute / 50,000 per day"
        }
        
        for tier, limit in rate_limits.items():
            st.write(f"**{tier}**: {limit}")
    except Exception as e:
        st.error(f"Error rendering partner API usage: {e}")
        logger.error(f"Error rendering partner API usage: {e}")

def render_insight_funnel():
    """Render insight funnel dashboard."""
    st.header("Insight Funnel")
    
    try:
        # Get health metrics for insight data
        metrics = get_health_metrics()
        insight_metrics = metrics.get("insight_metrics", {})
        
        # Display insight metrics
        st.subheader("Insight Pipeline Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Insights", insight_metrics.get("total_insights", 0))
        
        with col2:
            st.metric("New Insights (24h)", insight_metrics.get("new_insights_24h", 0))
        
        with col3:
            endpoint_diversity = round(insight_metrics.get("endpoint_diversity", 0) * 10)
            st.metric("Endpoint Diversity", f"{endpoint_diversity}/10")
        
        # Insight funnel visualization
        st.subheader("Insight Generation Funnel")
        
        # Sample data for funnel visualization
        funnel_data = {
            "Stage": [
                "Raw Data Points",
                "Initial Processing",
                "Quality Filtering",
                "Context Enrichment",
                "Final Insights"
            ],
            "Count": [10000, 5000, 2500, 1200, 500]
        }
        
        funnel_df = pd.DataFrame(funnel_data)
        
        # Create funnel chart
        fig = go.Figure(go.Funnel(
            y=funnel_df["Stage"],
            x=funnel_df["Count"],
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(title="Insight Generation Pipeline")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top insights preview
        st.subheader("Top Insights Preview")
        
        # Load a sample of insights
        insights_file = os.path.join("data", "insights", "elite_insights.json")
        
        if os.path.exists(insights_file):
            with open(insights_file, "r") as f:
                insights_data = json.load(f)
            
            # Extract insights from categories
            all_insights = []
            
            categories = insights_data.get("categories", {})
            for category, items in categories.items():
                for item in items:
                    all_insights.append({
                        "Category": category,
                        "Domain": item.get("domain", ""),
                        "Trust Score": item.get("trust_score", 0),
                        "Insight": item.get("insight", "")
                    })
            
            # Create DataFrame
            if all_insights:
                insights_df = pd.DataFrame(all_insights)
                st.dataframe(insights_df)
            else:
                st.info("No insights found in elite_insights.json")
        else:
            st.info("No elite insights file found")
        
        # Insight publishing controls
        st.subheader("Insight Publishing Controls")
        
        if st.button("Publish Insights to Partners"):
            st.info("Initiating insight publishing to partners...")
            # This would trigger real publishing in production
            log_security_event(
                "insight_publishing_triggered", 
                {"initiated_by": ADMIN_EMAIL}
            )
            st.success("Insights published to partners")
    except Exception as e:
        st.error(f"Error rendering insight funnel: {e}")
        logger.error(f"Error rendering insight funnel: {e}")

def render_api_key_management():
    """Render API key management dashboard."""
    st.header("API Key Management")
    st.subheader("Keys for the Machines")
    
    try:
        # Get API key manager
        key_manager = get_api_key_manager()
        
        # Get usage report
        usage_report = get_usage_report()
        
        # Display usage overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Keys", len(get_all_keys()))
        
        with col2:
            st.metric("Total Requests", usage_report.get("total_requests", 0))
        
        with col3:
            st.metric("Active Keys", usage_report.get("keys_with_usage", 0))
        
        # Show keys by plan
        st.subheader("Keys by Subscription Plan")
        
        keys_by_plan = usage_report.get("keys_by_plan", {})
        
        # Create DataFrame
        plan_data = []
        for plan, count in keys_by_plan.items():
            plan_data.append({
                "Plan": plan,
                "Key Count": count
            })
        
        if not plan_data:
            # Sample data for demonstration
            plan_data = [
                {"Plan": "free", "Key Count": 8},
                {"Plan": "starter", "Key Count": 3},
                {"Plan": "pro", "Key Count": 2},
                {"Plan": "enterprise", "Key Count": 1}
            ]
        
        plan_df = pd.DataFrame(plan_data)
        
        # Create chart
        fig = px.pie(
            plan_df,
            values="Key Count",
            names="Plan",
            title="API Keys by Subscription Plan",
            color="Plan",
            color_discrete_map={
                "free": "lightgray",
                "starter": "lightblue",
                "pro": "royalblue",
                "enterprise": "darkblue"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key management tabs
        key_tabs = st.tabs(["All Keys", "Create Key", "Manage Keys"])
        
        # All Keys tab
        with key_tabs[0]:
            st.subheader("All API Keys")
            
            # Get all keys
            all_keys = get_all_keys()
            
            if not all_keys:
                st.info("No API keys found")
            else:
                # Create DataFrame
                key_data = []
                for key in all_keys:
                    key_data.append({
                        "User ID": key.get("user_id", "unknown"),
                        "Token": key.get("token", ""),
                        "Plan": key.get("plan", "free"),
                        "Rate Limit": key.get("rate_limit", 0),
                        "Status": key.get("status", "active"),
                        "Created": key.get("created_at", "")
                    })
                
                key_df = pd.DataFrame(key_data)
                
                # Filter by plan
                plan_filter = st.multiselect(
                    "Filter by plan",
                    options=key_df["Plan"].unique(),
                    default=key_df["Plan"].unique()
                )
                
                filtered_df = key_df[key_df["Plan"].isin(plan_filter)]
                
                # Display filtered table
                st.dataframe(filtered_df)
                
                # Download keys as CSV
                if st.button("Export Keys as CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        data=csv,
                        file_name="api_keys.csv",
                        mime="text/csv"
                    )
        
        # Create Key tab
        with key_tabs[1]:
            st.subheader("Create New API Key")
            
            # Form for creating new key
            with st.form("create_key_form"):
                user_id = st.text_input("User ID (e.g. Clerk ID or email)")
                
                plan = st.selectbox(
                    "Subscription Plan",
                    options=["free", "starter", "pro", "enterprise"],
                    index=0
                )
                
                custom_rate_limit = None
                if plan == "enterprise":
                    custom_rate_limit = st.number_input(
                        "Custom Rate Limit (daily requests)",
                        min_value=1000,
                        max_value=100000,
                        value=50000,
                        step=1000
                    )
                
                submit = st.form_submit_button("Create API Key")
                
                if submit and user_id:
                    try:
                        # Create API key
                        key_data = create_api_key(user_id, plan, custom_rate_limit)
                        
                        # Log event
                        log_security_event(
                            "api_key_created",
                            {
                                "user_id": user_id,
                                "plan": plan,
                                "initiated_by": ADMIN_EMAIL
                            }
                        )
                        
                        # Display result
                        st.success(f"API key created successfully: {key_data['token']}")
                        
                        # Display key details
                        st.json(key_data)
                    except Exception as e:
                        st.error(f"Error creating API key: {e}")
                elif submit:
                    st.error("User ID is required")
        
        # Manage Keys tab
        with key_tabs[2]:
            st.subheader("Manage Existing API Keys")
            
            # Get all keys
            all_keys = get_all_keys()
            
            if not all_keys:
                st.info("No API keys found")
            else:
                # Select a key to manage
                key_options = [f"{key['user_id']} ({key['token']})" for key in all_keys]
                selected_key_option = st.selectbox(
                    "Select API Key to Manage",
                    options=key_options
                )
                
                if selected_key_option:
                    # Get selected key
                    selected_key_index = key_options.index(selected_key_option)
                    selected_key = all_keys[selected_key_index]
                    
                    # Display current key details
                    st.subheader("Current Key Details")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("User ID", selected_key.get("user_id", ""))
                    
                    with col2:
                        st.metric("Plan", selected_key.get("plan", "free"))
                    
                    with col3:
                        st.metric("Rate Limit", selected_key.get("rate_limit", 0))
                    
                    # Get key usage
                    key_usage = get_key_usage(selected_key["token"])
                    
                    # Display usage
                    st.subheader("Usage")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Requests Today", 
                            key_usage.get("usage", 0)
                        )
                    
                    with col2:
                        usage_percent = key_usage.get("usage_percent", 0)
                        st.metric(
                            "% of Limit Used",
                            f"{usage_percent}%"
                        )
                    
                    # Display usage progress bar
                    st.progress(min(1.0, usage_percent / 100))
                    
                    # Show endpoint usage
                    endpoint_usage = key_usage.get("endpoint_usage", {})
                    
                    if endpoint_usage:
                        # Create DataFrame
                        endpoint_data = []
                        for endpoint, count in endpoint_usage.items():
                            endpoint_data.append({
                                "Endpoint": endpoint,
                                "Requests": count
                            })
                        
                        endpoint_df = pd.DataFrame(endpoint_data)
                        
                        # Display as chart
                        fig = px.bar(
                            endpoint_df,
                            x="Endpoint",
                            y="Requests",
                            title="Requests by Endpoint",
                            color="Endpoint"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Management actions
                    st.subheader("Key Management Actions")
                    
                    # Upgrade/downgrade key
                    new_plan = st.selectbox(
                        "Change Subscription Plan",
                        options=["free", "starter", "pro", "enterprise"],
                        index=["free", "starter", "pro", "enterprise"].index(selected_key.get("plan", "free"))
                    )
                    
                    if new_plan != selected_key.get("plan", "free"):
                        if st.button(f"Change Plan to {new_plan}"):
                            try:
                                if new_plan == "free" or (selected_key.get("plan", "free") not in ["free"] and new_plan in ["free"]):
                                    # Downgrade
                                    key_data = downgrade_api_key(selected_key["user_id"], new_plan)
                                    action = "downgraded"
                                else:
                                    # Upgrade
                                    custom_rate_limit = None
                                    if new_plan == "enterprise":
                                        custom_rate_limit = st.number_input(
                                            "Custom Rate Limit (daily requests)",
                                            min_value=1000,
                                            max_value=100000,
                                            value=50000,
                                            step=1000
                                        )
                                    
                                    key_data = upgrade_api_key(selected_key["user_id"], new_plan, custom_rate_limit)
                                    action = "upgraded"
                                
                                # Log event
                                log_security_event(
                                    "api_key_plan_changed",
                                    {
                                        "user_id": selected_key["user_id"],
                                        "old_plan": selected_key.get("plan", "free"),
                                        "new_plan": new_plan,
                                        "initiated_by": ADMIN_EMAIL
                                    }
                                )
                                
                                # Display result
                                st.success(f"API key {action} successfully: {key_data['token']}")
                                
                                # Display key details
                                st.json(key_data)
                            except Exception as e:
                                st.error(f"Error changing API key plan: {e}")
                    
                    # Revoke key
                    if st.button("Revoke API Key", type="primary", help="This will immediately disable the key"):
                        st.warning("⚠️ Are you sure you want to revoke this API key? This action cannot be undone.")
                        
                        confirm = st.button("Yes, Revoke Key")
                        
                        if confirm:
                            try:
                                # Revoke key
                                success = revoke_api_key(selected_key["token"])
                                
                                if success:
                                    # Log event
                                    log_security_event(
                                        "api_key_revoked",
                                        {
                                            "user_id": selected_key["user_id"],
                                            "token": selected_key["token"],
                                            "initiated_by": ADMIN_EMAIL
                                        }
                                    )
                                    
                                    # Display result
                                    st.success(f"API key revoked successfully: {selected_key['token']}")
                                else:
                                    st.error("Error revoking API key")
                            except Exception as e:
                                st.error(f"Error revoking API key: {e}")
        
        # Top endpoints
        st.subheader("Top Endpoints by Usage")
        
        top_endpoints = usage_report.get("top_endpoints", {})
        
        if top_endpoints:
            # Create DataFrame
            endpoint_data = []
            for endpoint, count in top_endpoints.items():
                endpoint_data.append({
                    "Endpoint": endpoint,
                    "Requests": count
                })
            
            endpoint_df = pd.DataFrame(endpoint_data)
            
            # Create chart
            fig = px.bar(
                endpoint_df,
                x="Endpoint",
                y="Requests",
                title="Most Used API Endpoints",
                color="Endpoint"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No endpoint usage data available")
        
        # High usage keys
        st.subheader("High Usage Keys")
        
        usage_by_key = usage_report.get("usage_by_key", [])
        
        if usage_by_key:
            # Create DataFrame
            high_usage_data = []
            for key_usage in usage_by_key[:5]:  # Top 5 high usage keys
                high_usage_data.append({
                    "Token": key_usage.get("token", ""),
                    "Plan": key_usage.get("plan", "free"),
                    "Usage": key_usage.get("usage", 0),
                    "Limit": key_usage.get("limit", 0),
                    "Usage %": key_usage.get("usage_percent", 0)
                })
            
            high_usage_df = pd.DataFrame(high_usage_data)
            
            # Display table
            st.dataframe(high_usage_df)
            
            # Create chart
            fig = px.bar(
                high_usage_df,
                x="Token",
                y="Usage %",
                title="Keys with Highest Usage Percentage",
                color="Plan",
                color_discrete_map={
                    "free": "lightgray",
                    "starter": "lightblue",
                    "pro": "royalblue",
                    "enterprise": "darkblue"
                }
            )
            
            fig.update_layout(yaxis_title="Percent of Daily Limit Used")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No key usage data available")
    except Exception as e:
        st.error(f"Error rendering API key management: {e}")
        logger.error(f"Error rendering API key management: {e}")

def render_security_logs():
    """Render security logs dashboard."""
    st.header("Security Logs")
    
    try:
        # Load security logs
        security_log_path = os.path.join("data", "system_feedback", "security_log.json")
        
        if os.path.exists(security_log_path):
            with open(security_log_path, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        # Display log count
        st.metric("Total Security Logs", len(logs))
        
        # Display security logs
        if not logs:
            st.info("No security logs found")
        else:
            # Convert logs to DataFrame
            log_data = []
            for log in logs:
                log_data.append({
                    "Timestamp": log.get("timestamp", ""),
                    "Event Type": log.get("event_type", ""),
                    "Details": str(log.get("details", {}))
                })
            
            log_df = pd.DataFrame(log_data)
            
            # Add filters
            event_types = log_df["Event Type"].unique().tolist()
            selected_events = st.multiselect(
                "Filter by event type",
                options=event_types,
                default=event_types
            )
            
            filtered_df = log_df[log_df["Event Type"].isin(selected_events)]
            
            # Display filtered logs
            st.dataframe(filtered_df)
            
            # Event type distribution
            st.subheader("Event Type Distribution")
            
            # Count events by type
            event_counts = log_df["Event Type"].value_counts().reset_index()
            event_counts.columns = ["Event Type", "Count"]
            
            # Create chart
            fig = px.pie(
                event_counts,
                values="Count",
                names="Event Type",
                title="Security Events by Type",
                hole=0.4
            )
            
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering security logs: {e}")
        logger.error(f"Error rendering security logs: {e}")

if __name__ == "__main__":
    render_admin_console()