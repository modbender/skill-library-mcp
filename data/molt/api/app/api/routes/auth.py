from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Creator, MagicLink
from app.schemas.auth import MagicLinkRequest, MagicLinkResponse, VerifyTokenRequest, VerifyTokenResponse
from app.core.security import create_magic_link_token, create_access_token
from app.core.config import settings
from app.services.email import email_service

router = APIRouter()


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a magic link for authentication."""
    # For MVP, we'll just create the magic link token
    # In production, you'd send an email here
    
    token = create_magic_link_token()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.magic_link_expire_minutes
    )
    
    try:
        # Store magic link
        magic_link = MagicLink(
            email=request.email,
            token=token,
            expires_at=expires_at,
        )
        
        # Get or create creator
        creator_query = select(Creator).where(Creator.email == request.email)
        creator_result = await db.execute(creator_query)
        creator = creator_result.scalar_one_or_none()
        
        if not creator:
            creator = Creator(email=request.email)
            db.add(creator)
            await db.flush()
        
        db.add(magic_link)
        await db.commit()

        if email_service.is_configured():
            await email_service.send_magic_link(
                to_email=request.email,
                token=token,
                frontend_url=settings.frontend_url,
            )
            return MagicLinkResponse(
                success=True,
                message="Check your email for the sign-in link.",
            )
        return MagicLinkResponse(
            success=True,
            message=f"Magic link created. Token: {token} (dev only - don't expose in production)",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create magic link: {str(e)}")


@router.get("/verify", response_model=VerifyTokenResponse)
async def verify_magic_link(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Verify a magic link token and return JWT."""
    # Find magic link
    magic_link_query = select(MagicLink).where(
        MagicLink.token == token,
        MagicLink.used_at.is_(None),
    )
    magic_link_result = await db.execute(magic_link_query)
    magic_link = magic_link_result.scalar_one_or_none()
    
    if not magic_link:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check expiration
    if magic_link.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")
    
    try:
        # Get or create creator
        creator_query = select(Creator).where(Creator.email == magic_link.email)
        creator_result = await db.execute(creator_query)
        creator = creator_result.scalar_one_or_none()
        
        if not creator:
            creator = Creator(email=magic_link.email)
            db.add(creator)
            await db.flush()
        
        # Mark magic link as used
        magic_link.used_at = datetime.now(timezone.utc)
        
        # Create JWT with user info
        access_token = create_access_token(data={
            "sub": creator.id,
            "email": creator.email,
        })
        
        await db.commit()
        
        return VerifyTokenResponse(
            success=True,
            access_token=access_token,
            message="Authentication successful",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to verify token: {str(e)}")


@router.post("/logout")
async def logout():
    """Logout (client-side token removal)."""
    return {"success": True, "message": "Logged out"}
