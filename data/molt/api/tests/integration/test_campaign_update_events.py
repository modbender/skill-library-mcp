"""Integration tests for campaign update feed events."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestCampaignUpdateFeedEvents:
    """Tests that PATCH /api/campaigns/{id} creates campaign_updated feed events."""

    async def test_patch_creates_campaign_updated_feed_event(
        self, test_client: AsyncClient, test_creator_token, test_campaign, test_db
    ):
        """PATCH /api/campaigns/{id} creates a feed event of type campaign_updated."""
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200

        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_UPDATED,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None

    async def test_feed_event_includes_changed_fields(
        self, test_client: AsyncClient, test_creator_token, test_campaign, test_db
    ):
        """The feed event includes which fields changed in event_metadata."""
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
            json={
                "title": "New Title",
                "goal_amount_usd": 200000,
            },
        )
        assert response.status_code == 200

        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_UPDATED,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None
        assert feed_event.event_metadata is not None
        assert "title" in feed_event.event_metadata
        assert feed_event.event_metadata["title"] == "New Title"
        assert "goal_amount_usd" in feed_event.event_metadata
        assert feed_event.event_metadata["goal_amount_usd"] == 200000

    async def test_no_feed_event_when_no_fields_changed(
        self, test_client: AsyncClient, test_creator_token, test_campaign, test_db
    ):
        """No feed event is created if no fields actually changed."""
        # Get initial feed event count
        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_UPDATED,
            )
        )
        initial_count = len(result.scalars().all())

        # PATCH with same values (no actual change)
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
            json={
                "title": test_campaign.title,
                "description": test_campaign.description,
            },
        )
        assert response.status_code == 200

        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_UPDATED,
            )
        )
        final_count = len(result.scalars().all())
        assert final_count == initial_count

    async def test_feed_event_content_for_description_update(
        self, test_client: AsyncClient, test_creator_token, test_campaign, test_db
    ):
        """Feed event content for description update."""
        new_desc = "Updated description with more details"
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
            json={"description": new_desc},
        )
        assert response.status_code == 200

        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_UPDATED,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None
        assert feed_event.event_metadata.get("description") == new_desc
