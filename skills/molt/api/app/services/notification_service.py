"""Notification service for campaign milestones and advocate alerts."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import Campaign
from app.services.email import email_service

logger = logging.getLogger(__name__)

MILESTONES = [25, 50, 75, 100]


async def check_and_send_milestone_notifications(db: AsyncSession, campaign_id: str) -> None:
    """
    Check if campaign has crossed funding milestones (25/50/75/100%) and send emails.
    Updates notification_milestones_sent to avoid duplicates.
    """
    result = await db.execute(
        select(Campaign)
        .where(Campaign.id == campaign_id)
        .options(selectinload(Campaign.creator))
    )
    campaign = result.scalar_one_or_none()
    if not campaign or not campaign.goal_amount_usd:
        return

    percent_reached = int(
        (campaign.current_total_usd_cents / campaign.goal_amount_usd) * 100
    )
    sent = campaign.notification_milestones_sent or []

    for m in MILESTONES:
        if m <= percent_reached and m not in sent:
            try:
                await email_service.send_campaign_milestone(
                    to_email=campaign.contact_email,
                    campaign_title=campaign.title,
                    milestone_percent=m,
                )
                sent = list(sent) + [m]
                campaign.notification_milestones_sent = sent
                await db.commit()
            except Exception as e:
                logger.warning(
                    f"Failed to send milestone {m}% email for campaign {campaign_id}: {e}"
                )
                # Graceful degradation: do not re-raise
