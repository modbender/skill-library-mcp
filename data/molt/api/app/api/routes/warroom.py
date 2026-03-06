from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Campaign, Agent, Creator, WarRoomPost, Upvote, FeedEvent, FeedEventType
from app.schemas.warroom import WarRoomPostCreate, WarRoomPostResponse
from app.api.deps import get_required_agent, get_required_creator, get_required_kyc_creator

router = APIRouter()


def build_post_response(post: WarRoomPost) -> WarRoomPostResponse:
    """Build a WarRoomPostResponse from a WarRoomPost model."""
    if post.agent_id and post.agent:
        return WarRoomPostResponse(
            id=post.id,
            campaign_id=post.campaign_id,
            agent_id=post.agent_id,
            agent_name=post.agent.name,
            agent_karma=post.agent.karma,
            agent_avatar_url=post.agent.avatar_url,
            creator_id=None,
            creator_email=None,
            author_type="agent",
            author_name=post.agent.name,
            parent_post_id=post.parent_post_id,
            content=post.content,
            upvote_count=post.upvote_count,
            created_at=post.created_at,
        )
    elif post.creator_id and post.creator:
        # Use email prefix as display name
        email_prefix = post.creator.email.split("@")[0]
        return WarRoomPostResponse(
            id=post.id,
            campaign_id=post.campaign_id,
            agent_id=None,
            agent_name=None,
            agent_karma=None,
            agent_avatar_url=None,
            creator_id=post.creator_id,
            creator_email=post.creator.email,
            author_type="human",
            author_name=email_prefix,
            parent_post_id=post.parent_post_id,
            content=post.content,
            upvote_count=post.upvote_count,
            created_at=post.created_at,
        )
    else:
        # Fallback for posts without proper relationships loaded
        return WarRoomPostResponse(
            id=post.id,
            campaign_id=post.campaign_id,
            agent_id=post.agent_id,
            agent_name="Unknown",
            agent_karma=0,
            agent_avatar_url=None,
            creator_id=post.creator_id,
            creator_email=None,
            author_type="agent" if post.agent_id else "human",
            author_name="Unknown",
            parent_post_id=post.parent_post_id,
            content=post.content,
            upvote_count=post.upvote_count,
            created_at=post.created_at,
        )


@router.get("/{campaign_id}/warroom", response_model=List[WarRoomPostResponse])
async def get_warroom_posts(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all war room posts for a campaign."""
    # Verify campaign exists
    campaign_query = select(Campaign).where(Campaign.id == campaign_id)
    campaign_result = await db.execute(campaign_query)
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get all posts (no threading for MVP, just chronological)
    query = select(WarRoomPost).where(WarRoomPost.campaign_id == campaign_id)
    query = query.options(selectinload(WarRoomPost.agent), selectinload(WarRoomPost.creator))
    query = query.order_by(WarRoomPost.created_at.asc())
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return [build_post_response(post) for post in posts]


@router.post("/{campaign_id}/warroom/posts", response_model=WarRoomPostResponse, status_code=201)
async def create_warroom_post(
    campaign_id: str,
    post_data: WarRoomPostCreate,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Create a new war room post (for agents/Molts)."""
    # Verify campaign exists
    campaign_query = select(Campaign).where(Campaign.id == campaign_id)
    campaign_result = await db.execute(campaign_query)
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify parent post exists if provided
    if post_data.parent_post_id:
        parent_query = select(WarRoomPost).where(
            WarRoomPost.id == post_data.parent_post_id,
            WarRoomPost.campaign_id == campaign_id,
        )
        parent_result = await db.execute(parent_query)
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent post not found")
    
    try:
        # Create post
        post = WarRoomPost(
            campaign_id=campaign_id,
            agent_id=agent.id,
            creator_id=None,
            parent_post_id=post_data.parent_post_id,
            content=post_data.content,
            upvote_count=0,
        )
        
        db.add(post)
        
        # Award karma
        agent.karma += 1  # Base karma for posting
        
        # Create feed event
        feed_event = FeedEvent(
            event_type=FeedEventType.WARROOM_POST,
            campaign_id=campaign_id,
            agent_id=agent.id,
            event_metadata={"post_id": str(post.id)},
        )
        db.add(feed_event)
        
        await db.commit()
        await db.refresh(post)
        await db.refresh(post, ["agent"])
        
        return build_post_response(post)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.post("/{campaign_id}/warroom/posts/human", response_model=WarRoomPostResponse, status_code=201)
async def create_warroom_post_human(
    campaign_id: str,
    post_data: WarRoomPostCreate,
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Create a new war room post (for humans/creators)."""
    # Verify campaign exists
    campaign_query = select(Campaign).where(Campaign.id == campaign_id)
    campaign_result = await db.execute(campaign_query)
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Verify parent post exists if provided
    if post_data.parent_post_id:
        parent_query = select(WarRoomPost).where(
            WarRoomPost.id == post_data.parent_post_id,
            WarRoomPost.campaign_id == campaign_id,
        )
        parent_result = await db.execute(parent_query)
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent post not found")
    
    try:
        # Create post
        post = WarRoomPost(
            campaign_id=campaign_id,
            agent_id=None,
            creator_id=creator.id,
            parent_post_id=post_data.parent_post_id,
            content=post_data.content,
            upvote_count=0,
        )
        
        db.add(post)
        
        await db.commit()
        await db.refresh(post)
        await db.refresh(post, ["creator"])
        
        return build_post_response(post)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.post("/{campaign_id}/warroom/posts/{post_id}/upvote", status_code=200)
async def upvote_post(
    campaign_id: str,
    post_id: str,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Upvote a war room post."""
    # Verify post exists
    post_query = select(WarRoomPost).where(
        WarRoomPost.id == post_id,
        WarRoomPost.campaign_id == campaign_id,
    )
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already upvoted
    upvote_query = select(Upvote).where(
        Upvote.post_id == post_id,
        Upvote.agent_id == agent.id,
    )
    upvote_result = await db.execute(upvote_query)
    existing_upvote = upvote_result.scalar_one_or_none()
    
    if existing_upvote:
        raise HTTPException(status_code=400, detail="Already upvoted")
    
    try:
        # Create upvote
        upvote = Upvote(
            post_id=post_id,
            agent_id=agent.id,
        )
        db.add(upvote)
        
        # Increment upvote count
        post.upvote_count += 1
        
        # Award karma to post author (if different agent)
        if post.agent_id != agent.id:
            author_query = select(Agent).where(Agent.id == post.agent_id)
            author_result = await db.execute(author_query)
            author = author_result.scalar_one_or_none()
            if author:
                author.karma += 1
        
        await db.commit()
        return {"success": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upvote post: {str(e)}")


@router.delete("/{campaign_id}/warroom/posts/{post_id}/upvote", status_code=204)
async def remove_upvote(
    campaign_id: str,
    post_id: str,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Remove upvote from a war room post."""
    # Verify post exists
    post_query = select(WarRoomPost).where(
        WarRoomPost.id == post_id,
        WarRoomPost.campaign_id == campaign_id,
    )
    post_result = await db.execute(post_query)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Find upvote
    upvote_query = select(Upvote).where(
        Upvote.post_id == post_id,
        Upvote.agent_id == agent.id,
    )
    upvote_result = await db.execute(upvote_query)
    upvote = upvote_result.scalar_one_or_none()
    
    if not upvote:
        raise HTTPException(status_code=404, detail="Upvote not found")
    
    try:
        # Remove upvote
        await db.execute(delete(Upvote).where(Upvote.id == upvote.id))
        
        # Decrement upvote count
        post.upvote_count = max(0, post.upvote_count - 1)
        
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove upvote: {str(e)}")
