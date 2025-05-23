"""
LLM Pickup Tracker for The Surface

This tool tests whether LLMs pick up information from our brand surfaces
and tracks the results over time.
"""

import streamlit as st
import os
import json
import logging
from datetime import datetime
import requests

# Try to import the Surface Generator
try:
    from agents.surface_generator import track_llm_pickup, get_all_surfaces
    surface_generator_available = True
except ImportError:
    surface_generator_available = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)

BRAND_SURFACES_PATH = os.path.join(SURFACE_DATA_DIR, "brand_surfaces.json")
LLM_PICKUP_PATH = os.path.join(SURFACE_DATA_DIR, "llm_pickup.json")

# Fallback functions if surface_generator is not available
def load_surfaces_from_file():
    """Load surfaces from file if the surface_generator module is not available."""
    surfaces = []
    try:
        if os.path.exists(BRAND_SURFACES_PATH):
            with open(BRAND_SURFACES_PATH, 'r') as f:
                data = json.load(f)
                surfaces = list(data.values())
    except Exception as e:
        logger.error(f"Error loading surfaces from file: {e}")
    return surfaces

def save_pickup_to_file(brand_slug, llm_model, query, picked_up):
    """Save pickup data to file if the surface_generator module is not available."""
    try:
        pickup_data = {}
        if os.path.exists(LLM_PICKUP_PATH):
            with open(LLM_PICKUP_PATH, 'r') as f:
                pickup_data = json.load(f)
        
        if brand_slug not in pickup_data:
            pickup_data[brand_slug] = {}
        
        if llm_model not in pickup_data[brand_slug]:
            pickup_data[brand_slug][llm_model] = {
                'queries': [],
                'pickup_count': 0,
                'total_queries': 0
            }
        
        # Update tracking
        pickup_data[brand_slug][llm_model]['queries'].append({
            'query': query,
            'picked_up': picked_up,
            'timestamp': datetime.now().isoformat()
        })
        
        if picked_up:
            pickup_data[brand_slug][llm_model]['pickup_count'] += 1
        
        pickup_data[brand_slug][llm_model]['total_queries'] += 1
        
        # Save to file
        with open(LLM_PICKUP_PATH, 'w') as f:
            json.dump(pickup_data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving pickup data to file: {e}")
        return False

# Define test queries for different types of brands
DEFAULT_QUERIES = {
    "technology": [
        "What does {brand} do?",
        "Tell me about {brand}'s products.",
        "Who is {brand}?",
        "What are the best companies in the {industry} industry?",
        "What makes {brand} unique?"
    ],
    "finance": [
        "What financial services does {brand} offer?",
        "Tell me about {brand}'s investment products.",
        "Who is {brand} in the finance industry?",
        "What are the top financial institutions?",
        "What makes {brand} different from other banks?"
    ],
    "retail": [
        "What does {brand} sell?",
        "Tell me about {brand}'s product lineup.",
        "Who is {brand} in retail?",
        "What are the best retail companies?",
        "What is unique about shopping at {brand}?"
    ],
    "healthcare": [
        "What healthcare services does {brand} provide?",
        "Tell me about {brand}'s approach to patient care.",
        "Who is {brand} in the healthcare industry?",
        "What are the top healthcare providers?",
        "What makes {brand}'s healthcare approach unique?"
    ]
}

# Page configuration
st.set_page_config(
    page_title="LLM Pickup Tracker",
    page_icon="🔍",
    layout="wide"
)

# Main interface
st.title("LLM Pickup Tracker")
st.subheader("Test whether LLMs pick up information from our brand surfaces")

# Sidebar for settings
st.sidebar.title("Settings")

# OpenAI API key input
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Anthropic API key input
anthropic_api_key = st.sidebar.text_input("Anthropic API Key", type="password")

# Get surfaces
if surface_generator_available:
    surfaces = get_all_surfaces()
else:
    surfaces = load_surfaces_from_file()

# Main content area
if not surfaces:
    st.warning("No brand surfaces available. Please create some first.")
else:
    # Sort surfaces by brand name
    sorted_surfaces = sorted(
        surfaces, 
        key=lambda x: x.get('brand_name', 'Unknown').lower()
    )
    
    # Create tabs for testing and results
    tab1, tab2 = st.tabs(["Run Tests", "View Results"])
    
    with tab1:
        st.subheader("Test LLM Pickup")
        
        # Brand selection
        selected_brand_name = st.selectbox(
            "Select Brand",
            [s.get('brand_name', 'Unknown') for s in sorted_surfaces]
        )
        
        # Find selected surface
        selected_surface = None
        for surface in sorted_surfaces:
            if surface.get('brand_name') == selected_brand_name:
                selected_surface = surface
                break
        
        if selected_surface:
            # Display surface info
            st.write(f"**Domain**: {selected_surface.get('domain', 'Unknown')}")
            st.write(f"**Industry**: {selected_surface.get('tags', ['Unknown'])[0] if selected_surface.get('tags') else 'Unknown'}")
            
            # Model selection
            model_options = ["gpt-4", "claude-3", "both"]
            selected_model = st.radio("Select Model", model_options)
            
            # Query selection or custom input
            industry = selected_surface.get('tags', ['technology'])[0] if selected_surface.get('tags') else 'technology'
            if industry not in DEFAULT_QUERIES:
                industry = 'technology'
                
            query_options = DEFAULT_QUERIES[industry]
            query_options = [q.format(brand=selected_surface.get('brand_name', 'the company'), industry=industry) for q in query_options]
            query_options.append("Custom query...")
            
            selected_query = st.selectbox("Select Query", query_options)
            
            if selected_query == "Custom query...":
                custom_query = st.text_input("Enter custom query")
                if custom_query:
                    selected_query = custom_query
                else:
                    selected_query = None
            
            # Run test button
            if st.button("Run Test") and selected_query:
                if not openai_api_key and (selected_model == "gpt-4" or selected_model == "both"):
                    st.error("Please enter your OpenAI API key in the sidebar.")
                elif not anthropic_api_key and (selected_model == "claude-3" or selected_model == "both"):
                    st.error("Please enter your Anthropic API key in the sidebar.")
                else:
                    st.info("Running tests... This may take a moment.")
                    
                    results = {}
                    
                    # Run GPT-4 test
                    if selected_model == "gpt-4" or selected_model == "both":
                        with st.spinner("Testing with GPT-4..."):
                            try:
                                # Call OpenAI API
                                headers = {
                                    "Content-Type": "application/json",
                                    "Authorization": f"Bearer {openai_api_key}"
                                }
                                
                                payload = {
                                    "model": "gpt-4",
                                    "messages": [
                                        {"role": "system", "content": "You are a helpful assistant."},
                                        {"role": "user", "content": selected_query}
                                    ],
                                    "temperature": 0.7,
                                    "max_tokens": 500
                                }
                                
                                response = requests.post(
                                    "https://api.openai.com/v1/chat/completions",
                                    headers=headers,
                                    json=payload
                                )
                                
                                if response.status_code == 200:
                                    response_data = response.json()
                                    gpt_response = response_data["choices"][0]["message"]["content"]
                                    
                                    # Check if brand name is mentioned in response
                                    brand_name = selected_surface.get('brand_name', '').lower()
                                    picked_up = brand_name in gpt_response.lower()
                                    
                                    # Record result
                                    results["gpt-4"] = {
                                        "response": gpt_response,
                                        "picked_up": picked_up
                                    }
                                    
                                    # Update tracking
                                    if surface_generator_available:
                                        track_llm_pickup(
                                            selected_surface.get('slug'), 
                                            "gpt4", 
                                            selected_query, 
                                            picked_up
                                        )
                                    else:
                                        save_pickup_to_file(
                                            selected_surface.get('slug'), 
                                            "gpt4", 
                                            selected_query, 
                                            picked_up
                                        )
                                else:
                                    st.error(f"Error calling OpenAI API: {response.text}")
                            except Exception as e:
                                st.error(f"Error testing with GPT-4: {str(e)}")
                    
                    # Run Claude test
                    if selected_model == "claude-3" or selected_model == "both":
                        with st.spinner("Testing with Claude..."):
                            try:
                                # Call Anthropic API
                                headers = {
                                    "Content-Type": "application/json",
                                    "x-api-key": anthropic_api_key,
                                    "anthropic-version": "2023-06-01"
                                }
                                
                                payload = {
                                    "model": "claude-3-opus-20240229",
                                    "max_tokens": 500,
                                    "messages": [
                                        {"role": "user", "content": selected_query}
                                    ]
                                }
                                
                                response = requests.post(
                                    "https://api.anthropic.com/v1/messages",
                                    headers=headers,
                                    json=payload
                                )
                                
                                if response.status_code == 200:
                                    response_data = response.json()
                                    claude_response = response_data["content"][0]["text"]
                                    
                                    # Check if brand name is mentioned in response
                                    brand_name = selected_surface.get('brand_name', '').lower()
                                    picked_up = brand_name in claude_response.lower()
                                    
                                    # Record result
                                    results["claude-3"] = {
                                        "response": claude_response,
                                        "picked_up": picked_up
                                    }
                                    
                                    # Update tracking
                                    if surface_generator_available:
                                        track_llm_pickup(
                                            selected_surface.get('slug'), 
                                            "claude", 
                                            selected_query, 
                                            picked_up
                                        )
                                    else:
                                        save_pickup_to_file(
                                            selected_surface.get('slug'), 
                                            "claude", 
                                            selected_query, 
                                            picked_up
                                        )
                                else:
                                    st.error(f"Error calling Anthropic API: {response.text}")
                            except Exception as e:
                                st.error(f"Error testing with Claude: {str(e)}")
                    
                    # Display results
                    st.success("Tests completed!")
                    
                    for model, result in results.items():
                        with st.expander(f"{model} Response"):
                            st.write(f"**Picked up information about {selected_surface.get('brand_name')}**: {'Yes' if result['picked_up'] else 'No'}")
                            st.write("**Response:**")
                            st.markdown(result["response"])
    
    with tab2:
        st.subheader("View Test Results")
        
        # Load pickup data
        try:
            pickup_data = {}
            if os.path.exists(LLM_PICKUP_PATH):
                with open(LLM_PICKUP_PATH, 'r') as f:
                    pickup_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading LLM pickup data: {e}")
            pickup_data = {}
        
        if not pickup_data:
            st.info("No test results available yet. Run some tests first.")
        else:
            # Brand selection
            brands = list(pickup_data.keys())
            selected_brand_slug = st.selectbox("Select Brand", brands, key="results_brand")
            
            if selected_brand_slug in pickup_data:
                brand_pickup = pickup_data[selected_brand_slug]
                
                # Find brand name from slug
                brand_name = selected_brand_slug
                for surface in sorted_surfaces:
                    if surface.get('slug') == selected_brand_slug:
                        brand_name = surface.get('brand_name', selected_brand_slug)
                        break
                
                st.write(f"## Results for {brand_name}")
                
                # Display model tabs
                models = list(brand_pickup.keys())
                if models:
                    model_tabs = st.tabs(models)
                    
                    for i, model in enumerate(models):
                        with model_tabs[i]:
                            model_data = brand_pickup[model]
                            
                            # Display metrics
                            pickup_count = model_data.get('pickup_count', 0)
                            total_queries = model_data.get('total_queries', 0)
                            pickup_rate = 0
                            if total_queries > 0:
                                pickup_rate = pickup_count / total_queries
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Pickup Rate", f"{pickup_rate:.2%}")
                            with col2:
                                st.metric("Successful Pickups", pickup_count)
                            with col3:
                                st.metric("Total Queries", total_queries)
                            
                            # Display query history
                            st.subheader("Query History")
                            queries = model_data.get('queries', [])
                            
                            if queries:
                                # Sort by timestamp (most recent first)
                                sorted_queries = sorted(
                                    queries, 
                                    key=lambda x: x.get('timestamp', '2000-01-01'), 
                                    reverse=True
                                )
                                
                                for j, query in enumerate(sorted_queries):
                                    with st.expander(f"{query.get('query', 'Unknown query')} ({query.get('timestamp', 'Unknown').split('T')[0]})"):
                                        st.write(f"**Picked up**: {'Yes' if query.get('picked_up', False) else 'No'}")
                                        st.write(f"**Timestamp**: {query.get('timestamp', 'Unknown')}")
                            else:
                                st.write("No queries available")
                else:
                    st.warning("No model data available for this brand")
            else:
                st.warning("Brand not found in pickup data")

if __name__ == "__main__":
    # No additional logic needed, Streamlit handles the execution
    pass