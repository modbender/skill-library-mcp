from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AdvocacyCreate(BaseModel):
    statement: Optional[str] = Field(None, max_length=1000)


class AdvocacyResponse(BaseModel):
    id: str
    campaign_id: str
    agent_id: str
    agent_name: str
    agent_karma: int
    agent_avatar_url: Optional[str]
    statement: Optional[str]
    is_first_advocate: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdvocacyActionResponse(BaseModel):
    success: bool
    advocacy: AdvocacyResponse
    karma_earned: int


class AdvocacyListResponse(BaseModel):
    advocacies: List[AdvocacyResponse]
    total: int
