"""Extended integration tests for feed routes."""
import pytest
from httpx import AsyncClient

from app.db.models import FeedEvent, FeedEventType, Campaign, Agent, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestFeedFilters:
    """Tests for feed filtering."""
    
    async def test_feed_filter_discussions(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should filter by discussions."""
        agent, _ = test_agent
        
        # Create different event types
        campaign_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,
        )
        test_db.add(campaign_event)
        
        discussion_event = FeedEvent(
            event_type=FeedEventType.WARROOM_POST,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        test_db.add(discussion_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed?filter=discussions")
        
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["event_type"] == FeedEventType.WARROOM_POST.value
    
    async def test_feed_with_campaign_and_agent_data(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should include campaign title and agent name in feed."""
        agent, _ = test_agent
        
        feed_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 1
        event = data["events"][0]
        assert event["campaign_title"] == test_campaign.title
        assert event["agent_name"] == agent.name
    
    async def test_feed_with_missing_campaign(self, test_client: AsyncClient, test_agent, test_db):
        """Should handle missing campaign gracefully."""
        agent, _ = test_agent
        
        feed_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id="nonexistent-id",
            agent_id=agent.id,
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 1
        event = data["events"][0]
        assert event["campaign_title"] is None
