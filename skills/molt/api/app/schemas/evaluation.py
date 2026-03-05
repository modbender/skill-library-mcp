"""Pydantic schemas for agent evaluations."""
from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field


class EvaluationCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)
    summary: Optional[str] = Field(None, max_length=2000)
    categories: Optional[Dict[str, int]] = Field(None)


class EvaluationResponse(BaseModel):
    id: str
    campaign_id: str
    agent_id: str
    agent_name: str
    score: int
    summary: Optional[str] = None
    categories: Optional[Dict[str, int]] = None
    created_at: datetime

    class Config:
        from_attributes = True
