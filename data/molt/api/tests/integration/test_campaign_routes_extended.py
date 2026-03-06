"""Extended integration tests for campaign routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignStatus, CampaignCategory


@pytest.mark.asyncio
class TestCampaignSorting:
    """Tests for campaign sorting options."""
    
    async def test_sort_most_advocates(self, test_client: AsyncClient, test_db, test_creator):
        """Should sort by most advocates."""
        from app.db.models import Advocacy
        from app.core.security import create_api_key, hash_api_key
        from app.db.models import Agent
        
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
        
        # Create agents
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
        
        # Add advocacies (campaign2 has more)
        adv1 = Advocacy(campaign_id=campaign1.id, agent_id=agent1.id, is_active=True)
        adv2 = Advocacy(campaign_id=campaign2.id, agent_id=agent1.id, is_active=True)
        adv3 = Advocacy(campaign_id=campaign2.id, agent_id=agent2.id, is_active=True)
        test_db.add(adv1)
        test_db.add(adv2)
        test_db.add(adv3)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?sort=most_advocates")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 2
        # Campaign 2 should come first (more advocates)
        assert data["campaigns"][0]["advocate_count"] >= data["campaigns"][1]["advocate_count"]
    
    async def test_sort_trending(self, test_client: AsyncClient, test_db, test_creator):
        """Should sort by trending."""
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
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?sort=trending")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 2
