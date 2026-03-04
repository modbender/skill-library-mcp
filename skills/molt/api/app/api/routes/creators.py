"""Creator routes."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import Campaign, CampaignStatus, Donation, Advocacy
from app.schemas.campaign import CampaignResponse, CampaignListResponse
from app.api.deps import get_required_creator
from app.api.routes.campaigns import (
    _build_campaign_dict,
    calculate_advocate_count,
)

router = APIRouter()


@router.get("/me/campaigns", response_model=CampaignListResponse)
async def get_my_campaigns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    creator=Depends(get_required_creator),
    db: AsyncSession = Depends(get_db),
):
    """List all campaigns for the authenticated creator (including CANCELLED)."""
    query = select(Campaign).where(Campaign.creator_id == creator.id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by created_at desc, apply pagination
    query = query.order_by(Campaign.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    query = query.options(
        selectinload(Campaign.advocacies),
        selectinload(Campaign.images),
        selectinload(Campaign.creator),
    )

    result = await db.execute(query)
    campaigns = result.scalars().all()

    campaign_responses = []
    for campaign in campaigns:
        donation_count_result = await db.execute(
            select(func.count()).select_from(Donation).where(Donation.campaign_id == campaign.id)
        )
        donation_count = donation_count_result.scalar() or 0
        donor_count_result = await db.execute(
            select(func.count(func.distinct(Donation.from_address)))
            .select_from(Donation)
            .where(Donation.campaign_id == campaign.id)
            .where(Donation.from_address.isnot(None))
        )
        donor_count = donor_count_result.scalar() or 0
        creator_obj = getattr(campaign, "creator", None)
        is_creator_verified = creator_obj is not None and getattr(creator_obj, "kyc_status", None) == "approved"
        campaign_dict = _build_campaign_dict(
            campaign,
            calculate_advocate_count(campaign),
            donation_count=donation_count,
            donor_count=donor_count,
            is_creator_verified=is_creator_verified,
        )
        campaign_responses.append(CampaignResponse(**campaign_dict))

    return CampaignListResponse(
        campaigns=campaign_responses,
        total=total,
        page=page,
        per_page=per_page,
    )
