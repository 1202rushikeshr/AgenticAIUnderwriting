from pydantic import BaseModel
from typing import List

# ----------------------------
# APPLICATION SCHEMAS
# ----------------------------
class Applicant(BaseModel):
    name: str
    age: int
    email: str
    contact_number: str
    income: int
    occupation: str
    location: str
    prior_claims: int
    smoking_status: str


class ApplicationCreate(BaseModel):
    applicant: Applicant
    product_type: str
    coverage_amount: int


class ApplicationRead(ApplicationCreate):
    application_id: int
    status: str


# ----------------------------
# UNDERWRITING SCHEMAS
# ----------------------------
class UnderwritingRequest(BaseModel):
    document_text: str
    product_type: str
    coverage_amount: int


class UnderwritingResultResponse(BaseModel):
    application_id: int
    decision: str
    risk_score: float
    reasoning: List[str]
