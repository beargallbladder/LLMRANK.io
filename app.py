import streamlit as st
import asyncio
import os
import threading
from datetime import datetime
import time
import json
import random
import logging
import uvicorn
from fastapi import FastAPI

from dashboard import render_dashboard
from dashboard_v2 import render_v2_dashboard
from dashboard_v3 import render_v3_dashboard
from dashboard_v5 import render_v5_dashboard
from dashboard_v6 import render_v6_dashboard
from dashboard_v7 import render_v7_dashboard
from dashboard_v9_fixed import render_v9_dashboard
from dashboard_v10 import render_v10_dashboard
from dashboard_health import render_runtime_health_dashboard
from cookie_combat_dashboard import render_cookie_combat_dashboard
from mcp_dashboard import render_mcp_dashboard
from scheduler import setup_scheduler
from config import ADMIN_EMAIL, ADMIN_PASSWORD, VERSION_INFO, SYSTEM_VERSION
from init_db import initialize_database
from api_server import app as api_app
# Import health monitoring (for production)
import initialize_health_data

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for health monitor thread
health_monitor_thread = None

# Set page config
st.set_page_config(
    page_title=f"LLMPageRank V{SYSTEM_VERSION} - Trust Signal Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize database
    if 'db_initialized' not in st.session_state:
        logger.info("Initializing database on first app run")
        initialize_database(skip_migration=True)
        st.session_state.db_initialized = True
        
    # Start health monitoring if not already started
    global health_monitor_thread
    if health_monitor_thread is None or not health_monitor_thread.is_alive():
        try:
            # Use runtime health monitor instead of basic initialization
            import runtime_monitor
            health_monitor_thread = runtime_monitor.start_monitor()
            logger.info("Runtime health monitoring started in background thread")
        except Exception as e:
            logger.error(f"Error starting health monitor: {e}")
    
    # Initialize version selection state
    if 'use_v2' not in st.session_state:
        st.session_state.use_v2 = True  # Default to V2
    
    # Authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title(f"LLMPageRank V{SYSTEM_VERSION} - Trust Signal Intelligence")
        st.subheader("Admin Login")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.info("Enter your admin credentials to access the dashboard")
            email = st.text_input("Email", value="")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if email.strip() == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please check your email and password.")
        
        with col2:
            st.markdown(f"""
            ### LLMPageRank V{SYSTEM_VERSION} Engine
            
            A precision trust signal machine that discovers, tests, and scores domains 
            for LLM visibility with an enhanced intelligence dashboard.
            
            **Features:**
            - Prompt Precision Engine with versioned prompts
            - Target Discovery focused on trust-critical verticals
            - Time-Series + Longitudinal Trust Tracking
            - Customer Targeting and Opportunity Scoring
            - Private Observability Layer for trust signals
            """)
            
            # Display version info
            st.markdown("---")
            st.markdown(f"**Version {VERSION_INFO['version']}** ({VERSION_INFO['release_date']})")
            
            features_list = ""
            for feature in VERSION_INFO['features']:
                features_list += f"- {feature}\n"
            
            with st.expander("New Features"):
                st.markdown(features_list)
    else:
        # Initialize scheduler in background
        if 'scheduler_initialized' not in st.session_state:
            st.session_state.scheduler_initialized = True
            setup_scheduler()
            
        # Initialize API server in background
        if 'api_initialized' not in st.session_state:
            st.session_state.api_initialized = True
            # Start API server in a background thread
            # Note: In production, this would be a separate process
            def start_api_server():
                uvicorn.run(api_app, host="0.0.0.0", port=8080, log_level="error")
            
            api_thread = threading.Thread(target=start_api_server, daemon=True)
            api_thread.start()
            logger.info("API server started in background thread")
        
        # Add version selector in sidebar
        st.sidebar.title("LLMPageRank Settings")
        
        # Initialize dashboard states if not present
        if 'use_mcp' not in st.session_state:
            st.session_state.use_mcp = True  # Default to MCP Dashboard
            
        if 'use_cookie_combat' not in st.session_state:
            st.session_state.use_cookie_combat = False
            
        if 'use_health' not in st.session_state:
            st.session_state.use_health = False
            
        if 'use_v10' not in st.session_state:
            st.session_state.use_v10 = False
            
        if 'use_v9' not in st.session_state:
            st.session_state.use_v9 = False
            
        if 'use_v7' not in st.session_state:
            st.session_state.use_v7 = False
            
        if 'use_v6' not in st.session_state:
            st.session_state.use_v6 = False
            
        if 'use_v5' not in st.session_state:
            st.session_state.use_v5 = False
            
        if 'use_v3' not in st.session_state:
            st.session_state.use_v3 = False
            
        if 'use_v2' not in st.session_state:
            st.session_state.use_v2 = False
        
        version_options = ["V15 Model Context Protocol", "V14 Cookie Combat Economy", "V10 Runtime Health Monitor", "V10 Runtime Cadence & Learning", "V9 API Checkpoint & Integrity", "V7 Agent-Based Runtime", "V6 Replit Agent Game", "V5 Data Integrity & Truth Accountability", "V3 Enterprise Trust Intelligence", "V2 Trust Signal Intelligence", "V1 Original Dashboard"]
        selected_version = st.sidebar.radio("Dashboard Version", version_options)
        
        # Set dashboard version based on selection
        st.session_state.use_mcp = selected_version == version_options[0]
        st.session_state.use_cookie_combat = selected_version == version_options[1]
        st.session_state.use_health = selected_version == version_options[2]
        st.session_state.use_v10 = selected_version == version_options[3]
        st.session_state.use_v9 = selected_version == version_options[4]
        st.session_state.use_v7 = selected_version == version_options[5]
        st.session_state.use_v6 = selected_version == version_options[6]
        st.session_state.use_v5 = selected_version == version_options[7]
        st.session_state.use_v3 = selected_version == version_options[8]
        st.session_state.use_v2 = selected_version == version_options[9]
        
        # Display session info
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {ADMIN_EMAIL}")
        
        # Add data protection notice
        st.sidebar.markdown("""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 15px;'>
        <strong>Data Protection:</strong> All data is preserved and secured according to V3 Master Directive standards.
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        # Render the appropriate dashboard based on version selection
        if st.session_state.use_mcp:
            render_mcp_dashboard()
        elif st.session_state.use_cookie_combat:
            render_cookie_combat_dashboard()
        elif st.session_state.use_health:
            render_runtime_health_dashboard()
        elif st.session_state.use_v10:
            render_v10_dashboard()
        elif st.session_state.use_v9:
            render_v9_dashboard()
        elif st.session_state.use_v7:
            render_v7_dashboard()
        elif st.session_state.use_v6:
            render_v6_dashboard()
        elif st.session_state.use_v5:
            render_v5_dashboard()
        elif st.session_state.use_v3:
            render_v3_dashboard()
        elif st.session_state.use_v2:
            render_v2_dashboard()
        else:
            render_dashboard()

if __name__ == "__main__":
    main()
