"""Comprehensive integration tests for advocacy routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Advocacy, Agent, Campaign, CampaignCategory, CampaignStatus
from app.core.security import create_api_key, hash_api_key


@pytest.mark.asyncio
class TestAdvocacyComprehensive:
    """Comprehensive tests for advocacy routes."""
    
    async def test_list_advocates_with_multiple_advocates(self, test_client: AsyncClient, test_campaign, test_db):
        """Should list multiple advocates correctly."""
        # Create multiple agents
        agent1 = Agent(
            name="agent1",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        agent2 = Agent(
            name="agent2",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(agent1)
        test_db.add(agent2)
        await test_db.flush()
        
        # Create advocacies
        adv1 = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent1.id,
            statement="First advocate",
            is_active=True,
            is_first_advocate=True,
        )
        adv2 = Advocacy(
            campaign_id=test_campaign.id,
            agent_id=agent2.id,
            statement="Second advocate",
            is_active=True,
            is_first_advocate=False,
        )
        test_db.add(adv1)
        test_db.add(adv2)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/advocates")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Check ordering (ascending by created_at)
        assert data[0]["agent_name"] == "agent1"
        assert data[1]["agent_name"] == "agent2"
        assert data[0]["is_first_advocate"] is True
        assert data[1]["is_first_advocate"] is False
