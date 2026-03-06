from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.db.models import FeedEventType


class FeedEventResponse(BaseModel):
    id: str
    event_type: FeedEventType
    campaign_id: Optional[str]
    campaign_title: Optional[str]
    agent_id: Optional[str]
    agent_name: Optional[str]
    agent_avatar_url: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    events: List[FeedEventResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


class FeedListResponse(BaseModel):
    events: List[FeedEventResponse]
    total: int
    page: int
    per_page: int
