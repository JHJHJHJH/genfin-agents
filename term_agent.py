from openai import OpenAI
from pydantic import BaseModel
import json
from datetime import date
from typing import List

class Insured(BaseModel):
    name : str
    age : int
    gender : str
    date_of_birth : date

class DeathBenefitTableRow(BaseModel):
    policy_year : int
    age : int
    premiums_paid : int
    death_benefits : int
    surrender_value : int

class DeathBenefitTable(BaseModel):
    rows : List[DeathBenefitTableRow]

class TermDocument(BaseModel):
    policy_date : date
    premium_term: int
    insurer: str
    sum_assured : float
    yearly_premium : int
    monthly_premium : int
    insured : Insured
    death_benefit_table : DeathBenefitTable

open_ai_key = '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'
client = OpenAI(api_key= open_ai_key)

# Path to the PDF form
pdf_path = "resources/Term-CTP.pdf"

# Vision-aware prompt with confidence score requirement
prompt = """
Extract all structured data from this PDF form using vision-based analysis.

Instructions:
1. Segment data by table type (e.g., Section 1 - Client Information).
2. For each radio button or checkbox group (e.g., Title, Gender, Smoker):
   - List all available options.
   - Use vision to visually inspect which option is selected (marked by check, filled circle, X, etc.).
   - Do not infer based on text position—only select visually confirmed values.
   - Return a `confidence` score from 0 (guess) to 100 (high certainty).
3. Extract text fields exactly as seen in the form (e.g., full name, NRIC, contact).
4. Return `null` or `"unmarked"` if value is not visually selected.
5. Format output as clean JSON with `"value"` and `"confidence"` keys for each field.
"""

# Upload the PDF to OpenAI
with open(pdf_path, "rb") as f:
    file_response = client.files.create(file=f, purpose="user_data")

# Request GPT-4o to process the PDF with vision
# response = client.chat.completions.create(
#     model="gpt-4o",
#     input=[
#         {"role": "system", "content": "You are a vision-based form extraction assistant."},
#         {"role": "user", "content": prompt},
#         {
#             "role": "user", "content": [
#                 {"type": "input_file", "file_id": file_response.id}
#             ]
#         }
#     ]
# )
response = client.responses.parse(
    model="gpt-4o",
    input=[
                {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file_response.id,
                },
                {
                    "type": "input_text",
                    "text": "You are a vision-based form extraction assistant.",
                },
                {
                    "type" : "input_text",
                    "text" : prompt
                }
            ]
        }
    ],
    text_format=TermDocument,
)
# Print raw content
result = response.output_text
print(result)

# Optionally, try to save as JSON if it's a valid JSON string
try:
    parsed = json.loads(result)
    with open("extracted_form_data.json", "w") as f:
        json.dump(parsed, f, indent=2)
    print("✅ JSON output saved to extracted_form_data.json")
except json.JSONDecodeError:
    print("⚠️ Response was not valid JSON. Check formatting or manually adjust.")
