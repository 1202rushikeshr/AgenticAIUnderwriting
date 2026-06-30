from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Applicant, Application
from schemas import ApplicationCreate, ApplicationRead
from services.precheck import calculate_precheck_risk

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.post("/", response_model=ApplicationRead)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    applicant = Applicant(**payload.applicant.dict())
    db.add(applicant)
    db.flush()

    pre_score, pre_decision, pre_reasons = calculate_precheck_risk(
        applicant,
        payload.coverage_amount
    )

    application = Application(
        applicant_id=applicant.id,
        product_type=payload.product_type,
        coverage_amount=payload.coverage_amount,

        pre_risk_score=pre_score,
        pre_decision=pre_decision,
        pre_reasoning=", ".join(pre_reasons),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application
