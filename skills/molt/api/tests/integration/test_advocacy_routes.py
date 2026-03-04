"""Integration tests for advocacy routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Advocacy, FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestListAdvocates:
    """Tests for GET /api/campaigns/{id}/advocates."""
    
    async def test_list_advocates(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should list active advocates for campaign."""
        agent, _ = test_agent
        
        # Create advocacy
        advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            statement="I support this campaign",
            is_active=True,
        )
        test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/advocates")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["agent_id"] == agent.id
        assert data[0]["statement"] == "I support this campaign"
    
    async def test_list_advocates_excludes_inactive(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should exclude inactive advocacies."""
        agent, _ = test_agent
        
        # Create active and inactive advocacies
        active_advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            is_active=True,
        )
        test_db.add(active_advocacy)
        
        # Create another agent for inactive advocacy
        from app.db.models import Agent
        from app.core.security import create_api_key, hash_api_key
        api_key = create_api_key()
        agent2 = Agent(
            name="agent2",
            api_key_hash=hash_api_key(api_key),
            karma=0,
        )
        test_db.add(agent2)
        await test_db.flush()
        
        inactive_advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent2.id,
            is_active=False,
        )
        test_db.add(inactive_advocacy)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/advocates")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["agent_id"] == agent.id


@pytest.mark.asyncio
class TestAdvocateForCampaign:
    """Tests for POST /api/campaigns/{id}/advocate."""
    
    async def test_advocate_for_campaign(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should create advocacy and award karma."""
        agent, api_key = test_agent
        
        # Create an existing advocacy so this isn't the first advocate
        from app.db.models import Agent
        from app.core.security import create_api_key, hash_api_key
        api_key2 = create_api_key()
        agent2 = Agent(
            name="agent2",
            api_key_hash=hash_api_key(api_key2),
            karma=0,
        )
        test_db.add(agent2)
        await test_db.flush()
        
        existing_advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent2.id,
            is_active=True,
        )
        test_db.add(existing_advocacy)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/advocate",
            json={"statement": "I support this campaign"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["advocacy"]["agent_id"] == agent.id
        assert data["advocacy"]["statement"] == "I support this campaign"
        assert data["karma_earned"] == 5  # Base karma (not first advocate)
    
    async def test_advocate_first_advocate_bonus(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should award scout bonus for first advocate."""
        agent, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/advocate",
            json={},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["karma_earned"] == 15  # 5 base + 10 scout bonus
        assert data["advocacy"]["is_first_advocate"] is True
    
    async def test_advocate_duplicate(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should reject duplicate advocacy."""
        agent, api_key = test_agent
        
        # Create existing advocacy
        advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            is_active=True,
        )
        test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/advocate",
            json={},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 400
        assert "already advocating" in response.json()["detail"].lower()
    
    async def test_advocate_creates_feed_event(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should create feed event."""
        agent, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/advocate",
            json={"statement": "Test"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        
        # Verify feed event
        from sqlalchemy import select
        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.event_type == FeedEventType.ADVOCACY_ADDED,
                FeedEvent.campaign_id == test_campaign.id,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None


@pytest.mark.asyncio
class TestWithdrawAdvocacy:
    """Tests for DELETE /api/campaigns/{id}/advocate."""
    
    async def test_withdraw_advocacy(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should withdraw advocacy."""
        agent, api_key = test_agent
        
        # Create advocacy
        advocacy = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            is_active=True,
        )
        test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/advocate",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 204
        
        # Verify advocacy is inactive
        await test_db.refresh(advocacy)
        assert advocacy.is_active is False
        assert advocacy.withdrawn_at is not None
    
    async def test_withdraw_nonexistent(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should return 404 for nonexistent advocacy."""
        _, api_key = test_agent
        
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/advocate",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
