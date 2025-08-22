import streamlit as st

from agents.DocumentTermAgent import DocumentTermAgent
from agents.PolicyClassifierAgent import PolicyClassifierAgent
from agents.FnaAgent import FnaAgent
import io
from openai import OpenAI
# App title
st.set_page_config(
    layout="wide",  # Options: "centered" (default) or "wide"
    page_title="GEN FA",
    page_icon="🚀"
)
_ , page, _ = st.columns([1,3.5,1])

with page:
    st.title("👾 Gen FA KYC Verification")
    st.info("Your documents are processed using enterprise-grade encryption and are never stored permanently.\nAll data is handled in compliance with industry security standards and privacy regulations.")

    # File uploaders
    st.header("Upload Files")
    col1, col2 = st.columns(2, gap="medium", width=1300)

    with col1 :

        # First file input
        fna_file = st.file_uploader(
            "FNA file", 
            type=['pdf'],
            key="fna_file"
        )
      
    with col2:
    # Second file input
        bi_file = st.file_uploader(
            "BI file", 
            type=['pdf'],
            key="bi_file"
        )
    
    if fna_file and bi_file:
        if st.button("Process Files"):
            with col1:
                st.subheader("FNA Details")
                st.write(f"**Filename:** {fna_file.name}")
                with st.status("Processing FNA file...⏳", expanded=True) as fna_status:
                    st.write("Extracting FNA information...")
                    fna_agent = FnaAgent()
                    kyc_data = fna_agent.extract(file_obj=fna_file)
                    fna_status.update(
                        label="FNA processing complete!", state="complete", expanded=False
                    )
                            
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
                
                st.write(f"**Total Premium:** { kyc_data.premium + sum(r.premium for r in kyc_data.riders)}")

            with col2:
                st.subheader("BI Details")
                st.write(f"**Filename:** {bi_file.name}")
                # st.write(f"**File type:** {fna_file.type}")
                # st.write(f"**File size:** {fna_file.size} bytes")
                with st.status("Processing BI...⏳", expanded=True) as status:
                    st.write("Classifying document...")
                    buffered_reader= io.BufferedReader(bi_file)
                    # content = file.read()
                    # Upload the PDF to OpenAI
                    client = client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    file_response = client.files.create(file=buffered_reader, purpose="user_data")
                    file_id = file_response.id

                    classifier_agent = PolicyClassifierAgent(st.secrets["OPENAI_API_KEY"])
                    policy_type = classifier_agent.classify(file_id=file_id)
                    st.write(f"Identified Policy Type : **{policy_type.policy_type}** with **{policy_type.confidence}** Confidence")
                    st.write(f"Running **{policy_type.policy_type}** Agent... Extracting BI information...")
                    term_agent = DocumentTermAgent(st.secrets["OPENAI_API_KEY"])
                    doc = term_agent.extract(file_id=file_id)
                    
                    status.update(
                        label="BI processing complete!", state="complete", expanded=False
                    )
                client = doc.insured_details
                policy = doc.policy_details
                st.write(f"**Personal Details**")
                st.write(f"**Name:** {client.name.value} (Page {client.name.page} | Confidence {client.name.confidence} )")
                st.write(f"**Age:** {client.age.value} (Page {client.age.page} | Confidence {client.age.confidence} )")
                st.write(f"**Gender:**  {client.gender.value} (Page {client.gender.page} | Confidence {client.gender.confidence} )")
                st.write(f"**Is Smoker?:** {client.is_smoker.value} (Page {client.is_smoker.page} | Confidence {client.is_smoker.confidence} )")
                st.divider()
                st.write(f"**Policy Details**")
                st.write(f"**Policy:** {policy.policy_name.value} (Page {policy.policy_name.page} | Confidence {policy.policy_name.confidence} )")
                st.write(f"**Term:** {policy.premium_term.value} (Page {policy.premium_term.page} | Confidence {policy.premium_term.confidence} )")
                st.write(f"**Policy Date:** {policy.policy_date.value} (Page {policy.policy_date.page} | Confidence {policy.policy_date.confidence} )")
                st.write(f"**Insurer :** {policy.insurer_company.value} (Page {policy.insurer_company.page} | Confidence {policy.insurer_company.confidence} )")
                st.write(f"**Sum assured :** {policy.sum_assured.value} (Page {policy.sum_assured.page} | Confidence {policy.sum_assured.confidence} )")
                for i, rider in enumerate( policy.policy_riders ):
                    st.write(f"**Rider {str(i)} :** {rider.value} (Page {rider.page} | Confidence {rider.confidence} )")
                st.write(f"**Total Premium :** {policy.yearly_premium.value} (Page {policy.yearly_premium.page} | Confidence {policy.yearly_premium.confidence} )")


                

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
# st.sidebar.header("Instructions")
# st.sidebar.write("""
# 1. Upload your first file using the first uploader
# 2. Upload your second file using the second uploader
# 3. The app will display file information and previews
# 4. Supported file types: PDF
# """)