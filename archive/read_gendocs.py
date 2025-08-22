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
