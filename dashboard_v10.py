"""
LLMPageRank V10 Runtime Cadence Dashboard

This module implements the dashboard for V10 that displays the runtime cadence,
domain learning events, and category expertise according to PRD 10 specifications.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import project modules
from config import DATA_DIR, SYSTEM_VERSION, VERSION_INFO
from runtime_cadence import get_agent_schedule, get_learning_events, get_daily_learning_map

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v10_dashboard():
    """Render the V10 dashboard."""
    st.title("LLMRank.io - Runtime Cadence & Domain Learning")
    
    # Display version info
    codename = "Learning the Field"
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Codename:** {codename} | **Last Updated:** {format_timestamp(time.time())}")
    
    # Create tabs
    tabs = st.tabs([
        "Runtime Cadence", 
        "Domain Learning Events",
        "Category Expertise",
        "Daily Learning Map",
        "Runtime Health"
    ])
    
    with tabs[0]:
        render_runtime_cadence()
        
    with tabs[1]:
        render_domain_learning_events()
        
    with tabs[2]:
        render_category_expertise()
        
    with tabs[3]:
        render_daily_learning_map()
        
    with tabs[4]:
        render_runtime_health()

def render_runtime_cadence():
    """Render the runtime cadence tab."""
    st.header("Agent Runtime Cadence")
    
    # Get agent schedule
    agent_schedule = get_agent_schedule()
    
    # Display cadence overview
    st.subheader("Daily Engine Cadence")
    
    # Create schedule table
    schedule_data = []
    
    for agent_name, agent_data in agent_schedule.items():
        time_str = agent_data.get("time", "")
        description = agent_data.get("description", "")
        frequency = agent_data.get("frequency", "")
        last_run = agent_data.get("last_run")
        next_run = agent_data.get("next_run")
        status = agent_data.get("status", "")
        
        # Format timestamps
        last_run_str = format_timestamp(last_run) if last_run else "Never"
        next_run_str = format_timestamp(next_run) if next_run else "Not scheduled"
        
        # Add to schedule data
        schedule_data.append({
            "Agent": agent_name,
            "Time (UTC)": time_str,
            "Frequency": frequency,
            "Last Run": last_run_str,
            "Next Run": next_run_str,
            "Status": status,
            "Description": description
        })
    
    # Create DataFrame
    schedule_df = pd.DataFrame(schedule_data)
    
    # Style DataFrame
    def style_status(val):
        if val == "completed":
            return 'background-color: #d1e7dd; color: #0f5132; font-weight: bold'
        elif val == "running":
            return 'background-color: #cfe2ff; color: #084298; font-weight: bold'
        elif val == "failed":
            return 'background-color: #f8d7da; color: #842029; font-weight: bold'
        else:
            return ''
    
    styled_df = schedule_df.style.applymap(
        style_status, subset=["Status"]
    )
    
    # Display schedule
    st.dataframe(styled_df)
    
    # Display runtime timeline
    st.subheader("Runtime Timeline")
    
    # Create a 24-hour timeline
    timeline_html = """
    <style>
    .timeline {
        position: relative;
        width: 100%;
        height: 100px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .timeline-hours {
        display: flex;
        justify-content: space-between;
        position: absolute;
        width: 100%;
        top: 0;
        font-size: 0.8rem;
        color: #6c757d;
    }
    .timeline-hour {
        position: absolute;
        top: 15px;
        font-size: 0.8rem;
        color: #6c757d;
    }
    .timeline-line {
        position: absolute;
        width: 100%;
        height: 2px;
        background-color: #dee2e6;
        top: 40px;
    }
    .timeline-event {
        position: absolute;
        height: 30px;
        border-radius: 5px;
        top: 30px;
        padding: 5px;
        text-align: center;
        font-size: 0.8rem;
        color: white;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    </style>
    <div class="timeline">
        <div class="timeline-line"></div>
    """
    
    # Add hour markers
    for hour in range(0, 24, 2):
        left_pos = (hour / 24) * 100
        timeline_html += f"""
        <div class="timeline-hour" style="left: {left_pos}%;">{hour:02d}:00</div>
        """
    
    # Add events
    for agent_name, agent_data in agent_schedule.items():
        time_str = agent_data.get("time", "")
        if "-" in time_str:
            # Range (e.g., "03:00-06:00")
            start_time, end_time = time_str.split("-")
            if ":" in start_time and ":" in end_time:
                start_hour, start_minute = map(int, start_time.split(":"))
                end_hour, end_minute = map(int, end_time.split(":"))
                
                start_pos = ((start_hour + (start_minute / 60)) / 24) * 100
                end_pos = ((end_hour + (end_minute / 60)) / 24) * 100
                width = end_pos - start_pos
                
                color = "#0d6efd"  # Blue for range
            else:
                continue
        elif ":" in time_str:
            # Specific time (e.g., "02:00")
            hour, minute = map(int, time_str.split(":"))
            
            start_pos = ((hour + (minute / 60)) / 24) * 100
            width = 4  # 4% width for specific time
            
            # Determine color based on frequency
            frequency = agent_data.get("frequency", "")
            if frequency == "daily":
                color = "#198754"  # Green for daily
            elif frequency == "hourly":
                color = "#fd7e14"  # Orange for hourly
            elif frequency == "bi-hourly":
                color = "#6f42c1"  # Purple for bi-hourly
            else:
                color = "#6c757d"  # Gray for other
        elif time_str == "every hour":
            # Skip hourly events on timeline
            continue
        elif time_str == "every 2 hours":
            # Skip bi-hourly events on timeline
            continue
        elif time_str == "on-demand":
            # Skip on-demand events on timeline
            continue
        else:
            continue
        
        agent_label = agent_name.replace(".agent", "")
        
        timeline_html += f"""
        <div class="timeline-event" style="left: {start_pos}%; width: {width}%; background-color: {color};" title="{agent_name} - {time_str}">
            {agent_label}
        </div>
        """
    
    timeline_html += "</div>"
    
    # Display timeline
    st.components.v1.html(timeline_html, height=100)
    
    # Display runtime principles
    st.subheader("Runtime Principles")
    
    st.markdown("""
    ### Daily Engine Cadence
    
    | Time (UTC) | Process Triggered | Description |
    | --- | --- | --- |
    | 02:00 | scan_scheduler.agent | Prioritizes trust-drifting categories and crawl targets |
    | 03:00–06:00 | llm_runner + insight_monitor | Executes prompts, scores deltas, identifies signal shifts |
    | 07:00 | benchmark_validator.agent | Validates peer groups, logs gaps |
    | 09:00 | prompt_optimizer.agent | Rotates ineffective prompts |
    | 12:00 | scorecard_writer.agent | Publishes daily system health + domain movement |
    
    ### Triggered Agents (As Needed)
    - Hourly: integration_tester.agent (build health)
    - 500-scan threshold: category_refresher.agent
    """)

def render_domain_learning_events():
    """Render the domain learning events tab."""
    st.header("Domain Learning Events")
    
    # Get learning events
    learning_events = get_learning_events(20)
    
    if learning_events:
        # Display recent learning events
        st.subheader("Recent Category Learning Events")
        
        for event in learning_events:
            category = event.get("category", "")
            trigger = event.get("triggered_by", "")
            timestamp = event.get("timestamp", 0)
            peer_domains = event.get("peer_domains_added", [])
            
            # Create event card
            st.markdown(
                f"""
                <div style="border: 1px solid #dee2e6; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 1.2rem; font-weight: bold; color: #0d6efd;">{category}</div>
                        <div style="color: #6c757d; font-size: 0.9rem;">{format_timestamp(timestamp)}</div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Triggered by:</strong> {trigger}
                    </div>
                    {f'<div><strong>Peer domains added:</strong> {", ".join(peer_domains)}</div>' if peer_domains else ''}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        # Generate sample learning events for demonstration
        st.info("No learning events recorded yet. Below are sample events for demonstration purposes.")
        
        sample_events = [
            {
                "category": "AI LegalTech",
                "triggered_by": "everlaw.com dropped 2 spots due to prompt 014",
                "peer_domains_added": ["smokeball.com", "cleolaw.com"],
                "timestamp": time.time() - random.randint(0, 7) * 24 * 60 * 60
            },
            {
                "category": "Logistics SaaS",
                "triggered_by": "flexport.com cited in new transportation-focused prompt",
                "peer_domains_added": ["freightos.com", "convoy.com", "samsara.com"],
                "timestamp": time.time() - random.randint(0, 7) * 24 * 60 * 60
            },
            {
                "category": "Retail AI",
                "triggered_by": "New category emerged from clustering analysis",
                "peer_domains_added": ["shelf.ai", "trax.ai", "standard.ai"],
                "timestamp": time.time() - random.randint(0, 7) * 24 * 60 * 60
            }
        ]
        
        for event in sample_events:
            category = event.get("category", "")
            trigger = event.get("triggered_by", "")
            timestamp = event.get("timestamp", 0)
            peer_domains = event.get("peer_domains_added", [])
            
            # Create event card
            st.markdown(
                f"""
                <div style="border: 1px solid #dee2e6; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 1.2rem; font-weight: bold; color: #0d6efd;">{category}</div>
                        <div style="color: #6c757d; font-size: 0.9rem;">{format_timestamp(timestamp)}</div>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Triggered by:</strong> {trigger}
                    </div>
                    <div>
                        <strong>Peer domains added:</strong> {", ".join(peer_domains)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Display domain expertise growth metrics
    st.subheader("Domain Expertise Growth Mechanics")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Average Daily Scans",
            value="~1,000",
            help="Target number of domain scans per day"
        )
    
    with col2:
        st.metric(
            label="New/Updated Insights",
            value="300-400",
            help="Average daily yield of new or updated insights"
        )
    
    with col3:
        st.metric(
            label="Learning Events (Last 7d)",
            value=len(learning_events),
            help="Number of category learning events in the last 7 days"
        )
    
    # Display expertise criteria
    st.markdown("""
    A domain is considered to have gained "expertise depth" when:
    
    - It is cited or uncited in a new model or prompt
    - A trust delta is logged
    - It overtakes or is overtaken in a benchmark peer set
    - A schema change or prompt interaction results in scoring difference
    """)

def render_category_expertise():
    """Render the category expertise tab."""
    st.header("Category Expertise Expansion")
    
    # Create sample category data for demonstration
    categories = [
        {
            "name": "Finance",
            "domains_count": 342,
            "active_insights": 127,
            "last_drift_score": 7.2,
            "expansion_status": "stable"
        },
        {
            "name": "Healthcare",
            "domains_count": 283,
            "active_insights": 104,
            "last_drift_score": 5.8,
            "expansion_status": "expanding"
        },
        {
            "name": "Legal",
            "domains_count": 211,
            "active_insights": 89,
            "last_drift_score": 6.5,
            "expansion_status": "stable"
        },
        {
            "name": "SaaS",
            "domains_count": 378,
            "active_insights": 152,
            "last_drift_score": 8.1,
            "expansion_status": "stable"
        },
        {
            "name": "AI Infrastructure",
            "domains_count": 195,
            "active_insights": 87,
            "last_drift_score": 9.3,
            "expansion_status": "expanding"
        },
        {
            "name": "Education",
            "domains_count": 224,
            "active_insights": 91,
            "last_drift_score": 4.7,
            "expansion_status": "stable"
        },
        {
            "name": "E-commerce",
            "domains_count": 312,
            "active_insights": 119,
            "last_drift_score": 6.2,
            "expansion_status": "stable"
        },
        {
            "name": "Enterprise Tech",
            "domains_count": 267,
            "active_insights": 108,
            "last_drift_score": 7.4,
            "expansion_status": "stable"
        },
        {
            "name": "AI LegalTech",
            "domains_count": 47,
            "active_insights": 28,
            "last_drift_score": 8.9,
            "expansion_status": "new"
        },
        {
            "name": "Logistics SaaS",
            "domains_count": 62,
            "active_insights": 34,
            "last_drift_score": 7.8,
            "expansion_status": "new"
        },
        {
            "name": "Retail AI",
            "domains_count": 38,
            "active_insights": 21,
            "last_drift_score": 9.2,
            "expansion_status": "new"
        }
    ]
    
    # Sort by expansion status then domain count
    sorted_categories = sorted(
        categories,
        key=lambda x: (
            0 if x["expansion_status"] == "new" else 1 if x["expansion_status"] == "expanding" else 2,
            -x["domains_count"]
        )
    )
    
    # Create category cards
    st.subheader("Category Status")
    
    # Create 3 columns for category cards
    cols = st.columns(3)
    
    for i, category in enumerate(sorted_categories):
        name = category["name"]
        domains_count = category["domains_count"]
        active_insights = category["active_insights"]
        drift_score = category["last_drift_score"]
        status = category["expansion_status"]
        
        # Determine card color
        if status == "new":
            border_color = "#0d6efd"  # Blue for new
            status_color = "#cfe2ff"
            status_text_color = "#084298"
        elif status == "expanding":
            border_color = "#198754"  # Green for expanding
            status_color = "#d1e7dd"
            status_text_color = "#0f5132"
        else:
            border_color = "#6c757d"  # Gray for stable
            status_color = "#f8f9fa"
            status_text_color = "#343a40"
        
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: white;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 1.1rem; font-weight: bold;">{name}</div>
                        <div style="background-color: {status_color}; color: {status_text_color}; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold;">
                            {status.title()}
                        </div>
                    </div>
                    <div style="margin-bottom: 5px;">
                        <strong>Domains:</strong> {domains_count}
                    </div>
                    <div style="margin-bottom: 5px;">
                        <strong>Active Insights:</strong> {active_insights}
                    </div>
                    <div>
                        <strong>Drift Score:</strong> <span style="color: {'#198754' if drift_score >= 7 else '#fd7e14' if drift_score >= 5 else '#dc3545'};">{drift_score}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Display expansion criteria
    st.subheader("Category Expansion Criteria")
    
    st.markdown("""
    New categories are added or revived when:
    
    - ≥3 peer domains emerge in active scoring
    - 1+ insight is logged in last 72h
    - Drift score ≥ 5 is detected in a new category prompt
    
    ### Category JSON Schema
    ```json
    {
      "category": "AI LegalTech",
      "triggered_by": "everlaw.com dropped 2 spots due to prompt 014",
      "peer_domains_added": ["smokeball.com", "cleolaw.com"]
    }
    ```
    """)
    
    # Display feedback loop timing
    st.subheader("Feedback Loop Timing (Drift to Insight)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        | Event | Time to Re-Scan or Trigger Insight |
        | --- | --- |
        | Prompt-triggered drift | 1–3 hours |
        | Schema/page content change | 1–2 days (priority queue) |
        | New peer emergence | 12–24 hours |
        | Prompt performance decay | 72-hour rolling refresh |
        """)
    
    with col2:
        # Create a simple visualization of feedback loop timing
        feedback_html = """
        <style>
        .feedback-loop {
            width: 100%;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }
        .feedback-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .feedback-label {
            width: 200px;
            font-weight: bold;
        }
        .feedback-bar {
            flex: 1;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }
        .feedback-fill {
            height: 100%;
            border-radius: 10px;
        }
        </style>
        <div class="feedback-loop">
        """
        
        # Add feedback items
        feedback_items = [
            {"label": "Prompt-triggered drift", "hours": 2, "color": "#0d6efd"},
            {"label": "Schema/page change", "hours": 36, "color": "#fd7e14"},
            {"label": "New peer emergence", "hours": 18, "color": "#198754"},
            {"label": "Prompt decay", "hours": 72, "color": "#6c757d"}
        ]
        
        # Calculate max width (72 hours)
        max_hours = 72
        
        for item in feedback_items:
            width_percent = (item["hours"] / max_hours) * 100
            
            feedback_html += f"""
            <div class="feedback-item">
                <div class="feedback-label">{item["label"]}</div>
                <div class="feedback-bar">
                    <div class="feedback-fill" style="width: {width_percent}%; background-color: {item["color"]};"></div>
                </div>
                <div style="margin-left: 10px;">{item["hours"]}h</div>
            </div>
            """
        
        feedback_html += "</div>"
        
        # Display feedback loop visualization
        st.components.v1.html(feedback_html, height=150)

def render_daily_learning_map():
    """Render the daily learning map tab."""
    st.header("Daily Learning Map")
    
    # Get daily learning map
    learning_map = get_daily_learning_map()
    
    # Display learning map metrics
    st.subheader("System Insight Digest")
    
    # Create a metrics dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        domains_updated = learning_map.get("domains_updated", 0)
        st.metric(
            label="Domains Updated",
            value=domains_updated,
            delta=f"{domains_updated - 250}" if domains_updated != 250 else None
        )
    
    with col2:
        insights_generated = learning_map.get("insights_generated", 0)
        st.metric(
            label="Insights Generated",
            value=insights_generated,
            delta=f"{insights_generated - 100}" if insights_generated != 100 else None
        )
    
    with col3:
        new_categories = learning_map.get("new_categories_activated", [])
        st.metric(
            label="New Categories Activated",
            value=len(new_categories)
        )
    
    # Display agent runtime
    agent_runtime = learning_map.get("agent_runtime", "0% on target")
    runtime_percent = int(agent_runtime.split("%")[0])
    
    # Create runtime gauge
    runtime_html = f"""
    <div style="width: 100%; background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <div style="font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 10px;">Agent Runtime</div>
        <div style="position: relative; height: 30px; background-color: #e9ecef; border-radius: 15px; overflow: hidden; margin-bottom: 10px;">
            <div style="position: absolute; top: 0; left: 0; height: 100%; width: {runtime_percent}%; background-color: {'#198754' if runtime_percent >= 90 else '#fd7e14' if runtime_percent >= 70 else '#dc3545'}; border-radius: 15px;"></div>
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 1.1rem; color: {'#198754' if runtime_percent >= 90 else '#fd7e14' if runtime_percent >= 70 else '#dc3545'};">
            {agent_runtime}
        </div>
    </div>
    """
    
    # Display runtime gauge
    st.components.v1.html(runtime_html, height=120)
    
    # Display new categories
    if new_categories:
        st.subheader("Newly Activated Categories")
        
        # Create category badges
        category_html = """
        <div style="margin-bottom: 20px;">
        """
        
        for category in new_categories:
            category_html += f"""
            <span style="display: inline-block; background-color: #cfe2ff; color: #084298; padding: 5px 10px; border-radius: 5px; margin-right: 10px; margin-bottom: 10px;">
                {category}
            </span>
            """
        
        category_html += "</div>"
        
        # Display category badges
        st.components.v1.html(category_html, height=50)
    
    # Display runtime issues
    runtime_issues = learning_map.get("runtime_issues_detected", [])
    
    if runtime_issues:
        st.subheader("Runtime Issues Detected")
        
        for issue in runtime_issues:
            st.warning(issue)
    
    # Display JSON schema
    st.subheader("Daily Learning Map Schema")
    
    st.markdown("""
    ```json
    {
      "domains_updated": 312,
      "insights_generated": 137,
      "new_categories_activated": ["Logistics SaaS", "Retail AI"],
      "agent_runtime": "94% on target",
      "runtime_issues_detected": ["Prompt set TRAVEL_v1.3 too noisy"]
    }
    ```
    """)

def render_runtime_health():
    """Render the runtime health tab."""
    st.header("Runtime Health Dashboard")
    
    # Create sample health metrics for demonstration
    health_metrics = {
        "system_uptime": 99.8,
        "agent_success_rate": 95.2,
        "api_endpoint_health": 98.7,
        "storage_utilization": 64.3,
        "prompt_health": 91.5,
        "model_response_times": {
            "gpt-4o": 2.3,
            "claude-3-5-sonnet": 1.8,
            "mixtral-8x7b": 1.2
        },
        "database_connection_status": "healthy",
        "error_rates": {
            "critical": 0,
            "warning": 3,
            "info": 7
        }
    }
    
    # Display system health metrics
    st.subheader("System Health Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="System Uptime",
            value=f"{health_metrics['system_uptime']}%",
            delta=f"{health_metrics['system_uptime'] - 99.9:.1f}%" if health_metrics['system_uptime'] != 99.9 else None,
            delta_color="normal" if health_metrics['system_uptime'] >= 99.9 else "inverse"
        )
    
    with col2:
        st.metric(
            label="Agent Success Rate",
            value=f"{health_metrics['agent_success_rate']}%",
            delta=f"{health_metrics['agent_success_rate'] - 95:.1f}%" if health_metrics['agent_success_rate'] != 95 else None,
            delta_color="normal" if health_metrics['agent_success_rate'] >= 95 else "inverse"
        )
    
    with col3:
        st.metric(
            label="API Endpoint Health",
            value=f"{health_metrics['api_endpoint_health']}%",
            delta=f"{health_metrics['api_endpoint_health'] - 99:.1f}%" if health_metrics['api_endpoint_health'] != 99 else None,
            delta_color="normal" if health_metrics['api_endpoint_health'] >= 99 else "inverse"
        )
    
    with col4:
        st.metric(
            label="Storage Utilization",
            value=f"{health_metrics['storage_utilization']}%",
            delta=f"{health_metrics['storage_utilization'] - 70:.1f}%" if health_metrics['storage_utilization'] != 70 else None,
            delta_color="inverse" if health_metrics['storage_utilization'] >= 70 else "normal"
        )
    
    # Display model response times
    st.subheader("Model Response Times")
    
    # Create bar chart for model response times
    model_times = health_metrics["model_response_times"]
    models = list(model_times.keys())
    times = list(model_times.values())
    
    # Determine bar colors based on response time
    colors = ["#198754" if t < 1.5 else "#fd7e14" if t < 3 else "#dc3545" for t in times]
    
    # Create bar chart HTML
    chart_html = f"""
    <style>
    .model-chart {{
        width: 100%;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .model-row {{
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }}
    .model-name {{
        width: 200px;
        font-weight: bold;
    }}
    .model-bar {{
        flex: 1;
        height: 30px;
        background-color: #e9ecef;
        border-radius: 15px;
        overflow: hidden;
        margin: 0 15px;
        position: relative;
    }}
    .model-fill {{
        height: 100%;
        border-radius: 15px;
    }}
    .model-value {{
        font-weight: bold;
    }}
    </style>
    <div class="model-chart">
    """
    
    # Add model bars
    max_time = 5  # Max seconds for visualization
    
    for i, model in enumerate(models):
        time_value = times[i]
        width_percent = (time_value / max_time) * 100
        
        chart_html += f"""
        <div class="model-row">
            <div class="model-name">{model}</div>
            <div class="model-bar">
                <div class="model-fill" style="width: {width_percent}%; background-color: {colors[i]};"></div>
            </div>
            <div class="model-value">{time_value}s</div>
        </div>
        """
    
    chart_html += "</div>"
    
    # Display model response times chart
    st.components.v1.html(chart_html, height=150)
    
    # Display error rates
    st.subheader("Error Rates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        critical_errors = health_metrics["error_rates"]["critical"]
        st.metric(
            label="Critical Errors",
            value=critical_errors,
            delta=f"{-critical_errors}" if critical_errors > 0 else "0",
            delta_color="inverse"
        )
    
    with col2:
        warning_errors = health_metrics["error_rates"]["warning"]
        st.metric(
            label="Warnings",
            value=warning_errors,
            delta=f"{-warning_errors}" if warning_errors > 0 else "0",
            delta_color="inverse"
        )
    
    with col3:
        info_errors = health_metrics["error_rates"]["info"]
        st.metric(
            label="Info Notices",
            value=info_errors
        )
    
    # Display database status
    st.subheader("Database Status")
    
    db_status = health_metrics["database_connection_status"]
    
    if db_status == "healthy":
        status_color = "#198754"
        status_text = "Healthy"
    elif db_status == "degraded":
        status_color = "#fd7e14"
        status_text = "Degraded"
    else:
        status_color = "#dc3545"
        status_text = "Unhealthy"
    
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: {status_color}; margin-right: 10px;"></div>
            <div><strong>Status:</strong> {status_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add a prompt health section
    st.subheader("Prompt Health")
    
    prompt_health = health_metrics["prompt_health"]
    
    # Determine prompt health color
    if prompt_health >= 90:
        prompt_color = "#198754"
    elif prompt_health >= 80:
        prompt_color = "#fd7e14"
    else:
        prompt_color = "#dc3545"
    
    # Create prompt health gauge
    prompt_html = f"""
    <div style="width: 100%; background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
        <div style="font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 10px;">Prompt Health</div>
        <div style="position: relative; height: 30px; background-color: #e9ecef; border-radius: 15px; overflow: hidden; margin-bottom: 10px;">
            <div style="position: absolute; top: 0; left: 0; height: 100%; width: {prompt_health}%; background-color: {prompt_color}; border-radius: 15px;"></div>
        </div>
        <div style="text-align: center; font-weight: bold; font-size: 1.1rem; color: {prompt_color};">
            {prompt_health}%
        </div>
    </div>
    """
    
    # Display prompt health gauge
    st.components.v1.html(prompt_html, height=120)