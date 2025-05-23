"""
Run Insight Dashboard

This script runs the Insight Dashboard for the LLMRank Insight Engine.
It displays domain memory metrics, ranking changes, and model comparisons.
"""

import streamlit as st
import insight_dashboard

if __name__ == "__main__":
    insight_dashboard.main()