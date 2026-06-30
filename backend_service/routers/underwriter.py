from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

from sqlalchemy.orm import Session

from database import get_db  
from models import Application,Applicant  

router = APIRouter(prefix="/underwriter", tags=["Underwriter"])

Decision = Literal["APPROVE", "DECLINE", "REFER"]

class DecisionOverrideRequest(BaseModel):
    decision: Decision
    reason: str = Field(..., min_length=3, max_length=2000)
    underwriter: str = Field(..., min_length=2, max_length=200)

    # Optional override (if you want to allow it without DB changes)
    risk_score_override: Optional[float] = Field(default=None, ge=0, le=100)

class BulkDecisionOverrideRequest(BaseModel):
    application_ids: List[int] = Field(..., min_items=1)
    decision: Decision
    reason: str = Field(..., min_length=3, max_length=2000)
    underwriter: str = Field(..., min_length=2, max_length=200)
    risk_score_override: Optional[float] = Field(default=None, ge=0, le=100)

def append_manual_note(existing: Optional[str], note: str) -> str:
    if existing and existing.strip():
        return existing.strip() + "\n\n" + note
    return note

@router.patch("/applications/{application_id}/decision")
def override_decision(
    application_id: int,
    req: DecisionOverrideRequest,
    db: Session = Depends(get_db),
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    previous = app.final_decision

    # No DB changes: write into existing fields
    app.final_decision = req.decision

    if req.risk_score_override is not None:
        app.final_risk_score = float(req.risk_score_override)

    note = (
        f"[MANUAL OVERRIDE] {datetime.utcnow().isoformat()}Z\n"
        f"Underwriter: {req.underwriter}\n"
        f"Decision: {req.decision}\n"
        f"Reason: {req.reason}"
    )
    app.final_reasoning = append_manual_note(app.final_reasoning, note)

    db.add(app)
    db.commit()
    db.refresh(app)

    return {
        "application_id": app.id,
        "previous_decision": previous,
        "new_decision": app.final_decision,
    }

@router.patch("/applications/decision/bulk")
def override_decision_bulk(
    req: BulkDecisionOverrideRequest,
    db: Session = Depends(get_db),
):
    updated = []
    skipped = []

    apps = (
        db.query(Application)
        .filter(Application.id.in_(req.application_ids))
        .all()
    )
    found_ids = {a.id for a in apps}

    for app_id in req.application_ids:
        if app_id not in found_ids:
            skipped.append({"application_id": app_id, "reason": "Not found"})

    for app in apps:
        prev = app.final_decision
        app.final_decision = req.decision

        if req.risk_score_override is not None:
            app.final_risk_score = float(req.risk_score_override)

        note = (
            f"[MANUAL OVERRIDE] {datetime.utcnow().isoformat()}Z\n"
            f"Underwriter: {req.underwriter}\n"
            f"Decision: {req.decision}\n"
            f"Reason: {req.reason}"
        )
        app.final_reasoning = append_manual_note(app.final_reasoning, note)

        updated.append({"application_id": app.id, "previous": prev, "new": app.final_decision})

    db.commit()

    return {"updated": updated, "skipped": skipped}