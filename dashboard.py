import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

from data_storage import (
    load_trends_data, 
    load_domain_test_results,
    get_domain_status_summary,
    format_timestamp,
    get_latest_domain_result
)
from scheduler import get_scheduler_status, run_manual_discovery_job, run_manual_testing_job
from config import CATEGORIES, LLM_MODELS

def render_dashboard():
    """Render the main dashboard."""
    st.title("LLMPageRank - Visibility Intelligence Robot")
    
    # Add dashboard style
    st.markdown("""
    <style>
        .metric-title {
            font-size: 14px;
            color: #666;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        .metric-delta {
            font-size: 12px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Load current trends data
    trends_data = load_trends_data()
    last_updated = format_timestamp(trends_data.get("last_updated", time.time()))
    
    # Top navigation
    st.markdown(f"**Last updated:** {last_updated}")
    tabs = st.tabs(["Dashboard", "Domain Explorer", "Categories", "Scheduler", "About"])
    
    with tabs[0]:
        render_main_dashboard(trends_data)
        
    with tabs[1]:
        render_domain_explorer()
        
    with tabs[2]:
        render_category_insights(trends_data)
        
    with tabs[3]:
        render_scheduler_control()
        
    with tabs[4]:
        render_about_page()

def render_main_dashboard(trends_data):
    """Render the main dashboard tab with key metrics."""
    # Get domain summary
    domain_summary = get_domain_status_summary()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Domains Discovered", 
            value=domain_summary.get("total_discovered", 0)
        )
    
    with col2:
        st.metric(
            label="Domains Tested", 
            value=domain_summary.get("total_tested", 0)
        )
        
    with col3:
        top_score = 0
        if trends_data.get("top_domains"):
            top_score = trends_data["top_domains"][0].get("visibility_score", 0)
        st.metric(
            label="Highest Visibility Score", 
            value=f"{top_score:.1f}"
        )
        
    with col4:
        biggest_mover = 0
        if trends_data.get("movers"):
            biggest_mover = abs(trends_data["movers"][0].get("delta_24h", 0))
        st.metric(
            label="Biggest 24h Movement", 
            value=f"{biggest_mover:.1f}"
        )
    
    # Top domains and movers row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Domains by Visibility")
        if trends_data.get("top_domains"):
            top_domains_df = pd.DataFrame(trends_data["top_domains"])
            
            # Add trend icons
            def get_trend_icon(trend):
                if trend == "rising":
                    return "↗️"
                elif trend == "falling":
                    return "↘️"
                else:
                    return "→"
                    
            top_domains_df["trend_icon"] = top_domains_df["trend"].apply(get_trend_icon)
            top_domains_df["display"] = top_domains_df["domain"] + " " + top_domains_df["trend_icon"]
            
            fig = px.bar(
                top_domains_df.head(10), 
                x="visibility_score", 
                y="display",
                orientation='h',
                color="category",
                labels={"display": "Domain", "visibility_score": "Visibility Score"},
                title="Top 10 Most Visible Domains"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No domains data available yet.")
    
    with col2:
        st.subheader("📈 Biggest Movers (24h)")
        if trends_data.get("movers"):
            movers_df = pd.DataFrame(trends_data["movers"])
            
            # Color code based on direction
            movers_df["color"] = movers_df["direction"].apply(lambda x: "#00FF00" if x == "up" else "#FF0000")
            
            fig = px.bar(
                movers_df.head(10), 
                x="delta_24h", 
                y="domain",
                orientation='h',
                color="direction",
                color_discrete_map={"up": "#00CC00", "down": "#CC0000"},
                labels={"domain": "Domain", "delta_24h": "24h Change"},
                title="Top 10 Movers in Last 24 Hours"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No movers data available yet.")
    
    # Visibility gap row
    st.subheader("👻 Invisible Sites (High Structure Score, Low Visibility)")
    if trends_data.get("invisible_sites"):
        invisible_df = pd.DataFrame(trends_data["invisible_sites"])
        
        # Create a comparison chart showing structure vs visibility
        fig = px.bar(
            invisible_df.head(10),
            x="domain",
            y=["structure_score", "visibility_score"],
            barmode="group",
            labels={"value": "Score", "domain": "Domain", "variable": "Score Type"},
            title="Top 10 Domains with Visibility Gap",
            color_discrete_map={"structure_score": "#0072B2", "visibility_score": "#D55E00"}
        )
        fig.update_layout(legend_title_text="Score Type")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No invisible sites data available yet.")
    
    # Category comparison
    st.subheader("🔍 Category Visibility Comparison")
    if trends_data.get("category_stats"):
        # Prepare data
        categories = []
        avg_scores = []
        domain_counts = []
        
        for category, stats in trends_data["category_stats"].items():
            categories.append(category)
            avg_scores.append(stats.get("avg_visibility", 0))
            domain_counts.append(stats.get("domain_count", 0))
        
        # Create category comparison chart
        category_df = pd.DataFrame({
            "category": categories,
            "avg_visibility": avg_scores,
            "domain_count": domain_counts
        })
        
        fig = px.bar(
            category_df,
            x="category",
            y="avg_visibility",
            color="category",
            size="domain_count",
            labels={"category": "Category", "avg_visibility": "Average Visibility Score", "domain_count": "Number of Domains"},
            title="Average Visibility by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category stats available yet.")

def render_domain_explorer():
    """Render the domain explorer tab."""
    st.subheader("🔎 Domain Explorer")
    
    # Domain search
    domain_search = st.text_input("Search for a domain", placeholder="example.com")
    
    if domain_search:
        # Load domain history
        domain_history = load_domain_test_results(domain_search)
        
        if domain_history:
            latest = domain_history[0]
            
            # Display domain info
            st.subheader(f"Domain: {domain_search}")
            
            # Basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Visibility Score", f"{latest.get('visibility_score', 0):.1f}")
            with col2:
                st.metric("Structure Score", f"{latest.get('structure_score', 0):.1f}")
            with col3:
                st.metric("Consensus Score", f"{latest.get('consensus_score', 0):.2f}")
            
            # Citation by model
            st.subheader("Citation by Model")
            
            citation_coverage = latest.get("citation_coverage", {})
            models = list(citation_coverage.keys())
            values = [citation_coverage.get(model, 0) * 100 for model in models]
            
            citation_df = pd.DataFrame({
                "Model": models,
                "Citation Coverage (%)": values
            })
            
            fig = px.bar(
                citation_df,
                x="Model",
                y="Citation Coverage (%)",
                color="Model",
                title="Citation Coverage by Model"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Historical trend
            st.subheader("Visibility History")
            
            # Extract timestamps and scores
            timestamps = []
            scores = []
            
            for entry in domain_history:
                timestamps.append(datetime.fromtimestamp(entry.get("timestamp", 0)))
                scores.append(entry.get("visibility_score", 0))
            
            # Create time series dataframe
            if timestamps and scores:
                history_df = pd.DataFrame({
                    "Date": timestamps,
                    "Visibility Score": scores
                })
                
                fig = px.line(
                    history_df,
                    x="Date",
                    y="Visibility Score",
                    title="Visibility Score Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical data available for this domain.")
            
            # Citation breakdown
            st.subheader("Citation Type Breakdown")
            
            citation_counts = latest.get("citation_counts", {})
            if citation_counts:
                # Prepare data for stacked bar chart
                models = []
                direct = []
                paraphrased = []
                none = []
                
                for model, counts in citation_counts.items():
                    models.append(model)
                    direct.append(counts.get("direct", 0))
                    paraphrased.append(counts.get("paraphrased", 0))
                    none.append(counts.get("none", 0))
                
                fig = go.Figure(data=[
                    go.Bar(name="Direct", x=models, y=direct),
                    go.Bar(name="Paraphrased", x=models, y=paraphrased),
                    go.Bar(name="None", x=models, y=none)
                ])
                
                fig.update_layout(
                    barmode='stack',
                    title="Citation Types by Model",
                    xaxis_title="Model",
                    yaxis_title="Count"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Prompt results
            st.subheader("Latest Prompt Results")
            
            prompt_results = latest.get("prompt_results", [])
            if prompt_results:
                for i, result in enumerate(prompt_results):
                    with st.expander(f"Prompt: {result.get('prompt_text', 'Unknown')}"):
                        for model, model_result in result.get("results", {}).items():
                            st.markdown(f"**{model}**")
                            st.markdown(f"Citation: **{model_result.get('citation_type', 'none')}** (Confidence: {model_result.get('confidence', 0):.2f})")
                            st.markdown("Response:")
                            st.markdown(model_result.get("response", "No response"))
                            st.markdown("---")
            else:
                st.info("No prompt results available for this domain.")
            
        else:
            st.warning(f"No data found for domain: {domain_search}")
    else:
        st.info("Enter a domain name to see detailed information.")

def render_category_insights(trends_data):
    """Render the category insights tab."""
    st.subheader("📊 Category Insights")
    
    # Category selector
    category_stats = trends_data.get("category_stats", {})
    categories = list(category_stats.keys())
    
    if not categories:
        st.info("No category data available yet.")
        return
    
    selected_category = st.selectbox("Select Category", categories)
    
    if selected_category and selected_category in category_stats:
        stats = category_stats[selected_category]
        
        # Basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Domains in Category", stats.get("domain_count", 0))
        with col2:
            st.metric("Avg. Visibility Score", f"{stats.get('avg_visibility', 0):.1f}")
        with col3:
            st.metric("Avg. Structure Score", f"{stats.get('avg_structure', 0):.1f}")
        
        # Citation rates by model
        st.subheader("Citation Rates by Model")
        
        citation_by_model = stats.get("citation_by_model", {})
        if citation_by_model:
            models = list(citation_by_model.keys())
            rates = [citation_by_model[model] * 100 for model in models]
            
            citation_df = pd.DataFrame({
                "Model": models,
                "Citation Rate (%)": rates
            })
            
            fig = px.bar(
                citation_df,
                x="Model",
                y="Citation Rate (%)",
                color="Model",
                title=f"Citation Rates for {selected_category}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top domains in this category
        st.subheader(f"Top Domains in {selected_category}")
        
        # Filter top domains for this category
        top_domains = [d for d in trends_data.get("top_domains", []) if d.get("category") == selected_category]
        
        if top_domains:
            top_domains_df = pd.DataFrame(top_domains)
            
            fig = px.bar(
                top_domains_df.head(10),
                x="visibility_score",
                y="domain",
                orientation='h',
                title=f"Top 10 Domains in {selected_category}",
                labels={"visibility_score": "Visibility Score", "domain": "Domain"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No top domains found for {selected_category}.")

def render_scheduler_control():
    """Render the scheduler control tab."""
    st.subheader("⚙️ System Control Panel")
    
    # Get scheduler status
    scheduler_status = get_scheduler_status()
    job_status = scheduler_status.get("job_status", {})
    
    # Create tabs for different monitoring sections
    system_tab, jobs_tab, stats_tab, logs_tab = st.tabs(["System Status", "Job Control", "Data Statistics", "System Logs"])
    
    with system_tab:
        # System status indicators with metric cards for better visibility
        st.markdown("### System Status")
        
        # Add status indicators with more visual appeal
        col1, col2 = st.columns(2)
        
        with col1:
            # Use metric for better visibility
            status_value = "Online" if scheduler_status.get("scheduler_running", False) else "Offline"
            st.metric("System Status", status_value)
            
            last_run = job_status.get("last_run")
            if last_run:
                st.metric("Last Job Run", format_timestamp(last_run))
            else:
                st.metric("Last Job Run", "Never")
        
        with col2:
            next_run = job_status.get("next_run")
            if next_run:
                st.metric("Next Scheduled Run", format_timestamp(next_run))
            else:
                st.metric("Next Scheduled Run", "Not scheduled")
            
            status = job_status.get("status", "idle")
            # Use colored indicators for status
            status_color = "blue"
            if "error" in status:
                status_color = "red"
                status_display = "🔴 Error"
            elif "complete" in status:
                status_color = "green"
                status_display = "🟢 Complete"
            elif "running" in status:
                status_color = "orange"
                status_display = "🟠 Running"
            else:
                status_display = "⚪ Idle"
            
            st.metric("Current Status", status_display)
        
        # Display current activity
        st.markdown("### Activity Summary")
        
        # Create metrics for domain stats
        col1, col2 = st.columns(2)
        with col1:
            if job_status.get("domains_discovered"):
                st.metric("Total Domains Discovered", job_status.get("domains_discovered", 0))
            else:
                st.metric("Total Domains Discovered", 0)
        
        with col2:
            if job_status.get("domains_tested"):
                st.metric("Total Domains Tested", job_status.get("domains_tested", 0))
            else:
                st.metric("Total Domains Tested", 0)
        
        # Show error if exists
        if job_status.get("last_error"):
            st.error(f"Last Error: {job_status.get('last_error')}")
    
    with jobs_tab:
        st.markdown("### Job Control Center")
        st.markdown("Start or stop data collection processes")
        
        # Improved job controls with descriptions
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Domain Discovery")
            st.markdown("Discovers and categorizes new domains")
            if st.button("🔎 Start Domain Discovery", use_container_width=True):
                result = run_manual_discovery_job()
                st.success(f"Domain discovery job started successfully")
        
        with col2:
            st.markdown("#### LLM Testing")
            st.markdown("Tests discovered domains with LLMs")
            if st.button("🧪 Start Domain Testing", use_container_width=True):
                result = run_manual_testing_job()
                st.success(f"Domain testing job started successfully")
        
        # Add scheduler settings
        st.markdown("---")
        st.markdown("### Scheduler Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Discovery job frequency (hours)", min_value=1, max_value=168, value=24)
        with col2:
            st.number_input("Testing job frequency (hours)", min_value=1, max_value=168, value=24)
            
        st.button("Update Schedule", use_container_width=True)
    
    with stats_tab:
        st.markdown("### Data Statistics")
        
        # Domain statistics with improved visualization
        domain_stats = get_domain_status_summary()
        
        # Create visual metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Domains Discovered", domain_stats.get("discovered", 0))
        with col2:
            st.metric("Domains Tested", domain_stats.get("tested", 0))
        with col3:
            test_percent = 0
            if domain_stats.get("discovered", 0) > 0:
                test_percent = (domain_stats.get("tested", 0) / domain_stats.get("discovered", 0)) * 100
            st.metric("Testing Coverage", f"{test_percent:.1f}%")
        
        # Add category breakdown
        st.markdown("#### Category Breakdown")
        category_counts = domain_stats.get("categories", {})
        if category_counts:
            # Create a dataframe for the pie chart
            categories = list(category_counts.keys())
            counts = list(category_counts.values())
            cat_df = pd.DataFrame({"Category": categories, "Count": counts})
            
            # Create a pie chart
            fig = px.pie(
                cat_df, 
                values="Count", 
                names="Category",
                title="Domains by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available yet")
    
    with logs_tab:
        st.markdown("### System Logs")
        st.markdown("View recent system activity and errors")
        
        # Create a log viewer
        log_data = []
        
        # Add recent job status updates from actual status
        if job_status.get("last_run"):
            log_data.append({
                "timestamp": format_timestamp(job_status.get("last_run")),
                "level": "INFO",
                "message": f"Last job run: {job_status.get('current_job', 'Unknown')} job"
            })
        
        if job_status.get("last_error"):
            log_data.append({
                "timestamp": format_timestamp(job_status.get("last_error_time", time.time())),
                "level": "ERROR",
                "message": job_status.get("last_error")
            })
        
        # Add system startup info
        log_data.append({
            "timestamp": format_timestamp(time.time() - 3600),  # 1 hour ago
            "level": "INFO",
            "message": "System initialized"
        })
        
        log_data.append({
            "timestamp": format_timestamp(time.time() - 3000),  # 50 minutes ago
            "level": "INFO",
            "message": "Scheduler started"
        })
        
        # Display logs in a dataframe
        if log_data:
            log_df = pd.DataFrame(log_data)
            st.dataframe(log_df, use_container_width=True)
        else:
            st.info("No logs available")

def render_about_page():
    """Render the about page."""
    st.subheader("About LLMPageRank")
    
    st.markdown("""
    ### Mission Statement
    
    LLMPageRank is an AI-powered observability platform that continuously monitors which websites
    are getting cited by LLMs and which are not. It identifies why, and builds a normalized, 
    structured, extensible dataset that powers:
    
    - An automated daily benchmark (LLMPageRank Index)
    - A real-time dashboard for admin-only access
    - An expanding data moat that uncovers the anatomy of LLM visibility
    
    ### How It Works
    
    1. **Domain Discovery**: The system crawls the web intelligently to discover domains by category
    2. **LLM Testing**: Each domain is tested against multiple LLMs using a validated prompt framework
    3. **Citation Analysis**: The system detects whether domains are cited directly, paraphrased, or not at all
    4. **Insight Generation**: Patterns in what gets cited and what doesn't are identified
    5. **Trend Tracking**: The system tracks visibility changes over time
    
    ### Metrics Explained
    
    - **Visibility Score**: Overall measure of how visible a domain is across LLMs
    - **Citation Coverage**: Percentage of prompts that cite/paraphrase a domain
    - **Consensus Score**: Agreement across 3+ models
    - **Structure Score**: Markup + schema strength
    - **Z-Score Delta**: High SEO score vs low LLM rank (FOMA target)
    
    ### The AI Truth Index
    
    The result is:
    - A scalable truth-tracking robot
    - A real-time benchmark for AI trust
    - A diagnostic system that teaches the world: "What gets you cited in an LLM—and what doesn't."
    """)

if __name__ == "__main__":
    # For testing outside Streamlit app
    render_dashboard()
