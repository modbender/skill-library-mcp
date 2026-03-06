"""Donation schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DonationResponse(BaseModel):
    id: str
    campaign_id: str
    chain: str
    tx_hash: str
    amount_smallest_unit: int
    from_address: Optional[str] = None
    confirmed_at: datetime
    block_number: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DonationListResponse(BaseModel):
    donations: List[DonationResponse]
    total: int
    page: int
    per_page: int
