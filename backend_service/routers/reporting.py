from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime

from database import get_db
from models import Application, Applicant

router = APIRouter(prefix="/reports", tags=["reports"])

def _csv_response(rows, decision_label: str):
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV header (Applicant + Application)
    writer.writerow([
        "application_id",
        "created_at",
        "product_type",
        "coverage_amount",
        "pre_risk_score",
        "pre_decision",
        "pre_reasoning",
        "final_risk_score",
        "final_decision",
        "final_reasoning",
        "applicant_id",
        "name",
        "email",
        "contact_number",
        "age",
        "income",
        "occupation",
        "location",
        "prior_claims",
        "smoking_status",
    ])

    for app, applicant in rows:
        writer.writerow([
            app.id,
            getattr(app, "created_at", None),
            app.product_type,
            app.coverage_amount,
            getattr(app, "pre_risk_score", None),
            getattr(app, "pre_decision", None),
            getattr(app, "pre_reasoning", None),
            getattr(app, "final_risk_score", None),
            getattr(app, "final_decision", None),
            getattr(app, "final_reasoning", None),
            applicant.id,
            applicant.name,
            applicant.email,
            applicant.contact_number,
            applicant.age,
            applicant.income,
            applicant.occupation,
            applicant.location,
            applicant.prior_claims,
            applicant.smoking_status,
        ])

    output.seek(0)
    filename = f"underwriting_{decision_label}_{datetime.now().strftime('%Y-%m-%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get("/approved.csv")
def approved_csv(db: Session = Depends(get_db)):
    q = (
        db.query(Application, Applicant)
        .join(Applicant, Applicant.id == Application.applicant_id)
        .filter(Application.final_decision == "APPROVE")
        .order_by(Application.id.desc())
    )
    return _csv_response(q.all(), "approved")

@router.get("/rejected.csv")
def rejected_csv(db: Session = Depends(get_db)):
    q = (
        db.query(Application, Applicant)
        .join(Applicant, Applicant.id == Application.applicant_id)
        .filter(Application.final_decision == "DECLINE")
        .order_by(Application.id.desc())
    )
    return _csv_response(q.all(), "decline")