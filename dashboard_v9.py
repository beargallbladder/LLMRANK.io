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
import math
import requests
from agents.self_revision import get_revision_stats, get_agent_revisions
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

def render_validator_performance():
    """Render the validator performance tab."""
    st.header("API Validator Performance")
    
    # Get API logs
    api_logs = _load_api_logs()
    
    if api_logs:
        # Calculate performance metrics
        total_checks = len(api_logs)
        total_endpoints_checked = sum(log.get("endpoints_checked", 0) for log in api_logs)
        total_endpoints_passed = sum(log.get("endpoints_passed", 0) for log in api_logs)
        total_endpoints_failed = sum(log.get("endpoints_failed", 0) for log in api_logs)
        
        overall_pass_rate = total_endpoints_passed / total_endpoints_checked if total_endpoints_checked > 0 else 0
        
        # Display performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Validation Runs",
                value=total_checks
            )
        
        with col2:
            st.metric(
                label="Total Endpoints Checked",
                value=total_endpoints_checked
            )
        
        with col3:
            st.metric(
                label="Overall Pass Rate",
                value=f"{overall_pass_rate:.1%}"
            )
        
        # Display validation history
        st.subheader("Validation History")
        
        # Create DataFrame for validation history
        history_data = []
        
        for log in api_logs:
            timestamp = log.get("timestamp", 0)
            endpoints_checked = log.get("endpoints_checked", 0)
            endpoints_passed = log.get("endpoints_passed", 0)
            pass_rate = endpoints_passed / endpoints_checked if endpoints_checked > 0 else 0
            
            history_data.append({
                "timestamp": timestamp,
                "formatted_time": format_timestamp(timestamp),
                "endpoints_checked": endpoints_checked,
                "endpoints_passed": endpoints_passed,
                "pass_rate": pass_rate
            })
        
        history_df = pd.DataFrame(history_data)
        
        if not history_df.empty:
            # Create pass rate chart using HTML
            st.markdown("<div style='margin-bottom: 30px;'>", unsafe_allow_html=True)
            
            for i, row in enumerate(history_data):
                pass_rate = row["pass_rate"] * 100
                bar_color = "#198754" if pass_rate >= 95 else "#fd7e14" if pass_rate >= 80 else "#dc3545"
                
                st.markdown(
                    f"""
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div>{row["formatted_time"]}</div>
                            <div>{pass_rate:.1f}%</div>
                        </div>
                        <div style="width: 100%; height: 15px; background-color: #e9ecef; border-radius: 7px;">
                            <div style="width: {pass_rate}%; height: 15px; background-color: {bar_color}; border-radius: 7px;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display most recent validation details
            st.subheader("Most Recent Validation")
            
            latest_log = api_logs[-1]
            st.json(latest_log)
        else:
            st.info("No validation history data available.")
    else:
        st.info("No API validation logs available. The API validator agent will generate these logs when it runs.")
    
    # API validator agent information
    st.subheader("API Validator Agent")
    
    st.markdown("""
    The `api_validator.agent` runs every 2 hours to ensure API integrity:
    
    1. **Validates** all API endpoints for freshness and accuracy
    2. **Detects** out-of-sync endpoints and triggers alerts
    3. **Monitors** data consistency between the API and trust movement
    4. **Ensures** proper metadata and versioning across all responses
    
    When validation fails, the agent triggers the `revalidator.agent` to refresh data
    and ensure all API endpoints stay current.
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
        sample_logs = _generate_sample_logs()
        
        # Save sample logs
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w') as f:
                json.dump(sample_logs, f, indent=2)
            
            return sample_logs
        except Exception as e:
            st.error(f"Error saving sample logs: {e}")
            return []
    
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading API logs: {e}")
        return []

def render_agent_competition():
    """Render the agent competition tab."""
    st.header("Agent Competition")
    
    # Load agents from registry
    registry_file = "agents/registry.json"
    try:
        with open(registry_file, 'r') as f:
            registry = json.load(f)
            agents = registry.get("agents", [])
    except Exception as e:
        st.error(f"Error loading agent registry: {e}")
        agents = []
    
    if agents:
        # Create cookie scoreboard
        st.subheader("Cookie Jar Scoreboard")
        
        st.markdown("""
        <style>
        .cookie-jar {
            width: 100%;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .agent-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .agent-name {
            flex: 2;
            font-weight: bold;
        }
        .agent-cookies {
            flex: 1;
            text-align: right;
            font-weight: bold;
        }
        .cookie-bar {
            flex: 3;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            margin: 0 15px;
            position: relative;
        }
        .cookie-fill {
            height: 100%;
            border-radius: 10px;
            position: absolute;
            top: 0;
            left: 0;
        }
        .agent-status {
            flex: 1;
            text-align: center;
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: bold;
        }
        .strata-gold {
            background-color: #ffd700;
            color: #000;
        }
        .strata-silver {
            background-color: #c0c0c0;
            color: #000;
        }
        .strata-rust {
            background-color: #b7410e;
            color: #fff;
        }
        </style>
        <div class="cookie-jar">
        """, unsafe_allow_html=True)
        
        # Sort agents by cookies (descending)
        sorted_agents = sorted(agents, key=lambda x: x.get("cookies_last_7d", 0), reverse=True)
        
        for agent in sorted_agents:
            name = agent.get("agent_name", "")
            cookies = agent.get("cookies_last_7d", 0)
            status = agent.get("status", "active")
            
            # Determine strata based on cookies
            strata = "Gold" if cookies >= 8 else "Silver" if cookies >= 6 else "Rust"
            strata_class = f"strata-{strata.lower()}"
            
            # Calculate fill percentage (max cookies = 10)
            fill_percent = min(100, (cookies / 10) * 100)
            
            # Determine fill color based on cookies
            if cookies >= 8:
                fill_color = "#ffd700"  # Gold
            elif cookies >= 6:
                fill_color = "#c0c0c0"  # Silver
            elif cookies >= 4:
                fill_color = "#cd7f32"  # Bronze
            else:
                fill_color = "#b7410e"  # Rust
            
            st.markdown(
                f"""
                <div class="agent-row">
                    <div class="agent-name">{name}</div>
                    <div class="cookie-bar">
                        <div class="cookie-fill" style="width: {fill_percent}%; background-color: {fill_color};"></div>
                    </div>
                    <div class="agent-cookies">{cookies:.1f} 🍪</div>
                    <div class="agent-status {strata_class}">{strata}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Competition metrics
        st.subheader("Competition Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gold_count = sum(1 for a in agents if a.get("cookies_last_7d", 0) >= 8)
            st.metric(
                label="Gold Agents",
                value=gold_count,
                delta=f"{gold_count - 3}" if gold_count != 3 else None
            )
        
        with col2:
            total_cookies = sum(a.get("cookies_last_7d", 0) for a in agents)
            avg_cookies = total_cookies / len(agents) if agents else 0
            st.metric(
                label="Avg. Cookies per Agent",
                value=f"{avg_cookies:.1f}",
                delta=f"{avg_cookies - 6.5:.1f}" if avg_cookies != 6.5 else None,
                delta_color="normal" if avg_cookies >= 6.5 else "inverse"
            )
        
        with col3:
            inactive_count = sum(1 for a in agents if a.get("status", "") != "active")
            st.metric(
                label="Inactive Agents",
                value=inactive_count,
                delta=f"{-inactive_count}" if inactive_count > 0 else None,
                delta_color="inverse"  # Lower is better
            )
        
        # Agent relationship diagram
        st.subheader("Agent Relationship Network")
        
        # Generate agent nodes
        nodes = []
        edges = []
        
        for i, agent in enumerate(agents):
            name = agent.get("agent_name", "").replace(".agent", "")
            cookies = agent.get("cookies_last_7d", 0)
            trigger = agent.get("trigger", "unknown")
            
            # Determine node color based on cookies
            if cookies >= 8:
                color = "#ffd700"  # Gold
            elif cookies >= 6:
                color = "#c0c0c0"  # Silver
            elif cookies >= 4:
                color = "#cd7f32"  # Bronze
            else:
                color = "#b7410e"  # Rust
            
            # Add node
            nodes.append({
                "id": i,
                "name": name,
                "cookies": cookies,
                "trigger": trigger,
                "color": color,
                "size": 10 + (cookies * 2)  # Node size based on cookies
            })
            
            # Generate relationships based on triggers
            for j, other_agent in enumerate(agents):
                if i == j:
                    continue
                    
                other_trigger = other_agent.get("trigger", "")
                
                # Create edges based on trigger relationships
                if trigger == "post-scan" and other_trigger == "daily":
                    edges.append({"source": j, "target": i, "value": 2})
                elif trigger == "weekly" and other_trigger == "daily":
                    edges.append({"source": j, "target": i, "value": 1})
                elif trigger == "hourly" and other_trigger == "bi-hourly":
                    edges.append({"source": i, "target": j, "value": 3})
                elif trigger == "on-demand" and other_trigger == "bi-hourly":
                    edges.append({"source": j, "target": i, "value": 4})
        
        # Generate network diagram HTML
        network_html = f"""
        <div id="agent-network" style="height: 500px; background-color: #f8f9fa; border-radius: 10px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
        <script>
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(edges)};
            
            const width = document.getElementById('agent-network').clientWidth;
            const height = 500;
            
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            const svg = d3.select("#agent-network")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
            
            // Node and link visualization would be rendered by D3.js in the browser
            // This is a simplified placeholder that doesn't use JavaScript arrow functions
            // which are causing syntax errors in Python
            
        </script>
        """
        
        # Display network diagram
        st.components.v1.html(network_html, height=500)
    else:
        st.info("No agents found in registry.")
    
    # Agent competition rules
    st.subheader("Competition Rules")
    
    st.markdown("""
    ### The Cookie Economy
    
    Agents receive cookies (🍪) based on their contributions:
    
    | Action | Cookies Earned |
    | --- | --- |
    | Prompt improvement | 0.5 - 2.0 🍪 |
    | Trust movement detection | 1.0 - 3.0 🍪 |
    | Peer reordering | 2.0 - 4.0 🍪 |
    | Narrative clarity | 0.5 - 3.0 🍪 |
    | API integrity | 0.0 - 8.0 🍪 |
    
    ### Strata Ranking
    
    Agents are classified into three strata:
    
    | Strata | Cookie Threshold | Privileges |
    | --- | --- | --- |
    | Gold | ≥ 8.0 🍪 | First access to new data |
    | Silver | ≥ 6.0 🍪 | Standard operational access |
    | Rust | < 6.0 🍪 | Risk of dormancy/rotation |
    
    Agents that fail to earn enough cookies for 3+ cycles are rotated out of the active roster.
    """)

def render_insight_scoreboard():
    """Render the insight scoreboard tab."""
    st.header("Insight Scoreboard")
    
    # Generate sample insights
    sample_insights = []
    for i in range(10):
        event_types = ["rank_drop", "peer_takeover", "prompt_induced", "flat_category", "top_insight"]
        event_type = random.choice(event_types)
        
        # Generate domain based on event type
        if event_type == "rank_drop":
            domain = f"falling{i}.example.com"
        elif event_type == "peer_takeover":
            domain = f"overtaken{i}.example.com"
        elif event_type == "prompt_induced":
            domain = f"prompt{i}.example.com"
        elif event_type == "flat_category":
            domain = f"flat{i}.example.com"
        else:  # top_insight
            domain = f"rising{i}.example.com"
        
        # Generate delta based on event type
        if event_type == "rank_drop":
            delta = -random.uniform(3, 8)
        elif event_type == "peer_takeover":
            delta = -random.uniform(2, 5)
        elif event_type == "prompt_induced":
            delta = random.uniform(-4, 4)
        elif event_type == "flat_category":
            delta = random.uniform(-0.5, 0.5)
        else:  # top_insight
            delta = random.uniform(3, 8)
        
        # Generate narrative score based on event type
        if event_type == "rank_drop" or event_type == "peer_takeover" or event_type == "top_insight":
            narrative_score = random.uniform(0.7, 0.95)
        elif event_type == "prompt_induced":
            narrative_score = random.uniform(0.5, 0.8)
        else:  # flat_category
            narrative_score = random.uniform(0.3, 0.6)
        
        # Generate impact level based on narrative score
        if narrative_score >= 0.8:
            impact_level = "high"
        elif narrative_score >= 0.6:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        # Generate summary based on event type
        if event_type == "rank_drop":
            summary = f"{domain} dropped from #{random.randint(1, 5)} to #{random.randint(6, 10)} in rankings after competitor content updates"
        elif event_type == "peer_takeover":
            summary = f"{domain} was overtaken by peer{i}.example.com in category rankings with a {delta:.1f} point swing"
        elif event_type == "prompt_induced":
            summary = f"{domain} experienced a {delta:+.1f} point shift after prompt changes affected visibility"
        elif event_type == "flat_category":
            summary = f"{domain} shows minimal movement ({delta:+.1f}) in a stable category alongside peers"
        else:  # top_insight
            summary = f"{domain} climbed to top position with a {delta:+.1f} point gain, outpacing all peers"
        
        # Add random peers
        peer_count = random.randint(2, 4)
        peers = [f"peer{j}.example.com" for j in range(peer_count)]
        
        # Add insight
        sample_insights.append({
            "domain": domain,
            "compared_to": peers,
            "delta": delta,
            "summary": summary,
            "narrative_score": narrative_score,
            "impact_level": impact_level,
            "event_type": event_type,
            "timestamp": time.time() - random.randint(0, 7 * 24 * 60 * 60)  # Random time in last week
        })
    
    # Sort insights by narrative score (descending)
    sorted_insights = sorted(sample_insights, key=lambda x: x.get("narrative_score", 0), reverse=True)
    
    # Display insight metrics
    st.subheader("Insight Quality Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_impact = sum(1 for i in sample_insights if i.get("impact_level") == "high")
        st.metric(
            label="High Impact Insights",
            value=high_impact,
            delta=f"{high_impact - 3}" if high_impact != 3 else None,
            delta_color="normal" if high_impact >= 3 else "inverse"
        )
    
    with col2:
        avg_score = sum(i.get("narrative_score", 0) for i in sample_insights) / len(sample_insights)
        st.metric(
            label="Avg. Narrative Score",
            value=f"{avg_score:.2f}",
            delta=f"{avg_score - 0.7:.2f}" if avg_score != 0.7 else None,
            delta_color="normal" if avg_score >= 0.7 else "inverse"
        )
    
    with col3:
        event_types = [i.get("event_type") for i in sample_insights]
        most_common = max(set(event_types), key=event_types.count)
        st.metric(
            label="Most Common Event",
            value=most_common.replace("_", " ").title()
        )
    
    # Visual insight scoreboard
    st.subheader("Top Insights")
    
    # Display insights with visual styling
    for i, insight in enumerate(sorted_insights[:5]):
        domain = insight.get("domain", "")
        summary = insight.get("summary", "")
        delta = insight.get("delta", 0)
        narrative_score = insight.get("narrative_score", 0)
        impact_level = insight.get("impact_level", "low")
        event_type = insight.get("event_type", "")
        timestamp = insight.get("timestamp", 0)
        
        # Determine event type styling
        if event_type == "rank_drop":
            event_color = "#dc3545"  # Red for rank drop
            event_icon = "📉"
            event_title = "Rank Drop"
        elif event_type == "peer_takeover":
            event_color = "#fd7e14"  # Orange for peer takeover
            event_icon = "🔄"
            event_title = "Peer Takeover"
        elif event_type == "prompt_induced":
            event_color = "#ffc107"  # Yellow for prompt induced
            event_icon = "🔥"
            event_title = "Prompt Induced"
        elif event_type == "flat_category":
            event_color = "#6c757d"  # Gray for flat category
            event_icon = "➖"
            event_title = "Flat Category"
        else:  # top_insight
            event_color = "#0d6efd"  # Blue for top insight
            event_icon = "👑"
            event_title = "Top Insight"
        
        # Determine impact level styling
        if impact_level == "high":
            impact_color = "#198754"  # Green for high impact
        elif impact_level == "medium":
            impact_color = "#fd7e14"  # Orange for medium impact
        else:
            impact_color = "#6c757d"  # Gray for low impact
        
        # Format delta
        delta_str = f"{delta:+.1f}" if delta else "0.0"
        delta_color = "#198754" if delta > 0 else "#dc3545" if delta < 0 else "#6c757d"
        
        # Create insight card
        st.markdown(
            f"""
            <div style="border: 1px solid #dee2e6; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: white;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <span style="font-size: 1.2rem; font-weight: bold;">{domain}</span>
                        <span style="margin-left: 10px; color: {delta_color}; font-weight: bold;">{delta_str}</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: {event_color}; color: white; padding: 5px 10px; border-radius: 5px; margin-right: 10px;">
                            <span style="margin-right: 5px;">{event_icon}</span>
                            <span>{event_title}</span>
                        </div>
                        <div style="background-color: {impact_color}; color: white; padding: 5px 10px; border-radius: 5px;">
                            {impact_level.title()} Impact
                        </div>
                    </div>
                </div>
                <div style="margin-bottom: 10px;">
                    {summary}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; color: #6c757d; font-size: 0.9rem;">
                    <div>
                        <span>Narrative Score: </span>
                        <span style="font-weight: bold;">{narrative_score:.2f}</span>
                    </div>
                    <div>
                        {format_timestamp(timestamp)}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Insight distribution
    st.subheader("Insight Event Distribution")
    
    # Count event types
    event_counts = {}
    for insight in sample_insights:
        event_type = insight.get("event_type", "")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    # Create event type distribution
    event_types = list(event_counts.keys())
    event_values = list(event_counts.values())
    
    # Create bar chart HTML
    chart_data = []
    for event_type, count in event_counts.items():
        # Determine event color
        if event_type == "rank_drop":
            color = "#dc3545"
        elif event_type == "peer_takeover":
            color = "#fd7e14"
        elif event_type == "prompt_induced":
            color = "#ffc107"
        elif event_type == "flat_category":
            color = "#6c757d"
        else:  # top_insight
            color = "#0d6efd"
        
        # Format event type name
        name = event_type.replace("_", " ").title()
        
        chart_data.append({
            "name": name,
            "value": count,
            "color": color
        })
    
    chart_html = f"""
    <div style="width: 100%; height: 300px; background-color: #f8f9fa; border-radius: 10px; padding: 20px;">
        <div id="event-chart" style="width: 100%; height: 100%;"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script>
        const data = {json.dumps(chart_data)};
        
        const margin = {{top: 30, right: 30, bottom: 70, left: 60}};
        const width = document.getElementById('event-chart').clientWidth - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;
        
        const svg = d3.select("#event-chart")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        const x = d3.scaleBand()
            .range([0, width])
            .domain(data.map(d => d.name))
            .padding(0.2);
        
        svg.append("g")
            .attr("transform", `translate(0,${{height}}`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "translate(-10,0)rotate(-45)")
            .style("text-anchor", "end");
        
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value) * 1.2])
            .range([height, 0]);
        
        svg.append("g")
            .call(d3.axisLeft(y));
        
        svg.selectAll("bars")
            .data(data)
            .enter()
            .append("rect")
            .attr("x", d => x(d.name))
            .attr("y", d => y(d.value))
            .attr("width", x.bandwidth())
            .attr("height", d => height - y(d.value))
            .attr("fill", d => d.color);
    </script>
    """
    
    # Display chart
    st.components.v1.html(chart_html, height=300)
    
    # Insight standards
    st.subheader("Insight Quality Standards")
    
    st.markdown("""
    ### Insight Quality Metrics
    
    Each insight is scored based on:
    
    | Metric | Weight |
    | --- | --- |
    | Emotional Impact | 40% |
    | Numerical Auditability | 25% |
    | Comparative Clarity | 25% |
    | Temporal Relevance | 10% |
    
    ### Visualization Requirements
    
    Event specific visualizations include:
    
    | Event | Visual Format |
    | --- | --- |
    | Rank drop ≥ 3 | Red spike / cliff |
    | Peer takeover | Arrow sweep / bump |
    | Prompt-induced movement | Prompt heat flames |
    | Flat category | Gray shelf |
    | Top insight of the week | Blue flame crown |
    """)

def render_self_revision_loop():
    """Render the self-revision loop tab."""
    st.header("Agent Self-Revision Loop")
    
    # Get revision stats
    revision_stats = get_revision_stats()
    
    # Display revision metrics
    st.subheader("Revision Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revisions = revision_stats.get("total_revisions", 0)
        st.metric(
            label="Total Revisions",
            value=total_revisions
        )
    
    with col2:
        successful_revisions = revision_stats.get("successful_revisions", 0)
        success_rate = revision_stats.get("success_rate", 0)
        
        st.metric(
            label="Successful Revisions",
            value=successful_revisions,
            delta=f"{successful_revisions - (total_revisions//2)}" if total_revisions > 0 else None,
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.1%}",
            delta=f"{success_rate - 0.75:.1%}" if success_rate != 0.75 else None,
            delta_color="normal" if success_rate >= 0.75 else "inverse"
        )
    
    # Generate or load sample revision data
    revision_examples = []
    
    # If no real data, generate samples
    if total_revisions == 0:
        agents = ["prompt_optimizer.agent", "insight_monitor.agent", "trust_drift.agent", "api_validator.agent"]
        reasons = ["no_prompt_yielded_drift", "data_format_inconsistent", "execution_timeout", "low_insight_yield"]
        
        for i in range(5):
            agent = random.choice(agents)
            reason = random.choice(reasons)
            
            # Generate strategies based on reason
            if reason == "no_prompt_yielded_drift":
                strategies = [
                    "Inject category comparative prompt logic",
                    "Add schema-recency tests",
                    "Drop prompts with trust score overlap"
                ]
            elif reason == "data_format_inconsistent":
                strategies = [
                    "Add schema validation pre-processing",
                    "Normalize output formats",
                    "Implement strict type checking"
                ]
            elif reason == "execution_timeout":
                strategies = [
                    "Optimize data processing loops",
                    "Implement incremental processing",
                    "Add timeout handlers with partial results return"
                ]
            else:  # low_insight_yield
                strategies = [
                    "Enhance narrative clarity metrics",
                    "Implement insight diversity scoring",
                    "Add comparative insight generation"
                ]
            
            # Generate success flag (80% chance of success)
            success = random.random() < 0.8
            
            # Generate before/after metrics
            cookies_before = random.uniform(3, 5.5)
            cookies_after = random.uniform(6, 9) if success else random.uniform(3, 5)
            
            revision_examples.append({
                "agent": agent,
                "timestamp": time.time() - random.randint(0, 30 * 24 * 60 * 60),
                "failure_reason": reason,
                "revision_plan": strategies,
                "status": "completed",
                "success": success,
                "metrics_before": {
                    "cookies_last_7d": cookies_before,
                    "failed_cycles": random.randint(2, 3)
                },
                "metrics_after": {
                    "cookies_last_7d": cookies_after,
                    "failed_cycles": 0 if success else random.randint(1, 2)
                },
                "cookies_improvement": cookies_after - cookies_before
            })
    
    # Display revision examples
    st.subheader("Recent Agent Revisions")
    
    for revision in revision_examples:
        agent = revision.get("agent", "")
        reason = revision.get("failure_reason", "")
        strategies = revision.get("revision_plan", [])
        status = revision.get("status", "")
        success = revision.get("success", False)
        cookies_before = revision.get("metrics_before", {}).get("cookies_last_7d", 0)
        cookies_after = revision.get("metrics_after", {}).get("cookies_last_7d", 0)
        improvement = revision.get("cookies_improvement", 0)
        timestamp = revision.get("timestamp", 0)
        
        # Format reason
        reason_str = reason.replace("_", " ").title()
        
        # Determine status color
        if status == "completed" and success:
            status_color = "#198754"  # Green for success
            status_label = "Success"
        elif status == "completed" and not success:
            status_color = "#dc3545"  # Red for failure
            status_label = "Failed"
        else:
            status_color = "#fd7e14"  # Orange for in progress
            status_label = "In Progress"
        
        # Create revision card
        st.markdown(
            f"""
            <div style="border: 1px solid #dee2e6; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: white;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <span style="font-size: 1.2rem; font-weight: bold;">{agent}</span>
                    </div>
                    <div style="background-color: {status_color}; color: white; padding: 5px 10px; border-radius: 5px;">
                        {status_label}
                    </div>
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Failure Reason:</strong> {reason_str}
                </div>
                <div style="margin-bottom: 15px;">
                    <strong>Revision Strategies:</strong>
                    <ul style="margin-top: 5px; margin-bottom: 5px;">
                        {"".join([f"<li>{strategy}</li>" for strategy in strategies])}
                    </ul>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <strong>Before:</strong> {cookies_before:.1f} 🍪
                    </div>
                    <div style="text-align: center;">
                        <i class="fas fa-arrow-right"></i>
                    </div>
                    <div>
                        <strong>After:</strong> {cookies_after:.1f} 🍪
                    </div>
                    <div>
                        <strong>Improvement:</strong> <span style="color: {'#198754' if improvement > 0 else '#dc3545'};">{improvement:+.1f} 🍪</span>
                    </div>
                </div>
                <div style="color: #6c757d; font-size: 0.9rem; text-align: right;">
                    {format_timestamp(timestamp)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Self-revision process
    st.subheader("Self-Revision Process")
    
    st.markdown("""
    ### Agent Self-Revision Workflow
    
    Agents can self-annotate failures and propose fix strategies:
    
    ```json
    {
      "agent": "prompt_optimizer.agent",
      "failure_reason": "no prompt yielded drift",
      "revision_plan": [
        "Inject category comparative prompt logic",
        "Add schema-recency tests",
        "Drop prompts with trust score overlap"
      ]
    }
    ```
    
    ### Revision Triggers
    
    | Trigger | Description |
    | --- | --- |
    | Low Cookie Count | < 5.0 cookies for 2+ cycles |
    | Failed Cycles | 2+ consecutive failed runs |
    | Strata Drop | Falling from Gold/Silver to Rust |
    | Output Quality | Low narrative scores on insights |
    
    ### Success Metrics
    
    A revision is considered successful when:
    
    1. Agent returns to active status
    2. Cookie count increases by at least 2.0
    3. No failed cycles in the next 3 runs
    """)

def _generate_sample_logs() -> List[Dict]:
    """
    Generate sample API logs for demonstration purposes.
    
    Returns:
        List of sample API log dictionaries
    """
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
        
        # Generate results for endpoints
        for j in range(endpoints_checked):
            endpoint_type = random.choice(["score", "top", "delta", "foma"])
            endpoint_category = random.choice(["finance", "healthcare", "legal", "saas"])
            endpoint_domain = f"example{j}.{endpoint_category}.com"
            
            if endpoint_type == "score":
                endpoint = f"/score/{endpoint_domain}"
            elif endpoint_type == "top":
                endpoint = f"/top/{endpoint_category}"
            elif endpoint_type == "delta":
                endpoint = f"/delta/{endpoint_category}"
            else:  # foma
                endpoint = f"/foma/{endpoint_domain}"
            
            # Determine if this endpoint passes
            passes = random.random() < success_rate
            
            result = {
                "endpoint": endpoint,
                "timestamp": timestamp - random.randint(0, 3600),
                "last_scan_time": datetime.fromtimestamp(timestamp - random.randint(86400, 172800)).isoformat(),
                "delta_check": "pass" if passes else "fail",
                "score_in_sync_with_trust_drift": passes,
                "meta_tag_valid": passes or random.random() < 0.9,  # Meta tags are usually valid
                "recommendations": []
            }
            
            # Add recommendations if needed
            if result["delta_check"] == "fail":
                result["recommendations"].append("Rescan domain to update delta values")
            
            if not result["score_in_sync_with_trust_drift"]:
                result["recommendations"].append("Trust drift needs recalculation")
            
            if not result["meta_tag_valid"]:
                result["recommendations"].append("Update metadata tags to latest version")
            
            # Determine overall status
            result["overall_status"] = "pass" if (
                result["delta_check"] == "pass" and
                result["score_in_sync_with_trust_drift"] and
                result["meta_tag_valid"]
            ) else "fail"
            
            results.append(result)
            
            # Add to out of sync if failing
            if result["overall_status"] == "fail":
                out_of_sync_endpoints.append(endpoint)
        
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