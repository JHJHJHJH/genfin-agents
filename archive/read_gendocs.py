import pymupdf4llm
import fitz  # PyMuPDF
from io import BytesIO

pdf_file = "resources/Term.pdf"
password = 'GENFA_1234'
# # Example: Load PDF from a file into memory
with open(pdf_file, "rb") as f:
    pdf_bytes = f.read()

# Wrap in BytesIO
pdf_stream = BytesIO(pdf_bytes)

doc = fitz.open(stream=pdf_stream, filetype="pdf")

# Check if password is needed
if doc.needs_pass:
    
    if not doc.authenticate(password):
        print("Wrong password!")
    else:
        md_text = pymupdf4llm.to_markdown(doc=doc)
        print("PDF successfully unlocked from memory.")
else:
    print("PDF is not password protected.")

doc.close()

# print(md_text)
# .\myenv\Scripts\activate
#shield = hospital plan - no BI, because generally only have public and private. publicly available data

# Wholelife & term covers (SAME FOR BOTH) :
# death
# total permanent disability (TPD)
# critical illness (early-severe stage) 
# -death benefit table (main)
# -ci table
# -tpd table
# -surrender value table (only wholelife )

# Wholelife 
# - low coverage, high premium. Has cash value if nothing happens (Will have surrender value table)
# Term 
# - high coverage, low premium. No cash value. 
# No multiplier


#Annuity
#lifetime income product , e.g. put 3-5 years payment term, yield yearly income
#-impt points
#1. guarranteed income
#2. total income 

#Navigator - like syfe/stashaway
#no BI

