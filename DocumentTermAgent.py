from openai import OpenAI
from pydantic import BaseModel, Field
import json
from datetime import date
from typing import List

class Insured(BaseModel):
    name : str
    age : int
    gender : str
    date_of_birth : date
    is_smoker : bool

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


class DocumentTermAgent:
    
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

        response = client.responses.parse(
            model="gpt-4o",
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
            text_format=TermDocument,
        )
        # Print raw content
        result = response.output_parsed
        print(result)
        return result



