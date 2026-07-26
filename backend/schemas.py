"""
GrowthGuru AI — Pydantic Schemas
==================================
Defines request and response structures for the API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List

class ChatRequest(BaseModel):
    """Request model for the /api/chat endpoints."""
    user_prompt: str = Field(..., description="The user's query or instruction.")

class ChatResponse(BaseModel):
    """Response model for the /api/chat endpoint."""
    success: bool
    data: str
    error: str | None = None

class AnalyzeRequest(BaseModel):
    """Request model for the /analyze endpoint."""
    file_id: str = Field(..., description="The unique file ID returned from the /upload endpoint.")

class BusinessProfileBase(BaseModel):
    business_name: str
    business_type: str
    target_audience: str
    business_goals: str

class GrowthPlanRequest(BaseModel):
    """Request model for the /generate-growth-plan endpoint."""
    file_id: str = Field(..., description="The unique file ID returned from the /upload endpoint.")
    business_profile: BusinessProfileBase

class ValidateAlignmentRequest(BaseModel):
    """Request model for /validate-alignment endpoint."""
    file_id: str = Field(..., description="The unique file ID returned from the /upload endpoint.")
    business_type: str = Field(..., description="The selected business type.")

class SimulateImpactRequest(BaseModel):
    """Request model for /simulate-impact endpoint."""
    file_id: str = Field(..., description="The unique file ID returned from the /upload endpoint.")
