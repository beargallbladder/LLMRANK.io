"""
LLMPageRank V5 Admin Dashboard

This module implements the Admin Dashboard for V5 focused on data integrity,
insight validation, and trust accountability.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time
import re
from datetime import datetime, timedelta

# Import from project modules
from config import DATA_DIR, CATEGORIES, LLM_MODELS, SYSTEM_VERSION, VERSION_INFO
import database as db
import insight_monitor as im
import replit_delivery_protocol as rdp

# Constants
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_CONSOLE_DIR = f"{DATA_DIR}/admin_insight_console"
TRUST_DRIFT_DIR = f"{DATA_DIR}/trust_drift/time_series"
BENCHMARKS_DIR = f"{DATA_DIR}/benchmarks/by_category"

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v5_dashboard():
    """Render the V5 admin dashboard."""
    st.title("LLMRank.io - Admin Insight Console")
    
    # Display version info
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Last Updated:** {format_timestamp(time.time())}")
    
    # Add dashboard style
    st.markdown("""
    <style>
        .metric-container {
            background-color: #f5f5f5;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .insight-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .insight-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
        }
        .insight-summary {
            font-size: 14px;
            color: #555;
            margin-bottom: 10px;
        }
        .insight-meta {
            font-size: 12px;
            color: #777;
        }
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffecb5;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .success-box {
            background-color: #d1e7dd;
            border: 1px solid #badbcc;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .error-box {
            background-color: #f8d7da;
            border: 1px solid #f5c2c7;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .info-box {
            background-color: #cfe2ff;
            border: 1px solid #b6d4fe;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .data-integrity-high {
            color: #198754;
        }
        .data-integrity-medium {
            color: #fd7e14;
        }
        .data-integrity-low {
            color: #dc3545;
        }
        .admin-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .admin-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: #343a40;
        }
        .admin-alert {
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }
        .admin-alert-critical {
            background-color: #dc3545;
            color: white;
        }
        .admin-alert-warning {
            background-color: #ffc107;
            color: #212529;
        }
        .admin-alert-success {
            background-color: #198754;
            color: white;
        }
        .trust-drift-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #0dcaf0;
        }
        .benchmark-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #20c997;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "System Integrity",
        "Trust Movement",
        "Benchmark Analysis",
        "Insight Scorecard",
        "Data Signal Review",
        "Delivery Scoring"
    ])
    
    with tabs[0]:
        render_system_integrity()
        
    with tabs[1]:
        render_trust_movement()
        
    with tabs[2]:
        render_benchmark_analysis()
        
    with tabs[3]:
        render_insight_scorecard()
        
    with tabs[4]:
        render_data_signal_review()
        
    with tabs[5]:
        render_delivery_scoring()

def render_system_integrity():
    """Render the system integrity tab."""
    st.header("System Integrity Snapshot")
    
    # Get scan integrity snapshot
    scan_integrity = im.get_scan_integrity_snapshot()
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        domains_scanned = scan_integrity.get("domains_scanned", 0)
        st.metric(
            label="Domains Scanned",
            value=domains_scanned
        )
    
    with col2:
        insights_generated = scan_integrity.get("insights_generated", 0)
        st.metric(
            label="Insights Generated",
            value=insights_generated
        )
    
    with col3:
        insight_yield = scan_integrity.get("insight_yield_percent", 0)
        st.metric(
            label="Insight Yield",
            value=f"{insight_yield:.1f}%",
            delta=None
        )
    
    with col4:
        flat_flags = scan_integrity.get("flat_benchmark_flags", 0)
        st.metric(
            label="Flat Benchmark Flags",
            value=flat_flags,
            delta=None
        )
    
    # Determine system health
    health_status = "Healthy"
    health_class = "success-box"
    health_issues = []
    
    if insight_yield < 30:
        health_status = "Needs Attention"
        health_class = "warning-box"
        health_issues.append("Low insight yield (<30%)")
    
    if flat_flags > 0.5 * domains_scanned and domains_scanned > 0:
        health_status = "Critical"
        health_class = "error-box"
        health_issues.append("High proportion of flat benchmarks")
    
    if scan_integrity.get("data_quality_warnings", 0) > 0:
        health_status = "Critical" if health_status != "Critical" else health_status
        health_class = "error-box" if health_class != "error-box" else health_class
        health_issues.append(f"{scan_integrity.get('data_quality_warnings', 0)} data quality warnings")
    
    # Display health status
    st.subheader("System Health Status")
    
    st.markdown(
        f"<div class='{health_class}'>"
        f"<h3>Status: {health_status}</h3>"
        f"<p>{'<br>'.join(health_issues) if health_issues else 'No issues detected.'}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Display insight type distribution
    st.subheader("Insight Type Distribution")
    
    # Sample insight type data for demonstration
    insight_types = {
        "trust_score_increase": 15,
        "trust_score_decrease": 12,
        "peer_outpaced": 7,
        "peer_outpacing": 5,
        "benchmark_gap": 8,
        "structure_visibility_gap": 6
    }
    
    # Create DataFrame
    insight_df = pd.DataFrame({
        'type': list(insight_types.keys()),
        'count': list(insight_types.values())
    })
    
    # Sort by count
    insight_df = insight_df.sort_values('count', ascending=False)
    
    # Create chart
    fig = px.bar(
        insight_df,
        x='count',
        y='type',
        orientation='h',
        labels={
            'count': 'Frequency',
            'type': 'Insight Type'
        },
        title='Insight Type Distribution'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display insight quality distribution
    st.subheader("Insight Quality Distribution")
    
    # Sample quality data for demonstration
    quality_counts = {
        "high": 18,
        "medium": 24,
        "low": 11
    }
    
    # Create DataFrame
    quality_df = pd.DataFrame({
        'quality': list(quality_counts.keys()),
        'count': list(quality_counts.values())
    })
    
    # Create chart
    fig = px.pie(
        quality_df,
        values='count',
        names='quality',
        title='Insight Quality Distribution',
        color='quality',
        color_discrete_map={
            'high': '#198754',
            'medium': '#fd7e14',
            'low': '#dc3545'
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data quality warnings
    st.subheader("Data Quality Warnings")
    
    if scan_integrity.get("data_quality_warnings", 0) > 0:
        st.warning(f"{scan_integrity.get('data_quality_warnings', 0)} data quality warnings detected")
        
        # Sample warnings for demonstration
        warnings = [
            "Category 'healthcare' has insufficient peer set coverage",
            "Domain 'example.com' has inconsistent trust signal history",
            "Category 'legal' shows model hallucination patterns"
        ]
        
        for warning in warnings:
            st.markdown(f"<div class='warning-box'>{warning}</div>", unsafe_allow_html=True)
    else:
        st.success("No data quality warnings detected")

def render_trust_movement():
    """Render the trust movement tab."""
    st.header("Trust Movement Tracking")
    
    # Get all tested domains
    all_domains = db.get_all_tested_domains()
    
    if not all_domains:
        st.warning("No domains available for analysis. Add domains to the system first.")
        return
    
    # Create domain selector
    selected_domain = st.selectbox(
        "Select Domain to Analyze",
        all_domains
    )
    
    if not selected_domain:
        st.info("Select a domain to view trust movement.")
        return
    
    # Get trust drift log
    trust_drift = im.get_trust_drift_log(selected_domain)
    
    # Display domain info
    st.subheader(f"Domain: {selected_domain}")
    
    # Get latest result
    latest_result = db.get_latest_domain_result(selected_domain)
    
    if latest_result:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Current LLMRank",
                value=f"{latest_result.get('visibility_score', 0):.1f}"
            )
        
        with col2:
            st.metric(
                label="Category",
                value=latest_result.get('category', 'Unknown')
            )
        
        with col3:
            # Calculate recent volatility
            volatility = 0
            history = db.get_domain_history(selected_domain)
            
            if len(history) > 1:
                current = history[0].get('visibility_score', 0)
                previous = history[1].get('visibility_score', 0)
                volatility = abs(current - previous)
            
            volatility_label = "Low"
            if volatility > 5:
                volatility_label = "High"
            elif volatility > 2:
                volatility_label = "Medium"
            
            st.metric(
                label="Volatility",
                value=volatility_label,
                delta=f"{volatility:.1f} points"
            )
    
    # Display trust drift events
    drift_events = trust_drift.get("drift_events", [])
    
    if drift_events:
        st.subheader("Trust Drift Events")
        
        # Sort by timestamp (descending)
        drift_events.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # Display events
        for event in drift_events:
            timestamp = format_timestamp(event.get("timestamp", 0))
            insight_type = event.get("insight_type", "")
            delta = event.get("delta", 0)
            summary = event.get("summary", "")
            quality = event.get("insight_quality", "")
            
            # Format the delta
            delta_str = f"{delta:+.1f}"
            delta_color = "#198754" if delta > 0 else "#dc3545" if delta < 0 else "#6c757d"
            
            # Quality badge
            quality_color = "#198754" if quality == "high" else "#fd7e14" if quality == "medium" else "#dc3545"
            
            # Icon based on insight type
            icon = "📈" if "increase" in insight_type else "📉" if "decrease" in insight_type else "🔄"
            
            # Display drift event
            st.markdown(
                f"<div class='trust-drift-container'>"
                f"<div style='display: flex; justify-content: space-between;'>"
                f"<div style='font-weight: bold;'>{icon} {summary}</div>"
                f"<div style='color: {delta_color}; font-weight: bold;'>{delta_str}</div>"
                f"</div>"
                f"<div style='display: flex; justify-content: space-between; margin-top: 10px;'>"
                f"<div><span style='background-color: {quality_color}; color: white; padding: 2px 5px; border-radius: 3px;'>{quality.upper()}</span> {insight_type.replace('_', ' ').title()}</div>"
                f"<div style='color: #6c757d;'>{timestamp}</div>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Create time-series visualization
        st.subheader("Trust Signal History")
        
        # Get domain history
        history = db.get_domain_history(selected_domain)
        
        if len(history) > 1:
            # Prepare data for chart
            history_data = []
            
            for result in history:
                history_data.append({
                    "timestamp": result.get("timestamp", 0),
                    "formatted_time": format_timestamp(result.get("timestamp", 0)),
                    "visibility_score": result.get("visibility_score", 0),
                    "structure_score": result.get("structure_score", 0)
                })
            
            # Sort by timestamp
            history_data.sort(key=lambda x: x["timestamp"])
            
            # Create DataFrame
            df = pd.DataFrame(history_data)
            
            # Create chart
            fig = go.Figure()
            
            # Add visibility score
            fig.add_trace(go.Scatter(
                x=df["formatted_time"],
                y=df["visibility_score"],
                mode='lines+markers',
                name='LLMRank',
                line=dict(color='#0d6efd', width=3)
            ))
            
            # Add drift events
            for event in drift_events:
                event_time = format_timestamp(event.get("timestamp", 0))
                event_score = next((item["visibility_score"] for item in history_data 
                                  if format_timestamp(item["timestamp"]) == event_time), None)
                
                if event_time in df["formatted_time"].values and event_score is not None:
                    # Add marker for event
                    color = "#198754" if event.get("delta", 0) > 0 else "#dc3545"
                    
                    fig.add_trace(go.Scatter(
                        x=[event_time],
                        y=[event_score],
                        mode='markers',
                        marker=dict(
                            size=12,
                            color=color,
                            line=dict(width=2, color='white')
                        ),
                        name=event.get("insight_type", "").replace("_", " ").title(),
                        hovertext=event.get("summary", "")
                    ))
            
            fig.update_layout(
                title="Trust Signal History with Drift Events",
                xaxis_title="Date",
                yaxis_title="LLMRank Score",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient historical data for visualization.")
    else:
        st.info("No trust drift events recorded for this domain.")

def render_benchmark_analysis():
    """Render the benchmark analysis tab."""
    st.header("Benchmark Analysis")
    
    # Get all categories
    categories = CATEGORIES
    
    if not categories:
        st.warning("No categories defined in the system.")
        return
    
    # Create category selector
    selected_category = st.selectbox(
        "Select Category to Analyze",
        categories
    )
    
    if not selected_category:
        st.info("Select a category to view benchmark analysis.")
        return
    
    # Get category benchmark
    benchmark = im.get_category_benchmark(selected_category)
    
    # Display category info
    st.subheader(f"Category: {selected_category}")
    
    if benchmark:
        # Format benchmark data
        benchmark_domain = benchmark.get("benchmark_domain", "None")
        peer_set = benchmark.get("peer_set", [])
        score_range = benchmark.get("llm_score_range", [0, 0])
        last_shift = benchmark.get("last_shift", "N/A")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Benchmark Domain",
                value=benchmark_domain
            )
        
        with col2:
            st.metric(
                label="Peer Set Size",
                value=len(peer_set)
            )
        
        with col3:
            st.metric(
                label="Last Benchmark Shift",
                value=last_shift
            )
        
        # Display benchmark details
        st.markdown(
            f"<div class='benchmark-container'>"
            f"<div class='insight-title'>Benchmark Definition</div>"
            f"<p><strong>Benchmark Domain:</strong> {benchmark_domain}</p>"
            f"<p><strong>Score Range:</strong> {score_range[0]:.1f} - {score_range[1]:.1f}</p>"
            f"<p><strong>Peer Set:</strong> {', '.join(peer_set) if peer_set else 'None'}</p>"
            f"<p><strong>Last Shift:</strong> {last_shift}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Get domain scores
        domain_scores = []
        
        # Add benchmark domain
        benchmark_result = db.get_latest_domain_result(benchmark_domain)
        if benchmark_result:
            domain_scores.append({
                "domain": benchmark_domain,
                "score": benchmark_result.get("visibility_score", 0),
                "is_benchmark": True
            })
        
        # Add peer domains
        for peer in peer_set:
            peer_result = db.get_latest_domain_result(peer)
            if peer_result:
                domain_scores.append({
                    "domain": peer,
                    "score": peer_result.get("visibility_score", 0),
                    "is_benchmark": False
                })
        
        if domain_scores:
            # Sort by score (descending)
            domain_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Create DataFrame
            df = pd.DataFrame(domain_scores)
            
            # Create chart
            fig = px.bar(
                df,
                x="domain",
                y="score",
                color="is_benchmark",
                color_discrete_map={True: "#198754", False: "#6c757d"},
                labels={
                    "domain": "Domain",
                    "score": "LLMRank Score",
                    "is_benchmark": "Is Benchmark"
                },
                title=f"Benchmark Comparison for {selected_category}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No score data available for this benchmark.")
        
        # Calculate benchmark clarity
        if domain_scores and len(domain_scores) > 1:
            benchmark_score = next((item["score"] for item in domain_scores if item["is_benchmark"]), 0)
            next_score = next((item["score"] for item in domain_scores if not item["is_benchmark"]), 0)
            
            gap = benchmark_score - next_score
            
            clarity_label = "Low"
            clarity_class = "data-integrity-low"
            
            if gap >= 10:
                clarity_label = "High"
                clarity_class = "data-integrity-high"
            elif gap >= 5:
                clarity_label = "Medium"
                clarity_class = "data-integrity-medium"
            
            st.markdown(
                f"<div class='admin-box'>"
                f"<div class='admin-header'>Benchmark Clarity</div>"
                f"<p>Gap to nearest peer: <strong>{gap:.1f} points</strong></p>"
                f"<p>Clarity: <strong class='{clarity_class}'>{clarity_label}</strong></p>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Sample historical shifts
        shifts = [
            {"date": "2025-05-15", "from": "salesforce.com", "to": "hubspot.com"},
            {"date": "2025-04-28", "from": "hubspot.com", "to": "salesforce.com"},
            {"date": "2025-03-15", "from": "zoho.com", "to": "hubspot.com"}
        ]
        
        if selected_category == "saas":
            st.subheader("Historical Benchmark Shifts")
            
            shift_df = pd.DataFrame(shifts)
            
            st.table(shift_df)
    else:
        st.warning(f"No benchmark defined for category: {selected_category}")
        
        st.info("To create a benchmark, the system needs at least 3 domains in this category with test results.")

def render_insight_scorecard():
    """Render the insight scorecard tab."""
    st.header("System Insight Scorecard")
    
    # Get scorecard data
    scorecard = im.get_scorecard()
    
    # Display key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Most Cited Category</div>"
            f"<p>{scorecard.get('most_cited_category', 'Unknown')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Clearest Trust Leader</div>"
            f"<p>{scorecard.get('clearest_trust_leader', 'Unknown')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Most Volatile Category</div>"
            f"<p>{scorecard.get('most_volatile_category', 'Unknown')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Most Flat Category</div>"
            f"<p>{scorecard.get('most_flat_category', 'Unknown')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        top_delta = scorecard.get('top_trust_delta', {})
        delta_value = top_delta.get('delta', '0.0')
        delta_color = 'data-integrity-high' if delta_value.startswith('+') else 'data-integrity-low'
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Top Trust Delta</div>"
            f"<p>{top_delta.get('domain', 'Unknown')}: <span class='{delta_color}'>{delta_value}</span></p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Lowest Signal Category</div>"
            f"<p>{scorecard.get('lowest_signal_category', 'Unknown')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # Category benchmark completion
    st.subheader("Category Benchmark Completion")
    
    # Sample data for demonstration
    category_completion = {}
    for category in CATEGORIES:
        benchmark = im.get_category_benchmark(category)
        category_completion[category] = {
            "has_benchmark": bool(benchmark and benchmark.get("benchmark_domain")),
            "peer_count": len(benchmark.get("peer_set", [])) if benchmark else 0
        }
    
    # Convert to DataFrame
    completion_data = []
    
    for category, data in category_completion.items():
        status = "Complete" if data["has_benchmark"] and data["peer_count"] >= 3 else "Incomplete"
        completion_data.append({
            "category": category,
            "status": status,
            "peer_count": data["peer_count"],
            "has_benchmark": data["has_benchmark"]
        })
    
    # Create DataFrame
    df = pd.DataFrame(completion_data)
    
    # Create chart
    fig = px.bar(
        df,
        x="category",
        y="peer_count",
        color="status",
        color_discrete_map={"Complete": "#198754", "Incomplete": "#dc3545"},
        labels={
            "category": "Category",
            "peer_count": "Peer Count",
            "status": "Status"
        },
        title="Category Benchmark Completion"
    )
    
    # Add threshold line
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(CATEGORIES) - 0.5,
        y0=3,
        y1=3,
        line=dict(
            color="red",
            width=2,
            dash="dash"
        )
    )
    
    # Add annotation for threshold
    fig.add_annotation(
        x=0,
        y=3.2,
        text="Minimum Peer Threshold",
        showarrow=False,
        font=dict(
            color="red"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trust signal distribution
    st.subheader("Trust Signal Distribution Across Categories")
    
    # Sample trust signal data
    trust_signal = {}
    for category in CATEGORIES:
        # Get domains in category
        domains_by_category = db.load_domains_by_category()
        category_domains = domains_by_category.get(category, [])
        
        # Calculate average score
        scores = []
        for domain_info in category_domains:
            domain = domain_info.get("domain", "")
            if domain:
                result = db.get_latest_domain_result(domain)
                if result:
                    scores.append(result.get("visibility_score", 0))
        
        trust_signal[category] = {
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "domain_count": len(category_domains)
        }
    
    # Convert to DataFrame
    signal_data = []
    
    for category, data in trust_signal.items():
        signal_data.append({
            "category": category,
            "avg_score": data["avg_score"],
            "domain_count": data["domain_count"]
        })
    
    # Create DataFrame
    df = pd.DataFrame(signal_data)
    
    # Sort by average score
    df = df.sort_values("avg_score", ascending=False)
    
    # Create chart
    fig = px.bar(
        df,
        x="category",
        y="avg_score",
        color="domain_count",
        color_continuous_scale="Viridis",
        labels={
            "category": "Category",
            "avg_score": "Average LLMRank Score",
            "domain_count": "Domain Count"
        },
        title="Trust Signal Distribution Across Categories"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_delivery_scoring():
    """Render the delivery scoring tab."""
    st.header("Replit Delivery Scoring Protocol")
    
    # Get delivery scorecard
    delivery_scorecard = rdp.get_scorecard()
    
    # Get grading summary
    grading_summary = rdp.get_grading_summary()
    
    # Display scorecard header
    st.subheader("Delivery Scorecard")
    
    # Format the score with appropriate styling
    score = delivery_scorecard.get("score", "C")
    score_color = "#198754" if score.startswith("A") else "#fd7e14" if score.startswith("B") else "#dc3545"
    
    st.markdown(
        f"<div style='background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>"
        f"<div style='display: flex; justify-content: space-between; align-items: center;'>"
        f"<div>"
        f"<h3 style='margin-bottom: 5px;'>Week of {delivery_scorecard.get('week', 'N/A')}</h3>"
        f"<p style='color: #6c757d;'>PRD Version: {grading_summary.get('prd_version', 'N/A')}</p>"
        f"</div>"
        f"<div style='background-color: {score_color}; color: white; font-size: 32px; font-weight: bold; width: 60px; height: 60px; border-radius: 50%; display: flex; justify-content: center; align-items: center;'>"
        f"{score}"
        f"</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Modules Delivered",
            value=delivery_scorecard.get("modules_delivered", 0)
        )
    
    with col2:
        scan_delta = delivery_scorecard.get("scan_volume_delta", 0)
        delta_str = f"+{scan_delta}" if scan_delta > 0 else str(scan_delta)
        
        st.metric(
            label="Scan Volume Delta",
            value=scan_delta,
            delta=delta_str
        )
    
    with col3:
        yield_rate = delivery_scorecard.get("insight_yield_rate", 0)
        
        st.metric(
            label="Insight Yield Rate",
            value=f"{yield_rate:.0%}"
        )
    
    with col4:
        trust_deltas = delivery_scorecard.get("new_trust_deltas_detected", 0)
        
        st.metric(
            label="Trust Deltas Detected",
            value=trust_deltas
        )
    
    # Display additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        flat_benchmarks = delivery_scorecard.get("flat_benchmarks_detected", 0)
        
        st.metric(
            label="Flat Benchmarks Detected",
            value=flat_benchmarks
        )
    
    with col2:
        invalid_prompts = delivery_scorecard.get("invalid_prompts_removed", 0)
        
        st.metric(
            label="Invalid Prompts Removed",
            value=invalid_prompts
        )
    
    with col3:
        watchlist_updates = delivery_scorecard.get("watchlist_updates", 0)
        
        st.metric(
            label="Watchlist Updates",
            value=watchlist_updates
        )
    
    # Display notes
    notes = delivery_scorecard.get("notes", "")
    
    st.markdown(
        f"<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;'>"
        f"<h4>Delivery Notes:</h4>"
        f"<p>{notes}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Display grading criteria
    st.subheader("Grading Criteria by PRD Version")
    
    grading_criteria = [
        {
            "version": "V1",
            "modules": "Scanner, Crawler, LLM API, Score Engine",
            "focus": "Crawl/score functioning w/ basic logic"
        },
        {
            "version": "V2",
            "modules": "Prompt manager, secure storage, streamlit UI",
            "focus": "Prompt versioning + scan normalization"
        },
        {
            "version": "V3",
            "modules": "Benchmarking, peer set enforcement, FOMA triggers",
            "focus": "Peer scoring + delta detection"
        },
        {
            "version": "V4",
            "modules": "Insight agent, FOMA generator, leaderboard drift",
            "focus": "Movement logs + category deltas"
        },
        {
            "version": "V5",
            "modules": "Recursive scoring, QA metrics, system dashboard",
            "focus": "Self-evaluation + insight audit trail"
        }
    ]
    
    # Create DataFrame
    criteria_df = pd.DataFrame(grading_criteria)
    
    # Display as table
    st.table(criteria_df)
    
    # Display grading summary
    st.subheader("System Grading Summary")
    
    scorecard_data = grading_summary.get("scorecard", {})
    
    # Format status colors
    status_colors = {
        "excellent": "#198754",
        "good": "#20c997",
        "stable": "#0dcaf0",
        "stalled": "#dc3545",
        "active": "#198754",
        "moderate": "#fd7e14",
        "struggling": "#dc3545",
        "comprehensive": "#198754",
        "enabled": "#0dcaf0",
        "limited": "#fd7e14",
        "disabled": "#dc3545",
        "actively maintained": "#198754",
        "partially stale": "#fd7e14",
        "stale": "#dc3545",
        "strong": "#198754"
    }
    
    # Create HTML for status indicators
    status_html = ""
    
    for key, value in scorecard_data.items():
        display_key = key.replace("_", " ").title()
        color = status_colors.get(value, "#6c757d")
        
        status_html += f"""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <div style="font-weight: bold;">{display_key}</div>
                <div style="color: {color};">{value.title()}</div>
            </div>
            <div style="width: 100%; height: 5px; background-color: #e9ecef; border-radius: 3px; margin-top: 5px;">
                <div style="width: {100 if 'excellent' in value or 'comprehensive' in value or 'actively' in value or 'strong' in value else 75 if 'good' in value or 'active' in value or 'enabled' in value else 50 if 'stable' in value or 'moderate' in value or 'partially' in value or 'limited' in value else 25}%; height: 5px; background-color: {color}; border-radius: 3px;"></div>
            </div>
        </div>
        """
    
    st.markdown(
        f"<div style='background-color: #f8f9fa; padding: 20px; border-radius: 5px;'>"
        f"{status_html}"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Evaluate button
    if st.button("Run Delivery Evaluation"):
        with st.spinner("Evaluating delivery..."):
            # Run evaluation
            updated_scorecard = rdp.evaluate_delivery()
            
            # Display success message
            st.success("Delivery evaluation complete!")
            
            # Display new score
            st.metric(
                label="Updated Score",
                value=updated_scorecard.get("score", "C")
            )
            
            # Offer to refresh
            st.info("Refresh the page to see updated metrics.")

def render_data_signal_review():
    """Render the data signal review tab."""
    st.header("Data Signal Review")
    
    # Get data signal review
    data_signal = im.get_data_signal_review()
    
    # Display validation metrics
    col1, col2 = st.columns(2)
    
    with col1:
        foma_grade = data_signal.get("foma_grade_insights", False)
        foma_color = "data-integrity-high" if foma_grade else "data-integrity-low"
        foma_icon = "✓" if foma_grade else "✗"
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>FOMA-Grade Insights</div>"
            f"<p class='{foma_color}'>{foma_icon} {str(foma_grade).replace('True', 'Yes').replace('False', 'No')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        benchmark_stable = data_signal.get("benchmark_leaders_stable", True)
        benchmark_color = "data-integrity-high" if benchmark_stable else "data-integrity-low"
        benchmark_icon = "✓" if benchmark_stable else "✗"
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Benchmark Leaders Stable</div>"
            f"<p class='{benchmark_color}'>{benchmark_icon} {str(benchmark_stable).replace('True', 'Yes').replace('False', 'No')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        right_targets = data_signal.get("scanning_right_targets", True)
        targets_color = "data-integrity-high" if right_targets else "data-integrity-low"
        targets_icon = "✓" if right_targets else "✗"
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Scanning Right Targets</div>"
            f"<p class='{targets_color}'>{targets_icon} {str(right_targets).replace('True', 'Yes').replace('False', 'No')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        reliable_tracking = data_signal.get("tracking_movement_reliably", True)
        tracking_color = "data-integrity-high" if reliable_tracking else "data-integrity-low"
        tracking_icon = "✓" if reliable_tracking else "✗"
        
        st.markdown(
            f"<div class='admin-box'>"
            f"<div class='admin-header'>Tracking Movement Reliably</div>"
            f"<p class='{tracking_color}'>{tracking_icon} {str(reliable_tracking).replace('True', 'Yes').replace('False', 'No')}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # Display corrective action plan if needed
    actions = data_signal.get("corrective_action_plan", [])
    
    if actions:
        st.subheader("Corrective Action Plan")
        
        st.markdown(
            f"<div class='warning-box'>"
            f"<h3>Action Required</h3>"
            f"<p>The following corrective actions are recommended:</p>"
            f"<ul>{''.join('<li>' + action + '</li>' for action in actions)}</ul>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.success("No corrective actions needed at this time.")
    
    # System feedback visualization
    st.subheader("System Feedback Visualization")
    
    # Create metrics for visualization
    metrics = {
        "Insight Yield": data_signal.get("foma_grade_insights", False) * 100,
        "Benchmark Stability": data_signal.get("benchmark_leaders_stable", True) * 100,
        "Target Selection": data_signal.get("scanning_right_targets", True) * 100,
        "Movement Tracking": data_signal.get("tracking_movement_reliably", True) * 100
    }
    
    # Convert to DataFrame
    metrics_df = pd.DataFrame({
        'metric': list(metrics.keys()),
        'value': list(metrics.values())
    })
    
    # Create chart
    fig = px.bar(
        metrics_df,
        x="metric",
        y="value",
        color="value",
        color_continuous_scale=["#dc3545", "#fd7e14", "#198754"],
        range_color=[0, 100],
        labels={
            "metric": "Metric",
            "value": "Score (%)"
        },
        title="System Integrity Metrics"
    )
    
    # Add threshold line at 80%
    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=len(metrics) - 0.5,
        y0=80,
        y1=80,
        line=dict(
            color="#6c757d",
            width=2,
            dash="dash"
        )
    )
    
    # Add annotation for threshold
    fig.add_annotation(
        x=1,
        y=85,
        text="Minimum Acceptable Performance",
        showarrow=False,
        font=dict(
            color="#6c757d"
        )
    )
    
    fig.update_layout(
        yaxis=dict(
            range=[0, 100]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Data path matrix
    st.subheader("Data Integrity Paths")
    
    paths = [
        {
            "path": "/system_feedback/scan_integrity_snapshot.json",
            "exists": os.path.exists(f"{SYSTEM_FEEDBACK_DIR}/scan_integrity_snapshot.json"),
            "description": "Tracks overall scan integrity and insight yield"
        },
        {
            "path": "/trust_drift/time_series/{domain}.json",
            "exists": os.path.exists(TRUST_DRIFT_DIR) and len(os.listdir(TRUST_DRIFT_DIR)) > 0,
            "description": "Stores prompt-triggered trust changes for domains"
        },
        {
            "path": "/benchmarks/by_category/{category}.json",
            "exists": os.path.exists(BENCHMARKS_DIR) and len(os.listdir(BENCHMARKS_DIR)) > 0,
            "description": "Establishes category leaders and trust deltas"
        },
        {
            "path": "/admin_insight_console/scorecard.json",
            "exists": os.path.exists(f"{ADMIN_INSIGHT_CONSOLE_DIR}/scorecard.json"),
            "description": "Executive-level insight overview"
        },
        {
            "path": "/admin_insight_console/data_signal_review.json",
            "exists": os.path.exists(f"{ADMIN_INSIGHT_CONSOLE_DIR}/data_signal_review.json"),
            "description": "System-wide alignment with business vision"
        }
    ]
    
    # Convert to DataFrame
    paths_df = pd.DataFrame(paths)
    
    # Fancy display
    for index, row in paths_df.iterrows():
        status = "✅ Available" if row["exists"] else "❌ Missing"
        status_class = "success-box" if row["exists"] else "error-box"
        
        st.markdown(
            f"<div class='{status_class}' style='padding: 10px;'>"
            f"<strong>{row['path']}</strong> - {status}<br>"
            f"{row['description']}"
            f"</div>",
            unsafe_allow_html=True
        )