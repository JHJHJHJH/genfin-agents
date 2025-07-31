from openai import OpenAI
from pydantic import BaseModel, Field
import json
from datetime import date
from typing import List


class PolicyType(BaseModel):
    policy_type: str
    confidence: float = Field(ge=0, le=1)

class PolicyClassifierAgent:
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def ReadDoc(self):
        pass

open_ai_key = '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'
client = OpenAI(api_key= open_ai_key)

# Path to the PDF form
pdf_path = "resources/Term-CTP.pdf" #fileid = 'file-VWsgoAhsmzuz4hMXmBye1x'

# Upload the PDF to OpenAI
with open(pdf_path, "rb") as f:
    file_response = client.files.create(file=f, purpose="user_data")



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
                    "text": "You are a vision-based insurance-document classifier.",
                },
                {
                    "type" : "input_text",
                    "text" : "Identify the policy type succinctly (e.g., 'Term', 'Whole Life', 'Endowment', 'ILP'.)."
                }
            ]
        }
    ],
    text_format=PolicyType,
)
# Print raw content
result = response.output_parsed
print(result)

