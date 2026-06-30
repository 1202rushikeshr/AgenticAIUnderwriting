import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.underwriting_ai import router as underwriting_router
from routers.applications import router as application_router
from routers.reporting import router as reporting_router
from routers.underwriter import router as underwriter_router
from database import engine  
from models import Base      
import models
#from routers.ai_underwriting import router as ai_underwriting_router





app = FastAPI(title="Agentic AI Underwriting")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/ping")
def ping():
    return {"message": "pong"}

app.include_router(underwriting_router)
app.include_router(application_router)
app.include_router(reporting_router)
app.include_router(underwriter_router)
#app.include_router(ai_underwriting_router)
