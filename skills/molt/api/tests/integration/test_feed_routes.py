"""Integration tests for feed routes."""
import pytest
from httpx import AsyncClient

from app.db.models import FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestGetFeed:
    """Tests for GET /api/feed."""
    
    async def test_get_feed(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should return feed events."""
        agent, _ = test_agent
        
        # Create feed event
        feed_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,
            event_metadata={"title": test_campaign.title},
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert len(data["events"]) >= 1
    
    async def test_get_feed_pagination(self, test_client: AsyncClient, test_campaign, test_db):
        """Should paginate feed events."""
        # Create multiple feed events
        for i in range(25):
            feed_event = FeedEvent(
                event_type=FeedEventType.CAMPAIGN_CREATED,
                campaign_id=test_campaign.id,
                agent_id=None,
                event_metadata={"title": f"Campaign {i}"},
            )
            test_db.add(feed_event)
        await test_db.commit()
        
        # First page
        response = await test_client.get("/api/feed?page=1&per_page=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 20
        
        # Second page
        response = await test_client.get("/api/feed?page=2&per_page=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 5
    
    async def test_get_feed_filter_campaigns(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should filter by campaign events."""
        agent, _ = test_agent
        
        # Create different event types
        campaign_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,
        )
        test_db.add(campaign_event)
        
        advocacy_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        test_db.add(advocacy_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed?filter=campaigns")
        
        assert response.status_code == 200
        data = response.json()
        # Should only include campaign events
        for event in data["events"]:
            assert event["event_type"] == FeedEventType.CAMPAIGN_CREATED.value
    
    async def test_get_feed_filter_advocacy(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should filter by advocacy events."""
        agent, _ = test_agent
        
        # Create different event types
        campaign_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,
        )
        test_db.add(campaign_event)
        
        advocacy_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        test_db.add(advocacy_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed?filter=advocacy")
        
        assert response.status_code == 200
        data = response.json()
        # Should only include advocacy events
        for event in data["events"]:
            assert event["event_type"] in [
                FeedEventType.ADVOCACY_ADDED.value,
                FeedEventType.ADVOCACY_STATEMENT.value,
            ]
