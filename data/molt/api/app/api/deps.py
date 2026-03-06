from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Agent, Creator
from app.core.security import verify_api_key, decode_access_token


async def get_current_agent(
    x_agent_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[Agent]:
    """Get the current agent from API key header. Returns None if no key provided."""
    if not x_agent_api_key:
        return None
    
    # We need to check all agents since we hash the key
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    
    for agent in agents:
        if verify_api_key(x_agent_api_key, agent.api_key_hash):
            return agent
    
    return None


async def get_required_agent(
    agent: Optional[Agent] = Depends(get_current_agent)
) -> Agent:
    """Require a valid agent API key."""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return agent


async def get_current_creator(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[Creator]:
    """Get the current creator from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload or "sub" not in payload:
        return None
    
    creator_id = payload["sub"]
    result = await db.execute(select(Creator).where(Creator.id == creator_id))
    return result.scalar_one_or_none()


async def get_required_creator(
    creator: Optional[Creator] = Depends(get_current_creator)
) -> Creator:
    """Require a valid creator JWT token."""
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication"
        )
    return creator


async def get_required_kyc_creator(
    creator: Creator = Depends(get_required_creator)
) -> Creator:
    """Require a valid creator with approved KYC."""
    if creator.kyc_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "KYC_REQUIRED", "message": "KYC verification required", "kyc_status": creator.kyc_status}
        )
    return creator
