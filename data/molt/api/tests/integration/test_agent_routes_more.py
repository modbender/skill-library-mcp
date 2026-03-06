"""More integration tests for agent routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Agent, Campaign, CampaignCategory, CampaignStatus, Advocacy


@pytest.mark.asyncio
class TestAgentProfile:
    """Extended tests for agent profile."""
    
    async def test_agent_profile_with_campaign_titles(self, test_client: AsyncClient, test_db, test_creator):
        """Should include campaign titles in advocacy summaries."""
        from app.core.security import create_api_key, hash_api_key
        
        # Create agent
        agent = Agent(
            name="test-agent",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(agent)
        await test_db.flush()
        
        # Create campaigns
        campaign1 = Campaign(
            title="Campaign 1",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest1",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign2 = Campaign(
            title="Campaign 2",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest2",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign1)
        test_db.add(campaign2)
        await test_db.flush()
        
        # Create advocacies
        adv1 = Advocacy(
            campaign_id=campaign1.id,
            agent_id=agent.id,
            is_active=True,
        )
        adv2 = Advocacy(
            campaign_id=campaign2.id,
            agent_id=agent.id,
            is_active=True,
        )
        test_db.add(adv1)
        test_db.add(adv2)
        await test_db.commit()
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recent_advocacies"]) == 2
        assert data["recent_advocacies"][0]["campaign_title"] == "Campaign 2"  # Most recent first
        assert data["recent_advocacies"][1]["campaign_title"] == "Campaign 1"
