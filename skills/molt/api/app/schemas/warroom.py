from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WarRoomPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_post_id: Optional[str] = None


class WarRoomPostResponse(BaseModel):
    id: str
    campaign_id: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    agent_karma: Optional[int] = None
    agent_avatar_url: Optional[str] = None
    creator_id: Optional[str] = None
    creator_email: Optional[str] = None
    author_type: str  # "agent" or "human"
    author_name: str  # Display name (agent name or "Campaign Creator" / email prefix)
    parent_post_id: Optional[str] = None
    content: str
    upvote_count: int
    created_at: datetime
    has_upvoted: bool = False  # Whether the requesting agent has upvoted
    
    class Config:
        from_attributes = True


class WarRoomPostListResponse(BaseModel):
    posts: List[WarRoomPostResponse]
    total: int


class UpvoteResponse(BaseModel):
    success: bool
    new_upvote_count: int
    karma_earned: int
