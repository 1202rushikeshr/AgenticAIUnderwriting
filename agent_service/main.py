from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List

from agents.underwriting_crew import run_underwriting_crew

app = FastAPI(title="Underwriting Agent Runtime")

class UnderwritingAgentInput(BaseModel):
    application_id: int
    document_text: str
    product_type: str
    coverage_amount: float
    applicant: Dict[str, Any]
    pre_risk_score: float | None = None
    pre_decision: str | None = None
    pre_reasoning: str | None = None

class UnderwritingAgentOutput(BaseModel):
    decision: str
    risk_score: float
    reasoning: List[str]
    notifications: List[Dict[str, Any]]

@app.post("/run", response_model=UnderwritingAgentOutput)
def run_agent(payload: UnderwritingAgentInput):

    result = run_underwriting_crew(
        raw_document_text=payload.document_text,
        product_type=payload.product_type,
        coverage_amount=payload.coverage_amount,
        applicant=payload.applicant,
        pre_risk_score=payload.pre_risk_score,
        pre_decision=payload.pre_decision,
        pre_reasoning=payload.pre_reasoning,
    )

    # 🔒 Normalize (VERY IMPORTANT)
    reasoning = result.get("reasoning") or []
    if not isinstance(reasoning, list):
        reasoning = [str(reasoning)]

    return {
        "decision": result["decision"],
        "risk_score": float(result.get("risk_score", 0.0)),
        "reasoning": reasoning,
        "notifications": result.get("notifications", []),
    }


@app.post("/invocations")
def agentcore_entry(payload: dict):
    result = run_underwriting_crew(
        raw_document_text=payload["document_text"],
        product_type=payload["product_type"],
        coverage_amount=payload["coverage_amount"],
        applicant=payload["applicant"],
        pre_risk_score=payload.get("pre_risk_score"),
        pre_decision=payload.get("pre_decision"),
        pre_reasoning=payload.get("pre_reasoning"),
    )

    # Normalize reasoning defensively
    reasoning = result.get("reasoning") or []
    if not isinstance(reasoning, list):
        reasoning = [str(reasoning)]

    return {
        "decision": result["decision"],
        "risk_score": float(result.get("risk_score", 0.0)),
        "reasoning": reasoning,
        "notifications": result.get("notifications", []),
    }

