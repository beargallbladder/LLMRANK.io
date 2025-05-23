"""
Brand Surface Claim Page

This application allows brands to claim and manage their Surface pages.
"""

import streamlit as st
import json
import os
import logging
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SURFACE_DATA_DIR = "data/surface"
os.makedirs(SURFACE_DATA_DIR, exist_ok=True)

BRAND_SURFACES_PATH = os.path.join(SURFACE_DATA_DIR, "brand_surfaces.json")
CLAIMS_PATH = os.path.join(SURFACE_DATA_DIR, "claims.json")

# Functions for managing claims
def load_surfaces():
    """Load all brand surfaces from file."""
    surfaces = {}
    try:
        if os.path.exists(BRAND_SURFACES_PATH):
            with open(BRAND_SURFACES_PATH, 'r') as f:
                surfaces = json.load(f)
    except Exception as e:
        logger.error(f"Error loading surfaces: {e}")
    return surfaces

def load_claims():
    """Load all claims from file."""
    claims = {}
    try:
        if os.path.exists(CLAIMS_PATH):
            with open(CLAIMS_PATH, 'r') as f:
                claims = json.load(f)
    except Exception as e:
        logger.error(f"Error loading claims: {e}")
        claims = {}
    return claims

def save_claim(email, brand_slug):
    """Save a new claim request."""
    claims = load_claims()
    
    if brand_slug not in claims:
        claims[brand_slug] = []
    
    # Check if this email already made a claim
    for claim in claims[brand_slug]:
        if claim.get('email') == email:
            return False
    
    # Add new claim
    claims[brand_slug].append({
        'email': email,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    })
    
    try:
        with open(CLAIMS_PATH, 'w') as f:
            json.dump(claims, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving claim: {e}")
        return False

def update_surface(brand_slug, updates):
    """Update a brand surface."""
    surfaces = load_surfaces()
    
    if brand_slug not in surfaces:
        return False
    
    # Update fields
    surface = surfaces[brand_slug]
    if 'summary' in updates:
        surface['summary'] = updates['summary']
    
    if 'faq' in updates:
        surface['faq'] = updates['faq']
    
    if 'tags' in updates:
        surface['tags'] = updates['tags']
    
    # Update timestamps
    surface['updated_at'] = datetime.now().isoformat()
    
    try:
        with open(BRAND_SURFACES_PATH, 'w') as f:
            json.dump(surfaces, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error updating surface: {e}")
        return False

def verify_domain_ownership(email, domain):
    """
    Verify that the user owns the domain.
    
    In a real implementation, this would send a verification email
    or check for DNS verification. For this demo, we'll assume any
    email that matches the domain is valid.
    """
    try:
        email_domain = email.split('@')[1]
        if email_domain == domain or domain.endswith('.' + email_domain):
            return True
        return False
    except:
        return False

# Page configuration
st.set_page_config(
    page_title="Claim Your Brand Surface",
    page_icon="🏢",
    layout="wide"
)

# Main interface
st.title("Claim Your Brand Surface")
st.subheader("Take control of your brand's memory in LLMs")

st.markdown("""
LLMPageRank's The Surface feature provides structured, semantically-optimized
public memory artifacts for your brand. By claiming your brand surface, you can:

- Control your brand's narrative in LLMs
- Receive alerts about memory drift
- Track when LLMs pick up information about your brand
- Ensure accurate information is used by language models
""")

# Load all surfaces
surfaces = load_surfaces()

# Tabs for claim and manage
tab1, tab2 = st.tabs(["Claim Your Surface", "Manage Your Surfaces"])

with tab1:
    st.header("Claim Your Brand Surface")
    
    # Get list of unclaimed surfaces
    unclaimed_surfaces = {slug: surface for slug, surface in surfaces.items() 
                         if not surface.get('claimed', False)}
    
    if not unclaimed_surfaces:
        st.info("No unclaimed surfaces are available at this time.")
    else:
        # Allow selection of brand
        brand_options = []
        for slug, surface in unclaimed_surfaces.items():
            brand_name = surface.get('brand_name', 'Unknown')
            domain = surface.get('domain', 'unknown.com')
            brand_options.append(f"{brand_name} ({domain})")
        
        selected_brand_index = st.selectbox(
            "Select Your Brand",
            range(len(brand_options)),
            format_func=lambda i: brand_options[i]
        )
        
        # Get selected surface
        selected_slug = list(unclaimed_surfaces.keys())[selected_brand_index]
        selected_surface = unclaimed_surfaces[selected_slug]
        
        # Display surface info
        st.subheader(f"About {selected_surface.get('brand_name', 'Unknown')}")
        st.write(f"**Domain**: {selected_surface.get('domain', 'unknown.com')}")
        st.write(f"**Preservation Score**: {selected_surface.get('preservation_score', 0):.2f}")
        
        # Display current memory draft
        with st.expander("Current Memory Draft"):
            st.write(selected_surface.get('summary', 'No summary available'))
            
            faqs = selected_surface.get('faq', [])
            if faqs:
                st.subheader("FAQ")
                for faq in faqs:
                    st.write(f"**Q: {faq.get('question', '')}**")
                    st.write(f"A: {faq.get('answer', '')}")
        
        # Claim form
        st.subheader("Claim This Surface")
        with st.form(key="claim_form"):
            st.write("To claim this surface, you must verify ownership of the domain.")
            
            # Contact information
            email = st.text_input("Business Email (must match domain)")
            name = st.text_input("Your Name")
            title = st.text_input("Your Title")
            
            # Terms agreement
            terms_agreed = st.checkbox("I agree to the terms and conditions")
            
            # Submit button
            submit_button = st.form_submit_button("Submit Claim")
            
            if submit_button:
                if not email or not name or not title:
                    st.error("Please fill out all fields.")
                elif not terms_agreed:
                    st.error("You must agree to the terms and conditions.")
                else:
                    # Verify domain ownership
                    domain = selected_surface.get('domain', '').lower()
                    if verify_domain_ownership(email, domain):
                        # Save claim
                        if save_claim(email, selected_slug):
                            st.success("""
                            Claim submitted successfully! We'll review your claim and send you an email with next steps.
                            Once approved, you'll be able to manage your brand surface.
                            """)
                        else:
                            st.error("There was an error submitting your claim. Please try again.")
                    else:
                        st.error(f"Your email must match the domain {domain} to claim this surface.")

with tab2:
    st.header("Manage Your Surfaces")
    
    # In a real implementation, this would check for authenticated users
    # For this demo, we'll use a simple login form
    with st.expander("Login to Manage Your Surfaces"):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_button = st.button("Login")
        
        if login_button:
            if login_email and login_password:
                # In a real implementation, this would verify credentials
                # For this demo, we'll accept any input
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = login_email
                st.rerun()
            else:
                st.error("Please enter your email and password.")
    
    # Check if user is logged in
    if st.session_state.get('logged_in'):
        email = st.session_state.get('user_email')
        
        # Find claimed surfaces for this user
        claims = load_claims()
        user_claims = []
        
        for brand_slug, claim_list in claims.items():
            for claim in claim_list:
                if claim.get('email') == email and claim.get('status') != 'rejected':
                    # Check if surface exists
                    if brand_slug in surfaces:
                        user_claims.append((brand_slug, surfaces[brand_slug]))
        
        if not user_claims:
            st.info("You don't have any claimed surfaces yet.")
        else:
            # Display tabs for each claimed surface
            claimed_tabs = st.tabs([surface[1].get('brand_name', 'Unknown') for surface in user_claims])
            
            for i, (brand_slug, surface) in enumerate(user_claims):
                with claimed_tabs[i]:
                    # Display current status
                    claim_status = "Pending"
                    for claim in claims.get(brand_slug, []):
                        if claim.get('email') == email:
                            claim_status = claim.get('status', 'Pending')
                            break
                    
                    st.info(f"Claim Status: {claim_status.capitalize()}")
                    
                    if claim_status.lower() == 'approved':
                        # Allow editing surface content
                        with st.form(key=f"edit_form_{i}"):
                            st.subheader("Edit Surface Content")
                            
                            new_summary = st.text_area(
                                "Summary", 
                                value=surface.get('summary', ''), 
                                height=150
                            )
                            
                            # FAQ editor
                            st.subheader("FAQ Items")
                            faqs = surface.get('faq', [])
                            new_faqs = []
                            
                            for j, faq in enumerate(faqs):
                                col1, col2 = st.columns(2)
                                with col1:
                                    question = st.text_input(
                                        f"Question {j+1}", 
                                        value=faq.get('question', ''),
                                        key=f"q_{brand_slug}_{j}"
                                    )
                                with col2:
                                    answer = st.text_input(
                                        f"Answer {j+1}", 
                                        value=faq.get('answer', ''),
                                        key=f"a_{brand_slug}_{j}"
                                    )
                                new_faqs.append({"question": question, "answer": answer})
                            
                            # Add new FAQ button
                            if st.checkbox("Add New FAQ Item", key=f"add_faq_{brand_slug}"):
                                new_q = st.text_input("New Question", key=f"new_q_{brand_slug}")
                                new_a = st.text_input("New Answer", key=f"new_a_{brand_slug}")
                                if new_q and new_a:
                                    new_faqs.append({"question": new_q, "answer": new_a})
                            
                            # Tags editor
                            tags_str = ", ".join(surface.get('tags', []))
                            new_tags_str = st.text_input("Tags (comma-separated)", value=tags_str)
                            new_tags = [tag.strip() for tag in new_tags_str.split(",") if tag.strip()]
                            
                            # Save button
                            submit_button = st.form_submit_button("Save Changes")
                            
                            if submit_button:
                                # Prepare content updates
                                updates = {
                                    "summary": new_summary,
                                    "faq": new_faqs,
                                    "tags": new_tags
                                }
                                
                                # Update content
                                if update_surface(brand_slug, updates):
                                    st.success("Content updated successfully! Refresh to see changes.")
                                else:
                                    st.error("Failed to update content. Please try again.")
                    else:
                        st.write("You'll be able to edit this surface once your claim is approved.")
                    
                    # Display current content
                    st.subheader("Current Content")
                    st.write(surface.get('summary', 'No summary available'))
                    
                    faqs = surface.get('faq', [])
                    if faqs:
                        st.subheader("FAQ")
                        for faq in faqs:
                            st.write(f"**Q: {faq.get('question', '')}**")
                            st.write(f"A: {faq.get('answer', '')}")
                    
                    # Display URL
                    st.subheader("Access URL")
                    st.code(f"https://llmpagerank.com/brands/{brand_slug}")
    else:
        st.info("Please login to manage your surfaces.")

if __name__ == "__main__":
    # No additional logic needed, Streamlit handles the execution
    pass