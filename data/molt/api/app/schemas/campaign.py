from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.db.models import CampaignCategory, CampaignStatus


class CampaignImageResponse(BaseModel):
    id: str
    image_url: str
    display_order: int


class CampaignBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=5000)
    category: CampaignCategory
    goal_amount_usd: int = Field(..., gt=0, description="Goal amount in cents")
    eth_wallet_address: Optional[str] = Field(None, max_length=42)
    btc_wallet_address: Optional[str] = Field(None, max_length=62)
    usdc_base_wallet_address: Optional[str] = Field(None, max_length=42)
    sol_wallet_address: Optional[str] = Field(None, max_length=44)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    end_date: Optional[datetime] = None
    
    @field_validator("eth_wallet_address", "btc_wallet_address", "sol_wallet_address", "usdc_base_wallet_address", mode="before")
    @classmethod
    def validate_at_least_one_wallet(cls, v, info):
        return v


class CampaignCreate(CampaignBase):
    contact_email: str = Field(..., max_length=255)
    creator_name: Optional[str] = Field(None, max_length=100)
    creator_story: Optional[str] = Field(None, max_length=2000)
    
    @field_validator("contact_email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v


class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    category: Optional[CampaignCategory] = None
    goal_amount_usd: Optional[int] = Field(None, gt=0)
    creator_name: Optional[str] = Field(None, max_length=100)
    creator_story: Optional[str] = Field(None, max_length=2000)
    eth_wallet_address: Optional[str] = Field(None, max_length=42)
    btc_wallet_address: Optional[str] = Field(None, max_length=62)
    sol_wallet_address: Optional[str] = Field(None, max_length=44)
    usdc_base_wallet_address: Optional[str] = Field(None, max_length=42)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    end_date: Optional[datetime] = None
    status: Optional[CampaignStatus] = None


class CampaignResponse(CampaignBase):
    id: str
    status: CampaignStatus
    creator_name: Optional[str] = None
    creator_story: Optional[str] = None
    advocate_count: int = 0
    donation_count: int = 0
    donor_count: int = 0
    is_creator_verified: bool = False
    images: List[CampaignImageResponse] = []
    current_btc_satoshi: int = 0
    current_eth_wei: int = 0
    current_sol_lamports: int = 0
    current_usdc_base: int = 0
    last_balance_check: Optional[datetime] = None
    current_total_usd_cents: int = 0
    withdrawal_detected: bool = False
    withdrawal_detected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    creator_id: str


class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    per_page: int
