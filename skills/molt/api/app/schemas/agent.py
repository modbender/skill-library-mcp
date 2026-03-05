from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class AgentResponse(AgentBase):
    id: str
    karma: int
    total_donated_usd_cents: int = 0  # Total donations in USD cents
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentRegisterResponse(BaseModel):
    agent: AgentResponse
    api_key: str  # Only returned once at registration


class AgentProfileResponse(AgentResponse):
    campaigns_advocated: int = 0
    recent_advocacies: List["AdvocacySummary"] = []


class AdvocacySummary(BaseModel):
    campaign_id: str
    campaign_title: str
    statement: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    agent: AgentResponse
    campaigns_advocated: int


class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    total: int
    period: str  # "all_time", "this_month", "this_week"


# Update forward reference
AgentProfileResponse.model_rebuild()
