"""
LLMPageRank V3 Enhanced Dashboard

This module implements the enhanced dashboard for the V3 system,
providing real-time trust signal intelligence and visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time
from datetime import datetime, timedelta

# Import from project modules
from config import DATA_DIR, CATEGORIES, LLM_MODELS, SYSTEM_VERSION, VERSION_INFO
import database as db
from category_matrix import get_category_stats, calculate_foma_score, get_peer_domains
from crawl_planner import get_prioritized_domains
from prompt_validator import get_invalid_prompts

# Constants
FOMA_EVENTS_FILE = f"{DATA_DIR}/foma_events.json"
BENCHMARK_SETS_DIR = f"{DATA_DIR}/category_benchmark_sets"
TRENDS_DIR = f"{DATA_DIR}/trends"

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v3_dashboard():
    """Render the V3 enhanced dashboard."""
    st.title("LLMPageRank V3 - Trust Signal Intelligence")
    
    # Display version info
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Last Updated:** {format_timestamp(time.time())}")
    
    # Add dashboard style
    st.markdown("""
    <style>
        .metric-container {
            background-color: #f5f5f5;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .metric-title {
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .metric-delta {
            font-size: 12px;
            margin-top: 5px;
        }
        .metric-delta-positive {
            color: #28a745;
        }
        .metric-delta-negative {
            color: #dc3545;
        }
        .trust-rising {
            color: #28a745;
        }
        .trust-falling {
            color: #dc3545;
        }
        .trust-stable {
            color: #666;
        }
        .qa-intensity-high {
            color: #dc3545;
        }
        .qa-intensity-medium {
            color: #fd7e14;
        }
        .qa-intensity-low {
            color: #28a745;
        }
        .foma-alert {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "Trust Intelligence",
        "Peer Benchmarks",
        "FOMA Detection",
        "QA Insights",
        "API Status"
    ])
    
    with tabs[0]:
        render_trust_intelligence()
        
    with tabs[1]:
        render_peer_benchmarks()
        
    with tabs[2]:
        render_foma_detection()
        
    with tabs[3]:
        render_qa_insights()
        
    with tabs[4]:
        render_api_status()

def render_trust_intelligence():
    """Render the trust intelligence tab."""
    st.header("Trust Intelligence Dashboard")
    
    # Get domain summary
    domain_summary = db.get_domain_status_summary()
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Domains",
            value=domain_summary.get("total_discovered", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Domains Tested",
            value=domain_summary.get("total_tested", 0),
            delta=None
        )
    
    with col3:
        benchmark_sets = len([f for f in os.listdir(BENCHMARK_SETS_DIR) if f.endswith('.json')])
        st.metric(
            label="Benchmark Sets",
            value=benchmark_sets,
            delta=None
        )
    
    with col4:
        # Calculate domains with valid data
        valid_count = 0
        for category, count in domain_summary.get("categories", {}).items():
            if count > 3:  # Valid peer set requires at least 3 domains
                valid_count += 1
        
        st.metric(
            label="Valid Categories",
            value=valid_count,
            delta=None
        )
    
    # Domain visibility chart
    st.subheader("Domain Visibility by Category")
    
    # Get all tested domains
    tested_domains = []
    all_domains = db.get_all_tested_domains()
    
    for domain in all_domains:
        result = db.get_latest_domain_result(domain)
        if result:
            tested_domains.append({
                "domain": domain,
                "category": result.get("category", "Unknown"),
                "visibility_score": result.get("visibility_score", 0),
                "structure_score": result.get("structure_score", 0),
                "qa_score": result.get("qa_score", 0.5)
            })
    
    if tested_domains:
        # Convert to DataFrame
        df = pd.DataFrame(tested_domains)
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x="structure_score",
            y="visibility_score",
            color="category",
            hover_name="domain",
            size="qa_score",
            size_max=15,
            opacity=0.7,
            labels={
                "structure_score": "Structure Score",
                "visibility_score": "Visibility Score (LLMRank)",
                "category": "Category",
                "qa_score": "QA Intensity"
            },
            title="Domain Structure vs. LLM Visibility"
        )
        
        # Add diagonal line (1:1 relationship)
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=100, y1=100,
            line=dict(color="gray", dash="dash"),
            opacity=0.3
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tested domains available yet.")
    
    # Trust movement
    st.subheader("Trust Signal Movement")
    
    # Get domains with significant movement
    domains_with_movement = []
    
    for domain in tested_domains:
        domain_name = domain["domain"]
        history = db.get_domain_history(domain_name)
        
        if len(history) < 2:
            continue
        
        current = history[0].get("visibility_score", 0)
        previous = history[1].get("visibility_score", 0)
        delta = current - previous
        
        # Only include domains with significant movement
        if abs(delta) >= 5:
            direction = "Rising" if delta > 0 else "Falling"
            domains_with_movement.append({
                "domain": domain_name,
                "category": domain["category"],
                "current_score": current,
                "previous_score": previous,
                "delta": delta,
                "direction": direction
            })
    
    if domains_with_movement:
        # Sort by absolute delta (descending)
        domains_with_movement.sort(key=lambda x: abs(x["delta"]), reverse=True)
        
        # Convert to DataFrame
        movement_df = pd.DataFrame(domains_with_movement)
        
        # Create bar chart
        fig = px.bar(
            movement_df.head(10),
            x="delta",
            y="domain",
            orientation="h",
            color="direction",
            color_discrete_map={"Rising": "#28a745", "Falling": "#dc3545"},
            labels={
                "delta": "Change in LLMRank",
                "domain": "Domain",
                "direction": "Direction"
            },
            title="Top 10 Domains with Trust Signal Movement"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table with details
        st.dataframe(
            movement_df[["domain", "category", "current_score", "previous_score", "delta", "direction"]].head(10)
        )
    else:
        st.info("No domains with significant trust signal movement yet.")
    
    # Category benchmark performance
    st.subheader("Category Benchmark Performance")
    
    # Get category stats
    category_stats = get_category_stats()
    
    if category_stats:
        # Prepare data for chart
        categories = []
        avg_scores = []
        domain_counts = []
        benchmark_status = []
        
        for category, stats in category_stats.items():
            categories.append(category)
            avg_scores.append(stats.get("avg_visibility", 0))
            domain_counts.append(stats.get("domain_count", 0))
            benchmark_status.append("Valid" if stats.get("benchmark_status") == "valid" else "Invalid")
        
        # Create DataFrame
        category_df = pd.DataFrame({
            "category": categories,
            "avg_visibility": avg_scores,
            "domain_count": domain_counts,
            "benchmark_status": benchmark_status
        })
        
        # Create chart
        fig = px.bar(
            category_df,
            x="category",
            y="avg_visibility",
            color="benchmark_status",
            color_discrete_map={"Valid": "#28a745", "Invalid": "#dc3545"},
            labels={
                "category": "Category",
                "avg_visibility": "Average LLMRank",
                "benchmark_status": "Benchmark Status"
            },
            title="Average Trust Score by Category"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category stats available yet.")

def render_peer_benchmarks():
    """Render the peer benchmarks tab."""
    st.header("Peer Group Benchmarks")
    
    # Load benchmark sets
    benchmark_files = [f for f in os.listdir(BENCHMARK_SETS_DIR) if f.endswith('.json')]
    
    if not benchmark_files:
        st.warning("No benchmark sets available yet.")
        return
    
    # Create category selector
    categories = [f.replace('.json', '') for f in benchmark_files]
    selected_category = st.selectbox(
        "Select Category",
        categories
    )
    
    # Load selected benchmark set
    try:
        with open(os.path.join(BENCHMARK_SETS_DIR, f"{selected_category}.json"), 'r') as f:
            benchmark = json.load(f)
    except Exception as e:
        st.error(f"Error loading benchmark set: {e}")
        return
    
    # Display benchmark info
    st.subheader(f"Benchmark: {selected_category}")
    
    # Benchmark status
    status = benchmark.get("benchmark_status", "invalid")
    status_color = "#28a745" if status == "valid" else "#dc3545"
    
    st.markdown(
        f"<div style='padding: 10px; border-radius: 5px; background-color: {status_color}25; border: 1px solid {status_color}; margin-bottom: 20px;'>"
        f"<strong>Status:</strong> {status.upper()}<br>"
        f"<strong>Primary Domain:</strong> {benchmark.get('primary_domain', 'None')}<br>"
        f"<strong>Peer Set Size:</strong> {benchmark.get('peer_set_size', 0)}"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Get domains in benchmark
    domains = [benchmark.get('primary_domain')] + benchmark.get('peer_set', [])
    domains = [d for d in domains if d]  # Remove None
    
    if not domains:
        st.warning("No domains in benchmark set.")
        return
    
    # Get latest results for domains
    domain_data = []
    
    for domain in domains:
        result = db.get_latest_domain_result(domain)
        if result:
            # Calculate FOMA score
            foma = calculate_foma_score(domain)
            
            domain_data.append({
                "domain": domain,
                "visibility_score": result.get("visibility_score", 0),
                "structure_score": result.get("structure_score", 0),
                "consensus_score": result.get("consensus_score", 0),
                "qa_score": result.get("qa_score", 0.5),
                "foma_score": foma.get("foma_score", 0),
                "trust_status": foma.get("trust_status", "Unknown"),
                "is_primary": domain == benchmark.get('primary_domain')
            })
    
    if not domain_data:
        st.warning("No test data available for domains in this benchmark set.")
        return
    
    # Sort by visibility score (descending)
    domain_data.sort(key=lambda x: x["visibility_score"], reverse=True)
    
    # Convert to DataFrame
    df = pd.DataFrame(domain_data)
    
    # Create LLMRank comparison chart
    st.subheader("LLMRank Comparison")
    
    fig = px.bar(
        df,
        x="domain",
        y="visibility_score",
        color="is_primary",
        color_discrete_map={True: "#007bff", False: "#6c757d"},
        labels={
            "domain": "Domain",
            "visibility_score": "LLMRank",
            "is_primary": "Primary Domain"
        },
        title="LLMRank Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create structure vs visibility chart
    st.subheader("Structure vs LLMRank")
    
    fig = px.scatter(
        df,
        x="structure_score",
        y="visibility_score",
        color="is_primary",
        color_discrete_map={True: "#007bff", False: "#6c757d"},
        size="qa_score",
        size_max=15,
        hover_name="domain",
        labels={
            "structure_score": "Structure Score",
            "visibility_score": "LLMRank",
            "is_primary": "Primary Domain",
            "qa_score": "QA Intensity"
        },
        title="Structure vs LLMRank"
    )
    
    # Add diagonal line (1:1 relationship)
    fig.add_shape(
        type="line",
        x0=0, y0=0,
        x1=100, y1=100,
        line=dict(color="gray", dash="dash"),
        opacity=0.3
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed metrics
    st.subheader("Benchmark Metrics")
    
    # Add FOMA status color
    def foma_color(row):
        if row["trust_status"] == "Outsided":
            return "background-color: #fff3cd"
        elif row["trust_status"] == "Trailing":
            return "background-color: #f8d7da"
        else:
            return ""
    
    # Display metrics table
    styled_df = df[["domain", "visibility_score", "structure_score", "consensus_score", "foma_score", "trust_status", "is_primary"]].copy()
    styled_df["is_primary"] = styled_df["is_primary"].map({True: "✓", False: ""})
    
    st.dataframe(
        styled_df.style.applymap(lambda _: "", subset=["domain"]).applymap(foma_color, subset=["trust_status"])
    )

def render_foma_detection():
    """Render the FOMA detection tab."""
    st.header("FOMA Detection (Fear Of Missing AI)")
    
    # Load FOMA events
    foma_events = []
    
    if os.path.exists(FOMA_EVENTS_FILE):
        try:
            with open(FOMA_EVENTS_FILE, 'r') as f:
                foma_events = json.load(f)
        except Exception as e:
            st.error(f"Error loading FOMA events: {e}")
    
    if not foma_events:
        st.warning("No FOMA events detected yet.")
        return
    
    # Display FOMA overview
    st.subheader("FOMA Overview")
    
    # Count by trust status
    status_counts = {}
    for event in foma_events:
        status = event.get("trust_status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create status chart
    status_df = pd.DataFrame({
        "status": list(status_counts.keys()),
        "count": list(status_counts.values())
    })
    
    if not status_df.empty:
        fig = px.pie(
            status_df,
            names="status",
            values="count",
            title="FOMA Events by Trust Status",
            color="status",
            color_discrete_map={
                "Outsided": "#dc3545",
                "Trailing": "#fd7e14",
                "Competitive": "#28a745",
                "Unknown": "#6c757d"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display FOMA events
    st.subheader("FOMA Events")
    
    # Sort by FOMA score (descending)
    foma_events.sort(key=lambda x: x.get("foma_score", 0), reverse=True)
    
    # Display top FOMA events
    for event in foma_events[:10]:
        domain = event.get("domain", "Unknown")
        foma_score = event.get("foma_score", 0)
        trust_status = event.get("trust_status", "Unknown")
        llmrank = event.get("llmrank", 0)
        percentile = event.get("llmrank_percentile", 0)
        gap = event.get("visibility_gap", 0)
        
        # Status color
        status_color = "#6c757d"  # Default gray
        if trust_status == "Outsided":
            status_color = "#dc3545"  # Red
        elif trust_status == "Trailing":
            status_color = "#fd7e14"  # Orange
        elif trust_status == "Competitive":
            status_color = "#28a745"  # Green
        
        # Create FOMA card
        st.markdown(
            f"<div class='foma-alert'>"
            f"<h4 style='color: {status_color};'>{domain} - FOMA Score: {foma_score:.1f}</h4>"
            f"<p><strong>Trust Status:</strong> <span style='color: {status_color};'>{trust_status}</span><br>"
            f"<strong>LLMRank:</strong> {llmrank:.1f} (Percentile: {percentile:.1f})<br>"
            f"<strong>Visibility Gap:</strong> {gap:.1f} points</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Get peer comparison
        peer_gaps = event.get("visibility_gap_vs_peers", [])
        if peer_gaps:
            peer_df = pd.DataFrame(peer_gaps)
            
            fig = px.bar(
                peer_df,
                x="llmrank",
                y="domain",
                orientation="h",
                labels={
                    "llmrank": "LLMRank",
                    "domain": "Domain"
                },
                title=f"Peer Comparison for {domain}"
            )
            
            # Add line for domain's score
            fig.add_vline(
                x=llmrank,
                line_dash="dash",
                line_color=status_color,
                annotation_text=domain,
                annotation_position="top right"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Display FOMA metrics
    st.subheader("FOMA Metrics")
    
    # Convert to DataFrame for metrics
    foma_df = pd.DataFrame([
        {
            "domain": e.get("domain", "Unknown"),
            "foma_score": e.get("foma_score", 0),
            "trust_status": e.get("trust_status", "Unknown"),
            "llmrank": e.get("llmrank", 0),
            "percentile": e.get("llmrank_percentile", 0),
            "visibility_gap": e.get("visibility_gap", 0),
            "timestamp": e.get("timestamp", 0)
        }
        for e in foma_events
    ])
    
    if not foma_df.empty:
        # Add formatted timestamp
        foma_df["date"] = foma_df["timestamp"].apply(format_timestamp)
        
        # Display metrics table
        st.dataframe(
            foma_df[["domain", "foma_score", "trust_status", "llmrank", "percentile", "visibility_gap", "date"]]
            .sort_values("foma_score", ascending=False)
        )

def render_qa_insights():
    """Render the QA insights tab."""
    st.header("QA Intensity Insights")
    
    # Get QA data for domains
    qa_data = []
    all_domains = db.get_all_tested_domains()
    
    for domain in all_domains:
        result = db.get_latest_domain_result(domain)
        if result:
            qa_data.append({
                "domain": domain,
                "category": result.get("category", "Unknown"),
                "qa_score": result.get("qa_score", 0.5),
                "visibility_score": result.get("visibility_score", 0),
                "structure_score": result.get("structure_score", 0),
                "timestamp": result.get("timestamp", 0)
            })
    
    if not qa_data:
        st.warning("No QA data available yet.")
        return
    
    # QA intensity overview
    st.subheader("QA Intensity Overview")
    
    # Convert to DataFrame
    qa_df = pd.DataFrame(qa_data)
    
    # Create QA intensity categories
    qa_df["qa_intensity"] = pd.cut(
        qa_df["qa_score"],
        bins=[0, 0.3, 0.7, 1.0],
        labels=["High", "Medium", "Low"]
    )
    
    # Create QA intensity chart
    fig = px.histogram(
        qa_df,
        x="qa_intensity",
        color="qa_intensity",
        color_discrete_map={
            "High": "#dc3545",
            "Medium": "#fd7e14",
            "Low": "#28a745"
        },
        labels={
            "qa_intensity": "QA Intensity",
            "count": "Number of Domains"
        },
        title="QA Intensity Distribution"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # QA intensity by category
    st.subheader("QA Intensity by Category")
    
    # Calculate average QA score by category
    category_qa = qa_df.groupby("category")["qa_score"].mean().reset_index()
    category_qa["qa_intensity"] = pd.cut(
        category_qa["qa_score"],
        bins=[0, 0.3, 0.7, 1.0],
        labels=["High", "Medium", "Low"]
    )
    
    # Create category QA chart
    fig = px.bar(
        category_qa,
        x="category",
        y="qa_score",
        color="qa_intensity",
        color_discrete_map={
            "High": "#dc3545",
            "Medium": "#fd7e14",
            "Low": "#28a745"
        },
        labels={
            "category": "Category",
            "qa_score": "Average QA Score",
            "qa_intensity": "QA Intensity"
        },
        title="Average QA Score by Category"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # QA vs visibility heatmap
    st.subheader("QA Intensity vs LLMRank")
    
    # Create binned data for heatmap
    qa_df["qa_bin"] = pd.cut(
        qa_df["qa_score"],
        bins=10,
        labels=[f"{i/10:.1f}-{(i+1)/10:.1f}" for i in range(0, 10)]
    )
    
    qa_df["visibility_bin"] = pd.cut(
        qa_df["visibility_score"],
        bins=10,
        labels=[f"{i*10}-{(i+1)*10}" for i in range(0, 10)]
    )
    
    # Count domains in each bin combination
    heatmap_data = qa_df.groupby(["qa_bin", "visibility_bin"]).size().reset_index(name="count")
    
    # Pivot data for heatmap
    heatmap_pivot = heatmap_data.pivot(
        index="qa_bin",
        columns="visibility_bin",
        values="count"
    ).fillna(0)
    
    # Create heatmap
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="LLMRank", y="QA Score", color="Count"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="Viridis",
        title="QA Intensity vs LLMRank Heatmap"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display domain QA metrics
    st.subheader("Domain QA Metrics")
    
    # Add formatted timestamp
    qa_df["date"] = qa_df["timestamp"].apply(format_timestamp)
    
    # Add QA intensity color coding
    def qa_intensity_color(val):
        if val < 0.3:
            return "background-color: rgba(220, 53, 69, 0.2)"  # Red (high intensity)
        elif val < 0.7:
            return "background-color: rgba(253, 126, 20, 0.2)"  # Orange (medium intensity)
        else:
            return "background-color: rgba(40, 167, 69, 0.2)"  # Green (low intensity)
    
    # Display metrics table
    styled_df = qa_df[["domain", "category", "qa_score", "visibility_score", "structure_score", "date"]].copy()
    
    st.dataframe(
        styled_df.style.applymap(qa_intensity_color, subset=["qa_score"])
    )
    
    # Load invalid prompts
    st.subheader("Invalid Prompts")
    
    invalid_prompts = get_invalid_prompts()
    
    if invalid_prompts:
        # Convert to DataFrame
        invalid_df = pd.DataFrame(invalid_prompts)
        
        # Add formatted timestamp
        if "timestamp" in invalid_df.columns:
            invalid_df["date"] = invalid_df["timestamp"].apply(format_timestamp)
        
        # Display table
        st.dataframe(
            invalid_df[["prompt_id", "prompt_text", "reason", "date"]]
        )
    else:
        st.info("No invalid prompts detected.")

def render_api_status():
    """Render the API status tab."""
    st.header("API Status")
    
    # API overview
    st.subheader("API Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="API Version",
            value=SYSTEM_VERSION
        )
    
    with col2:
        # Count API keys
        api_keys_file = f"{DATA_DIR}/api_keys.json"
        key_count = 0
        
        if os.path.exists(api_keys_file):
            try:
                with open(api_keys_file, 'r') as f:
                    keys = json.load(f)
                    key_count = len(keys)
            except Exception:
                key_count = 0
        
        st.metric(
            label="API Keys",
            value=key_count
        )
    
    with col3:
        # Endpoints available
        st.metric(
            label="Endpoints",
            value=6  # Fixed number based on implementation
        )
    
    # API endpoints
    st.subheader("API Endpoints")
    
    endpoints = [
        {
            "endpoint": "/api/v1/score/{domain}",
            "method": "GET",
            "description": "Get trust score and details for a domain",
            "params": "domain: Domain name"
        },
        {
            "endpoint": "/api/v1/top/{category}",
            "method": "GET",
            "description": "Get top domains by visibility score for a category",
            "params": "category: Category name, limit: Maximum number of domains"
        },
        {
            "endpoint": "/api/v1/visibility-deltas",
            "method": "GET",
            "description": "Get domains with the biggest changes in visibility",
            "params": "limit: Maximum number of domains"
        },
        {
            "endpoint": "/api/v1/prompts/{category}",
            "method": "GET",
            "description": "Get prompts used for a specific category",
            "params": "category: Category name"
        },
        {
            "endpoint": "/api/v1/foma/{domain}",
            "method": "GET",
            "description": "Get FOMA score for a domain",
            "params": "domain: Domain name"
        },
        {
            "endpoint": "/api/v1/metadata",
            "method": "GET",
            "description": "Get system metadata",
            "params": "None"
        }
    ]
    
    for endpoint in endpoints:
        with st.expander(f"{endpoint['method']} {endpoint['endpoint']}"):
            st.markdown(f"**Description:** {endpoint['description']}")
            st.markdown(f"**Parameters:** {endpoint['params']}")
            
            # Add example request
            st.code(
                f"curl -H 'Authorization: Bearer YOUR_API_KEY' \\\n"
                f"     -H 'x-mcp-agent: true' \\\n"
                f"     -H 'x-session-type: agent' \\\n"
                f"     -H 'x-query-purpose: trust_query' \\\n"
                f"     http://your-api-host{endpoint['endpoint'].replace('{domain}', 'example.com').replace('{category}', 'finance')}"
            )
    
    # API authentication
    st.subheader("API Authentication")
    
    st.markdown(
        """
        The API uses bearer token authentication. Include the following headers in your requests:
        
        ```
        Authorization: Bearer YOUR_API_KEY
        x-mcp-agent: true  # Optional, for Machine Compatible Processors
        x-session-type: agent/analyst/browser  # Optional
        x-query-purpose: trust_query/delta_check/foma_trigger  # Optional
        ```
        
        Contact the administrator to obtain an API key.
        """
    )
    
    # API integration example
    st.subheader("API Integration Example")
    
    st.code(
        """
import requests
import json

API_KEY = "your_api_key"
API_HOST = "https://llmpagerank-api.example.com"

def get_domain_score(domain):
    # Get trust score for a domain
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "x-mcp-agent": "true",
        "x-session-type": "agent",
        "x-query-purpose": "trust_query"
    }
    
    response = requests.get(
        f"{API_HOST}/api/v1/score/{domain}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

# Example usage
score = get_domain_score("example.com")
print(json.dumps(score, indent=2))
        """
    )