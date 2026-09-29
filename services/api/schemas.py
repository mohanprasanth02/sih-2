"""
LabelGuard AI - Pydantic Request & Response Schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Auth Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "inspector" # inspector, supervisor, admin
    organization: str = "Department of Legal Metrology"

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    organization: str
    is_active: bool

# Inspection Schemas
class InspectionCreate(BaseModel):
    product_name: str
    brand: Optional[str] = None
    category_code: str = "food"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

class FieldCorrectionRequest(BaseModel):
    corrected_value: str
    reason: str

class VerificationRequest(BaseModel):
    decision: str # COMPLIANT, NON_COMPLIANT, NEEDS_REVIEW
    notes: Optional[str] = None

class RescanRequest(BaseModel):
    surface_type: str
    reason: str

class RuleTestRequest(BaseModel):
    category_code: str
    fields: Dict[str, Any]
    conflicts: Optional[List[Dict[str, Any]]] = []

# Analytics Schemas
class OverviewKPI(BaseModel):
    total_inspections: int
    compliant: int
    potential_violations: int
    manual_reviews: int
    compliance_rate: float
