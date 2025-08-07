from openai import OpenAI
from pydantic import BaseModel, Field
import json
from datetime import date
from typing import List, Literal
import logging

prompt = """
Extract all structured data from this term insurance document using vision-based analysis.
Instructions:
1. If a field is missing, set it to null.
2. Return a "`confidence`" score from 0 (guess) to 1 (high certainty)
3. Format output as clean JSON with `"value"`, `"page"` and `"confidence"` keys for each field.
4. Identify the policy details ("policy_date" in DDMMYYYY, "premium_term", "insurer_company", "sum_assured", "yearly_premium", "monthly_premium"), and parse into `"PolicyDetails"`.
5. Identify the person/life insured details ("name", "age", "gender", "date_of_birth", "is_smoker"), and parse into  `"InsuredDetails"`.
6. Identify the death benefits table, and parse "ALL" visible rows into  `"DeathBenefitTable"`. There should be more than 10 rows.
"""
class BaseValue(BaseModel):
    confidence: float = Field(ge=0, le=1)
    page: int

class IntValue(BaseValue):
    value: int

class FloatValue(BaseValue):
    value: float

class StrValue(BaseValue):
    value: str

class DateValue(BaseValue):
    value: date

class BoolValue(BaseValue):
    value: bool

class InsuredDetails(BaseModel):
    name : StrValue
    age : IntValue
    gender : StrValue
    date_of_birth : DateValue
    is_smoker : BoolValue
    def __str__(self):
        s = 'Insured Details------------\n'
        s += f"Name : {self.name.value} \t (Page {self.name.page} | Confidence {self.name.confidence} )\n"
        s += f"Age: {self.age.value} \t (Page {self.age.page} | Confidence {self.age.confidence} )\n"
        s += f"Gender: {self.gender.value} \t (Page {self.gender.page} | Confidence {self.gender.confidence} )\n"
        s += f"DOB (DDMMYYYY): {self.date_of_birth.value} \t (Page {self.date_of_birth.page} | Confidence {self.date_of_birth.confidence} )\n"
        s += f"Is Smoker: {self.is_smoker.value} \t (Page {self.is_smoker.page} | Confidence {self.is_smoker.confidence} )\n"
        return s

class DeathBenefitTableRow(BaseModel):
    policy_year : IntValue
    age : IntValue
    premiums_paid : IntValue
    death_benefits : IntValue
    surrender_value : IntValue

class DeathBenefitTable(BaseModel):
    rows : List[DeathBenefitTableRow]
    def __str__(self):
        s = 'Death Benefits Table-----------------\n'
        s += 'End of Policy Year\t| Age\t| Premiums Paid($)\t| Death Benefits($)\t| Surrender($)\t| Confidence\t| Page\n'

        for row in self.rows:
            s += f"{row.policy_year.value}\t|{row.age.value}\t|{row.premiums_paid.value}\t|{row.death_benefits.value}\t|{row.surrender_value.value}\t|{row.policy_year.confidence}\t|{row.policy_year.page} \n"

        return s
class PolicyDetails(BaseModel):
    policy_date : DateValue
    premium_term: IntValue
    insurer_company: StrValue
    sum_assured : FloatValue
    yearly_premium : FloatValue
    monthly_premium : FloatValue
    
    def __str__(self):
        s = 'Policy Details----------------\n'
        s += f"Policy Date : {self.policy_date.value} \t (Page {self.policy_date.page} | Confidence {self.policy_date.confidence} )\n"
        s += f"Premium Term: {self.premium_term.value} \t (Page {self.premium_term.page} | Confidence {self.premium_term.confidence} )\n"
        s += f"Insurer: {self.insurer_company.value} \t (Page {self.insurer_company.page} | Confidence {self.insurer_company.confidence} )\n"
        s += f"Sum assured: {self.sum_assured.value} \t (Page {self.sum_assured.page} | Confidence {self.sum_assured.confidence} )\n"
        s += f"Yearly Premium: {self.yearly_premium.value} \t (Page {self.yearly_premium.page} | Confidence {self.yearly_premium.confidence} )\n"
        return s


class TermDocument(BaseModel):
    policy_details : PolicyDetails
    insured_details : InsuredDetails
    death_benefit_table : DeathBenefitTable

    def __str__(self):
        return str(self.insured_details) + '\n' + str(self.policy_details) + '\n' + str(self.death_benefit_table)
class DocumentTermAgent:
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def extract(self, file_id=None , file_path=None):
        client = OpenAI(api_key=self.api_key)
        
        if file_id == None and file_path == None:
            print("Either file_id or file_path must exist.")
            return
        elif file_path != None and file_id == None:      
            # Upload the PDF to OpenAI
            with open(file_path, "rb") as f:
                file_response = client.files.create(file=f, purpose="user_data")
                file_id = file_response.id

        logging.info("Term data extraction started...")
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
                            "text": prompt
                        }
                    ]
                }
            ],
            text_format=TermDocument,
        )
        # Print raw content
        result = response.output_parsed

        display_term_document(result)
        return result
    
def display_term_document(doc : TermDocument):
    logging.info("Term data extraction completed.")
    logging.info(str(doc))
    



