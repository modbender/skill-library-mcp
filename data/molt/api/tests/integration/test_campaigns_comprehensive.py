"""Comprehensive integration tests for campaign routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignStatus, CampaignCategory, Donation
from datetime import datetime, timezone


@pytest.mark.asyncio
class TestCampaignListComprehensive:
    """Comprehensive tests for campaign listing."""
    
    async def test_list_campaigns_with_advocates_count(self, test_client: AsyncClient, test_db, test_creator):
        """Should calculate advocate count correctly."""
        from app.db.models import Advocacy
        from app.core.security import create_api_key, hash_api_key
        from app.db.models import Agent
        
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
        
        # Create agents and advocacies
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
        
        # Add active advocacies
        adv1 = Advocacy(campaign_id=campaign.id, agent_id=agent1.id, is_active=True)
        adv2 = Advocacy(campaign_id=campaign.id, agent_id=agent2.id, is_active=True)
        test_db.add(adv1)
        test_db.add(adv2)
        await test_db.commit()
        
        # Withdraw one advocacy (make it inactive)
        adv1.is_active = False
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns")
        
        assert response.status_code == 200
        data = response.json()
        # Find our campaign
        campaign_data = next((c for c in data["campaigns"] if c["id"] == campaign.id), None)
        assert campaign_data is not None
        assert campaign_data["advocate_count"] == 1  # Only active advocacies (adv2)
    
    async def test_list_campaigns_all_sort_options(self, test_client: AsyncClient, test_db, test_creator):
        """Should test all sort options."""
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
        
        # Test newest sort
        response = await test_client.get("/api/campaigns?sort=newest")
        assert response.status_code == 200
        
        # Test most_advocates sort
        response = await test_client.get("/api/campaigns?sort=most_advocates")
        assert response.status_code == 200
        
        # Test trending sort
        response = await test_client.get("/api/campaigns?sort=trending")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestCampaignDetailComprehensive:
    """Comprehensive tests for campaign detail."""
    
    async def test_get_campaign_with_advocates(self, test_client: AsyncClient, test_campaign, test_db):
        """Should include advocate count in detail."""
        from app.db.models import Advocacy
        from app.core.security import create_api_key, hash_api_key
        from app.db.models import Agent
        
        agent = Agent(
            name="test-agent",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(agent)
        await test_db.flush()
        
        adv = Advocacy(campaign_id=test_campaign.id, agent_id=agent.id, is_active=True)
        test_db.add(adv)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["advocate_count"] == 1


@pytest.mark.asyncio
class TestDonationsComprehensive:
    """Comprehensive tests for donations endpoint."""
    
    async def test_list_donations_all_chains(self, test_client: AsyncClient, test_campaign, test_db):
        """Should list donations for all chains."""
        # Create donations for different chains
        donation1 = Donation(
            campaign_id=test_campaign.id,
            chain="btc",
            tx_hash="tx1",
            amount_smallest_unit=1000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        donation2 = Donation(
            campaign_id=test_campaign.id,
            chain="eth",
            tx_hash="tx2",
            amount_smallest_unit=2000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        donation3 = Donation(
            campaign_id=test_campaign.id,
            chain="usdc_base",
            tx_hash="tx3",
            amount_smallest_unit=3000000,  # 3 USDC (6 decimals)
            confirmed_at=datetime.now(timezone.utc),
        )
        donation4 = Donation(
            campaign_id=test_campaign.id,
            chain="sol",
            tx_hash="tx4",
            amount_smallest_unit=4000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        test_db.add(donation1)
        test_db.add(donation2)
        test_db.add(donation3)
        test_db.add(donation4)
        await test_db.commit()
        
        # Test filtering by each chain
        for chain in ["btc", "eth", "usdc_base", "sol"]:
            response = await test_client.get(f"/api/campaigns/{test_campaign.id}/donations?chain={chain}")
            assert response.status_code == 200
            data = response.json()
            assert len(data["donations"]) == 1
            assert data["donations"][0]["chain"] == chain
