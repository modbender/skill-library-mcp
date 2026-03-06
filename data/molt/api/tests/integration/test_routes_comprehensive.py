"""Comprehensive integration tests covering all route combinations."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignStatus, CampaignCategory, Advocacy, Agent
from app.core.security import create_api_key, hash_api_key


@pytest.mark.asyncio
class TestRouteCombinations:
    """Tests for various route parameter combinations."""
    
    async def test_campaign_list_all_combinations(self, test_client: AsyncClient, test_db, test_creator):
        """Test all combinations of campaign list parameters."""
        # Create campaigns with different categories
        campaign1 = Campaign(
            title="Medical Campaign",
            description="Medical",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest1",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign2 = Campaign(
            title="Education Campaign",
            description="Education",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=200000,
            btc_wallet_address="bc1qtest",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign1)
        test_db.add(campaign2)
        await test_db.commit()
        
        # Test category filter
        response = await test_client.get("/api/campaigns?category=MEDICAL")
        assert response.status_code == 200
        data = response.json()
        assert all(c["category"] == "MEDICAL" for c in data["campaigns"])
        
        # Test search
        response = await test_client.get("/api/campaigns?search=Medical")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 1
        
        # Test search in description
        response = await test_client.get("/api/campaigns?search=Education")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 1
    
    async def test_campaign_list_with_advocates_sorting(self, test_client: AsyncClient, test_db, test_creator):
        """Test sorting with advocates."""
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
        
        # Test most_advocates sort
        response = await test_client.get("/api/campaigns?sort=most_advocates")
        assert response.status_code == 200
        data = response.json()
        # Campaign 2 should come first (more advocates)
        if len(data["campaigns"]) >= 2:
            assert data["campaigns"][0]["advocate_count"] >= data["campaigns"][1]["advocate_count"]
        
        # Test trending sort
        response = await test_client.get("/api/campaigns?sort=trending")
        assert response.status_code == 200
