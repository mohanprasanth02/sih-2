"""
LabelGuard AI - Main FastAPI Application (SIH26034)
Scan. Verify. Detect. Report.
Legal Metrology (Packaged Commodities) Rules, 2011 Inspection System
"""
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from services.api.database import engine, Base
from services.api.routers import auth, inspections, rules, analytics, websocket, oiml_r76

# Create tables
Base.metadata.create_all(bind=engine)

# Ensure media folders
os.makedirs("uploads/inspections", exist_ok=True)
os.makedirs("uploads/evidence", exist_ok=True)
os.makedirs("uploads/demo", exist_ok=True)
os.makedirs("uploads/oiml_evidence", exist_ok=True)
os.makedirs("reports/generated", exist_ok=True)

app = FastAPI(
    title="Legal Metrology Platform & OIML R 76 NAWI Model Approval System",
    description="Backend API Gateway & Metrological Evaluation Service for Legal Metrology Act, 2009, Packaged Commodities Rules 2011, and OIML R 76 Non-Automatic Weighing Instruments Model Approval.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for images and evidence
app.mount("/static", StaticFiles(directory="uploads/inspections"), name="static")
app.mount("/evidence", StaticFiles(directory="uploads/evidence"), name="evidence")
app.mount("/oiml_evidence", StaticFiles(directory="uploads/oiml_evidence"), name="oiml_evidence")

# Include Routers with /api/v1 prefix
app.include_router(auth.router, prefix="/api/v1")
app.include_router(inspections.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(oiml_r76.router, prefix="/api/v1")
app.include_router(websocket.router)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "LabelGuard AI - API Gateway",
        "version": "1.0.0",
        "database": "CONNECTED",
        "ai_pipeline": "OPERATIONAL"
    }
