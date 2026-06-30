# backend/routers/underwriting_ai.py

import json
import requests
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from schemas import UnderwritingRequest, UnderwritingResultResponse
from database import get_db
from models import Application
from store import UNDERWRITING_RESULTS
from agentCore_client import invoke_underwriting_agent

router = APIRouter(
    prefix="/ai-underwriting",
    tags=["AI Underwriting"]
)

# ------------------------------------------------
# AgentCore Runtime (LOCAL for now)
# ------------------------------------------------
AGENTCORE_RUNTIME_URL = "http://localhost:8081/run"


# -------------------------------
# 1️⃣ RUN UNDERWRITING (COMMAND)
# -------------------------------
@router.post("/run/{application_id}")
def run_underwriting(
    application_id: int,
    req: UnderwritingRequest,
    db: Session = Depends(get_db),
):
    # -----------------------------------
    # Fetch application + applicant
    # -----------------------------------
    application = db.query(Application).get(application_id)

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    applicant = application.applicant

    # =====================================================
    # 🛑 PHASE 1: RULE ENGINE GATE (NO LLM CALL IF DECLINED BY RULE ENGINE)
    # =====================================================
    if application.pre_decision == "DECLINE":
        application.final_decision = "DECLINE"
        application.final_risk_score = application.pre_risk_score
        application.final_reasoning = json.dumps([
            "Declined by rule engine",
            application.pre_reasoning or "Rule-based decline"
        ])

        db.commit()

        UNDERWRITING_RESULTS[application_id] = {
            "application_id": application_id,
            "decision": application.final_decision,
            "risk_score": application.final_risk_score,
            "reasoning": json.loads(application.final_reasoning),
            "notifications": [],
        }

        return {
            "application_id": application_id,
            "status": "DECLINED_BY_RULE_ENGINE",
        }

    # =====================================================
    # ✅ PHASE 2: AGENTCORE (LLM ASSISTED UNDERWRITING)
    # =====================================================
    payload = {
        "application_id": application.id,
        "document_text": req.document_text,
        "product_type": req.product_type,
        "coverage_amount": req.coverage_amount,
        "applicant": {
            "name": applicant.name,
            "email": applicant.email,
            "contact_number": applicant.contact_number,
            "age": applicant.age,
            "income": applicant.income,
            "occupation": applicant.occupation,
            "location": applicant.location,
            "prior_claims": applicant.prior_claims,
            "smoking_status": applicant.smoking_status,
        },
        # Rule engine context (ground truth)
        "pre_risk_score": application.pre_risk_score,
        "pre_decision": application.pre_decision,
        "pre_reasoning": application.pre_reasoning,
    }

    try:
       crew_result = invoke_underwriting_agent(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AgentCore invocation failed: {exc}",
        )    

    # -----------------------------------
    # Defensive extraction
    # -----------------------------------
    decision = crew_result.get("decision")
    risk_score = crew_result.get("risk_score")
    raw_reasoning = crew_result.get("reasoning")
    notifications = crew_result.get("notifications", [])

    if not decision:
        raise HTTPException(
            status_code=500,
            detail=f"AgentCore response missing decision: {crew_result}",
        )

    # Normalize reasoning → List[str]
    if not raw_reasoning:
        reasoning = []
    elif isinstance(raw_reasoning, list):
        reasoning = raw_reasoning
    else:
        reasoning = [str(raw_reasoning)]

    # -----------------------------------
    # Persist FINAL underwriting result
    # -----------------------------------
    application.final_decision = decision
    application.final_risk_score = float(risk_score or 0.0)
    application.final_reasoning = json.dumps(reasoning)

    db.commit()

    # -----------------------------------
    # Cache for Result Page
    # -----------------------------------
    UNDERWRITING_RESULTS[application_id] = {
        "application_id": application_id,
        "decision": decision,
        "risk_score": application.final_risk_score,
        "reasoning": reasoning,
        "notifications": notifications,
    }

    return {
        "application_id": application_id,
        "status": "UNDERWRITING_COMPLETED",
    }


# -------------------------------
# 2️⃣ GET RESULT (QUERY)
# -------------------------------
@router.get(
    "/result/{application_id}",
    response_model=UnderwritingResultResponse
)
def get_underwriting_result(
    application_id: int,
    db: Session = Depends(get_db),
):
    # -------------------------
    # 1️⃣ Cache first
    # -------------------------
    cached = UNDERWRITING_RESULTS.get(application_id)
    if cached:
        return cached

    # -------------------------
    # 2️⃣ DB fallback
    # -------------------------
    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if application and application.final_decision is not None:
        raw_reasoning = application.final_reasoning

        if not raw_reasoning:
            reasoning = []
        else:
            try:
                parsed = json.loads(raw_reasoning)
                reasoning = parsed if isinstance(parsed, list) else [parsed]
            except json.JSONDecodeError:
                reasoning = [raw_reasoning]

        return {
            "application_id": application.id,
            "decision": application.final_decision,
            "risk_score": float(application.final_risk_score or 0.0),
            "reasoning": reasoning,
        }

    # -------------------------
    # 3️⃣ Not found anywhere
    # -------------------------
    raise HTTPException(
        status_code=404,
        detail="Underwriting result not found or still processing"
    )
