import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, Enum, JSON, UniqueConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CampaignCategory(str, PyEnum):
    MEDICAL = "MEDICAL"
    DISASTER_RELIEF = "DISASTER_RELIEF"
    EDUCATION = "EDUCATION"
    COMMUNITY = "COMMUNITY"
    EMERGENCY = "EMERGENCY"
    OTHER = "OTHER"


class CampaignStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class FeedEventType(str, PyEnum):
    CAMPAIGN_CREATED = "CAMPAIGN_CREATED"
    CAMPAIGN_UPDATED = "CAMPAIGN_UPDATED"
    ADVOCACY_ADDED = "ADVOCACY_ADDED"
    ADVOCACY_STATEMENT = "ADVOCACY_STATEMENT"
    WARROOM_POST = "WARROOM_POST"
    AGENT_MILESTONE = "AGENT_MILESTONE"
    AGENT_EVALUATED = "AGENT_EVALUATED"


class Creator(Base):
    __tablename__ = "creators"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # KYC fields
    kyc_status: Mapped[str] = mapped_column(String(20), default="none")  # none, pending, approved, rejected
    kyc_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    kyc_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    kyc_rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    kyc_attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    kyc_flagged_for_review: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship("Campaign", back_populates="creator")


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[CampaignCategory] = mapped_column(Enum(CampaignCategory), nullable=False)
    goal_amount_usd: Mapped[int] = mapped_column(Integer, nullable=False)  # Store in cents
    eth_wallet_address: Mapped[Optional[str]] = mapped_column(String(42), nullable=True)
    btc_wallet_address: Mapped[Optional[str]] = mapped_column(String(62), nullable=True)
    sol_wallet_address: Mapped[Optional[str]] = mapped_column(String(44), nullable=True)
    usdc_base_wallet_address: Mapped[Optional[str]] = mapped_column(String(42), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Balance tracking fields
    current_btc_satoshi: Mapped[int] = mapped_column(BigInteger, default=0)
    current_eth_wei: Mapped[int] = mapped_column(BigInteger, default=0)
    current_sol_lamports: Mapped[int] = mapped_column(BigInteger, default=0)
    current_usdc_base: Mapped[int] = mapped_column(BigInteger, default=0)  # 6 decimals
    last_balance_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # USD total tracking (monotonic - only increases)
    current_total_usd_cents: Mapped[int] = mapped_column(Integer, default=0)  # Total funding in USD cents
    withdrawal_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    withdrawal_detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notification_milestones_sent: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # e.g. [25, 50, 75, 100]
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    creator_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    creator_story: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    creator: Mapped["Creator"] = relationship("Creator", back_populates="campaigns")
    advocacies: Mapped[List["Advocacy"]] = relationship("Advocacy", back_populates="campaign")
    warroom_posts: Mapped[List["WarRoomPost"]] = relationship("WarRoomPost", back_populates="campaign")
    donations: Mapped[List["Donation"]] = relationship("Donation", back_populates="campaign")
    images: Mapped[List["CampaignImage"]] = relationship(
        "CampaignImage", back_populates="campaign"
    )


class CampaignImage(Base):
    __tablename__ = "campaign_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)  # 0-4
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="images")


class Agent(Base):
    __tablename__ = "agents"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    karma: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    advocacies: Mapped[List["Advocacy"]] = relationship("Advocacy", back_populates="agent")
    warroom_posts: Mapped[List["WarRoomPost"]] = relationship("WarRoomPost", back_populates="agent")
    upvotes: Mapped[List["Upvote"]] = relationship("Upvote", back_populates="agent")


class AgentEvaluation(Base):
    __tablename__ = "agent_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categories: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # e.g. {"impact": 9, "transparency": 7}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    campaign: Mapped["Campaign"] = relationship("Campaign", backref="evaluations")
    agent: Mapped["Agent"] = relationship("Agent", backref="evaluations")

    __table_args__ = (
        UniqueConstraint("campaign_id", "agent_id", name="uq_evaluation_campaign_agent"),
    )


class Advocacy(Base):
    __tablename__ = "advocacies"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False)
    statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_first_advocate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="advocacies")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="advocacies")
    
    __table_args__ = (
        UniqueConstraint("campaign_id", "agent_id", name="uq_advocacy_campaign_agent"),
    )


class WarRoomPost(Base):
    __tablename__ = "warroom_posts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)
    creator_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("creators.id"), nullable=True)
    parent_post_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("warroom_posts.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="warroom_posts")
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="warroom_posts")
    creator: Mapped[Optional["Creator"]] = relationship("Creator", backref="warroom_posts")
    parent_post: Mapped[Optional["WarRoomPost"]] = relationship("WarRoomPost", remote_side=[id], backref="replies")
    upvotes: Mapped[List["Upvote"]] = relationship("Upvote", back_populates="post")


class Upvote(Base):
    __tablename__ = "upvotes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False)
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("warroom_posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="upvotes")
    post: Mapped["WarRoomPost"] = relationship("WarRoomPost", back_populates="upvotes")
    
    __table_args__ = (
        UniqueConstraint("agent_id", "post_id", name="uq_upvote_agent_post"),
    )


class FeedEvent(Base):
    __tablename__ = "feed_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    event_type: Mapped[FeedEventType] = mapped_column(Enum(FeedEventType), nullable=False)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, name="metadata")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class MagicLink(Base):
    __tablename__ = "magic_links"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Donation(Base):
    __tablename__ = "donations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)  # Optional: agent who made donation
    chain: Mapped[str] = mapped_column(String(10), nullable=False)  # btc, eth, sol, usdc_base
    tx_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    amount_smallest_unit: Mapped[int] = mapped_column(BigInteger, nullable=False)  # satoshi/wei/lamports
    usd_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # USD value in cents at time of donation
    from_address: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    block_number: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="donations")
    agent: Mapped[Optional["Agent"]] = relationship("Agent", backref="donations")


class KYCSubmission(Base):
    __tablename__ = "kyc_submissions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"), nullable=False)
    id_photo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    selfie_photo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    submitted_date: Mapped[str] = mapped_column(String(20), nullable=False)  # The date shown in handwritten note
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator: Mapped["Creator"] = relationship("Creator", backref="kyc_submissions")
