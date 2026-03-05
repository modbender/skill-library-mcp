from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KYCStatusResponse(BaseModel):
    status: str  # none, pending, approved, rejected
    can_create_campaign: bool
    attempts_remaining: int
    rejection_reason: Optional[str] = None


class KYCSubmissionResponse(BaseModel):
    id: str
    status: str
    submitted_date: str
    created_at: datetime
