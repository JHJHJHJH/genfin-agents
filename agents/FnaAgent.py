import fitz
import requests
from io import BytesIO
import json
import pprint
import re
class KycData:
    def __init__(self): 
        # self.client_name = None
        # self.spouse_name = None
        # self.advisor_name = None
        # self.advisor_num = None
        # self.case_num = None
        # self.identity_type = None
        # self.identity_number = None
        # self.mobile_number = None
        # self.email = None
        pass

  #utility
def extract_text_from_next_block(blocks, current_index):
    """Helper function to extract cleaned text from the next block."""
    next_block = blocks[current_index + 1]
    txt = next_block[4].split('\n')[0]
    
    if '$' in txt:
      try :
        numeric_part = re.sub(r'[^\d.-]', '', txt)
        num = float(numeric_part)
        return num
      except ValueError as e:
         return 0
      
    
    return txt
    
  #process cover page
def process_firstpage( first_pg , kyc_dataobject):
    blocks = first_pg.get_text('blocks', sort= True)
    for i, block in enumerate(blocks):
      if i == 0:
        txt = block[4] # sample tuple data 'Name of Client\nChe Yao Han\n'
        client_name = txt.split('\n')[1]
        kyc_dataobject.client_name = client_name
      elif i == 1:  
        txt = block[4]
        spouse_name = txt.split('\n')[1]
        kyc_dataobject.spouse_name = spouse_name
      elif i == 2:
        txt = block[4]
        advisor_name = txt.split('\n')[1]
        kyc_dataobject.advisor_name = advisor_name
      elif i == 3:
        txt = block[4]
        advisor_num = txt.split('\n')[1]
        kyc_dataobject.advisor_num = advisor_num
      elif i == 4:
        txt = block[4]
        case_num = txt.split('\n')[1]
        kyc_dataobject.case_num = case_num

    return kyc_dataobject

  #process section10a

def process_section12( page, kyc_dataobject):
    def extract_rider_info(text):
      pattern = r'Rider (\d+): (.+?)\n'
      match = re.search(pattern, text)
      if match:
          rider_number = match.group(1)
          policy_name = match.group(2)
          return rider_number, policy_name
      return None, None
    #functions
    def is_basis_of_recommendations(block):
      txt = block[4]
      return 'Basis of Recommendations' in txt
    def is_client_risk_profile(block):
      txt = block[4]
      return 'Client\'s Risk Profile' in txt
    def is_policy_term(block):
      txt = block[4]
      return 'Policy Term' in txt
    def is_rider(block):
      txt = block[4]
      return 'Rider' in txt
    
    riders = []
    #process section1
    blocks = page.get_text('blocks', sort= True)
    #assert section and data existence then extract
    for i, block in enumerate(blocks):
      print(block)
      if is_basis_of_recommendations(block):
        kyc_dataobject.policy_name = extract_text_from_next_block(blocks, i)
      if is_client_risk_profile(block):
        kyc_dataobject.payment_frequency = extract_text_from_next_block(blocks, i+1)
        kyc_dataobject.settlement_mode = extract_text_from_next_block(blocks, i+2)
      if is_policy_term(block):
        kyc_dataobject.sum_assured = extract_text_from_next_block(blocks, i)
        kyc_dataobject.premium = extract_text_from_next_block(blocks, i+1)
        kyc_dataobject.premium_term = extract_text_from_next_block(blocks, i+2)
        kyc_dataobject.policy_term = extract_text_from_next_block(blocks, i+3)
      if is_rider(block):
        rider_txt = block[4]
        rider_number, rider_name = extract_rider_info(rider_txt)
        # coverage_index = 
        rider_sum_assured = extract_text_from_next_block(blocks, i+4)
        rider_premium = extract_text_from_next_block(blocks, i+5)
        rider_premium_term = extract_text_from_next_block(blocks, i+6)
        rider_coverage_term = extract_text_from_next_block(blocks, i+7)
        rider = {
          "id" : rider_number,
          "name" : rider_name,
          "sum_assured" : rider_sum_assured,
          "premium" : rider_premium,
          "premium_term" : rider_premium_term,
          "policy_term" : rider_coverage_term,
        }
        riders.append(rider)
    
    kyc_dataobject.riders = riders
    # kyc_dataobject.total_premium = kyc_dataobject.premium + sum(r['premium'] for r in riders)
        

# Name of policy - ok
# Name of riders - ok
# Premium amount - ok
# Premium Frequency - ok
# Life Insured - ok
# Sum Assured - ok (TODO:Can this be different for each rider?)
# Policy Term  - ok
# Settlement Mode -ok
 
def process_section10a( page, kyc_dataobject):
    #functions
    def has_annual_expenses(block):
      txt = block[4]
      return 'Annual Amount Needs Required for Living Expenses' in txt
      
    #process section1
    blocks = page.get_text('blocks', sort= True)
    #assert section and data existence then extract
    for i, block in enumerate(blocks):
      print(block)
      if has_annual_expenses(block):
          kyc_dataobject.annual_expenses = extract_text_from_next_block(blocks, i)


    #process section1

def process_section1( page, kyc_dataobject):
    #functions
    def has_identitytype(block):
      txt = block[4]
      return 'Identity Type' in txt

    def has_identitynumber(block):
      txt = block[4]
      return 'Identity Number' in txt

    def has_mobilenumber(block):
      txt = block[4]
      return 'Mobile Number' in txt

    def has_email(block):
      txt = block[4]
      return 'Email\n' in txt
      
    def has_occupation(block):
      txt = block[4]
      return 'Occupation\n' in txt
      
    def has_employer(block):
      txt = block[4]
      return 'Employer\n' in txt

    #process section1
    blocks = page.get_text('blocks', sort= True)
    #assert section and data existence then extract
    for i, block in enumerate(blocks):
      print(block)
      if has_identitytype(block):
          kyc_dataobject.identity_type = extract_text_from_next_block(blocks, i)
      elif has_identitynumber(block):
          kyc_dataobject.identity_number = extract_text_from_next_block(blocks, i)
      elif has_mobilenumber(block):
          kyc_dataobject.mobile_number = extract_text_from_next_block(blocks, i)
      elif has_email(block):
          kyc_dataobject.email = extract_text_from_next_block(blocks, i)
      elif has_occupation(block):
          kyc_dataobject.occupation = extract_text_from_next_block(blocks, i)
      elif has_employer(block):
          kyc_dataobject.employer = extract_text_from_next_block(blocks, i)

#main method
def parse_pdf(doc):
      
    def is_section1_page(page):
      blocks = page.get_text('blocks', sort= True)
      if len(blocks) == 0:
        return
        # image_data = pix.tobytes()  # Get raw image bytes
        # width, height = pix.width, pix.height
      first_block = blocks[0]
      txt = first_block[4]
      return 'SECTION 1 - CLIENT INFORMATION' in txt
      
    def is_section10a_page(page):
      blocks = page.get_text('blocks', sort= True)
      first_block = blocks[0]
      txt = first_block[4]
      return 'SECTION 10A - NEEDS ANALYSIS' in txt

    def is_section12_page(page):
      blocks = page.get_text('blocks', sort= True)
      first_block = blocks[0]
      txt = first_block[4]
      return 'SECTION 12 - ADVICE AND RECOMMENDATIONS' in txt

    #STORE ALL DATA HERE
    kyc_dataobj = KycData()
    # md_text = pymupdf4llm.to_markdown(doc)
    # print(md_text)
    for page in doc:
      page_num = page.number + 1
      print(f"--- Page {page_num} ---")
      #https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text
      #blocks = page.get_text('text', sort= True)

      if page_num == 1: 
        process_firstpage(page, kyc_dataobj)
      elif is_section1_page(page):
        process_section1(page, kyc_dataobj)
      elif is_section10a_page(page):
        process_section10a(page, kyc_dataobj)
      elif is_section12_page(page):
        process_section12(page, kyc_dataobj)
        
      # widgets = page.widgets() NO WIDGETS CAN BE FOUND

    # print(kyc_dataobj.__dict__)
    doc.close()
    return kyc_dataobj


def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    print(f"Total pages: {len(doc)}")
    
    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load the current page
        text = page.get_text()  # Extract text
        
        print(f"\n--- Page {page_num + 1} ---")
        print(text)
  
    doc.close()  # Close the document


class FnaAgent:
   def __init__(self):
      pass
   
   def extract(self, file_path ):
      # pdf_doc = fitz.open("resources/Annuity-FNA.pdf" ) # open a document
      pdf_doc = fitz.open(file_path) # open a document

      kyc_data = parse_pdf(pdf_doc)

      return kyc_data
   
def main():
    fna_file_path = 'resources/Term/Term-3-FNA.pdf'
    fna_agent = FnaAgent()
    kyc_data = fna_agent.extract(fna_file_path)
        
    pprint.pprint(kyc_data.__dict__, indent=2)

if __name__ == "__main__":
    main()

#if url
# url = 'some file url'
# response = requests.get(url)
# response.raise_for_status()  # Check for download errors
# # Open the PDF from memory
# pdf_data = BytesIO(response.content)
# dopdf_docc = fitz.open(stream=pdf_data, filetype="pdf")



# import base64
# from openai import OpenAI

# client = OpenAI()

# prompt = "What is in this image?"
# with open("path/to/image.png", "rb") as image_file:
#     b64_image = base64.b64encode(image_file.read()).decode("utf-8")

# response = client.responses.create(
#     model="gpt-4o-mini",
#     input=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "input_text", "text": prompt},
#                 {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
#             ],
#         }
#     ],
# )