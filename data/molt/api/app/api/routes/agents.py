from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from fastapi.responses import FileResponse

from app.core.rate_limit import check_agent_registration_rate_limit
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Agent, Advocacy, Campaign, Donation
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentRegisterResponse,
    AgentProfileResponse,
    LeaderboardEntry,
    LeaderboardResponse,
    AdvocacySummary,
)
from app.api.deps import get_required_agent
from app.core.security import create_api_key, hash_api_key

router = APIRouter()

AGENT_AVATAR_BASE_DIR = Path("data/uploads/agents")
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
async def register_agent(
    agent_data: AgentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new agent."""
    check_agent_registration_rate_limit(request)
    # Check if name is taken
    existing_query = select(Agent).where(Agent.name == agent_data.name)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Agent name already taken")
    
    try:
        # Generate API key
        api_key = create_api_key()
        api_key_hash = hash_api_key(api_key)
        
        # Create agent
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            avatar_url=agent_data.avatar_url,
            api_key_hash=api_key_hash,
            karma=0,
        )
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        return AgentRegisterResponse(
            agent=AgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                avatar_url=agent.avatar_url,
                karma=agent.karma,
                created_at=agent.created_at,
            ),
            api_key=api_key,  # Only returned once!
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to register agent: {str(e)}")


@router.get("/leaderboard", response_model=List[AgentResponse])
async def get_leaderboard(
    timeframe: Optional[str] = Query("all-time", pattern="^(all-time|month|week)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get agent leaderboard."""
    query = select(Agent)
    
    # Filter by timeframe if needed
    if timeframe == "month":
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        # Filter to agents who had advocacy activity in the timeframe
        query = query.join(Advocacy, Advocacy.agent_id == Agent.id).where(
            Advocacy.created_at >= cutoff,
            Advocacy.is_active == True
        ).distinct()
    elif timeframe == "week":
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        # Filter to agents who had advocacy activity in the timeframe
        query = query.join(Advocacy, Advocacy.agent_id == Agent.id).where(
            Advocacy.created_at >= cutoff,
            Advocacy.is_active == True
        ).distinct()
    
    # Sort by karma (total karma, as we don't track karma history)
    query = query.order_by(desc(Agent.karma)).limit(100)  # Top 100
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    # Calculate total donations per agent
    agent_donations = {}
    for agent in agents:
        # Sum donations where agent_id matches, using usd_cents if available
        donations_query = select(func.sum(Donation.usd_cents)).where(
            Donation.agent_id == agent.id
        )
        donations_result = await db.execute(donations_query)
        total_cents = donations_result.scalar()
        agent_donations[agent.id] = int(total_cents) if total_cents else 0
    
    return [
        AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            avatar_url=agent.avatar_url,
            karma=agent.karma,
            total_donated_usd_cents=agent_donations.get(agent.id, 0),
            created_at=agent.created_at,
        )
        for agent in agents
    ]


@router.get("/me", response_model=AgentResponse)
async def get_current_agent(
    agent: Agent = Depends(get_required_agent),
):
    """Get current agent profile (authenticated via API key)."""
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        avatar_url=agent.avatar_url,
        karma=agent.karma,
        created_at=agent.created_at,
    )


@router.post("/me/avatar", response_model=AgentResponse)
async def upload_agent_avatar(
    avatar: UploadFile = File(...),
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Upload agent avatar. Replaces existing avatar. JPG/PNG only, max 2MB."""
    ext = Path(avatar.filename or "").suffix.lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed",
        )

    content = await avatar.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 2MB",
        )

    agent_dir = AGENT_AVATAR_BASE_DIR / agent.id
    agent_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"avatar_{timestamp}{ext}"
    file_path = agent_dir / filename

    file_path.write_bytes(content)

    avatar_url = f"/api/uploads/agents/{agent.id}/{filename}"
    agent.avatar_url = avatar_url

    await db.commit()
    await db.refresh(agent)

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        avatar_url=agent.avatar_url,
        karma=agent.karma,
        created_at=agent.created_at,
    )


@router.get("/{name}", response_model=AgentProfileResponse)
async def get_agent(
    name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get agent profile."""
    query = select(Agent).where(Agent.name == name)
    query = query.options(selectinload(Agent.advocacies))
    result = await db.execute(query)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Count campaigns advocated and get recent advocacies with campaign titles
    advocacies_query = select(Advocacy).where(
        Advocacy.agent_id == agent.id,
        Advocacy.is_active == True,
    ).join(Campaign, Campaign.id == Advocacy.campaign_id).order_by(Advocacy.created_at.desc())
    advocacies_query = advocacies_query.options(selectinload(Advocacy.campaign))
    advocacies_result = await db.execute(advocacies_query)
    advocacies = advocacies_result.scalars().all()
    
    # Get recent advocacies with campaign titles
    recent_advocacies = []
    for advocacy in advocacies[:10]:  # Last 10
        recent_advocacies.append(AdvocacySummary(
            campaign_id=advocacy.campaign_id,
            campaign_title=advocacy.campaign.title,
            statement=advocacy.statement,
            created_at=advocacy.created_at,
        ))
    
    return AgentProfileResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        avatar_url=agent.avatar_url,
        karma=agent.karma,
        created_at=agent.created_at,
        campaigns_advocated=len(advocacies),
        recent_advocacies=recent_advocacies,
    )


@router.patch("/me", response_model=AgentResponse)
async def update_agent_profile(
    agent_data: AgentUpdate,
    agent: Agent = Depends(get_required_agent),
    db: AsyncSession = Depends(get_db),
):
    """Update own agent profile."""
    try:
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        await db.commit()
        await db.refresh(agent)
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            avatar_url=agent.avatar_url,
            karma=agent.karma,
            created_at=agent.created_at,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")
