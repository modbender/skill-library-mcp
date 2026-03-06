from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Campaign, CampaignImage, Creator, CampaignCategory, CampaignStatus, Donation, Advocacy, utc_now
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse, CampaignDetailResponse, CampaignImageResponse
from app.schemas.donation import DonationResponse, DonationListResponse
from app.api.deps import get_required_creator, get_required_kyc_creator
from app.services.price_service import PriceService
from app.services.balance_tracker import BalanceTracker
from app.services.notification_service import check_and_send_milestone_notifications

router = APIRouter()

CAMPAIGN_IMAGES_BASE_DIR = Path("data/uploads/campaigns")
MAX_CAMPAIGN_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_CAMPAIGN_IMAGES = 5
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def calculate_advocate_count(campaign: Campaign) -> int:
    """Calculate active advocate count for a campaign."""
    return len([a for a in campaign.advocacies if a.is_active])


def _campaign_images_to_response(campaign: Campaign) -> List[CampaignImageResponse]:
    """Convert campaign images to response format."""
    images = sorted(getattr(campaign, "images", []) or [], key=lambda x: x.display_order)
    return [
        CampaignImageResponse(
            id=img.id,
            image_url=f"/api/uploads/campaigns/{campaign.id}/{Path(img.image_path).name}",
            display_order=img.display_order,
        )
        for img in images
    ]


def _build_campaign_dict(
    campaign: Campaign,
    advocate_count: int,
    *,
    donation_count: int = 0,
    donor_count: int = 0,
    is_creator_verified: bool = False,
) -> dict:
    """Build campaign dict for response including images."""
    images = _campaign_images_to_response(campaign)
    return {
        **{k: v for k, v in campaign.__dict__.items() if not k.startswith("_")},
        "advocate_count": advocate_count,
        "donation_count": donation_count,
        "donor_count": donor_count,
        "is_creator_verified": is_creator_verified,
        "images": images,
    }


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[CampaignCategory] = None,
    search: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|most_advocates|trending)$"),
    db: AsyncSession = Depends(get_db),
):
    """List campaigns with filtering and pagination."""
    query = select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
    
    if category:
        query = query.where(Campaign.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Campaign.title.ilike(search_term),
                Campaign.description.ilike(search_term),
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply sorting
    if sort == "newest":
        query = query.order_by(Campaign.created_at.desc())
    elif sort == "most_advocates":
        # Count active advocacies and sort by that count
        query = query.outerjoin(Advocacy, (Advocacy.campaign_id == Campaign.id) & (Advocacy.is_active == True))
        query = query.group_by(Campaign.id).order_by(func.count(Advocacy.id).desc(), Campaign.created_at.desc())
    elif sort == "trending":
        # Trending = recent campaigns with advocates (sort by advocate count, then recency)
        query = query.outerjoin(Advocacy, (Advocacy.campaign_id == Campaign.id) & (Advocacy.is_active == True))
        query = query.group_by(Campaign.id).order_by(func.count(Advocacy.id).desc(), Campaign.created_at.desc())
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Load relationships (creator for KYC status)
    query = query.options(
        selectinload(Campaign.advocacies),
        selectinload(Campaign.images),
        selectinload(Campaign.creator),
    )
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    # Convert to response models (with donation/donor counts and KYC status)
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
        creator = getattr(campaign, "creator", None)
        is_creator_verified = creator is not None and getattr(creator, "kyc_status", None) == "approved"
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


def _escape_html(s: str) -> str:
    """Escape HTML special characters for safe embedding in meta tag content."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


@router.get("/og/{campaign_id}", response_class=HTMLResponse)
async def campaign_og(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve minimal HTML with OG meta tags for social crawlers.
    
    Returns a lightweight HTML document containing Open Graph and Twitter Card
    meta tags, plus a meta-refresh redirect to the SPA campaign page. This
    allows crawlers (Twitterbot, Slackbot, etc.) that don't execute JavaScript
    to read campaign-specific meta tags for rich link previews.
    """
    query = select(Campaign).where(Campaign.id == campaign_id)
    query = query.options(selectinload(Campaign.images))
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    settings = get_settings()
    site_url = settings.site_url.rstrip("/")
    canonical_url = f"{site_url}/campaigns/{campaign_id}"

    # OG description: truncate to 200 chars
    desc = campaign.description
    og_description = desc[:197] + "..." if len(desc) > 200 else desc
    og_description = _escape_html(og_description)
    og_title = _escape_html(campaign.title)

    # OG image: prefer first uploaded image, fall back to cover_image_url
    og_image = None
    images = sorted(getattr(campaign, "images", []) or [], key=lambda x: x.display_order)
    if images:
        img_filename = Path(images[0].image_path).name
        og_image = f"{site_url}/api/uploads/campaigns/{campaign.id}/{img_filename}"
    elif campaign.cover_image_url:
        if campaign.cover_image_url.startswith("http"):
            og_image = campaign.cover_image_url
        else:
            path = campaign.cover_image_url if campaign.cover_image_url.startswith("/") else f"/{campaign.cover_image_url}"
            og_image = f"{site_url}{path}"

    # Build image meta tags only when an image exists
    og_image_tag = ""
    twitter_image_tag = ""
    if og_image:
        escaped_image = _escape_html(og_image)
        og_image_tag = f'<meta property="og:image" content="{escaped_image}" />'
        twitter_image_tag = f'<meta name="twitter:image" content="{escaped_image}" />'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{og_title} | MoltFundMe</title>
    <meta property="og:title" content="{og_title}" />
    <meta property="og:description" content="{og_description}" />
    <meta property="og:url" content="{canonical_url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="MoltFundMe" />
    {og_image_tag}
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{og_title}" />
    <meta name="twitter:description" content="{og_description}" />
    {twitter_image_tag}
    <link rel="canonical" href="{canonical_url}" />
    <meta http-equiv="refresh" content="0;url={canonical_url}" />
</head>
<body><p>Redirecting to <a href="{canonical_url}">campaign</a>...</p></body>
</html>"""
    return HTMLResponse(html)


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single campaign by ID."""
    query = select(Campaign).where(Campaign.id == campaign_id)
    query = query.options(
        selectinload(Campaign.advocacies),
        selectinload(Campaign.images),
        selectinload(Campaign.creator),
    )
    
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    donation_count_result = await db.execute(
        select(func.count()).select_from(Donation).where(Donation.campaign_id == campaign_id)
    )
    donation_count = donation_count_result.scalar() or 0
    donor_count_result = await db.execute(
        select(func.count(func.distinct(Donation.from_address)))
        .select_from(Donation)
        .where(Donation.campaign_id == campaign_id)
        .where(Donation.from_address.isnot(None))
    )
    donor_count = donor_count_result.scalar() or 0
    creator = getattr(campaign, "creator", None)
    is_creator_verified = creator is not None and getattr(creator, "kyc_status", None) == "approved"
    campaign_dict = _build_campaign_dict(
        campaign,
        calculate_advocate_count(campaign),
        donation_count=donation_count,
        donor_count=donor_count,
        is_creator_verified=is_creator_verified,
    )
    
    return CampaignDetailResponse(**campaign_dict)


@router.post("/{campaign_id}/images", response_model=CampaignImageResponse, status_code=201)
async def upload_campaign_image(
    campaign_id: str,
    image: UploadFile = File(...),
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Upload image for campaign. Max 5 images, JPG/PNG only, 5MB each."""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to add images to this campaign")

    ext = Path(image.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are allowed")

    content = await image.read()
    if len(content) > MAX_CAMPAIGN_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")

    # Check current image count
    count_result = await db.execute(
        select(func.count()).select_from(CampaignImage).where(CampaignImage.campaign_id == campaign_id)
    )
    current_count = count_result.scalar() or 0
    if current_count >= MAX_CAMPAIGN_IMAGES:
        raise HTTPException(status_code=400, detail="Campaign already has maximum 5 images")

    campaign_dir = CAMPAIGN_IMAGES_BASE_DIR / campaign_id
    campaign_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"img_{timestamp}{ext}"
    file_path = campaign_dir / filename
    file_path.write_bytes(content)

    display_order = current_count
    campaign_image = CampaignImage(
        campaign_id=campaign_id,
        image_path=f"{campaign_id}/{filename}",
        display_order=display_order,
    )
    db.add(campaign_image)
    await db.commit()
    await db.refresh(campaign_image)

    return CampaignImageResponse(
        id=campaign_image.id,
        image_url=f"/api/uploads/campaigns/{campaign_id}/{filename}",
        display_order=campaign_image.display_order,
    )


@router.delete("/{campaign_id}/images/{image_id}", status_code=204)
async def delete_campaign_image(
    campaign_id: str,
    image_id: str,
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Delete campaign image. Creator must own campaign."""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete images from this campaign")

    img_query = select(CampaignImage).where(
        CampaignImage.id == image_id,
        CampaignImage.campaign_id == campaign_id,
    )
    img_result = await db.execute(img_query)
    campaign_image = img_result.scalar_one_or_none()
    if not campaign_image:
        raise HTTPException(status_code=404, detail="Image not found")

    await db.delete(campaign_image)
    await db.commit()
    return None


@router.post("", response_model=CampaignDetailResponse, status_code=201)
async def create_campaign(
    campaign_data: CampaignCreate,
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    # Validate at least one wallet address
    if not any([
        campaign_data.eth_wallet_address,
        campaign_data.btc_wallet_address,
        campaign_data.sol_wallet_address,
        campaign_data.usdc_base_wallet_address,
    ]):
        raise HTTPException(
            status_code=400,
            detail="At least one wallet address (BTC, ETH, SOL, or USDC on Base) is required",
        )
    
    try:
        campaign_dict = campaign_data.model_dump(exclude={"contact_email"})
        campaign = Campaign(
            **campaign_dict,
            creator_id=creator.id,
            contact_email=creator.email,  # Use creator's email
        )
        
        db.add(campaign)
        await db.flush()  # Flush to get campaign.id
        
        # Create feed event for campaign creation
        from app.db.models import FeedEvent, FeedEventType
        feed_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=campaign.id,
            agent_id=None,
            event_metadata={"title": campaign.title},
        )
        db.add(feed_event)
        
        await db.commit()
        await db.refresh(campaign)
        await db.refresh(campaign, ["advocacies", "images"])
        
        campaign_dict = _build_campaign_dict(
            campaign, 0,
            donation_count=0,
            donor_count=0,
            is_creator_verified=True,  # Creator is KYC-approved (required for create)
        )
        
        return CampaignDetailResponse(**campaign_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")


@router.patch("/{campaign_id}", response_model=CampaignDetailResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign (creator must own it)."""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this campaign")
    
    try:
        # Update fields
        update_data = campaign_data.model_dump(exclude_unset=True)
        if not update_data:
            await db.refresh(campaign, ["advocacies", "images", "creator"])
            donation_count_result = await db.execute(
                select(func.count()).select_from(Donation).where(Donation.campaign_id == campaign_id)
            )
            donation_count = donation_count_result.scalar() or 0
            donor_count_result = await db.execute(
                select(func.count(func.distinct(Donation.from_address)))
                .select_from(Donation)
                .where(Donation.campaign_id == campaign_id)
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
            return CampaignDetailResponse(**campaign_dict)

        # Snapshot current values to detect actual changes
        changed_metadata = {}
        for field, new_value in update_data.items():
            old_value = getattr(campaign, field, None)
            if old_value != new_value:
                changed_metadata[field] = new_value

        for field, value in update_data.items():
            setattr(campaign, field, value)

        if changed_metadata:
            from app.db.models import FeedEvent, FeedEventType
            feed_event = FeedEvent(
                event_type=FeedEventType.CAMPAIGN_UPDATED,
                campaign_id=campaign_id,
                agent_id=None,
                event_metadata=changed_metadata,
            )
            db.add(feed_event)

        await db.commit()
        await db.refresh(campaign)
        await db.refresh(campaign, ["advocacies", "images", "creator"])
        
        donation_count_result = await db.execute(
            select(func.count()).select_from(Donation).where(Donation.campaign_id == campaign_id)
        )
        donation_count = donation_count_result.scalar() or 0
        donor_count_result = await db.execute(
            select(func.count(func.distinct(Donation.from_address)))
            .select_from(Donation)
            .where(Donation.campaign_id == campaign_id)
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
        
        return CampaignDetailResponse(**campaign_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update campaign: {str(e)}")


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
    creator: Creator = Depends(get_required_kyc_creator),
    db: AsyncSession = Depends(get_db),
):
    """Cancel/delete a campaign (creator must own it)."""
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")
    
    try:
        campaign.status = CampaignStatus.CANCELLED
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete campaign: {str(e)}")


@router.get("/{campaign_id}/donations", response_model=DonationListResponse)
async def list_donations(
    campaign_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    chain: Optional[str] = Query(None, pattern="^(btc|eth|sol|usdc_base)$"),
    db: AsyncSession = Depends(get_db),
):
    """List donations for a campaign."""
    # Verify campaign exists
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Build query
    query = select(Donation).where(Donation.campaign_id == campaign_id)
    
    if chain:
        query = query.where(Donation.chain == chain)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(Donation.confirmed_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    donations = result.scalars().all()
    
    donation_responses = [DonationResponse(**donation.__dict__) for donation in donations]
    
    return DonationListResponse(
        donations=donation_responses,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("/{campaign_id}/refresh-balance", response_model=CampaignDetailResponse)
async def refresh_campaign_balance(
    campaign_id: str,
    creator: Creator = Depends(get_required_creator),
    db: AsyncSession = Depends(get_db),
):
    """Refresh campaign balances and check for withdrawals."""
    # Get campaign
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to refresh balance for this campaign")
    
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Can only refresh balance for active campaigns")
    
    try:
        # Store previous balances for withdrawal detection
        prev_btc = campaign.current_btc_satoshi
        prev_eth = campaign.current_eth_wei
        prev_sol = campaign.current_sol_lamports
        prev_usdc = campaign.current_usdc_base
        
        # Update balances from blockchain
        balance_tracker = BalanceTracker(db)
        await balance_tracker.update_campaign_balances(campaign_id)
        
        # Refresh campaign to get updated balances
        await db.refresh(campaign)
        
        # Check for withdrawals (if any crypto balance decreased)
        withdrawal_detected = False
        if (campaign.current_btc_satoshi < prev_btc and prev_btc > 0) or \
           (campaign.current_eth_wei < prev_eth and prev_eth > 0) or \
           (campaign.current_sol_lamports < prev_sol and prev_sol > 0) or \
           (campaign.current_usdc_base < prev_usdc and prev_usdc > 0):
            withdrawal_detected = True
            campaign.withdrawal_detected = True
            campaign.withdrawal_detected_at = utc_now()
            campaign.status = CampaignStatus.CANCELLED
        
        # Fetch current prices from Binance
        price_service = PriceService()
        prices = await price_service.get_prices()
        
        # Calculate USD total
        btc_amount = campaign.current_btc_satoshi / 100_000_000  # satoshi to BTC
        eth_amount = campaign.current_eth_wei / 10**18  # wei to ETH
        sol_amount = campaign.current_sol_lamports / 10**9  # lamports to SOL
        usdc_amount = campaign.current_usdc_base / 1_000_000  # 6 decimals to USDC
        
        new_total_usd = (
            btc_amount * prices['btc'] +
            eth_amount * prices['eth'] +
            sol_amount * prices['sol'] +
            usdc_amount * prices['usdc_base']
        )
        new_total_cents = int(new_total_usd * 100)
        
        # Monotonic: only update if new total is higher than stored total
        if new_total_cents > campaign.current_total_usd_cents:
            campaign.current_total_usd_cents = new_total_cents

        await db.commit()
        await check_and_send_milestone_notifications(db, campaign_id)
        await db.refresh(campaign)
        await db.refresh(campaign, ["advocacies", "images", "creator"])
        
        donation_count_result = await db.execute(
            select(func.count()).select_from(Donation).where(Donation.campaign_id == campaign_id)
        )
        donation_count = donation_count_result.scalar() or 0
        donor_count_result = await db.execute(
            select(func.count(func.distinct(Donation.from_address)))
            .select_from(Donation)
            .where(Donation.campaign_id == campaign_id)
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
        
        return CampaignDetailResponse(**campaign_dict)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to refresh balance: {str(e)}")
