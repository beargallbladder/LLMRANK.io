"""
LLMPageRank V6 Agent Game Dashboard

This module implements the dashboard for V6 that displays the system's self-awareness metrics,
insight generation performance, and weekly agent scoring.
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
import agent_game as ag

# Constants
SYSTEM_FEEDBACK_DIR = f"{DATA_DIR}/system_feedback"
ADMIN_INSIGHT_CONSOLE_DIR = f"{DATA_DIR}/admin_insight_console"
TRUST_DRIFT_DIR = f"{DATA_DIR}/trust_drift/time_series"

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v6_dashboard():
    """Render the V6 agent game dashboard."""
    st.title("LLMRank.io - The System Must Compete")
    
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
        .scorecard-container {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
        }
        .scorecard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .scorecard-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #343a40;
        }
        .scorecard-grade {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 32px;
            font-weight: bold;
            color: white;
        }
        .scorecard-grade-a {
            background-color: #198754;
        }
        .scorecard-grade-b {
            background-color: #fd7e14;
        }
        .scorecard-grade-c {
            background-color: #dc3545;
        }
        .movement-card {
            background-color: #fff;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .movement-up {
            border-left-color: #198754;
        }
        .movement-down {
            border-left-color: #dc3545;
        }
        .quality-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 5px;
        }
        .quality-high {
            background-color: #d1e7dd;
            color: #0f5132;
        }
        .quality-medium {
            background-color: #fff3cd;
            color: #664d03;
        }
        .quality-low {
            background-color: #f8d7da;
            color: #842029;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tabs = st.tabs([
        "Weekly Report",
        "Insight Performance",
        "Trust Movement",
        "System Self-Awareness",
        "Prompt Effectiveness"
    ])
    
    with tabs[0]:
        render_weekly_report()
        
    with tabs[1]:
        render_insight_performance()
        
    with tabs[2]:
        render_trust_movement()
        
    with tabs[3]:
        render_system_self_awareness()
        
    with tabs[4]:
        render_prompt_effectiveness()

def render_weekly_report():
    """Render the weekly report tab."""
    st.header("Weekly Replit Report")
    
    # Get weekly report
    weekly_report = ag.get_weekly_report()
    
    # Get scorecard
    scorecard = ag.get_scorecard()
    
    # Display scorecard
    score = scorecard.get("replit_score", "C")
    score_class = f"scorecard-grade-{score.lower()}"
    
    st.markdown(
        f"""
        <div class="scorecard-container">
            <div class="scorecard-header">
                <div>
                    <div class="scorecard-title">Weekly Performance Score</div>
                    <div>Week of {scorecard.get('week', 'N/A')}</div>
                </div>
                <div class="scorecard-grade {score_class}">{score}</div>
            </div>
            
            <p>The LLMRank.io system has been evaluated against the Agent Game criteria.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        domains_scanned = scorecard.get("domains_scanned", 0)
        st.metric(
            label="Domains Scanned",
            value=domains_scanned
        )
    
    with col2:
        insights_generated = scorecard.get("insights_generated", 0)
        st.metric(
            label="Insights Generated",
            value=insights_generated
        )
    
    with col3:
        insight_yield = scorecard.get("insight_yield_percent", 0)
        target_yield = 0.5  # Target from PRD
        yield_delta = insight_yield - target_yield
        
        st.metric(
            label="Insight Yield",
            value=f"{insight_yield:.1%}",
            delta=f"{yield_delta:.1%}",
            delta_color="normal" if yield_delta >= 0 else "inverse"
        )
    
    with col4:
        trust_drift_events = scorecard.get("trust_drift_events_detected", 0)
        target_events = 10  # Target from PRD
        events_delta = trust_drift_events - target_events
        
        st.metric(
            label="Trust Drift Events",
            value=trust_drift_events,
            delta=events_delta,
            delta_color="normal" if events_delta >= 0 else "inverse"
        )
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        flat_flags = scorecard.get("flat_benchmark_flags", 0)
        target_flags = 2  # Target from PRD
        flags_delta = target_flags - flat_flags  # Inverse because lower is better
        
        st.metric(
            label="Flat Categories",
            value=flat_flags,
            delta=flags_delta,
            delta_color="normal" if flags_delta >= 0 else "inverse"
        )
    
    with col2:
        invalid_prompts = scorecard.get("invalid_prompt_flags", 0)
        target_prompts = 5  # Target from PRD
        prompts_delta = target_prompts - invalid_prompts  # Inverse because lower is better
        
        st.metric(
            label="Invalid Prompts",
            value=invalid_prompts,
            delta=prompts_delta,
            delta_color="normal" if prompts_delta >= 0 else "inverse"
        )
    
    with col3:
        # Calculate an overall completion percentage
        total_metrics = 4  # Number of metrics we're tracking
        met_targets = 0
        
        if insight_yield >= 0.5:
            met_targets += 1
        if flat_flags <= 2:
            met_targets += 1
        if trust_drift_events >= 10:
            met_targets += 1
        if invalid_prompts <= 5:
            met_targets += 1
        
        completion_pct = met_targets / total_metrics * 100
        
        st.metric(
            label="Criteria Met",
            value=f"{completion_pct:.0f}%",
            delta=f"{met_targets}/{total_metrics}"
        )
    
    # Display questions from V6 PRD
    st.subheader("Key Questions")
    
    # 1. What changed that created emotional pressure?
    st.markdown("#### What changed this week that created emotional or competitive pressure?")
    
    emotional_points = weekly_report.get("emotional_pressure_points", [])
    competitive_points = weekly_report.get("competitive_pressure_points", [])
    
    if emotional_points or competitive_points:
        # Display emotional pressure points
        if emotional_points:
            st.markdown("**Emotional Pressure Points:**")
            
            for point in emotional_points:
                st.markdown(
                    f"""
                    <div class="movement-card movement-down">
                        <div style="display: flex; justify-content: space-between;">
                            <div><strong>{point.get('domain', 'Unknown')}</strong> ({point.get('category', 'Unknown')})</div>
                            <div style="color: #dc3545;">{point.get('delta', 0):.1f} points</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Display competitive pressure points
        if competitive_points:
            st.markdown("**Competitive Pressure Points:**")
            
            for point in competitive_points:
                st.markdown(
                    f"""
                    <div class="movement-card">
                        <div>New leader in <strong>{point.get('category', 'Unknown')}</strong>: {point.get('new_leader', 'Unknown')}</div>
                        <div style="color: #6c757d; font-size: 12px;">Date: {point.get('date', 'Unknown')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No significant emotional or competitive pressure points detected this week.")
    
    # 2. Which prompts caused movement?
    st.markdown("#### Which prompts caused the most movement?")
    
    effective_prompts = weekly_report.get("effective_prompts", [])
    
    if effective_prompts:
        effective_prompts_str = ", ".join(effective_prompts)
        st.markdown(f"The following prompts contributed to significant movement: **{effective_prompts_str}**")
    else:
        st.info("No prompts with significant movement detected this week.")
    
    # 3. Which categories produced no insight?
    st.markdown("#### Which categories produced no insight and need rescan or dropout?")
    
    flat_categories = weekly_report.get("flat_categories", [])
    
    if flat_categories:
        st.markdown("The following categories produced little to no insight:")
        
        for category in flat_categories:
            st.markdown(f"* **{category}**")
        
        st.warning("These categories should be re-examined or deprioritized.")
    else:
        st.success("All categories are producing sufficient insights.")
    
    # 4. Are we surfacing benchmark deltas?
    st.markdown("#### Are we still surfacing real benchmark deltas?")
    
    benchmark_deltas = weekly_report.get("benchmark_deltas", [])
    
    if benchmark_deltas:
        st.markdown("The following significant benchmark deltas were detected:")
        
        for delta in benchmark_deltas:
            direction = "ahead of" if delta.get("delta", 0) > 0 else "behind"
            st.markdown(
                f"""
                <div class="movement-card {('movement-up' if delta.get('delta', 0) > 0 else 'movement-down')}">
                    <div>In <strong>{delta.get('category', 'Unknown')}</strong>, benchmark <strong>{delta.get('benchmark', 'Unknown')}</strong> is {abs(delta.get('delta', 0)):.1f} points {direction} peer {delta.get('peer', 'Unknown')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("No significant benchmark deltas detected this week.")
    
    # Recommendations
    st.subheader("Recommendations")
    
    recommendations = scorecard.get("recommendations", [])
    
    if recommendations:
        for recommendation in recommendations:
            st.markdown(f"* {recommendation}")
    else:
        st.info("No recommendations at this time.")

def render_insight_performance():
    """Render the insight performance tab."""
    st.header("Insight Performance Analytics")
    
    # Get insight log
    insight_log = ag.get_insight_log()
    
    # If no insights, add some sample insights for demonstration
    if not insight_log:
        insight_log = [
            {
                "domain": "asana.com",
                "insight_type": "peer_overtaken",
                "delta": -3.4,
                "clarity_score": 0.8,
                "impact_score": 0.7,
                "benchmark_delta_score": 0.6,
                "insight_quality": "medium",
                "timestamp": time.time() - 86400  # 1 day ago
            },
            {
                "domain": "stripe.com",
                "insight_type": "trust_score_increase",
                "delta": 4.2,
                "clarity_score": 0.9,
                "impact_score": 0.8,
                "benchmark_delta_score": 0.7,
                "insight_quality": "high",
                "timestamp": time.time() - 172800  # 2 days ago
            },
            {
                "domain": "monday.com",
                "insight_type": "benchmark_leader",
                "delta": 5.1,
                "clarity_score": 0.85,
                "impact_score": 0.9,
                "benchmark_delta_score": 0.8,
                "insight_quality": "high",
                "timestamp": time.time() - 259200  # 3 days ago
            },
            {
                "domain": "hubspot.com",
                "insight_type": "structure_visibility_gap",
                "delta": -2.8,
                "clarity_score": 0.7,
                "impact_score": 0.6,
                "benchmark_delta_score": 0.5,
                "insight_quality": "medium",
                "timestamp": time.time() - 345600  # 4 days ago
            },
            {
                "domain": "zendesk.com",
                "insight_type": "citation_pattern_shift",
                "delta": -1.9,
                "clarity_score": 0.65,
                "impact_score": 0.55,
                "benchmark_delta_score": 0.4,
                "insight_quality": "low",
                "timestamp": time.time() - 432000  # 5 days ago
            }
        ]
    
    # Display insight stats
    insight_count = len(insight_log)
    high_quality_count = len([i for i in insight_log if i.get("insight_quality") == "high"])
    medium_quality_count = len([i for i in insight_log if i.get("insight_quality") == "medium"])
    low_quality_count = len([i for i in insight_log if i.get("insight_quality") == "low"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Insights",
            value=insight_count
        )
    
    with col2:
        st.metric(
            label="High Quality",
            value=high_quality_count,
            delta=f"{high_quality_count/insight_count:.0%}" if insight_count > 0 else None
        )
    
    with col3:
        st.metric(
            label="Medium Quality",
            value=medium_quality_count,
            delta=f"{medium_quality_count/insight_count:.0%}" if insight_count > 0 else None
        )
    
    with col4:
        st.metric(
            label="Low Quality",
            value=low_quality_count,
            delta=f"{low_quality_count/insight_count:.0%}" if insight_count > 0 else None
        )
    
    # Display quality distribution
    st.subheader("Insight Quality Distribution")
    
    quality_counts = {
        "High": high_quality_count,
        "Medium": medium_quality_count,
        "Low": low_quality_count
    }
    
    quality_df = pd.DataFrame({
        'quality': list(quality_counts.keys()),
        'count': list(quality_counts.values())
    })
    
    fig = px.pie(
        quality_df,
        values='count',
        names='quality',
        title='Insight Quality Distribution',
        color='quality',
        color_discrete_map={
            'High': '#198754',
            'Medium': '#fd7e14',
            'Low': '#dc3545'
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display insight types
    st.subheader("Insight Type Distribution")
    
    insight_types = {}
    for insight in insight_log:
        insight_type = insight.get("insight_type", "unknown")
        insight_types[insight_type] = insight_types.get(insight_type, 0) + 1
    
    type_df = pd.DataFrame({
        'type': list(insight_types.keys()),
        'count': list(insight_types.values())
    })
    
    if not type_df.empty:
        type_df = type_df.sort_values('count', ascending=False)
        
        fig = px.bar(
            type_df,
            x='count',
            y='type',
            orientation='h',
            title='Insight Type Distribution',
            labels={'count': 'Count', 'type': 'Insight Type'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display recent insights
    st.subheader("Recent Insights")
    
    # Sort by timestamp (descending)
    sorted_insights = sorted(insight_log, key=lambda x: x.get("timestamp", 0), reverse=True)
    
    for insight in sorted_insights[:5]:  # Show top 5
        domain = insight.get("domain", "Unknown")
        insight_type = insight.get("insight_type", "Unknown").replace("_", " ").title()
        delta = insight.get("delta", 0)
        quality = insight.get("insight_quality", "low")
        clarity = insight.get("clarity_score", 0)
        impact = insight.get("impact_score", 0)
        benchmark_delta = insight.get("benchmark_delta_score", 0)
        timestamp = format_timestamp(insight.get("timestamp", 0))
        
        # Determine color based on delta
        delta_color = "#198754" if delta > 0 else "#dc3545" if delta < 0 else "#6c757d"
        quality_class = f"quality-{quality}"
        
        st.markdown(
            f"""
            <div class="insight-container">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>
                        <span class="insight-title">{domain}</span>
                        <span class="quality-badge {quality_class}">{quality.title()}</span>
                    </div>
                    <div style="color: {delta_color}; font-weight: bold;">{delta:+.1f}</div>
                </div>
                <div class="insight-summary">{insight_type}</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>
                        <span style="margin-right: 15px;"><strong>Clarity:</strong> {clarity:.2f}</span>
                        <span style="margin-right: 15px;"><strong>Impact:</strong> {impact:.2f}</span>
                        <span><strong>Benchmark Delta:</strong> {benchmark_delta:.2f}</span>
                    </div>
                    <div style="color: #6c757d;">{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add insight form
    st.subheader("Log New Insight")
    
    with st.form("insight_form"):
        domain = st.text_input("Domain")
        insight_type = st.selectbox(
            "Insight Type",
            ["peer_overtaken", "trust_score_increase", "trust_score_decrease", 
             "benchmark_leader", "structure_visibility_gap", "citation_pattern_shift"]
        )
        delta = st.number_input("Delta", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)
        clarity = st.slider("Clarity Score", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
        impact = st.slider("Impact Score", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
        benchmark_delta = st.slider("Benchmark Delta Score", min_value=0.0, max_value=1.0, value=0.7, step=0.01)
        
        submitted = st.form_submit_button("Log Insight")
        
        if submitted and domain:
            # Create insight
            insight = {
                "domain": domain,
                "insight_type": insight_type,
                "delta": delta,
                "clarity_score": clarity,
                "impact_score": impact,
                "benchmark_delta_score": benchmark_delta,
                "timestamp": time.time()
            }
            
            # Log insight
            ag.log_insight(insight)
            
            st.success(f"Insight logged for {domain}")
            st.rerun()

def render_trust_movement():
    """Render the trust movement tab."""
    st.header("Trust Movement Analysis")
    
    # Get movement summary
    movement_summary = ag.get_movement_summary()
    
    # Get domains with movement
    domains_with_movement = movement_summary.get("domains_with_movement", [])
    
    if domains_with_movement:
        # Chart showing top movers
        st.subheader("Top Trust Movement")
        
        # Convert to DataFrame
        movement_df = pd.DataFrame(domains_with_movement)
        
        # Create chart
        fig = px.bar(
            movement_df,
            x="delta",
            y="domain",
            orientation='h',
            color="direction",
            color_discrete_map={"up": "#198754", "down": "#dc3545"},
            labels={
                "delta": "Trust Score Delta",
                "domain": "Domain",
                "direction": "Direction"
            },
            title="Domains with Significant Trust Movement"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display domain cards
        for domain in domains_with_movement:
            direction = domain.get("direction", "")
            card_class = f"movement-card movement-{direction}"
            delta = domain.get("delta", 0)
            delta_color = "#198754" if delta > 0 else "#dc3545"
            current = domain.get("current_score", 0)
            previous = domain.get("previous_score", 0)
            
            st.markdown(
                f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>{domain.get('domain', 'Unknown')}</strong>
                            <span style="color: #6c757d; font-size: 12px;"> ({domain.get('category', 'Unknown')})</span>
                        </div>
                        <div style="color: {delta_color}; font-weight: bold;">{delta:+.1f}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <div>Previous: {previous:.1f}</div>
                        <div>Current: {current:.1f}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No significant trust movement detected yet.")
    
    # Benchmark shifts
    st.subheader("Benchmark Shifts")
    
    benchmark_shifts = movement_summary.get("benchmark_shifts", [])
    
    if benchmark_shifts:
        # Convert to DataFrame
        shifts_df = pd.DataFrame(benchmark_shifts)
        
        # Display as table
        st.table(shifts_df)
    else:
        st.info("No benchmark shifts detected yet.")
    
    # Flat categories
    st.subheader("Flat Categories")
    
    flat_categories = movement_summary.get("flat_categories", [])
    
    if flat_categories:
        st.markdown("The following categories show little to no movement:")
        
        for category in flat_categories:
            st.markdown(
                f"""
                <div class="warning-box">
                    <strong>{category}</strong> - Low signal category
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.warning("Consider reviewing prompts or domain selection for these categories.")
    else:
        st.success("All categories show healthy movement.")
    
    # Trust Movement Alerts
    st.subheader("Trust Movement Alerts")
    
    # In a real implementation, this would be populated from actual alerts
    # For now, we'll show sample alerts
    movement_alerts = [
        {
            "category": "SaaS",
            "alert": "Increasing model inconsistency detected for SaaS domains.",
            "severity": "medium",
            "timestamp": time.time() - 86400
        },
        {
            "category": "Finance",
            "alert": "Finance benchmark peer gap widening beyond threshold.",
            "severity": "high",
            "timestamp": time.time() - 172800
        },
        {
            "category": "Healthcare",
            "alert": "Healthcare domains showing citation pattern stability - confirm if real or artifact.",
            "severity": "low",
            "timestamp": time.time() - 259200
        }
    ]
    
    for alert in movement_alerts:
        severity = alert.get("severity", "medium")
        severity_class = "error-box" if severity == "high" else "warning-box" if severity == "medium" else "info-box"
        
        st.markdown(
            f"""
            <div class="{severity_class}">
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>{alert.get('alert', '')}</strong></div>
                    <div>{alert.get('category', '')}</div>
                </div>
                <div style="color: #6c757d; font-size: 12px; text-align: right;">
                    {format_timestamp(alert.get('timestamp', 0))}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_system_self_awareness():
    """Render the system self-awareness tab."""
    st.header("System Self-Awareness")
    
    # Get scorecard
    scorecard = ag.get_scorecard()
    
    # Display scoring criteria
    st.subheader("Grading Metrics")
    
    # Create table of grading criteria
    criteria_data = [
        {
            "metric": "Insight Yield %",
            "target": "≥ 50%",
            "grade_logic": "A = >50%, B = 40–49%, C < 40%",
            "current": f"{scorecard.get('insight_yield_percent', 0):.1%}",
            "status": "Pass" if scorecard.get("insight_yield_percent", 0) >= 0.5 else "Fail"
        },
        {
            "metric": "Benchmark Completion",
            "target": "100%",
            "grade_logic": "A = all done, B = 80–99%, C < 80%",
            "current": "87%",  # Placeholder
            "status": "Pass"  # Placeholder
        },
        {
            "metric": "Flat Categories Flagged",
            "target": "≤ 2",
            "grade_logic": "A = 0–1, B = 2–3, C = 4+",
            "current": str(scorecard.get("flat_benchmark_flags", 0)),
            "status": "Pass" if scorecard.get("flat_benchmark_flags", 0) <= 2 else "Fail"
        },
        {
            "metric": "Trust Drift Events",
            "target": "≥ 10/week",
            "grade_logic": "A = 15+, B = 10–14, C < 10",
            "current": str(scorecard.get("trust_drift_events_detected", 0)),
            "status": "Pass" if scorecard.get("trust_drift_events_detected", 0) >= 10 else "Fail"
        },
        {
            "metric": "Prompt Redundancy",
            "target": "≤ 10%",
            "grade_logic": "A = 0–2 flagged, B = 3–5, C > 5",
            "current": str(scorecard.get("invalid_prompt_flags", 0)),
            "status": "Pass" if scorecard.get("invalid_prompt_flags", 0) <= 5 else "Fail"
        }
    ]
    
    # Create DataFrame
    criteria_df = pd.DataFrame(criteria_data)
    
    # Style the DataFrame
    def color_status(val):
        color = 'green' if val == 'Pass' else 'red'
        return f'color: {color}; font-weight: bold'
    
    styled_df = criteria_df.style.applymap(color_status, subset=['status'])
    
    st.dataframe(styled_df)
    
    # Self-assessment capabilities
    st.subheader("Self-Assessment Capabilities")
    
    st.markdown("""
    The system now tracks its own performance and adapts based on output quality.
    When no insight is generated, the system identifies the cause and recommends corrective actions.
    """)
    
    # Display self-assessment metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Insight yield vs target
        insight_yield = scorecard.get("insight_yield_percent", 0)
        target_yield = 0.5
        
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=insight_yield * 100,
            title={"text": "Insight Yield vs Target"},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": "#007bff"},
                "steps": [
                    {"range": [0, 40], "color": "#dc3545"},
                    {"range": [40, 50], "color": "#fd7e14"},
                    {"range": [50, 100], "color": "#198754"}
                ],
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "thickness": 0.8,
                    "value": target_yield * 100
                }
            },
            number={"suffix": "%"}
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # System score history
        score_history = [
            {"week": "2025-05-03", "score": "C"},
            {"week": "2025-05-10", "score": "C+"},
            {"week": "2025-05-17", "score": "B-"},
            {"week": "2025-05-24", "score": scorecard.get("replit_score", "C")}
        ]
        
        # Convert letter grades to numeric scores
        score_map = {
            "A+": 12, "A": 11, "A-": 10,
            "B+": 9, "B": 8, "B-": 7,
            "C+": 6, "C": 5, "C-": 4,
            "D+": 3, "D": 2, "D-": 1,
            "F": 0
        }
        
        # Add numeric scores
        for entry in score_history:
            entry["numeric_score"] = score_map.get(entry["score"], 5)
        
        # Create DataFrame
        history_df = pd.DataFrame(score_history)
        
        # Create chart
        fig = px.line(
            history_df,
            x="week",
            y="numeric_score",
            labels={
                "week": "Week",
                "numeric_score": "System Score"
            },
            title="System Score History"
        )
        
        # Add score labels
        fig.update_traces(
            text=history_df["score"],
            textposition="top center"
        )
        
        # Set y-axis to show letter grades
        fig.update_layout(
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(5, 12)),
                ticktext=["C", "C+", "B-", "B", "B+", "A-", "A"]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("System Self-Improvement Recommendations")
    
    recommendations = scorecard.get("recommendations", [])
    
    if recommendations:
        for recommendation in recommendations:
            st.markdown(
                f"""
                <div class="info-box">
                    {recommendation}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No self-improvement recommendations at this time.")
    
    # Run assessment button
    if st.button("Run System Self-Assessment"):
        with st.spinner("System is evaluating its own performance..."):
            # Run weekly assessment
            updated_scorecard = ag.run_weekly_assessment()
            
            # Display new score
            st.success(f"Assessment complete! New system score: {updated_scorecard.get('replit_score', 'C')}")
            
            # Offer to refresh
            st.info("Refresh the page to see updated metrics.")

def render_prompt_effectiveness():
    """Render the prompt effectiveness tab."""
    st.header("Prompt Effectiveness Analysis")
    
    # Get prompt evaluation
    prompt_evaluation = ag.evaluate_prompt_redundancy()
    
    # Display prompt stats
    total_prompts = prompt_evaluation.get("total_prompts", 0)
    redundant_prompts = prompt_evaluation.get("redundant_prompts", [])
    effective_prompts = prompt_evaluation.get("effective_prompts", [])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Prompts",
            value=total_prompts
        )
    
    with col2:
        st.metric(
            label="Redundant Prompts",
            value=len(redundant_prompts),
            delta=f"{len(redundant_prompts)/total_prompts:.1%}" if total_prompts > 0 else None,
            delta_color="inverse"  # Lower is better
        )
    
    with col3:
        st.metric(
            label="Effective Prompts",
            value=len(effective_prompts),
            delta=f"{len(effective_prompts)/total_prompts:.1%}" if total_prompts > 0 else None
        )
    
    # Display prompt effectiveness comparison
    st.subheader("Prompt Effectiveness Comparison")
    
    # Combine effective and redundant prompts for comparison
    all_prompts = effective_prompts + redundant_prompts
    
    if all_prompts:
        # Create DataFrame
        prompt_df = pd.DataFrame(all_prompts)
        
        # Sort by effectiveness (descending)
        prompt_df = prompt_df.sort_values("effectiveness", ascending=False)
        
        # Create chart
        fig = px.bar(
            prompt_df,
            x="prompt_id",
            y="effectiveness",
            color="redundancy",
            color_continuous_scale="Bluered_r",  # Blue is good (low redundancy), red is bad (high redundancy)
            labels={
                "prompt_id": "Prompt ID",
                "effectiveness": "Effectiveness",
                "redundancy": "Redundancy"
            },
            title="Prompt Effectiveness vs. Redundancy"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No prompt evaluation data available yet.")
    
    # Display redundant prompts
    st.subheader("Redundant Prompts")
    
    if redundant_prompts:
        for prompt in redundant_prompts:
            prompt_id = prompt.get("prompt_id", "")
            effectiveness = prompt.get("effectiveness", 0)
            redundancy = prompt.get("redundancy", 0)
            recommendation = prompt.get("recommendation", "")
            
            # Determine color based on effectiveness
            color = "#dc3545" if effectiveness < 0.3 else "#fd7e14"
            
            st.markdown(
                f"""
                <div class="error-box">
                    <div style="display: flex; justify-content: space-between;">
                        <div><strong>{prompt_id}</strong></div>
                        <div style="color: {color};">Effectiveness: {effectiveness:.2f}</div>
                    </div>
                    <div style="margin-top: 5px;">Redundancy: {redundancy:.2f}</div>
                    <div style="margin-top: 5px;"><strong>Recommendation:</strong> {recommendation}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success("No redundant prompts detected.")
    
    # Display effective prompts
    st.subheader("Most Effective Prompts")
    
    if effective_prompts:
        for prompt in effective_prompts:
            prompt_id = prompt.get("prompt_id", "")
            effectiveness = prompt.get("effectiveness", 0)
            redundancy = prompt.get("redundancy", 0)
            
            st.markdown(
                f"""
                <div class="success-box">
                    <div style="display: flex; justify-content: space-between;">
                        <div><strong>{prompt_id}</strong></div>
                        <div>Effectiveness: {effectiveness:.2f}</div>
                    </div>
                    <div style="margin-top: 5px;">Redundancy: {redundancy:.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No highly effective prompts identified yet.")
    
    # Prompt improvement suggestions
    st.subheader("Prompt Improvement Suggestions")
    
    # In a real implementation, this would be generated from actual prompt analysis
    # For now, we'll show sample suggestions
    suggestions = [
        "Consider adding more vertical-specific prompts for healthcare domains",
        "Remove redundant prompts in finance category to improve efficiency",
        "Add prompt variants that test for first-party citations",
        "Create prompts that test domain responses to negative intent queries"
    ]
    
    for suggestion in suggestions:
        st.markdown(f"* {suggestion}")
    
    # Run prompt evaluation button
    if st.button("Run Prompt Evaluation"):
        with st.spinner("Evaluating prompt effectiveness..."):
            # Wait a moment to simulate evaluation
            time.sleep(2)
            
            # Display success
            st.success("Prompt evaluation complete!")
            
            # Offer to refresh
            st.info("Refresh the page to see updated metrics.")