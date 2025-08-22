import streamlit as st
import pandas as pd

# App title
st.title("📁 File Uploader App")
st.write("Upload two files to process them")

# File uploaders
st.header("Upload Files")

# First file input
file1 = st.file_uploader(
    "Upload first file", 
    type=['txt', 'csv', 'json', 'xlsx', 'xls'],
    key="file1"
)

# Second file input
file2 = st.file_uploader(
    "Upload second file", 
    type=['txt', 'csv', 'json', 'xlsx', 'xls'],
    key="file2"
)

# Process files
if file1 is not None or file2 is not None:
    st.header("File Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if file1 is not None:
            st.subheader("First File Details")
            st.write(f"**Filename:** {file1.name}")
            st.write(f"**File type:** {file1.type}")
            st.write(f"**File size:** {file1.size} bytes")
            
            # Try to display content based on file type
            try:
                if file1.name.endswith('.csv'):
                    df1 = pd.read_csv(file1)
                    st.write("**Preview:**")
                    st.dataframe(df1.head())
                elif file1.name.endswith(('.xlsx', '.xls')):
                    df1 = pd.read_excel(file1)
                    st.write("**Preview:**")
                    st.dataframe(df1.head())
                elif file1.name.endswith('.txt'):
                    content = file1.read().decode('utf-8')
                    st.write("**Content preview:**")
                    st.text_area("Text content", content[:500] + "..." if len(content) > 500 else content, height=150)
                    file1.seek(0)  # Reset file pointer
            except Exception as e:
                st.error(f"Error reading file 1: {e}")
    
    with col2:
        if file2 is not None:
            st.subheader("Second File Details")
            st.write(f"**Filename:** {file2.name}")
            st.write(f"**File type:** {file2.type}")
            st.write(f"**File size:** {file2.size} bytes")
            
            # Try to display content based on file type
            try:
                if file2.name.endswith('.csv'):
                    df2 = pd.read_csv(file2)
                    st.write("**Preview:**")
                    st.dataframe(df2.head())
                elif file2.name.endswith(('.xlsx', '.xls')):
                    df2 = pd.read_excel(file2)
                    st.write("**Preview:**")
                    st.dataframe(df2.head())
                elif file2.name.endswith('.txt'):
                    content = file2.read().decode('utf-8')
                    st.write("**Content preview:**")
                    st.text_area("Text content", content[:500] + "..." if len(content) > 500 else content, height=150)
                    file2.seek(0)  # Reset file pointer
            except Exception as e:
                st.error(f"Error reading file 2: {e}")

# Simple file comparison (optional)
if file1 is not None and file2 is not None:
    st.header("File Comparison")
    st.write(f"Both files uploaded successfully!")
    st.write(f"Total size: {file1.size + file2.size} bytes")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Upload your first file using the first uploader
2. Upload your second file using the second uploader
3. The app will display file information and previews
4. Supported file types: CSV, Excel, TXT, JSON
""")