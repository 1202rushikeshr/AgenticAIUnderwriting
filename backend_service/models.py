# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
#from database import engine
from database import Base


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email= Column(String(100), nullable=True)
    contact_number= Column(String(15), nullable=True)
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    occupation = Column(String(200))
    location = Column(String(200))
    prior_claims = Column(Integer, default=0)
    smoking_status = Column(String(50))

    applications = relationship("Application", back_populates="applicant")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    product_type = Column(String(100), nullable=False)
    coverage_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
  # -------- PRE-CHECK (Backend Rules) --------
    pre_risk_score = Column(Float)
    pre_decision = Column(String)
    pre_reasoning = Column(Text)
    
  # -------- FINAL DECISION (CrewAI) --------
    final_risk_score = Column(Float)
    final_decision = Column(String(50))
    final_reasoning = Column(Text)

    applicant = relationship("Applicant", back_populates="applications")
    notifications = relationship("Notification", back_populates="application")  


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    recipient = Column(String(100), nullable=False)  # e.g. "applicant", "underwriter"
    channel = Column(String(50), nullable=False)     # e.g. "email", "dashboard"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    application = relationship("Application", back_populates="notifications")

# Create the tables in the database
#Base.metadata.create_all(bind=engine)
