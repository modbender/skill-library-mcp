"""
OASIS Forum - Data models
"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class DiscussionStatus(str, Enum):
    PENDING = "pending"
    DISCUSSING = "discussing"
    CONCLUDED = "concluded"
    CANCELLED = "cancelled"
    ERROR = "error"


class CreateTopicRequest(BaseModel):
    """Request body for creating a new discussion topic.

    Expert pool is built from schedule_yaml or schedule_file (at least one required).
    schedule_file takes priority if both provided.
      "tag#temp#N" → ExpertAgent; "tag#oasis#id" → SessionExpert (oasis);
      "title#sid" → SessionExpert (regular).  Tag used to lookup name/persona.

    For simple all-parallel scenarios, use:
      version: 1
      repeat: true
      plan:
        - all_experts: true
    """
    question: str
    user_id: str = "anonymous"
    max_rounds: int = Field(default=5, ge=1, le=20)
    schedule_yaml: Optional[str] = None
    schedule_file: Optional[str] = None
    bot_enabled_tools: Optional[list[str]] = None
    bot_timeout: Optional[float] = None
    early_stop: bool = False
    discussion: Optional[bool] = None  # None=use YAML setting; True=forum discussion; False=execute mode
    # Callback: when discussion concludes, POST result to this URL via /system_trigger
    callback_url: Optional[str] = None
    callback_session_id: Optional[str] = None


class PostInfo(BaseModel):
    """Single post in a discussion thread."""
    id: int
    author: str
    content: str
    reply_to: Optional[int] = None
    upvotes: int = 0
    downvotes: int = 0
    timestamp: float
    elapsed: float = 0.0


class TimelineEventInfo(BaseModel):
    """A single timeline event."""
    elapsed: float
    event: str
    agent: str = ""
    detail: str = ""


class TopicDetail(BaseModel):
    """Full detail of a discussion topic."""
    topic_id: str
    question: str
    user_id: str = "anonymous"
    status: DiscussionStatus
    current_round: int
    max_rounds: int
    posts: list[PostInfo]
    timeline: list[TimelineEventInfo] = []
    discussion: bool = True
    conclusion: Optional[str] = None


class TopicSummary(BaseModel):
    """Brief summary of a discussion topic (for listing)."""
    topic_id: str
    question: str
    user_id: str = "anonymous"
    status: DiscussionStatus
    post_count: int
    current_round: int
    max_rounds: int
    created_at: float
