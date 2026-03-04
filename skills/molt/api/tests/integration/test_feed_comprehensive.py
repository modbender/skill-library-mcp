"""Comprehensive integration tests for feed routes."""
import pytest
from httpx import AsyncClient

from app.db.models import FeedEvent, FeedEventType, Campaign, Agent, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestFeedComprehensive:
    """Comprehensive tests for feed routes."""
    
    async def test_feed_with_campaign_id_only(self, test_client: AsyncClient, test_campaign, test_db):
        """Should handle feed events with only campaign_id."""
        feed_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,  # No agent
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        event = next((e for e in data["events"] if e["id"] == feed_event.id), None)
        assert event is not None
        assert event["campaign_title"] == test_campaign.title
        assert event["agent_name"] is None
    
    async def test_feed_with_agent_id_only(self, test_client: AsyncClient, test_agent, test_db):
        """Should handle feed events with only agent_id."""
        agent, _ = test_agent
        
        feed_event = FeedEvent(
            event_type=FeedEventType.AGENT_MILESTONE,
            campaign_id=None,  # No campaign
            agent_id=agent.id,
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        event = next((e for e in data["events"] if e["id"] == feed_event.id), None)
        assert event is not None
        assert event["campaign_title"] is None
        assert event["agent_name"] == agent.name
    
    async def test_feed_with_missing_agent(self, test_client: AsyncClient, test_campaign, test_db):
        """Should handle feed events with nonexistent agent."""
        feed_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=test_campaign.id,
            agent_id="nonexistent-agent-id",
        )
        test_db.add(feed_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed")
        
        assert response.status_code == 200
        data = response.json()
        event = next((e for e in data["events"] if e["id"] == feed_event.id), None)
        assert event is not None
        assert event["agent_name"] is None
    
    async def test_feed_filter_all(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should return all events when filter=all."""
        agent, _ = test_agent
        
        # Create different event types
        campaign_event = FeedEvent(
            event_type=FeedEventType.CAMPAIGN_CREATED,
            campaign_id=test_campaign.id,
            agent_id=None,
        )
        advocacy_event = FeedEvent(
            event_type=FeedEventType.ADVOCACY_ADDED,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        discussion_event = FeedEvent(
            event_type=FeedEventType.WARROOM_POST,
            campaign_id=test_campaign.id,
            agent_id=agent.id,
        )
        test_db.add(campaign_event)
        test_db.add(advocacy_event)
        test_db.add(discussion_event)
        await test_db.commit()
        
        response = await test_client.get("/api/feed?filter=all")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) >= 3
