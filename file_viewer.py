import streamlit as st
import os
import glob

st.set_page_config(layout="wide", page_title="LLMPageRank Code Viewer")

st.title("LLMPageRank Code Viewer")

st.write("Use this page to view your code files")

# Get all Python files
files = sorted(glob.glob("*.py"))
folders = sorted([f for f in os.listdir() if os.path.isdir(f) and not f.startswith('.')])

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Files")
    selected_folder = st.selectbox("Select Folder", ["root"] + folders)
    
    if selected_folder == "root":
        file_list = files
    else:
        file_list = sorted(glob.glob(f"{selected_folder}/*.py"))
    
    selected_file = st.selectbox("Select File", file_list)

with col2:
    st.subheader(f"Viewing: {selected_file}")
    
    if selected_file:
        try:
            with open(selected_file, 'r') as f:
                code = f.read()
                st.code(code, language="python")
                
                # Also provide the code as text that can be copied easily
                with st.expander("Copy Code"):
                    st.text_area("", code, height=300)
        except Exception as e:
            st.error(f"Error reading file: {e}")