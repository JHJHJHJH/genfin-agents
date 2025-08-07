from openai import OpenAI
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict
import fitz
import logging
# =========================
#  Utility: PDF page text
# =========================
def load_pdf_pages(pdf_path: str) -> List[str]:
    doc = fitz.open(pdf_path)
    pages = []
    for i, p in enumerate(doc):
        text = p.get_text("text")
        pages.append(text)
    return pages

def join_pages(pages: List[str]) -> str:
    return "\n\n".join([f"=== Page {i+1} ===\n{t}" for i, t in enumerate(pages)])

def quick_candidate_pages(pages: List[str]) -> Dict[str, List[int]]:
    """
    Very rough keyword filters to help the LLM focus.
    We still let the LLM decide; this reduces tokens.
    """
    idx = {
        "client": [],
        "policy": [],
        "benefits": [],
    }
    for i, t in enumerate(pages):
        low = t.lower()
        if any(k in low for k in ["life insured", "proposer", "date of birth", "gender", "occupation", "residency"]):
            idx["client"].append(i)
        if any(k in low for k in ["policy term", "premium term", "sum assured", "insurer", "what are you purchasing", "product type"]):
            idx["policy"].append(i)
        if any(k in low for k in ["policy illustration", "end of policy year", "death benefit", "surrender value", "table"]):
            idx["benefits"].append(i)
    return idx


class PolicyType(BaseModel):
    policy_type: str
    confidence: float = Field(ge=0, le=1)
    def __str__(self):
        return f"Policy type: {self.policy_type} (Confidence: {self.confidence})"
    
class PolicyClassifierAgent:
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def classify(self, file_id=None , file_path=None):
        client = OpenAI(api_key=self.api_key)
        
        if file_id == None and file_path == None:
            print("Either file_id or file_path must exist.")
            return
        elif file_path != None and file_id == None:      
            # Upload the PDF to OpenAI
            with open(file_path, "rb") as f:
                file_response = client.files.create(file=f, purpose="user_data")
                file_id = file_response.id

        logging.info("Policy classification started...")
        response = client.responses.parse(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": file_id,
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
        logging.info("Policy classification completed...")
        logging.info( result )
        
        return result



