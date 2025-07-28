import pdfplumber 


pdf_file = "resources/Term.pdf"
password = 'GENFA_1234'
tables = {}
with pdfplumber.open(pdf_file, password=password) as pdf:
    for i, page in enumerate(pdf.pages):
        extracted_tables = page.extract_tables()
        tables[i] = extracted_tables
        # for table in extracted_tables:
        #     tables.append(table)

# Example: print first table
for row in tables[0]:
    print(row)