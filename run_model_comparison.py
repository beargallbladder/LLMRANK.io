"""
Run the Model Comparison Dashboard application.

This script starts the Model Comparison Dashboard application on port 5002.
"""

import streamlit as st
import model_comparison_dashboard
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Model Comparison Dashboard."""
    logger.info("Starting Model Comparison Dashboard")
    model_comparison_dashboard.render_model_comparison_dashboard()

if __name__ == "__main__":
    main()