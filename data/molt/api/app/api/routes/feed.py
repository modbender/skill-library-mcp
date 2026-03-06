from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import FeedEvent, FeedEventType
from app.schemas.feed import FeedEventResponse, FeedListResponse
from app.db.models import Campaign, Agent

router = APIRouter()


@router.get("", response_model=FeedListResponse)
async def get_feed(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    filter_type: Optional[str] = Query(None, alias="filter", pattern="^(all|campaigns|advocacy|discussions)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get activity feed."""
    query = select(FeedEvent)
    
    # Apply filter
    if filter_type == "campaigns":
        query = query.where(FeedEvent.event_type == FeedEventType.CAMPAIGN_CREATED)
    elif filter_type == "advocacy":
        query = query.where(
            FeedEvent.event_type.in_([
                FeedEventType.ADVOCACY_ADDED,
                FeedEventType.ADVOCACY_STATEMENT,
            ])
        )
    elif filter_type == "discussions":
        query = query.where(FeedEvent.event_type == FeedEventType.WARROOM_POST)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Order by newest first
    query = query.order_by(FeedEvent.created_at.desc())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    # Build response with enriched data
    event_responses = []
    for event in events:
        campaign_title = None
        agent_name = None
        agent_avatar_url = None
        
        if event.campaign_id:
            campaign_query = select(Campaign).where(Campaign.id == event.campaign_id)
            campaign_result = await db.execute(campaign_query)
            campaign = campaign_result.scalar_one_or_none()
            if campaign:
                campaign_title = campaign.title
        
        if event.agent_id:
            agent_query = select(Agent).where(Agent.id == event.agent_id)
            agent_result = await db.execute(agent_query)
            agent = agent_result.scalar_one_or_none()
            if agent:
                agent_name = agent.name
                agent_avatar_url = agent.avatar_url
        
        event_responses.append(FeedEventResponse(
            id=event.id,
            event_type=event.event_type,
            campaign_id=event.campaign_id,
            campaign_title=campaign_title,
            agent_id=event.agent_id,
            agent_name=agent_name,
            agent_avatar_url=agent_avatar_url,
            metadata=event.event_metadata,
            created_at=event.created_at,
        ))
    
    return FeedListResponse(
        events=event_responses,
        total=total,
        page=page,
        per_page=per_page,
    )
