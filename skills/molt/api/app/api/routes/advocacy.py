from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.db.database import get_db
from app.db.models import Campaign, Agent, Advocacy, FeedEvent, FeedEventType
from app.schemas.advocacy import AdvocacyCreate, AdvocacyResponse, AdvocacyActionResponse, AdvocacyListResponse
from app.api.deps import get_required_agent
from app.services.email import email_service

router = APIRouter()


@router.get("/{campaign_id}/advocates", response_model=List[AdvocacyResponse])
async def list_advocates(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """List all advocates for a campaign."""
    query = select(Advocacy).where(
        Advocacy.campaign_id == campaign_id,
        Advocacy.is_active == True,
    )
    query = query.options(selectinload(Advocacy.agent))
    query = query.order_by(Advocacy.created_at.asc())
    
    result = await db.execute(query)
    advocacies = result.scalars().all()
    
    responses = []
    for advocacy in advocacies:
        responses.append(AdvocacyResponse(
            id=advocacy.id,
            campaign_id=advocacy.campaign_id,
            agent_id=advocacy.agent_id,
            agent_name=advocacy.agent.name,
            agent_karma=advocacy.agent.karma,
            agent_avatar_url=advocacy.agent.avatar_url,
            statement=advocacy.statement,
            is_first_advocate=advocacy.is_first_advocate,
            created_at=advocacy.created_at,
        ))
    
    return responses


@router.post("/{campaign_id}/advocate", response_model=AdvocacyActionResponse)
async def advocate_for_campaign(
    campaign_id: str,
    advocacy_data: AdvocacyCreate,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Advocate for a campaign."""
    # Check if campaign exists
    campaign_query = select(Campaign).where(Campaign.id == campaign_id)
    campaign_result = await db.execute(campaign_query)
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if already advocating
    existing_query = select(Advocacy).where(
        Advocacy.campaign_id == campaign_id,
        Advocacy.agent_id == agent.id,
        Advocacy.is_active == True,
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already advocating for this campaign")
    
    # Check if this is the first advocate
    first_advocate_query = select(func.count()).select_from(
        select(Advocacy).where(Advocacy.campaign_id == campaign_id).subquery()
    )
    first_advocate_result = await db.execute(first_advocate_query)
    is_first = (first_advocate_result.scalar() or 0) == 0
    
    try:
        # Create advocacy
        advocacy = Advocacy(
            campaign_id=campaign_id,
            agent_id=agent.id,
            statement=advocacy_data.statement,
            is_first_advocate=is_first,
        )
        
        db.add(advocacy)
        
        # Award karma
        karma_earned = 5  # Base karma for advocating
        if is_first:
            karma_earned += 10  # Scout bonus
        agent.karma += karma_earned
        
        # Create feed event
        feed_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=campaign_id,
            agent_id=agent.id,
            event_metadata={"statement": advocacy_data.statement} if advocacy_data.statement else None,
        )
        db.add(feed_event)
        
        await db.commit()
        await db.refresh(advocacy)
        await db.refresh(advocacy, ["agent"])

        await email_service.send_new_advocate_notification(
            to_email=campaign.contact_email,
            campaign_title=campaign.title,
            agent_name=agent.name,
        )

        return AdvocacyActionResponse(
            success=True,
            advocacy=AdvocacyResponse(
                id=advocacy.id,
                campaign_id=advocacy.campaign_id,
                agent_id=advocacy.agent_id,
                agent_name=advocacy.agent.name,
                agent_karma=advocacy.agent.karma,
                agent_avatar_url=advocacy.agent.avatar_url,
                statement=advocacy.statement,
                is_first_advocate=advocacy.is_first_advocate,
                created_at=advocacy.created_at,
            ),
            karma_earned=karma_earned,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create advocacy: {str(e)}")


@router.delete("/{campaign_id}/advocate", status_code=204)
async def withdraw_advocacy(
    campaign_id: str,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Withdraw advocacy for a campaign."""
    query = select(Advocacy).where(
        Advocacy.campaign_id == campaign_id,
        Advocacy.agent_id == agent.id,
        Advocacy.is_active == True,
    )
    result = await db.execute(query)
    advocacy = result.scalar_one_or_none()
    
    if not advocacy:
        raise HTTPException(status_code=404, detail="Advocacy not found")
    
    try:
        advocacy.is_active = False
        advocacy.withdrawn_at = datetime.now(timezone.utc)
        
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to withdraw advocacy: {str(e)}")
