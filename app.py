import streamlit as st
import pandas as pd
from agents.DocumentTermAgent import DocumentTermAgent
from agents.FnaAgent import FnaAgent
# App title
st.title("📁 Kysee - Gen FA's KYC Verifier")
st.write("Upload FNA & BI documents")

# File uploaders
st.header("Upload Files")
col1, col2 = st.columns(2)

with col1 :

    # First file input
    fna_file = st.file_uploader(
        "Upload FNA file", 
        type=['pdf'],
        key="fna_file"
    )
    if fna_file is not None:
        st.subheader("FNA Details")
        st.write(f"**Filename:** {fna_file.name}")
        # st.write(f"**File type:** {fna_file.type}")
        # st.write(f"**File size:** {fna_file.size} bytes")
        with st.spinner("Processing FNA file...⏳"):
            fna_agent = FnaAgent()
            kyc_data = fna_agent.extract(file_obj=fna_file)
            st.success("Processing completed! ✅")
            st.write(f"**Personal Details**")
            st.write(f"**Name:** {kyc_data.client_name}")
            st.write(f"**NRIC:** {kyc_data.identity_number}")
            st.write(f"**Occupation:** {kyc_data.occupation}")
            st.write(f"**Employer:** {kyc_data.employer}")
            st.divider()
            st.write(f"**Policy Details**")
            st.write(f"**Policy:** {kyc_data.policy_name}")
            st.write(f"**Term:** {kyc_data.policy_term}")
            st.write(f"**Settlement Mode:** {kyc_data.settlement_mode}")
            st.write(f"**Sum Assured:** {kyc_data.sum_assured}")

            for r in kyc_data.riders:
                st.write(f"**Rider {r.id}:** {r.name}")

        
with col2:
# Second file input
    file2 = st.file_uploader(
        "Upload BI file", 
        type=['pdf'],
        key="file2"
    )

# Process files
# if fna_file is not None or file2 is not None:
#     st.header("File Information")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         if fna_file is not None:
#             st.subheader("FNA Details")
#             st.write(f"**Filename:** {fna_file.name}")
#             st.write(f"**File type:** {fna_file.type}")
#             st.write(f"**File size:** {fna_file.size} bytes")
            
#             # Try to display content based on file type
#             try:
#                 if fna_file.name.endswith('.csv'):
#                     df1 = pd.read_csv(fna_file)
#                     st.write("**Preview:**")
#                     st.dataframe(df1.head())

#             except Exception as e:
#                 st.error(f"Error reading FNA file: {e}")
    
#     with col2:
#         if file2 is not None:
#             st.subheader("Second File Details")
#             st.write(f"**Filename:** {file2.name}")
#             st.write(f"**File type:** {file2.type}")
#             st.write(f"**File size:** {file2.size} bytes")
            
#             # Try to display content based on file type
#             try:
#                 if file2.name.endswith('.csv'):
#                     df2 = pd.read_csv(file2)
#                     st.write("**Preview:**")
#                     st.dataframe(df2.head())
#                 elif file2.name.endswith(('.xlsx', '.xls')):
#                     df2 = pd.read_excel(file2)
#                     st.write("**Preview:**")
#                     st.dataframe(df2.head())
#                 elif file2.name.endswith('.txt'):
#                     content = file2.read().decode('utf-8')
#                     st.write("**Content preview:**")
#                     st.text_area("Text content", content[:500] + "..." if len(content) > 500 else content, height=150)
#                     file2.seek(0)  # Reset file pointer
#             except Exception as e:
#                 st.error(f"Error reading file 2: {e}")

# # Simple file comparison (optional)
# if fna_file is not None and file2 is not None:
#     st.header("File Comparison")
#     st.write(f"Both files uploaded successfully!")
#     st.write(f"Total size: {fna_file.size + file2.size} bytes")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Upload your first file using the first uploader
2. Upload your second file using the second uploader
3. The app will display file information and previews
4. Supported file types: PDF
""")