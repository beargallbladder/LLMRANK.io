"""
The Surface Dashboard - EchoLayer

This dashboard visualizes brand surfaces across competitive categories,
tracking memory drift, signal divergence, and LLM pickup.
"""

import streamlit as st
import json
import os
import logging
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)

PRIORITY_CATEGORIES_PATH = os.path.join(SURFACE_DATA_DIR, "priority_categories.json")
BRAND_SURFACES_PATH = os.path.join(SURFACE_DATA_DIR, "brand_surfaces.json")

# Helper functions
def load_categories():
    """Load priority categories from file."""
    try:
        if os.path.exists(PRIORITY_CATEGORIES_PATH):
            with open(PRIORITY_CATEGORIES_PATH, 'r') as f:
                data = json.load(f)
                primary_categories = data.get('priority_categories', [])
                additional_categories = data.get('additional_categories', [])
                return primary_categories + additional_categories
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
    return []

def load_surfaces():
    """Load brand surfaces from file."""
    surfaces = {}
    try:
        if os.path.exists(BRAND_SURFACES_PATH):
            with open(BRAND_SURFACES_PATH, 'r') as f:
                surfaces = json.load(f)
    except Exception as e:
        logger.error(f"Error loading surfaces: {e}")
    return surfaces

def generate_mock_surfaces():
    """Generate mock surfaces based on priority categories."""
    categories = load_categories()
    surfaces = {}
    
    for category in categories:
        category_name = category.get('category')
        top_brands = category.get('top_brands', [])
        
        for brand in top_brands:
            brand_name = brand.get('name')
            domain = brand.get('domain')
            search_terms = brand.get('search_terms', [])
            
            if not brand_name or not domain:
                continue
            
            # Create slug
            slug = brand_name.lower().replace(' ', '-')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')
            
            # Generate MISS score and history
            miss_score = round(random.uniform(20, 75), 1)
            miss_history = []
            base_score = random.uniform(30, 70)
            
            # Generate history for the last 10 weeks
            for i in range(10):
                # Add some random variation
                score = max(1, min(100, base_score + random.uniform(-8, 8)))
                
                # Calculate timestamp (going back in time)
                days_ago = (10 - i) * 7
                date = datetime.now().timestamp() - (days_ago * 24 * 3600)
                timestamp = datetime.fromtimestamp(date).isoformat()
                
                miss_history.append({
                    "timestamp": timestamp,
                    "rank": round(score, 1)
                })
                
                # Update base score for next entry (slight trend)
                base_score = base_score + random.uniform(-3, 3)
            
            # Generate preservation score
            preservation_score = round(random.uniform(0.4, 0.95), 2)
            
            # Generate summary
            summary = f"{brand_name} is a leading company in the {category_name} industry."
            
            # Generate surface
            surfaces[slug] = {
                "slug": slug,
                "brand_name": brand_name,
                "domain": domain,
                "category": category_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "claimed": random.choice([True, False]),
                "miss_score": miss_score,
                "miss_history": miss_history,
                "preservation_score": preservation_score,
                "summary": summary,
                "faq": [
                    {
                        "question": f"What does {brand_name} do?",
                        "answer": f"{brand_name} provides solutions in the {category_name} space."
                    }
                ],
                "tags": search_terms[:3] if search_terms else [],
                "llm_pickup": {
                    "gpt4": random.randint(0, 10),
                    "claude": random.randint(0, 10)
                }
            }
    
    return surfaces

# Page configuration
st.set_page_config(
    page_title="The Surface Dashboard - EchoLayer",
    page_icon="📊",
    layout="wide"
)

# Style
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066ff;
        margin-bottom: 0;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066ff;
    }
    .metric-label {
        font-size: 1rem;
        color: #4a5568;
    }
    .category-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1a202c;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main interface
st.markdown('<h1 class="main-header">The Surface Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Track memory drift, signal divergence, and LLM pickup across competitive categories</p>', unsafe_allow_html=True)

# Load data
categories = load_categories()
surfaces = load_surfaces()

# Generate mock data if needed
if not surfaces:
    surfaces = generate_mock_surfaces()
    # Save generated surfaces
    try:
        with open(BRAND_SURFACES_PATH, 'w') as f:
            json.dump(surfaces, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving surfaces: {e}")

# Count metrics
total_surfaces = len(surfaces)
claimed_surfaces = sum(1 for s in surfaces.values() if s.get('claimed', False))
avg_preservation = 0
if surfaces:
    avg_preservation = sum(s.get('preservation_score', 0) for s in surfaces.values()) / total_surfaces
pickup_count = sum(sum(p.values()) for p in [s.get('llm_pickup', {}) for s in surfaces.values()])

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{total_surfaces}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Brand Surfaces</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{claimed_surfaces}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Claimed Surfaces</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{avg_preservation:.0%}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Avg Preservation Score</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{pickup_count}</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">Total LLM Pickups</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation
st.markdown("## Explore Brand Surfaces")

# Create tabs for navigation
tabs = ["Categories Overview", "Brand Rankings", "Surface Details", "LLM Pickup Tracker"]
selected_tab = st.tabs(tabs)

# Categories Overview tab
with selected_tab[0]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Group surfaces by category
    category_counts = {}
    category_avg_miss = {}
    category_avg_preservation = {}
    
    for surface in surfaces.values():
        category = surface.get('category')
        if not category:
            continue
            
        if category not in category_counts:
            category_counts[category] = 0
            category_avg_miss[category] = []
            category_avg_preservation[category] = []
            
        category_counts[category] += 1
        category_avg_miss[category].append(surface.get('miss_score', 0))
        category_avg_preservation[category].append(surface.get('preservation_score', 0))
    
    # Calculate averages
    for category in category_avg_miss:
        if category_avg_miss[category]:
            category_avg_miss[category] = sum(category_avg_miss[category]) / len(category_avg_miss[category])
        else:
            category_avg_miss[category] = 0
            
        if category_avg_preservation[category]:
            category_avg_preservation[category] = sum(category_avg_preservation[category]) / len(category_avg_preservation[category])
        else:
            category_avg_preservation[category] = 0
    
    # Create dataframe for charts
    category_df = pd.DataFrame({
        'Category': list(category_counts.keys()),
        'Brand Count': list(category_counts.values()),
        'Avg MISS Score': [round(score, 1) for score in category_avg_miss.values()],
        'Avg Preservation Score': [round(score * 100, 1) for score in category_avg_preservation.values()]
    })
    
    # Sort by brand count
    category_df = category_df.sort_values('Brand Count', ascending=False)
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Brands per Category")
        fig = px.bar(
            category_df, 
            x='Category', 
            y='Brand Count',
            color='Brand Count',
            color_continuous_scale='Blues',
            title="Number of Tracked Brands per Category"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Average MISS Score by Category")
        fig = px.bar(
            category_df, 
            x='Category', 
            y='Avg MISS Score',
            color='Avg MISS Score',
            color_continuous_scale='RdYlGn_r',  # Red for high scores (bad), green for low scores (good)
            title="Average MISS Score by Category (Lower is Better)"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Preservation score chart
    st.subheader("Memory Preservation by Category")
    fig = px.bar(
        category_df, 
        x='Category', 
        y='Avg Preservation Score',
        color='Avg Preservation Score',
        color_continuous_scale='Greens',
        title="Average Preservation Score by Category (%)"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Brand Rankings tab
with selected_tab[1]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Create dataframe for brand rankings
    brands_data = []
    for slug, surface in surfaces.items():
        brands_data.append({
            'Brand': surface.get('brand_name', 'Unknown'),
            'Category': surface.get('category', 'Unknown'),
            'MISS Score': surface.get('miss_score', 0),
            'Preservation Score': surface.get('preservation_score', 0) * 100,
            'LLM Pickups': sum(surface.get('llm_pickup', {}).values()),
            'Claimed': 'Yes' if surface.get('claimed', False) else 'No',
            'Slug': slug
        })
    
    brands_df = pd.DataFrame(brands_data)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_categories = st.multiselect(
            "Filter by Category",
            options=sorted(brands_df['Category'].unique()),
            default=[]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            options=["MISS Score (Low to High)", "MISS Score (High to Low)", 
                    "Preservation Score (High to Low)", "LLM Pickups (High to Low)"]
        )
    
    # Apply filters
    filtered_df = brands_df
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    
    # Apply sorting
    if sort_by == "MISS Score (Low to High)":
        filtered_df = filtered_df.sort_values('MISS Score')
    elif sort_by == "MISS Score (High to Low)":
        filtered_df = filtered_df.sort_values('MISS Score', ascending=False)
    elif sort_by == "Preservation Score (High to Low)":
        filtered_df = filtered_df.sort_values('Preservation Score', ascending=False)
    elif sort_by == "LLM Pickups (High to Low)":
        filtered_df = filtered_df.sort_values('LLM Pickups', ascending=False)
    
    # Display brand rankings
    st.subheader("Brand Rankings")
    
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['Preservation Score'] = display_df['Preservation Score'].round(1).astype(str) + '%'
    display_df = display_df.drop('Slug', axis=1)
    
    # Display as table
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "MISS Score": st.column_config.NumberColumn(
                "MISS Score",
                help="Memory Integrity Signal Score - lower is better",
                format="%.1f"
            ),
            "Preservation Score": st.column_config.TextColumn(
                "Preservation Score",
                help="Percentage of memory preserved in LLMs"
            ),
            "LLM Pickups": st.column_config.NumberColumn(
                "LLM Pickups",
                help="Number of times LLMs picked up information from the surface"
            ),
            "Claimed": st.column_config.TextColumn(
                "Claimed",
                help="Whether the brand has claimed their surface"
            )
        }
    )
    
    # Visualization of top/bottom brands
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Brands (Lowest MISS Scores)")
        top_brands = brands_df.nsmallest(10, 'MISS Score')
        fig = px.bar(
            top_brands,
            x='Brand',
            y='MISS Score',
            color='Category',
            title="Top 10 Brands by MISS Score",
            hover_data=['Preservation Score', 'LLM Pickups', 'Claimed']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Bottom 10 Brands (Highest MISS Scores)")
        bottom_brands = brands_df.nlargest(10, 'MISS Score')
        fig = px.bar(
            bottom_brands,
            x='Brand',
            y='MISS Score',
            color='Category',
            title="Bottom 10 Brands by MISS Score",
            hover_data=['Preservation Score', 'LLM Pickups', 'Claimed']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Surface Details tab
with selected_tab[2]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Brand selector
    selected_slug = st.selectbox(
        "Select Brand",
        options=[(s.get('brand_name', 'Unknown') + ' - ' + s.get('category', 'Unknown'), slug) 
                for slug, s in surfaces.items()],
        format_func=lambda x: x[0]
    )[1]
    
    if selected_slug in surfaces:
        surface = surfaces[selected_slug]
        
        # Display brand details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(surface.get('brand_name', 'Unknown Brand'))
            st.write(f"**Category:** {surface.get('category', 'Unknown')}")
            st.write(f"**Domain:** {surface.get('domain', 'Unknown')}")
            
            # Tags
            tags = surface.get('tags', [])
            if tags:
                st.write("**Tags:**", ", ".join(tags))
            
            # Summary
            st.subheader("Surface Summary")
            st.write(surface.get('summary', 'No summary available'))
            
            # FAQ
            st.subheader("FAQ")
            faq = surface.get('faq', [])
            for item in faq:
                with st.expander(item.get('question', 'Unknown question')):
                    st.write(item.get('answer', 'No answer available'))
        
        with col2:
            # MISS score
            miss_score = surface.get('miss_score', 0)
            miss_color = 'green'
            if miss_score > 70:
                miss_color = 'red'
            elif miss_score > 30:
                miss_color = 'orange'
            
            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h3 style="margin-top: 0;">MISS Score</h3>
                <div style="font-size: 3rem; font-weight: 700; color: {miss_color};">{miss_score:.1f}</div>
                <div style="color: #4a5568; margin-bottom: 20px;">Memory Integrity Signal Score</div>
                
                <h3>Preservation Score</h3>
                <div style="font-size: 2rem; font-weight: 600; color: #38a169;">{surface.get('preservation_score', 0)*100:.1f}%</div>
                <div style="color: #4a5568; margin-bottom: 20px;">Memory preserved in LLMs</div>
                
                <h3>Status</h3>
                <div style="font-size: 1.5rem; font-weight: 500; color: {'#38a169' if surface.get('claimed', False) else '#dd6b20'};">
                    {'Claimed' if surface.get('claimed', False) else 'Unclaimed'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # LLM Pickup
            st.subheader("LLM Pickup")
            llm_pickup = surface.get('llm_pickup', {})
            pickup_data = pd.DataFrame({
                'Model': list(llm_pickup.keys()),
                'Pickups': list(llm_pickup.values())
            })
            
            if not pickup_data.empty:
                fig = px.bar(
                    pickup_data,
                    x='Model',
                    y='Pickups',
                    color='Pickups',
                    color_continuous_scale='Blues',
                    title="LLM Pickup Count"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No pickup data available")
        
        # MISS History
        st.subheader("MISS Score History")
        miss_history = surface.get('miss_history', [])
        
        if miss_history:
            # Convert to dataframe
            history_df = pd.DataFrame(miss_history)
            
            # Convert timestamps to datetime
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            
            # Sort by timestamp
            history_df = history_df.sort_values('timestamp')
            
            # Create chart
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=history_df['timestamp'],
                    y=history_df['rank'],
                    mode='lines+markers',
                    name='MISS Score',
                    line=dict(color='#0066ff', width=3),
                    marker=dict(size=8)
                )
            )
            
            fig.update_layout(
                title="MISS Score History (Lower is Better)",
                xaxis_title="Date",
                yaxis_title="MISS Score",
                hovermode="x unified",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No MISS history available")
        
    else:
        st.warning("Surface not found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# LLM Pickup Tracker tab
with selected_tab[3]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    st.subheader("LLM Pickup Analysis")
    st.write("Track how language models pick up information from brand surfaces.")
    
    # Calculate pickup rates by model
    pickup_by_model = {'gpt4': 0, 'claude': 0}
    total_by_model = {'gpt4': 0, 'claude': 0}
    
    for surface in surfaces.values():
        llm_pickup = surface.get('llm_pickup', {})
        for model, count in llm_pickup.items():
            if model in pickup_by_model:
                pickup_by_model[model] += count
                total_by_model[model] += 1
    
    # Create data for model comparison
    model_data = []
    for model in pickup_by_model:
        if total_by_model[model] > 0:
            pickup_rate = pickup_by_model[model] / total_by_model[model]
        else:
            pickup_rate = 0
        
        model_data.append({
            'Model': model.upper(),
            'Total Pickups': pickup_by_model[model],
            'Pickup Rate': pickup_rate
        })
    
    model_df = pd.DataFrame(model_data)
    
    # Display model comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Pickups by Model")
        fig = px.bar(
            model_df,
            x='Model',
            y='Total Pickups',
            color='Model',
            title="Total Pickup Count by LLM Model"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Pickup Rate by Model")
        fig = px.bar(
            model_df,
            x='Model',
            y='Pickup Rate',
            color='Model',
            title="Average Pickup Rate by LLM Model",
            labels={'Pickup Rate': 'Average Pickup Rate per Brand'}
        )
        fig.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig, use_container_width=True)
    
    # Calculate pickup by category
    pickup_by_category = {}
    
    for surface in surfaces.values():
        category = surface.get('category', 'Unknown')
        
        if category not in pickup_by_category:
            pickup_by_category[category] = {
                'total': 0,
                'count': 0
            }
        
        llm_pickup = surface.get('llm_pickup', {})
        pickup_by_category[category]['total'] += sum(llm_pickup.values())
        pickup_by_category[category]['count'] += 1
    
    # Create data for category comparison
    category_pickup_data = []
    for category, data in pickup_by_category.items():
        if data['count'] > 0:
            avg_pickup = data['total'] / data['count']
        else:
            avg_pickup = 0
        
        category_pickup_data.append({
            'Category': category,
            'Total Pickups': data['total'],
            'Average Pickups': avg_pickup
        })
    
    category_pickup_df = pd.DataFrame(category_pickup_data)
    
    # Sort by total pickups
    category_pickup_df = category_pickup_df.sort_values('Total Pickups', ascending=False)
    
    # Display category comparison
    st.subheader("LLM Pickup by Category")
    
    fig = px.bar(
        category_pickup_df,
        x='Category',
        y='Total Pickups',
        color='Average Pickups',
        color_continuous_scale='Blues',
        title="LLM Pickup by Category"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top brands with highest pickup
    st.subheader("Top Brands by LLM Pickup")
    
    brand_pickup_data = []
    for slug, surface in surfaces.items():
        llm_pickup = surface.get('llm_pickup', {})
        total_pickup = sum(llm_pickup.values())
        
        brand_pickup_data.append({
            'Brand': surface.get('brand_name', 'Unknown'),
            'Category': surface.get('category', 'Unknown'),
            'Total Pickups': total_pickup,
            'MISS Score': surface.get('miss_score', 0)
        })
    
    brand_pickup_df = pd.DataFrame(brand_pickup_data)
    
    # Sort by total pickups
    brand_pickup_df = brand_pickup_df.sort_values('Total Pickups', ascending=False)
    
    # Display top 10
    top_pickup_brands = brand_pickup_df.head(10)
    
    fig = px.bar(
        top_pickup_brands,
        x='Brand',
        y='Total Pickups',
        color='Category',
        title="Top 10 Brands by LLM Pickup",
        hover_data=['MISS Score']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # No additional logic needed, Streamlit handles the execution
    pass