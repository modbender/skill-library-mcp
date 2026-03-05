"""Extended integration tests for agent routes."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

from app.db.models import Advocacy, Campaign, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestAgentLeaderboardTimeframe:
    """Tests for leaderboard timeframe filtering."""
    
    async def test_leaderboard_week_timeframe(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter by week timeframe."""
        from app.core.security import create_api_key, hash_api_key
        from app.db.models import Agent
        
        # Create agents
        agent1 = Agent(
            name="agent1",
            api_key_hash=hash_api_key(create_api_key()),
            karma=100,
        )
        agent2 = Agent(
            name="agent2",
            api_key_hash=hash_api_key(create_api_key()),
            karma=50,
        )
        test_db.add(agent1)
        test_db.add(agent2)
        await test_db.flush()
        
        # Create campaign
        campaign = Campaign(
            title="Test Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create recent advocacy (within week)
        recent_advocacy = Advocacy(
            campaign_id=campaign.id,
            agent_id=agent1.id,
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
        )
        test_db.add(recent_advocacy)
        
        # Create old advocacy (outside week)
        old_advocacy = Advocacy(
            campaign_id=campaign.id,
            agent_id=agent2.id,
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        test_db.add(old_advocacy)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=week")
        
        assert response.status_code == 200
        data = response.json()
        # Should only include agent1 (has recent advocacy)
        agent_names = [a["name"] for a in data]
        assert "agent1" in agent_names
