import os
import re
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import date
from dateutil import parser as dateparser

import fitz  # PyMuPDF
import langchain
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False
os.environ['OPENAI_API_KEY'] = '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'

# LangChain (v0.2+ style)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser

# Pydantic models (align to your data model)
from pydantic import BaseModel, Field, validator


# =========================
#  Data Models (final)
# =========================
class Insured(BaseModel):
    name: str
    age: int
    gender: str
    date_of_birth: date

class DeathBenefitTableRow(BaseModel):
    policy_year: int
    age: int
    premiums_paid: int
    death_benefits: int
    surrender_value: int

class DeathBenefitTable(BaseModel):
    rows: List[DeathBenefitTableRow]

class TermDocument(BaseModel):
    policy_date: date
    premium_term: int
    insurer: str
    sum_assured: float
    yearly_premium: int
    monthly_premium: int
    insured: Insured
    death_benefit_table: DeathBenefitTable


# ===================================================
#  Partial models used during page-specific extraction
#  (allowing missing fields; we’ll assemble later)
# ===================================================
class InsuredPartial(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None

class PolicyInfoPartial(BaseModel):
    policy_date: Optional[date] = None
    premium_term: Optional[int] = None
    insurer: Optional[str] = None
    sum_assured: Optional[float] = None
    yearly_premium: Optional[int] = None
    monthly_premium: Optional[int] = None

class DeathBenefitTablePartial(BaseModel):
    rows: List[DeathBenefitTableRow] = Field(default_factory=list)


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


# =========================
#  Heuristics (optional)
#  Use these first to trim prompt sizes and prefill data
# =========================
CURRENCY_RE = re.compile(r"SGD|\$|S\$|Singapore Dollars", re.IGNORECASE)

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


# =========================
#  LLM setup
# =========================
@dataclass
class Settings:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0

def make_llm(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(model=settings.model, temperature=settings.temperature)


# ==========================================
# Step 1: Policy-type classifier (simple)
# ==========================================
class PolicyType(BaseModel):
    policy_type: str
    confidence: float = Field(ge=0, le=1)

def make_policy_type_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=PolicyType)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an insurance-document classifier. "
             "Identify the policy type succinctly (e.g., 'Term', 'Whole Life', 'Endowment', 'ILP'.)."),
            ("human",
             "Given the following document text (with page markers), identify the policy type.\n\n"
             "{doc}\n\n"
             "Return JSON with fields: policy_type (string), confidence (0..1)."
             "\n{format_instructions}")
        ]
    )
    return ( {"doc": RunnablePassthrough()} | prompt | llm | parser )


# ===================================================
# Step 2: Page locator: which pages contain what
# ===================================================
class PageLocator(BaseModel):
    client_detail_pages: List[int] = Field(default_factory=list, description="1-based page indexes")
    policy_info_pages: List[int] = Field(default_factory=list)
    benefits_table_pages: List[int] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.6)

def make_page_locator_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=PageLocator)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are an expert at finding sections in multi-page insurance PDFs. "
             "Use the content to return 1-based page numbers likely holding the requested sections. "
             "Prefer precision; do not include irrelevant pages."),
            ("human",
             "Document with page markers:\n\n{doc}\n\n"
             "Return a JSON with:\n"
             "- client_detail_pages: [ints]\n"
             "- policy_info_pages: [ints]\n"
             "- benefits_table_pages: [ints]\n"
             "- confidence: number 0..1\n"
             "{format_instructions}")
        ]
    )
    return ( {"doc": RunnablePassthrough()} | prompt | llm | parser )


# ===================================================
# Step 3: Page-specific extractors
# ===================================================
def _select_text(pages: List[str], one_based_pages: List[int]) -> str:
    # Merge selected pages into one string with page headers
    chunks = []
    for p in one_based_pages:
        if 1 <= p <= len(pages):
            chunks.append(f"=== Page {p} ===\n{pages[p-1]}")
    return "\n\n".join(chunks) if chunks else ""

# ---- 3A: Client Details
def make_client_details_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=InsuredPartial)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", 
             "Extract client details from the provided page(s). "
             "If a field is missing, set it to null. "
             "date_of_birth must be ISO date (YYYY-MM-DD)."),
            ("human",
             "Here are the candidate pages for client details:\n\n{page_text}\n\n"
             "Return JSON with fields: name, age, gender, date_of_birth.\n"
             "{format_instructions}")
        ]
    )
    return ( {"page_text": RunnablePassthrough()} | prompt | llm | parser )

# ---- 3B: Policy Info
def make_policy_info_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=PolicyInfoPartial)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "Extract policy info from the provided page(s). "
             "If missing, set to null. Dates must be YYYY-MM-DD. Monetary values are numbers without commas."),
            ("human",
             "Here are the candidate pages for policy info:\n\n{page_text}\n\n"
             "Extract: policy_date, premium_term (years), insurer, sum_assured, yearly_premium, monthly_premium.\n"
             "{format_instructions}")
        ]
    )
    return ( {"page_text": RunnablePassthrough()} | prompt | llm | parser )

# ---- 3C: Death Benefit Table
def make_benefits_table_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=DeathBenefitTablePartial)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "Extract the death benefit table rows from the provided page(s). "
             "For each row, return policy_year, age, premiums_paid, death_benefits, surrender_value as integers. "
             "If values include commas or currency, normalize to integers (e.g., '1,742' -> 1742). "
             "Include as many rows as are visible (e.g., 1..10, then 15, 20, etc.)."),
            ("human",
             "Here are the candidate pages for the death benefit table:\n\n{page_text}\n\n"
             "Return JSON with 'rows': [ {policy_year, age, premiums_paid, death_benefits, surrender_value}, ... ].\n"
             "{format_instructions}")
        ]
    )
    return ( {"page_text": RunnablePassthrough()} | prompt | llm | parser )


# ===================================================
# Step 4: Assembly & Normalization
# ===================================================
def _coerce_int(x: Optional[str | int | float]) -> Optional[int]:
    if x is None:
        return None
    if isinstance(x, int):
        return x
    # Strip currency and commas
    s = str(x)
    s = re.sub(r"[^\d\-]", "", s)
    if s == "":
        return None
    try:
        return int(s)
    except:
        return None

def _coerce_float(x: Optional[str | int | float]) -> Optional[float]:
    if x is None:
        return None
    s = str(x).replace(",", "")
    s = re.sub(r"[^0-9.\-]", "", s)
    if s == "" or s == "." or s == "-":
        return None
    try:
        return float(s)
    except:
        return None

def _coerce_date(x: Optional[str | date]) -> Optional[date]:
    if x is None:
        return None
    if isinstance(x, date):
        return x
    try:
        return dateparser.parse(str(x), dayfirst=False, yearfirst=False).date()
    except Exception:
        return None

def assemble_term_document(
    client: InsuredPartial,
    policy: PolicyInfoPartial,
    table: DeathBenefitTablePartial
) -> TermDocument:
    # Validate required fields and provide helpful errors if missing
    missing = []
    if not policy.policy_date: missing.append("policy_date")
    if policy.premium_term is None: missing.append("premium_term")
    if not policy.insurer: missing.append("insurer")
    if policy.sum_assured is None: missing.append("sum_assured")
    if policy.yearly_premium is None: missing.append("yearly_premium")
    if policy.monthly_premium is None: missing.append("monthly_premium")

    if not client.name: missing.append("insured.name")
    if client.age is None: missing.append("insured.age")
    if not client.gender: missing.append("insured.gender")
    if not client.date_of_birth: missing.append("insured.date_of_birth")

    if len(table.rows) == 0:
        missing.append("death_benefit_table.rows")

    if missing:
        raise ValueError(f"Missing required fields after extraction: {missing}")

    insured = Insured(
        name=client.name,
        age=int(client.age),
        gender=str(client.gender),
        date_of_birth=_coerce_date(client.date_of_birth)
    )

    # Normalize monetary values to expected types
    td = TermDocument(
        policy_date=_coerce_date(policy.policy_date),
        premium_term=int(policy.premium_term),
        insurer=str(policy.insurer),
        sum_assured=float(_coerce_float(policy.sum_assured)),
        yearly_premium=int(_coerce_int(policy.yearly_premium)),
        monthly_premium=int(_coerce_int(policy.monthly_premium)),
        insured=insured,
        death_benefit_table=DeathBenefitTable(rows=table.rows),
    )
    return td


# ===================================================
# Orchestration
# ===================================================
def extract_term_document(pdf_path: str, settings: Settings) -> Dict:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set")

    pages = load_pdf_pages(pdf_path)
    heur = quick_candidate_pages(pages)

    llm = make_llm(settings)

    # Step 1: classify policy type (uses the whole doc but token-capped by page markers)
    classifier_chain = make_policy_type_chain(llm)
    classifier_in = join_pages(pages[:4])  # usually first pages suffice; adjust as needed
    policy_type = classifier_chain.invoke(classifier_in)

    # Step 2: page locator (use entire doc with page markers, or a subset)
    locator_chain = make_page_locator_chain(llm)
    locator_in = join_pages(pages)
    locator: PageLocator = locator_chain.invoke(locator_in)

    # Merge heuristics with LLM picks (union, unique+sorted)
    def merge_pages(heur_list: List[int], llm_list: List[int]) -> List[int]:
        s = set([i+1 for i in heur_list])  # convert 0-based to 1-based
        s.update(llm_list or [])
        return sorted(s)

    client_pages = merge_pages(heur["client"], locator.client_detail_pages)
    policy_pages = merge_pages(heur["policy"], locator.policy_info_pages)
    benefit_pages = merge_pages(heur["benefits"], locator.benefits_table_pages)

    # Step 3A: client details
    client_text = _select_text(pages, client_pages or [1])
    client_chain = make_client_details_chain(llm)
    client_partial: InsuredPartial = client_chain.invoke(client_text)

    # Step 3B: policy info
    policy_text = _select_text(pages, policy_pages or [1, 2])
    policy_chain = make_policy_info_chain(llm)
    policy_partial: PolicyInfoPartial = policy_chain.invoke(policy_text)

    # Step 3C: benefits table
    benefits_text = _select_text(pages, benefit_pages or [3, 4, 5])
    benefits_chain = make_benefits_table_chain(llm)
    table_partial: DeathBenefitTablePartial = benefits_chain.invoke(benefits_text)

    # Step 4: assemble TermDocument (strict validation)
    term_doc = assemble_term_document(client_partial, policy_partial, table_partial)

    # Return everything for debugging/telemetry
    return {
        "policy_type": policy_type.dict(),
        "page_locator": {
            "client_pages": client_pages,
            "policy_pages": policy_pages,
            "benefits_pages": benefit_pages,
            "llm_confidence": locator.confidence,
        },
        "extracted": {
            "client": client_partial.dict(),
            "policy": policy_partial.dict(),
            "benefits_table_rows": [r.dict() for r in table_partial.rows],
        },
        "term_document": term_doc.dict(),
    }


def main():
    settings = Settings()
    pdf_path = "resources/Term-CTP.pdf"  # put your file next to this script
    result = extract_term_document(pdf_path, settings)

    # Pretty print (or write to JSON)
    import json
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
