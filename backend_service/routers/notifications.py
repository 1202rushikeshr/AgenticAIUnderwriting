# backend/routers/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Notification
from schemas import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/application/{application_id}", response_model=List[NotificationRead])
def get_notifications_for_application(
    application_id: int, db: Session = Depends(get_db)
):
    notifs = (
        db.query(Notification)
        .filter(Notification.application_id == application_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifs
