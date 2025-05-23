"""
Indexwide Scanning Dashboard
Codename: "Go Wider"

This dashboard visualizes the data collected by the three agent classes:
1. IndexScan-A1: Company metadata and competitor graphs
2. SurfaceSeed-B1: Surface page generation statistics
3. DriftPulse-C1: Signal differential benchmarks
"""

import os
import json
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any

# Constants
INDEX_SCAN_DIR = "data/index_scan/v1"
SURFACE_DIR = "data/surface"
BRANDS_DIR = f"{SURFACE_DIR}/brands"
DRIFT_DIR = f"{SURFACE_DIR}/drift"
RIVALRY_DIR = f"{DRIFT_DIR}/rivalries"
INDEXWIDE_DIR = "data/indexwide"
SUMMARY_PATH = f"{INDEXWIDE_DIR}/execution_summary.json"

def load_json_file(file_path: str) -> Dict:
    """Load a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            return {}
    else:
        return {}

def load_company_data() -> List[Dict]:
    """Load company data from IndexScan."""
    companies = []
    
    if os.path.exists(INDEX_SCAN_DIR):
        try:
            for filename in os.listdir(INDEX_SCAN_DIR):
                if filename.endswith('.json') and filename != 'scan_summary.json':
                    file_path = os.path.join(INDEX_SCAN_DIR, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            company_data = json.load(f)
                            companies.append(company_data)
                    except Exception as e:
                        st.error(f"Error loading {file_path}: {e}")
        except Exception as e:
            st.error(f"Error listing files in {INDEX_SCAN_DIR}: {e}")
    
    return companies

def load_brand_data() -> List[Dict]:
    """Load brand data from Surface pages."""
    brands = []
    
    if os.path.exists(BRANDS_DIR):
        try:
            for filename in os.listdir(BRANDS_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(BRANDS_DIR, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            brand_data = json.load(f)
                            brands.append(brand_data)
                    except Exception as e:
                        st.error(f"Error loading {file_path}: {e}")
        except Exception as e:
            st.error(f"Error listing files in {BRANDS_DIR}: {e}")
    
    return brands

def load_rivalry_data() -> List[Dict]:
    """Load rivalry data from DriftPulse."""
    rivalries = []
    
    if os.path.exists(RIVALRY_DIR):
        try:
            for filename in os.listdir(RIVALRY_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(RIVALRY_DIR, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            rivalry_data = json.load(f)
                            rivalries.append(rivalry_data)
                    except Exception as e:
                        st.error(f"Error loading {file_path}: {e}")
        except Exception as e:
            st.error(f"Error listing files in {RIVALRY_DIR}: {e}")
    
    return rivalries

def render_execution_summary():
    """Render execution summary section."""
    st.header("Execution Summary", divider="blue")
    
    execution_summary = load_json_file(SUMMARY_PATH)
    
    if not execution_summary:
        st.warning("No execution summary available. Run the indexwide scan first.")
        
        # Add button to run the scan
        if st.button("Run Indexwide Scan"):
            st.info("Starting indexwide scan... This may take a while.")
            try:
                # Import the run_indexwide_scan module
                import run_indexwide_scan
                
                # Run the scan
                run_indexwide_scan.run_full_indexwide_scan()
                
                st.success("Indexwide scan completed. Refresh the page to see the results.")
            except Exception as e:
                st.error(f"Error running indexwide scan: {e}")
        
        return
    
    # Create columns for the summary
    col1, col2, col3 = st.columns(3)
    
    # Overall execution time
    start_time = datetime.datetime.fromisoformat(execution_summary.get("overall_start_time", ""))
    end_time = datetime.datetime.fromisoformat(execution_summary.get("overall_end_time", ""))
    duration = execution_summary.get("overall_duration_seconds", 0)
    
    col1.metric(
        label="Execution Time",
        value=f"{duration:.2f} seconds",
        delta=f"Completed {(datetime.datetime.now() - end_time).days} days ago"
    )
    
    # Agent status
    index_scan_status = execution_summary.get("index_scan_result", {}).get("status", "Unknown")
    surface_seed_status = execution_summary.get("surface_seed_result", {}).get("status", "Unknown")
    drift_pulse_status = execution_summary.get("drift_pulse_result", {}).get("status", "Unknown")
    
    col2.metric(
        label="Agent Status",
        value=f"IndexScan: {index_scan_status}",
        delta=f"SurfaceSeed: {surface_seed_status}, DriftPulse: {drift_pulse_status}"
    )
    
    # Domains processed
    index_scan_companies = execution_summary.get("index_scan_result", {}).get("summary", {}).get("total_companies_processed", 0)
    surface_seed_surfaces = execution_summary.get("surface_seed_result", {}).get("summary", {}).get("successful_surfaces", 0)
    drift_pulse_rivalries = execution_summary.get("drift_pulse_result", {}).get("summary", {}).get("rivalries_found", 0)
    
    col3.metric(
        label="Domains Processed",
        value=f"{index_scan_companies} companies",
        delta=f"{surface_seed_surfaces} surfaces, {drift_pulse_rivalries} rivalries"
    )
    
    # Show execution timeline
    st.subheader("Execution Timeline")
    
    # Create timeline data
    timeline_data = []
    
    if "index_scan_result" in execution_summary:
        timeline_data.append({
            "Agent": "IndexScan-A1",
            "Start": datetime.datetime.fromisoformat(execution_summary["index_scan_result"].get("start_time", "")),
            "End": datetime.datetime.fromisoformat(execution_summary["index_scan_result"].get("end_time", "")),
            "Duration": execution_summary["index_scan_result"].get("duration_seconds", 0)
        })
    
    if "surface_seed_result" in execution_summary:
        timeline_data.append({
            "Agent": "SurfaceSeed-B1",
            "Start": datetime.datetime.fromisoformat(execution_summary["surface_seed_result"].get("start_time", "")),
            "End": datetime.datetime.fromisoformat(execution_summary["surface_seed_result"].get("end_time", "")),
            "Duration": execution_summary["surface_seed_result"].get("duration_seconds", 0)
        })
    
    if "drift_pulse_result" in execution_summary:
        timeline_data.append({
            "Agent": "DriftPulse-C1",
            "Start": datetime.datetime.fromisoformat(execution_summary["drift_pulse_result"].get("start_time", "")),
            "End": datetime.datetime.fromisoformat(execution_summary["drift_pulse_result"].get("end_time", "")),
            "Duration": execution_summary["drift_pulse_result"].get("duration_seconds", 0)
        })
    
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        
        fig = px.timeline(
            df,
            x_start="Start",
            x_end="End",
            y="Agent",
            color="Agent",
            hover_data=["Duration"]
        )
        
        fig.update_layout(
            title="Agent Execution Timeline",
            xaxis_title="Time",
            yaxis_title="Agent",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_index_scan_section(companies):
    """Render IndexScan section."""
    st.header("IndexScan-A1: Company Metadata", divider="blue")
    
    if not companies:
        st.warning("No company data available.")
        return
    
    # Company count by index
    st.subheader("Companies by Index")
    
    index_counts = {}
    for company in companies:
        for index in company.get("index_tags", []):
            if index not in index_counts:
                index_counts[index] = 0
            index_counts[index] += 1
    
    if index_counts:
        index_df = pd.DataFrame({
            "Index": list(index_counts.keys()),
            "Company Count": list(index_counts.values())
        })
        
        fig = px.bar(
            index_df,
            x="Index",
            y="Company Count",
            color="Index",
            text="Company Count"
        )
        
        fig.update_layout(
            title="Companies by Index",
            xaxis_title="Index",
            yaxis_title="Number of Companies"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Company count by category
    st.subheader("Companies by Category")
    
    category_counts = {}
    for company in companies:
        category = company.get("category", "Uncategorized")
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    if category_counts:
        category_df = pd.DataFrame({
            "Category": list(category_counts.keys()),
            "Company Count": list(category_counts.values())
        }).sort_values(by="Company Count", ascending=False)
        
        fig = px.bar(
            category_df,
            x="Category",
            y="Company Count",
            color="Company Count",
            text="Company Count"
        )
        
        fig.update_layout(
            title="Companies by Category",
            xaxis_title="Category",
            yaxis_title="Number of Companies"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Company competitor count distribution
    st.subheader("Competitor Count Distribution")
    
    competitor_counts = []
    for company in companies:
        competitor_count = len(company.get("competitor_domains", []))
        competitor_counts.append(competitor_count)
    
    if competitor_counts:
        fig = px.histogram(
            x=competitor_counts,
            nbins=max(competitor_counts) + 1 if competitor_counts else 10
        )
        
        fig.update_layout(
            title="Competitor Count Distribution",
            xaxis_title="Number of Competitors",
            yaxis_title="Number of Companies"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Company table
    st.subheader("Company Data")
    
    company_data = []
    for company in companies:
        company_data.append({
            "Ticker": company.get("ticker_symbol", ""),
            "Company Name": company.get("company_name", ""),
            "Domain": company.get("brand_domain", ""),
            "Category": company.get("category", ""),
            "Competitor Count": len(company.get("competitor_domains", []))
        })
    
    if company_data:
        company_df = pd.DataFrame(company_data)
        st.dataframe(company_df, use_container_width=True)

def render_surface_seed_section(brands):
    """Render SurfaceSeed section."""
    st.header("SurfaceSeed-B1: Surface Pages", divider="blue")
    
    if not brands:
        st.warning("No brand data available.")
        return
    
    # Brand count by category
    st.subheader("Brands by Category")
    
    category_counts = {}
    for brand in brands:
        category = brand.get("category", "Uncategorized")
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    if category_counts:
        category_df = pd.DataFrame({
            "Category": list(category_counts.keys()),
            "Brand Count": list(category_counts.values())
        }).sort_values(by="Brand Count", ascending=False)
        
        fig = px.bar(
            category_df,
            x="Category",
            y="Brand Count",
            color="Brand Count",
            text="Brand Count"
        )
        
        fig.update_layout(
            title="Brands by Category",
            xaxis_title="Category",
            yaxis_title="Number of Brands"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Surface creation timeline
    st.subheader("Surface Creation Timeline")
    
    surface_timestamps = []
    for brand in brands:
        if "surface_timestamp" in brand:
            surface_timestamps.append(datetime.datetime.fromisoformat(brand["surface_timestamp"]))
    
    if surface_timestamps:
        surface_timestamps.sort()
        
        # Create a DataFrame with dates and cumulative counts
        dates = []
        counts = []
        
        for i, timestamp in enumerate(surface_timestamps):
            dates.append(timestamp)
            counts.append(i + 1)
        
        timeline_df = pd.DataFrame({
            "Date": dates,
            "Cumulative Surfaces": counts
        })
        
        fig = px.line(
            timeline_df,
            x="Date",
            y="Cumulative Surfaces"
        )
        
        fig.update_layout(
            title="Surface Creation Timeline",
            xaxis_title="Date",
            yaxis_title="Cumulative Surfaces Created"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Memory vulnerability score distribution
    st.subheader("Memory Vulnerability Score Distribution")
    
    mvs_scores = []
    for brand in brands:
        if "memory_vulnerability_score" in brand:
            mvs_scores.append(brand["memory_vulnerability_score"])
    
    if mvs_scores:
        fig = px.histogram(
            x=mvs_scores,
            nbins=20
        )
        
        fig.update_layout(
            title="Memory Vulnerability Score Distribution",
            xaxis_title="Memory Vulnerability Score",
            yaxis_title="Number of Brands"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Brand table
    st.subheader("Brand Data")
    
    brand_data = []
    for brand in brands:
        brand_data.append({
            "Slug": brand.get("slug", ""),
            "Name": brand.get("name", ""),
            "Domain": brand.get("domain", ""),
            "Category": brand.get("category", ""),
            "MVS": brand.get("memory_vulnerability_score", 0),
            "Seeded": brand.get("index_seeded", False)
        })
    
    if brand_data:
        brand_df = pd.DataFrame(brand_data)
        st.dataframe(brand_df, use_container_width=True)

def render_drift_pulse_section(rivalries):
    """Render DriftPulse section."""
    st.header("DriftPulse-C1: Signal Differentials", divider="blue")
    
    if not rivalries:
        st.warning("No rivalry data available.")
        return
    
    # Category delta distribution
    st.subheader("Category Delta Distribution")
    
    delta_data = []
    for rivalry in rivalries:
        if "category" in rivalry and "delta" in rivalry:
            delta_data.append({
                "Category": rivalry["category"],
                "Delta": rivalry["delta"],
                "Outcite Ready": rivalry.get("outcite_ready", False)
            })
    
    if delta_data:
        delta_df = pd.DataFrame(delta_data).sort_values(by="Delta", ascending=False)
        
        fig = px.bar(
            delta_df,
            x="Category",
            y="Delta",
            color="Outcite Ready",
            text="Delta"
        )
        
        fig.update_layout(
            title="Category Delta Distribution",
            xaxis_title="Category",
            yaxis_title="Signal Delta"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top vs. Laggard brands
    st.subheader("Top vs. Laggard Brands")
    
    rivalry_table_data = []
    for rivalry in rivalries:
        if ("category" in rivalry and 
            "top_brand" in rivalry and 
            "laggard_brand" in rivalry and 
            "delta" in rivalry):
            
            top_brand = rivalry["top_brand"]
            laggard_brand = rivalry["laggard_brand"]
            
            rivalry_table_data.append({
                "Category": rivalry["category"],
                "Top Brand": top_brand.get("name", top_brand.get("domain", "")),
                "Top Signal": top_brand.get("signal", 0),
                "Laggard Brand": laggard_brand.get("name", laggard_brand.get("domain", "")),
                "Laggard Signal": laggard_brand.get("signal", 0),
                "Delta": rivalry["delta"],
                "Outcite Ready": rivalry.get("outcite_ready", False)
            })
    
    if rivalry_table_data:
        rivalry_df = pd.DataFrame(rivalry_table_data).sort_values(by="Delta", ascending=False)
        st.dataframe(rivalry_df, use_container_width=True)
    
    # SHIFT events
    st.subheader("SHIFT Events")
    
    shift_events = []
    for rivalry in rivalries:
        if rivalry.get("shift_event", False):
            shift_events.append({
                "Category": rivalry["category"],
                "Z-Score": rivalry.get("z_score", 0),
                "Delta": rivalry["delta"]
            })
    
    if shift_events:
        shift_df = pd.DataFrame(shift_events).sort_values(by="Z-Score", ascending=False)
        
        fig = px.bar(
            shift_df,
            x="Category",
            y="Z-Score",
            color="Z-Score",
            text="Z-Score"
        )
        
        fig.update_layout(
            title="SHIFT Events (Z-Score > ±2.0)",
            xaxis_title="Category",
            yaxis_title="Z-Score"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(shift_df, use_container_width=True)
    else:
        st.info("No SHIFT events detected.")
    
    # Outcite queue
    st.subheader("Outcite Queue")
    
    outcite_queue_path = f"{DRIFT_DIR}/outcite_queue.json"
    outcite_queue = load_json_file(outcite_queue_path)
    
    if outcite_queue and "queue" in outcite_queue and outcite_queue["queue"]:
        outcite_data = []
        
        for entry in outcite_queue["queue"]:
            rivalry_data = entry.get("rivalry_data", {})
            
            if rivalry_data:
                top_brand = rivalry_data.get("top_brand", {})
                laggard_brand = rivalry_data.get("laggard_brand", {})
                
                outcite_data.append({
                    "Category": rivalry_data.get("category", ""),
                    "Top Brand": top_brand.get("name", top_brand.get("domain", "")),
                    "Laggard Brand": laggard_brand.get("name", laggard_brand.get("domain", "")),
                    "Delta": rivalry_data.get("delta", 0),
                    "Timestamp": entry.get("timestamp", "")
                })
        
        if outcite_data:
            outcite_df = pd.DataFrame(outcite_data)
            st.dataframe(outcite_df, use_container_width=True)
    else:
        st.info("No entries in the outcite queue.")

def render_indexwide_dashboard():
    """Render the full indexwide dashboard."""
    st.set_page_config(
        page_title="Indexwide Scanning Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Indexwide Scanning Dashboard 📊")
    st.caption("Codename: \"Go Wider\"")
    
    # Load data
    companies = load_company_data()
    brands = load_brand_data()
    rivalries = load_rivalry_data()
    
    # Render sections
    render_execution_summary()
    
    # Create tabs for the three agent sections
    tab1, tab2, tab3 = st.tabs(["IndexScan-A1", "SurfaceSeed-B1", "DriftPulse-C1"])
    
    with tab1:
        render_index_scan_section(companies)
    
    with tab2:
        render_surface_seed_section(brands)
    
    with tab3:
        render_drift_pulse_section(rivalries)
    
    # Add run button at the bottom
    st.divider()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        This dashboard visualizes the data collected by the Go Wider directive's agent classes:
        
        1. **IndexScan-A1**: Collects company lists, metadata, and competitor graphs
        2. **SurfaceSeed-B1**: Generates minimal viable insight "Surface" pages
        3. **DriftPulse-C1**: Detects and benchmarks signal differentials
        """)
    
    with col2:
        if st.button("Run Indexwide Scan", key="run_scan_bottom"):
            st.info("Starting indexwide scan... This may take a while.")
            try:
                # Import the run_indexwide_scan module
                import run_indexwide_scan
                
                # Run the scan
                run_indexwide_scan.run_full_indexwide_scan()
                
                st.success("Indexwide scan completed. Refresh the page to see the results.")
            except Exception as e:
                st.error(f"Error running indexwide scan: {e}")

if __name__ == "__main__":
    render_indexwide_dashboard()