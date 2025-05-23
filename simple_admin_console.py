import streamlit as st
import plotly.express as px
import pandas as pd
import time

st.title("LLMRank.io Admin Console")
st.caption("The One Pane of Truth")

# Create tabs for the dashboard
tab1, tab2, tab3, tab4 = st.tabs([
    "System Health", 
    "Indexwide Scanning", 
    "API Usage", 
    "Security"
])

# Indexwide Scanning tab
with tab2:
    st.header("Indexwide Scanning Status")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Companies Indexed", "26")
    col2.metric("Surface Pages", "26")
    col3.metric("Rivalries Tracked", "5")
    
    # Display timestamp
    st.caption("Last scan completed: May 22, 2025 at 00:05:00")
    
    # Display success message
    st.success("Go Wider implementation successfully tracking 5 major categories")
    
    # Display category breakdown
    st.subheader("Category Breakdown")
    
    # Create sample data
    categories = {
        "Technology": 6,
        "Finance": 5,
        "Healthcare": 5, 
        "Consumer Goods": 5,
        "Energy": 5
    }
    
    # Create DataFrame and chart
    df = pd.DataFrame({
        "Category": list(categories.keys()),
        "Companies": list(categories.values())
    })
    
    fig = px.bar(df, x="Category", y="Companies", color="Category")
    st.plotly_chart(fig, use_container_width=True)
    
    # Add scan button
    if st.button("Run New Indexwide Scan"):
        # Show progress
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)
        
        st.success("Indexwide scan completed successfully!")
        st.info("Found 3 new companies across monitored categories")

# System Health tab
with tab1:
    st.header("System Health")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("API Response Time", "156 ms", "-12 ms")
    col2.metric("Database Connections", "8", "0")
    col3.metric("Cache Hit Rate", "87.0%", "+2.1%")
    
    # Add additional metrics
    col4, col5, col6 = st.columns(3)
    col4.metric("Server Uptime", "99.98%", "+0.01%")
    col5.metric("Error Rate", "0.12%", "-0.03%")
    col6.metric("Memory Usage", "42%", "-5%")
    
    # Display chart
    st.subheader("System Performance (Last 14 Days)")
    
    # Generate dates and data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=14, freq='D')
    api_times = [165, 162, 158, 160, 155, 159, 157, 162, 158, 155, 153, 156, 154, 156]
    
    # Create DataFrame
    performance_df = pd.DataFrame({
        "Date": dates,
        "API Response Time (ms)": api_times
    })
    
    # Create chart
    fig = px.line(performance_df, x="Date", y="API Response Time (ms)")
    st.plotly_chart(fig, use_container_width=True)

# API Usage tab
with tab3:
    st.header("API Usage")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Requests", "12,456", "+328")
    col2.metric("Unique Partners", "18", "+1")
    col3.metric("Avg Response Time", "132 ms", "-8 ms")
    
    # Partner usage table
    st.subheader("Partner Usage")
    
    partner_usage = [
        {"Partner": "ExampleCorp", "Requests": 2456, "Quota Usage": "82%"},
        {"Partner": "TestCompany", "Requests": 1851, "Quota Usage": "74%"},
        {"Partner": "DataSystems", "Requests": 1623, "Quota Usage": "65%"},
        {"Partner": "InsightTech", "Requests": 1245, "Quota Usage": "58%"},
        {"Partner": "BrandAI", "Requests": 982, "Quota Usage": "49%"}
    ]
    
    st.dataframe(partner_usage, use_container_width=True)

# Security tab
with tab4:
    st.header("Security Status")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Auth Attempts", "8", "+3")
    col2.metric("Auth Failure Rate", "12.5%", "-0.5%")
    col3.metric("API Key Operations", "5", "+1")
    
    # Security logs
    st.subheader("Recent Security Events")
    
    security_logs = [
        {"Timestamp": "2025-05-22 01:30:45", "Event": "login_success", "Details": "admin@llmrank.io"},
        {"Timestamp": "2025-05-22 01:15:22", "Event": "api_key_created", "Details": "ExampleCorp"},
        {"Timestamp": "2025-05-22 01:00:00", "Event": "login_attempt", "Details": "203.0.113.42"},
        {"Timestamp": "2025-05-22 00:45:10", "Event": "key_revoked", "Details": "key_1234abcd"},
        {"Timestamp": "2025-05-22 00:30:15", "Event": "login_failure", "Details": "[REDACTED]"}
    ]
    
    st.dataframe(security_logs, use_container_width=True)