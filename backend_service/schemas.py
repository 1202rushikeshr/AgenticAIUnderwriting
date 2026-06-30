# backend/schemas.py
from pydantic import BaseModel
from typing import Optional, List


# ---------- Applicant ----------
class ApplicantCreate(BaseModel):
    name: str
    email: str
    contact_number: str
    age: int
    income: float
    occupation: str
    location: str
    prior_claims: int
    smoking_status: str


# ---------- Application ----------
class ApplicationCreate(BaseModel):
    applicant: ApplicantCreate
    product_type: str
    coverage_amount: float


class ApplicationRead(BaseModel):
    id: int
    product_type: str
    coverage_amount: float

    # Pre-check (backend rules)
    pre_risk_score: Optional[float] = None
    pre_decision: Optional[str] = None
    pre_reasoning: Optional[str] = None

    # Final underwriting (CrewAI)
    final_risk_score: Optional[float] = None
    final_decision: Optional[str] = None
    final_reasoning: Optional[str] = None

    class Config:
        from_attributes = True  # ✅ REQUIRED for SQLAlchemy ORM


# ---------- AI Underwriting ----------
class UnderwritingRequest(BaseModel):
    document_text: str
    product_type: str
    coverage_amount: int


class UnderwritingResultResponse(BaseModel):
    application_id: int
    decision: str
    risk_score: float
    reasoning: List[str]
