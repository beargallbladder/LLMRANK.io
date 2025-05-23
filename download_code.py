import streamlit as st
import base64
import zipfile
import io
import os
import glob

st.set_page_config(page_title="LLMPageRank Code Download")
st.title("LLMPageRank Code Download")

# Create zip file in memory
def create_zip():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Add Python files from root directory
        for file in glob.glob("*.py"):
            zf.write(file)
        
        # Add important directories
        for folder in ['agents', 'data', 'api', 'prompts']:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zf.write(file_path)
    
    memory_file.seek(0)
    return memory_file

# Create download link
def get_download_link(file_bytes, file_name="llmrank_code.zip"):
    b64 = base64.b64encode(file_bytes.read()).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="{file_name}">Download {file_name}</a>'
    return href

# Create the zip file
zip_file = create_zip()

# Create download button
st.write("Click the link below to download your code as a zip file:")
st.markdown(get_download_link(zip_file), unsafe_allow_html=True)

# Show confirmation
st.success("The download link is ready. Click it to download your LLMPageRank code as a zip file.")