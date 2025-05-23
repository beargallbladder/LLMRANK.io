"""
LLMPageRank V7 Agent-Based Architecture Dashboard

This module implements the dashboard for V7 that displays the agent-based system,
showing agent performance, cookie scores, and system integration status.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import project modules
from config import DATA_DIR, SYSTEM_VERSION, VERSION_INFO
import agents.controller as agent_controller

def format_timestamp(timestamp):
    """Format a timestamp for display."""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

def render_v7_dashboard():
    """Render the V7 agent-based architecture dashboard."""
    st.title("LLMRank.io - Agent-Based Architecture")
    
    # Display version info
    st.markdown(f"**System Version:** {SYSTEM_VERSION} | **Codename:** Compete to Contribute | **Last Updated:** {format_timestamp(time.time())}")
    
    # Create tabs
    tabs = st.tabs([
        "Agent Overview", 
        "Cookie Jar System",
        "Integration Status",
        "Agent Competition",
        "Runtime Control"
    ])
    
    with tabs[0]:
        render_agent_overview()
        
    with tabs[1]:
        render_cookie_jar_system()
        
    with tabs[2]:
        render_integration_status()
        
    with tabs[3]:
        render_agent_competition()
        
    with tabs[4]:
        render_runtime_control()

def render_agent_overview():
    """Render the agent overview tab."""
    st.header("Agent Overview")
    
    # Get agent status
    agent_status = agent_controller.get_agent_status()
    agents = agent_status.get("agents", [])
    
    if not agents:
        st.warning("No agents registered in the system.")
        return
    
    # Display agent count
    total_agents = len(agents)
    active_agents = sum(1 for agent in agents if agent.get("status") == "active")
    dormant_agents = total_agents - active_agents
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Agents",
            value=total_agents
        )
    
    with col2:
        st.metric(
            label="Active Agents",
            value=active_agents,
            delta=f"{active_agents/total_agents:.0%}" if total_agents > 0 else None
        )
    
    with col3:
        st.metric(
            label="Dormant Agents",
            value=dormant_agents,
            delta=f"{dormant_agents/total_agents:.0%}" if total_agents > 0 else None,
            delta_color="inverse"  # Lower is better
        )
    
    # Display agent registry
    st.subheader("Agent Registry")
    
    agent_df = pd.DataFrame(agents)
    if not agent_df.empty:
        # Add current cookies column if missing
        if "current_cookies" not in agent_df.columns:
            agent_df["current_cookies"] = 0
        
        # Select and reorder columns
        display_columns = [
            "agent_name", "version", "task", "trigger", 
            "cookies_last_7d", "current_cookies", "status"
        ]
        
        display_columns = [col for col in display_columns if col in agent_df.columns]
        
        # Style the dataframe
        def style_status(val):
            color = "green" if val == "active" else "red"
            return f"color: {color}; font-weight: bold"
        
        # Convert to styled DataFrame
        styled_df = agent_df[display_columns].style.applymap(
            style_status, subset=["status"]
        )
        
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No agent data available.")
    
    # Display agent roles and responsibilities
    st.subheader("Agent Roles & Responsibilities")
    
    agent_roles = [
        {
            "agent_name": "scan_scheduler.agent",
            "role": "Chooses what to crawl next (category + peer fill)",
            "trigger": "daily"
        },
        {
            "agent_name": "prompt_optimizer.agent",
            "role": "Maintains prompt health, rotates ineffective prompts",
            "trigger": "post-scan"
        },
        {
            "agent_name": "benchmark_validator.agent",
            "role": "Confirms peer group integrity and benchmark readiness",
            "trigger": "weekly"
        },
        {
            "agent_name": "insight_monitor.agent",
            "role": "Scores insight clarity, impact, novelty on all scan outputs",
            "trigger": "post-scan"
        },
        {
            "agent_name": "trust_drift.agent",
            "role": "Logs domain trust movement and model citation drift",
            "trigger": "post-scan"
        },
        {
            "agent_name": "scorecard_writer.agent",
            "role": "Generates admin + Replit performance scorecards",
            "trigger": "weekly"
        },
        {
            "agent_name": "integration_tester.agent",
            "role": "Runs synthetic scan + test across endpoints hourly",
            "trigger": "hourly"
        }
    ]
    
    roles_df = pd.DataFrame(agent_roles)
    st.table(roles_df)

def render_cookie_jar_system():
    """Render the cookie jar system tab."""
    st.header("Cookie Jar System")
    
    # Get cookie jar data
    cookie_jar = agent_controller.get_cookies_jar()
    
    # Get agent status for historical cookies
    agent_status = agent_controller.get_agent_status()
    agents = agent_status.get("agents", [])
    
    # Create cookie comparison data
    cookie_data = []
    
    for agent in agents:
        agent_name = agent.get("agent_name", "unknown")
        cookies_last_7d = agent.get("cookies_last_7d", 0)
        current_cookies = cookie_jar.get(agent_name, 0)
        
        cookie_data.append({
            "agent_name": agent_name,
            "cookies_last_7d": cookies_last_7d,
            "current_cookies": current_cookies,
            "status": agent.get("status", "unknown")
        })
    
    # Display cookie jar metrics
    if cookie_data:
        st.subheader("Current Cookie Performance")
        
        # Create HTML for cookie jar visualization
        cookie_html = """
        <div style="margin-bottom: 20px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Agent</th>
                        <th style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6;">Current Cookies</th>
                        <th style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6;">Last 7 Days Avg</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Cookie Jar</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Sort by last 7 days cookies
        cookie_data.sort(key=lambda x: x["cookies_last_7d"], reverse=True)
        
        for data in cookie_data:
            agent_name = data["agent_name"]
            current = data["current_cookies"]
            last_7d = data["cookies_last_7d"]
            status = data["status"]
            
            # Calculate jar width
            jar_width = min(100, int(last_7d * 10))  # Scale for visualization
            
            # Status color
            status_color = "#198754" if status == "active" else "#dc3545"
            
            cookie_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                    <span style="color: {status_color};">●</span> {agent_name}
                </td>
                <td style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6;">{current:.1f}</td>
                <td style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6;">{last_7d:.1f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                    <div style="width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px;">
                        <div style="width: {jar_width}%; height: 20px; background-color: #fd7e14; border-radius: 10px;"></div>
                    </div>
                </td>
            </tr>
            """
        
        cookie_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(cookie_html, unsafe_allow_html=True)
    else:
        st.info("No cookie data available yet.")
    
    # Display rules of the cookie system
    st.subheader("Cookie Reward System")
    
    cookie_rules = [
        {
            "action": "Successful hourly integration test",
            "cookies": "1.0"
        },
        {
            "action": "Detecting and logging trust drift event",
            "cookies": "2.0"
        },
        {
            "action": "Identifying and removing ineffective prompt",
            "cookies": "1.5"
        },
        {
            "action": "Generating high-quality insight",
            "cookies": "1.0"
        },
        {
            "action": "Validating benchmark integrity",
            "cookies": "1.5"
        },
        {
            "action": "Producing comprehensive weekly report",
            "cookies": "2.0"
        },
        {
            "action": "Optimizing scan schedule efficiency",
            "cookies": "1.5"
        }
    ]
    
    rules_df = pd.DataFrame(cookie_rules)
    st.table(rules_df)
    
    # Dormancy rules
    st.markdown("""
    **Dormancy Rules:**
    
    * Agents earn cookies based on their value contribution
    * If no cookies are earned for 2 evaluation cycles → agent is marked as dormant
    * Dormant agents can be reactivated by earning cookies
    * The cookie jar is updated every 2 days
    """)

def render_integration_status():
    """Render the integration status tab."""
    st.header("Integration Status")
    
    # Try to load integration tester module
    integration_status = None
    integration_history = None
    
    try:
        from agents.integration_tester import get_latest_status, get_status_history
        integration_status = get_latest_status()
        integration_history = get_status_history()
    except Exception as e:
        st.error(f"Unable to load integration status: {e}")
    
    # Display latest status
    if integration_status:
        status = integration_status.get("result", "unknown")
        status_color = "#198754" if status == "pass" else "#dc3545"
        
        st.markdown(
            f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.2rem; font-weight: bold;">System Integration Status</div>
                        <div>Last tested: {format_timestamp(integration_status.get('timestamp', 0))}</div>
                    </div>
                    <div style="background-color: {status_color}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">
                        {status.upper()}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display test details
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Test Domain",
                value=integration_status.get("test_domain", "N/A")
            )
        
        with col2:
            model_response = integration_status.get("model_response", "unknown")
            st.metric(
                label="Model Response",
                value=model_response,
                delta="Success" if model_response == "success" else "Failure",
                delta_color="normal" if model_response == "success" else "inverse"
            )
        
        with col3:
            score_generated = integration_status.get("score_generated", False)
            st.metric(
                label="Score Generated",
                value="Yes" if score_generated else "No",
                delta="Success" if score_generated else "Failure",
                delta_color="normal" if score_generated else "inverse"
            )
        
        with col4:
            latency_ms = integration_status.get("latency_ms", 0)
            st.metric(
                label="Latency",
                value=f"{latency_ms} ms"
            )
    else:
        st.warning("No integration test results available.")
    
    # Display history
    if integration_history:
        st.subheader("Integration Test History")
        
        # Create DataFrame
        history_df = pd.DataFrame(integration_history)
        
        if not history_df.empty:
            # Format timestamp column
            if "timestamp" in history_df.columns:
                history_df["timestamp"] = history_df["timestamp"].apply(format_timestamp)
            
            # Style the dataframe
            def style_result(val):
                color = "green" if val == "pass" else "red"
                return f"color: {color}; font-weight: bold"
            
            styled_df = history_df.style.applymap(
                style_result, subset=["result"]
            )
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Analyze trends
            pass_rate = sum(1 for r in integration_history if r.get("result") == "pass") / len(integration_history)
            avg_latency = sum(r.get("latency_ms", 0) for r in integration_history) / len(integration_history)
            
            st.markdown(f"""
            **Integration Test Trends:**
            
            * **Pass Rate:** {pass_rate:.1%}
            * **Average Latency:** {avg_latency:.0f} ms
            * **Tests Completed:** {len(integration_history)}
            """)
        else:
            st.info("No test history data available.")
    
    # Alert history
    alert_file = f"{DATA_DIR}/system_feedback/integration_alert.json"
    if os.path.exists(alert_file):
        try:
            with open(alert_file, 'r') as f:
                alert_data = json.load(f)
            
            st.subheader("System Alerts")
            
            st.markdown(
                f"""
                <div style="background-color: #f8d7da; border: 1px solid #f5c2c7; border-radius: 5px; padding: 15px; margin-bottom: 15px;">
                    <div style="font-weight: bold; color: #842029;">⚠️ {alert_data.get('message', 'System Alert')}</div>
                    <div style="color: #842029; margin-top: 5px;">Time: {format_timestamp(alert_data.get('timestamp', 0))}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error loading alert data: {e}")

def render_agent_competition():
    """Render the agent competition tab."""
    st.header("Agent Competition")
    
    # Get agent status
    agent_status = agent_controller.get_agent_status()
    agents = agent_status.get("agents", [])
    
    if not agents:
        st.warning("No agents registered in the system.")
        return
    
    # Group agents by trigger type
    trigger_groups = {}
    for agent in agents:
        trigger = agent.get("trigger", "unknown")
        if trigger not in trigger_groups:
            trigger_groups[trigger] = []
        trigger_groups[trigger].append(agent)
    
    # Display competition by trigger type
    for trigger, trigger_agents in trigger_groups.items():
        st.subheader(f"{trigger.title()} Agents Competition")
        
        # Sort by cookies (descending)
        trigger_agents.sort(key=lambda x: x.get("cookies_last_7d", 0), reverse=True)
        
        # Create competition leaderboard
        competition_html = """
        <div style="margin-bottom: 30px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Rank</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Agent</th>
                        <th style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6;">Cookies (7d)</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Status</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6;">Performance</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, agent in enumerate(trigger_agents):
            agent_name = agent.get("agent_name", "unknown")
            cookies = agent.get("cookies_last_7d", 0)
            status = agent.get("status", "unknown")
            
            # Calculate medal and styling
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
            rank_color = "#FFD700" if i == 0 else "#C0C0C0" if i == 1 else "#CD7F32" if i == 2 else ""
            status_color = "#198754" if status == "active" else "#dc3545"
            
            # Calculate performance bar width
            max_cookies = max(a.get("cookies_last_7d", 0) for a in trigger_agents)
            bar_width = (cookies / max_cookies) * 100 if max_cookies > 0 else 0
            
            competition_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; color: {rank_color}; font-weight: bold;">
                    {i+1} {medal}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{agent_name}</td>
                <td style="padding: 10px; text-align: center; border-bottom: 1px solid #dee2e6; font-weight: bold;">{cookies:.1f}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6; color: {status_color};">{status}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">
                    <div style="width: 100%; height: 15px; background-color: #e9ecef; border-radius: 7px;">
                        <div style="width: {bar_width}%; height: 15px; background-color: {rank_color if rank_color else "#007bff"}; border-radius: 7px;"></div>
                    </div>
                </td>
            </tr>
            """
        
        competition_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(competition_html, unsafe_allow_html=True)
    
    # Display competition dynamics
    st.subheader("Competition Dynamics")
    
    st.markdown("""
    The Agent Competition implements a reinforcement mechanism where:
    
    1. **Agents compete for rewards** based on their contribution to the system
    2. **High-performing agents** receive more opportunities to execute
    3. **Low-performing agents** may become dormant if they consistently fail to earn cookies
    4. **The system evolves** to optimize for insight quality and system integrity
    
    This creates a self-optimizing insight economy where the best agents thrive and
    underperforming agents are replaced or improved.
    """)

def render_runtime_control():
    """Render the runtime control tab."""
    st.header("Runtime Control Center")
    
    # Get agent status
    agent_status = agent_controller.get_agent_status()
    controller_running = agent_status.get("controller_running", False)
    
    # Display controller status
    status_color = "#198754" if controller_running else "#dc3545"
    status_text = "Active" if controller_running else "Stopped"
    
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 1.2rem; font-weight: bold;">Agent Controller Status</div>
                </div>
                <div style="background-color: {status_color}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;">
                    {status_text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if not controller_running:
            if st.button("Start Agent Controller"):
                with st.spinner("Starting agent controller..."):
                    result = agent_controller.start_controller()
                    if result:
                        st.success("Agent controller started successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to start agent controller.")
    
    with col2:
        if controller_running:
            if st.button("Stop Agent Controller"):
                with st.spinner("Stopping agent controller..."):
                    result = agent_controller.stop_controller()
                    if result:
                        st.success("Agent controller stopped successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to stop agent controller.")
    
    # Action buttons
    st.subheader("Agent Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Run Integration Test"):
            with st.spinner("Running integration test..."):
                result = agent_controller.dispatch_agent("integration_tester.agent")
                if result.get("status") == "success":
                    test_result = result.get("result", {}).get("test_result", {})
                    test_status = test_result.get("result", "unknown")
                    if test_status == "pass":
                        st.success("Integration test passed successfully!")
                    else:
                        st.error("Integration test failed.")
                else:
                    st.error(f"Failed to run integration test: {result.get('message', 'Unknown error')}")
    
    with col2:
        if st.button("Optimize Prompts"):
            with st.spinner("Running prompt optimization..."):
                result = agent_controller.dispatch_agent("prompt_optimizer.agent")
                if result.get("status") == "success":
                    agent_result = result.get("result", {})
                    rotations = agent_result.get("rotations_implemented", 0)
                    if rotations > 0:
                        st.success(f"Prompt optimization complete! Implemented {rotations} rotations.")
                    else:
                        st.info("Prompt optimization complete! No rotations needed.")
                else:
                    st.error(f"Failed to run prompt optimization: {result.get('message', 'Unknown error')}")
    
    with col3:
        if st.button("Update Cookie Jar"):
            with st.spinner("Updating cookie jar..."):
                agent_controller.update_agent_cookies()
                st.success("Cookie jar updated successfully!")
                st.rerun()
    
    # Runtime scheduler
    st.subheader("Runtime Scheduler")
    
    st.markdown("""
    The agent runtime is managed by a scheduler that triggers agents based on their specified schedule:
    
    * **Hourly Agents:** Run every hour (e.g., integration tester)
    * **Daily Agents:** Run once per day (e.g., scan scheduler)
    * **Weekly Agents:** Run once per week (e.g., benchmark validator)
    * **Post-Scan Agents:** Run after each domain scan is completed
    
    Each agent execution is logged, and cookies are awarded based on performance.
    """)