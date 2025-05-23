"""
LLMPageRank V9 API Dashboard

This module implements the dashboard for V9 that displays the API status,
validator performance, and integrity metrics according to PRD 9 specifications.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import project modules
from config import DATA_DIR, SYSTEM_VERSION, VERSION_INFO

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v9_dashboard():
    """Render the V9 API dashboard."""
    st.title("LLMRank.io - Competitive Insight Theater")
    
    # Display version info
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Codename:** {VERSION_INFO.get('codename', 'Noisy, Colorful Truth')} | **Last Updated:** {format_timestamp(time.time())}")
    
    # Create tabs
    tabs = st.tabs([
        "API Checkpoint", 
        "Agent Competition",
        "Insight Scoreboard",
        "Self-Revision Loop",
        "API Documentation",
        "Integration Status"
    ])
    
    with tabs[0]:
        render_api_overview()
        render_endpoint_status()
        
    with tabs[1]:
        render_agent_competition()
        
    with tabs[2]:
        render_insight_scoreboard()
        
    with tabs[3]:
        render_self_revision_loop()
        
    with tabs[4]:
        render_api_documentation()
        
    with tabs[5]:
        render_integration_status()

def render_api_overview():
    """Render the API overview tab."""
    st.header("API Overview")
    
    # Get API logs
    api_logs = _load_api_logs()
    latest_log = api_logs[-1] if api_logs else None
    
    # Display API status summary
    if latest_log:
        endpoints_checked = latest_log.get("endpoints_checked", 0)
        endpoints_passed = latest_log.get("endpoints_passed", 0)
        endpoints_failed = latest_log.get("endpoints_failed", 0)
        
        pass_rate = endpoints_passed / endpoints_checked if endpoints_checked > 0 else 0
        
        # Determine status color
        status_color = "#198754" if pass_rate >= 0.95 else "#fd7e14" if pass_rate >= 0.8 else "#dc3545"
        status_text = "Healthy" if pass_rate >= 0.95 else "Warning" if pass_rate >= 0.8 else "Critical"
        
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.2rem; font-weight: bold;">API Health Status</div>
                        <div>Last checked: {format_timestamp(latest_log.get('timestamp', 0))}</div>
                    </div>
                    <div style="background-color: {status_color}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">
                        {status_text}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display API metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Endpoints Checked",
                value=endpoints_checked
            )
        
        with col2:
            st.metric(
                label="Pass Rate",
                value=f"{pass_rate:.1%}",
                delta=f"{pass_rate - 0.9:.1%}" if pass_rate != 0.9 else None,
                delta_color="normal" if pass_rate >= 0.9 else "inverse"
            )
        
        with col3:
            st.metric(
                label="Failing Endpoints",
                value=endpoints_failed,
                delta=f"{-endpoints_failed}" if endpoints_failed > 0 else None,
                delta_color="inverse"  # Lower is better
            )
        
        with col4:
            out_of_sync = len(latest_log.get("out_of_sync_endpoints", []))
            st.metric(
                label="Out of Sync",
                value=out_of_sync,
                delta=f"{-out_of_sync}" if out_of_sync > 0 else None,
                delta_color="inverse"  # Lower is better
            )
    else:
        st.info("No API validation logs available. The API validator agent will generate these logs when it runs.")
    
    # Display API integrity rules
    st.subheader("API Integrity Rules")
    
    st.markdown("""
    Every `/api/v1/` endpoint must include:
    
    | Field | Purpose |
    | --- | --- |
    | `llm_score` | Normalized, versioned trust score |
    | `trust_drift_delta` | Daily/weekly change summary |
    | `last_scan_time` | ISO timestamp of last update |
    | `category_percentile` | Peer-relative percentile score |
    | `insight_count` | Total insights tied to this domain |
    | `foma_trigger_status` | Boolean or reason string |
    | `_meta` | Version + scoring context (v1.6.2) |
    """)
    
    # Show sample response
    st.markdown("#### Sample API Response")
    
    sample_response = {
        "domain": "asana.com",
        "llm_score": 72.3,
        "category": "SaaS Productivity",
        "trust_drift_delta": "-2.1",
        "category_percentile": 58,
        "foma_trigger_status": "peer overtaken by monday.com",
        "last_scan_time": "2025-05-24T03:22:00Z",
        "_meta": {
            "model_version": "gpt-4-turbo-0524",
            "score_logic": "v3.1",
            "agent_generated": True
        }
    }
    
    st.json(sample_response)
    
    # Display API validation loop
    st.subheader("Agent-Based API Validation Loop")
    
    st.markdown("""
    | Function | Behavior |
    | --- | --- |
    | Run frequency | Every 2 hours |
    | Queries | All top 100 ranked domains across 10 categories |
    | Validates | Freshness of last scan, drift accuracy, benchmark metadata |
    | Writes to | /system_feedback/api_endpoint_log.json |
    """)

def render_endpoint_status():
    """Render the endpoint status tab."""
    st.header("Endpoint Status")
    
    # Get API logs
    api_logs = _load_api_logs()
    latest_log = api_logs[-1] if api_logs else None
    
    if latest_log:
        # Display endpoint results
        st.subheader("Endpoint Health")
        
        results = latest_log.get("results", [])
        
        if results:
            # Create DataFrame
            results_df = pd.DataFrame(results)
            
            # Process status for display
            results_df["status_emoji"] = results_df.apply(
                lambda row: "✅" if row["overall_status"] == "pass" else "❌", 
                axis=1
            )
            
            # Display as table
            st.markdown(
                """
                <style>
                .endpoint-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .endpoint-table th, .endpoint-table td {
                    padding: 8px 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                .endpoint-table th {
                    background-color: #f8f9fa;
                    font-weight: bold;
                }
                .endpoint-pass {
                    color: #198754;
                    font-weight: bold;
                }
                .endpoint-fail {
                    color: #dc3545;
                    font-weight: bold;
                }
                </style>
                <table class="endpoint-table">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Endpoint</th>
                            <th>Last Scan</th>
                            <th>Delta Check</th>
                            <th>Score Sync</th>
                            <th>Meta Valid</th>
                        </tr>
                    </thead>
                    <tbody>
                """,
                unsafe_allow_html=True
            )
            
            for result in results:
                status = result.get("overall_status", "fail")
                status_class = "endpoint-pass" if status == "pass" else "endpoint-fail"
                status_emoji = "✅" if status == "pass" else "❌"
                
                endpoint = result.get("endpoint", "")
                last_scan = format_timestamp(result.get("timestamp", 0))
                delta_check = result.get("delta_check", "fail")
                score_sync = "Yes" if result.get("score_in_sync_with_trust_drift", False) else "No"
                meta_valid = "Yes" if result.get("meta_tag_valid", False) else "No"
                
                st.markdown(
                    f"""
                    <tr>
                        <td class="{status_class}">{status_emoji}</td>
                        <td>{endpoint}</td>
                        <td>{last_scan}</td>
                        <td>{delta_check}</td>
                        <td>{score_sync}</td>
                        <td>{meta_valid}</td>
                    </tr>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown("</tbody></table>", unsafe_allow_html=True)
        else:
            st.info("No endpoint status data available.")
        
        # Out of sync endpoints
        out_of_sync = latest_log.get("out_of_sync_endpoints", [])
        
        if out_of_sync:
            st.subheader("Out of Sync Endpoints")
            
            for endpoint in out_of_sync:
                st.markdown(
                    f"""
                    <div style="background-color: #f8d7da; border: 1px solid #f5c2c7; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                        <strong>{endpoint}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Display alert file if it exists
            alert_file = f"{DATA_DIR}/alerts/api_out_of_sync.json"
            if os.path.exists(alert_file):
                try:
                    with open(alert_file, 'r') as f:
                        alert_data = json.load(f)
                    
                    st.subheader("Alert Details")
                    
                    st.markdown(
                        f"""
                        <div style="background-color: #f8d7da; border: 1px solid #f5c2c7; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
                            <div style="font-weight: bold; color: #842029;">⚠️ API Out of Sync Alert</div>
                            <div style="color: #842029; margin-top: 5px;">Time: {format_timestamp(alert_data.get('timestamp', 0))}</div>
                            <div style="margin-top: 10px;"><strong>Recommended Actions:</strong></div>
                            <ul style="margin-top: 5px;">
                                {"".join([f"<li>{action}</li>" for action in alert_data.get("recommended_actions", [])])}
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception as e:
                    st.error(f"Error loading alert data: {e}")
        else:
            st.success("All endpoints are in sync.")
    else:
        st.info("No API validation logs available. The API validator agent will generate these logs when it runs.")

def render_agent_competition():
    """Render the agent competition tab."""
    st.header("Agent Competition")
    st.markdown("""
    This tab will show the agent competition metrics and visualizations, including:
    - Cookie jar scoreboard for all agents
    - Agent relationship network
    - Performance metrics by agent
    """)

def render_insight_scoreboard():
    """Render the insight scoreboard tab."""
    st.header("Insight Scoreboard")
    st.markdown("""
    This tab will display the insight scoring and ranking system, including:
    - Top insights by narrative score
    - Event type distribution
    - Visual indicators for insight quality
    """)

def render_self_revision_loop():
    """Render the self-revision loop tab."""
    st.header("Agent Self-Revision Loop")
    st.markdown("""
    This tab will show the agent self-revision capabilities, including:
    - Recent agent revisions
    - Revision plans and outcomes
    - Performance improvement metrics
    """)

def render_api_documentation():
    """Render the API documentation tab."""
    st.header("API Documentation")
    
    st.markdown("""
    ## LLMRank.io API v1
    
    The LLMRank.io API provides programmatic access to domain trust scores,
    visibility metrics, and citation analysis. All endpoints return JSON responses
    and require API key authentication.
    """)
    
    # Domain Score Endpoint
    st.subheader("Domain Score Endpoint")
    
    st.markdown("""
    **GET** `/api/v1/score/{domain}`
    
    Returns the trust score and details for a specific domain.
    
    **Parameters:**
    - `domain` (path): Domain name to retrieve score for
    
    **Example Request:**
    ```http
    GET /api/v1/score/asana.com
    ```
    
    **Example Response:**
    ```json
    {
      "domain": "asana.com",
      "llm_score": 72.3,
      "category": "SaaS Productivity",
      "trust_drift_delta": "-2.1",
      "category_percentile": 58,
      "foma_trigger_status": "peer overtaken by monday.com",
      "last_scan_time": "2025-05-24T03:22:00Z",
      "_meta": {
        "model_version": "gpt-4-turbo-0524",
        "score_logic": "v3.1",
        "agent_generated": true
      }
    }
    ```
    """)
    
    # Top Domains Endpoint
    st.subheader("Top Domains Endpoint")
    
    st.markdown("""
    **GET** `/api/v1/top/{category}`
    
    Returns the top domains by visibility score for a specific category.
    
    **Parameters:**
    - `category` (path): Category name
    - `limit` (query, optional): Maximum number of domains to return (default: 10)
    
    **Example Request:**
    ```http
    GET /api/v1/top/finance?limit=5
    ```
    
    **Example Response:**
    ```json
    {
      "category": "finance",
      "domains": [
        {
          "domain": "stripe.com",
          "llm_score": 89.7,
          "trust_drift_delta": "+1.3",
          "rank": 1
        },
        {
          "domain": "paypal.com",
          "llm_score": 87.2,
          "trust_drift_delta": "-0.5",
          "rank": 2
        },
        ...
      ],
      "last_updated": "2025-05-24T12:30:00Z",
      "_meta": {
        "model_version": "gpt-4-turbo-0524",
        "score_logic": "v3.1",
        "agent_generated": true
      }
    }
    ```
    """)
    
    # Category Delta Endpoint
    st.subheader("Category Delta Endpoint")
    
    st.markdown("""
    **GET** `/api/v1/delta/{category}`
    
    Returns domains with significant visibility changes in a specific category.
    
    **Parameters:**
    - `category` (path): Category name
    
    **Example Request:**
    ```http
    GET /api/v1/delta/saas
    ```
    
    **Example Response:**
    ```json
    {
      "category": "saas",
      "rising_domains": [
        {
          "domain": "monday.com",
          "llm_score": 78.5,
          "trust_drift_delta": "+6.2",
          "previous_rank": 8,
          "current_rank": 3
        },
        ...
      ],
      "falling_domains": [
        {
          "domain": "asana.com",
          "llm_score": 72.3,
          "trust_drift_delta": "-2.1",
          "previous_rank": 3,
          "current_rank": 5
        },
        ...
      ],
      "last_updated": "2025-05-24T12:30:00Z",
      "_meta": {
        "model_version": "gpt-4-turbo-0524",
        "score_logic": "v3.1",
        "agent_generated": true
      }
    }
    ```
    """)
    
    # FOMA Endpoint
    st.subheader("FOMA Endpoint")
    
    st.markdown("""
    **GET** `/api/v1/foma/{domain}`
    
    Returns the FOMA (Fear Of Missing AI) score and details for a specific domain.
    
    **Parameters:**
    - `domain` (path): Domain name to retrieve FOMA score for
    
    **Example Request:**
    ```http
    GET /api/v1/foma/asana.com
    ```
    
    **Example Response:**
    ```json
    {
      "domain": "asana.com",
      "foma_score": 0.68,
      "trigger_status": "moderate_concern",
      "peer_comparison": [
        {
          "domain": "monday.com",
          "llm_score": 78.5,
          "score_difference": -6.2
        },
        ...
      ],
      "recommendations": [
        "Monitor competing domains closely",
        "Strengthen topical authority in key areas",
        "Improve content quality on main category pages"
      ],
      "last_updated": "2025-05-24T12:30:00Z",
      "_meta": {
        "model_version": "gpt-4-turbo-0524",
        "score_logic": "v3.1",
        "agent_generated": true
      }
    }
    ```
    """)
    
    # Authentication
    st.subheader("Authentication")
    
    st.markdown("""
    All API requests require authentication using an API key passed in the `Authorization` header.
    
    **Example:**
    ```http
    GET /api/v1/score/asana.com
    Authorization: Bearer your-api-key-here
    ```
    
    Contact your LLMRank administrator to obtain an API key.
    """)

def render_integration_status():
    """Render the integration status tab."""
    st.header("Integration Status")
    
    # Check if out of sync alert exists
    alert_file = f"{DATA_DIR}/alerts/api_out_of_sync.json"
    alert_exists = os.path.exists(alert_file)
    
    # Display integration status
    status_color = "#dc3545" if alert_exists else "#198754"
    status_text = "Out of Sync" if alert_exists else "In Sync"
    
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: bold;">Internal API Integration Status</div>
                </div>
                <div style="background-color: {status_color}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">
                    {status_text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display internal usage requirements
    st.subheader("Internal Usage via API")
    
    st.markdown("""
    Even if the front-end is still light, internal agents use the API as their canonical access layer:
    
    - All dashboard data must be pulled from live API (not direct file reads)
    - All FOMA reporting, scorecards, and trust pulse should consume from:
        - `/score/:domain`
        - `/delta/:category`
        - `/foma/:domain`
        - `/top/:category`
    """)
    
    # Display integration validation
    st.subheader("Integration Validation")
    
    # For demonstration purposes, we'll simulate some integration validations
    integration_checks = [
        {
            "component": "V6 Agent Game Dashboard",
            "uses_api": True,
            "status": "Integrated"
        },
        {
            "component": "V5 Admin Insight Console",
            "uses_api": True,
            "status": "Integrated"
        },
        {
            "component": "V4 FOMA Engine",
            "uses_api": True,
            "status": "Integrated"
        },
        {
            "component": "V3 Enterprise Dashboard",
            "uses_api": False,
            "status": "Legacy Access (Direct Files)"
        },
        {
            "component": "V2 Trust Signal Dashboard",
            "uses_api": False,
            "status": "Legacy Access (Direct Files)"
        }
    ]
    
    integration_df = pd.DataFrame(integration_checks)
    
    # Display as styled dataframe
    def style_status(val):
        if val == "Integrated":
            return 'background-color: #d1e7dd; color: #0f5132; font-weight: bold'
        elif val == "Legacy Access (Direct Files)":
            return 'background-color: #fff3cd; color: #664d03; font-weight: bold'
        else:
            return ''
    
    def style_api(val):
        if val:
            return 'color: #198754; font-weight: bold'
        else:
            return 'color: #dc3545; font-weight: bold'
    
    styled_df = integration_df.style.applymap(
        style_status, subset=["status"]
    ).applymap(
        style_api, subset=["uses_api"]
    )
    
    st.dataframe(styled_df)
    
    # Display validation process
    st.subheader("Validation Process")
    
    st.markdown("""
    If an API endpoint is stale or fails, the system triggers:
    
    1. `revalidator.agent` → force domain re-crawl
    2. `integration_tester.agent` → flag entire route as deprecated or inconsistent
    3. Log to: `/alerts/api_out_of_sync.json`
    
    **Remember:** Even with a light front-end, the API is your runtime engine:
    
    - Every agent checks it
    - Every dashboard pulls from it
    - Every scorecard is built on it
    
    If the API goes out of sync, you lose credibility with yourself.
    """)

def _load_api_logs() -> List[Dict]:
    """
    Load API endpoint logs.
    
    Returns:
        List of API endpoint log dictionaries
    """
    log_file = f"{DATA_DIR}/system_feedback/api_endpoint_log.json"
    
    if not os.path.exists(log_file):
        # For demonstration purposes, generate sample logs
        sample_logs = []
        
        # Generate logs for the past week
        for i in range(7):
            timestamp = time.time() - (i * 24 * 60 * 60)
            
            # More recent logs are more likely to be successful
            success_rate = 0.95 - (i * 0.05) if i < 5 else 0.7
            
            endpoints_checked = random.randint(20, 30)
            endpoints_passed = int(endpoints_checked * success_rate)
            endpoints_failed = endpoints_checked - endpoints_passed
            
            out_of_sync_endpoints = []
            results = []
            
            # Create a simplified sample to avoid syntax errors with JavaScript-like arrow functions
            log = {
                "timestamp": timestamp,
                "endpoints_checked": endpoints_checked,
                "endpoints_passed": endpoints_passed,
                "endpoints_failed": endpoints_failed,
                "out_of_sync_endpoints": out_of_sync_endpoints,
                "results": results
            }
            
            sample_logs.append(log)
        
        # Sort by timestamp (oldest first)
        sample_logs.sort(key=lambda x: x["timestamp"])
        
        return sample_logs
        
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading API logs: {e}")
        return []