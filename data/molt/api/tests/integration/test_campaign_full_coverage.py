"""Comprehensive integration tests for campaign routes to improve coverage.

This file tests all code paths in api/app/api/routes/campaigns.py including:
- list_campaigns: sorting (newest, most_advocates, trending), filtering, search, pagination
- get_campaign: success case with advocate count calculation
- create_campaign: successful creation with feed event, validation errors
- update_campaign: successful update, 403 for non-owner, 404 for missing
- delete_campaign: soft delete, 403 for non-owner, 404 for missing
- list_donations: filtering by chain, pagination
"""
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import (
    Campaign, CampaignStatus, CampaignCategory,
    Advocacy, Agent, Donation, Creator, FeedEvent, FeedEventType
)
from app.core.security import create_api_key, hash_api_key, create_access_token


@pytest.mark.asyncio
class TestListCampaignsSorting:
    """Tests for list_campaigns sorting options."""
    
    async def test_list_campaigns_sort_newest(self, test_client: AsyncClient, test_db, test_creator):
        """Should sort campaigns by newest first (created_at desc)."""
        # Create multiple campaigns with different timestamps
        campaign1 = Campaign(
            id="campaign-old",
            title="Old Campaign",
            description="Created first",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc) - timedelta(days=10),
        )
        campaign2 = Campaign(
            id="campaign-new",
            title="New Campaign",
            description="Created second",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=20000,
            eth_wallet_address="0x842d35Cc6634C0532925a3b844Bc9e7595f0cEc",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add_all([campaign1, campaign2])
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?sort=newest")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 2
        # Newest should come first
        titles = [c["title"] for c in data["campaigns"]]
        assert titles.index("New Campaign") < titles.index("Old Campaign")
    
    async def test_list_campaigns_sort_most_advocates(self, test_client: AsyncClient, test_db, test_creator):
        """Should sort campaigns by most advocates (advocacy count desc)."""
        # Create campaigns
        campaign_popular = Campaign(
            id="campaign-popular",
            title="Popular Campaign",
            description="Has many advocates",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign_unpopular = Campaign(
            id="campaign-unpopular",
            title="Unpopular Campaign",
            description="Has no advocates",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=20000,
            eth_wallet_address="0x842d35Cc6634C0532925a3b844Bc9e7595f0cEc",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add_all([campaign_popular, campaign_unpopular])
        await test_db.flush()
        
        # Create agents and advocacies for popular campaign
        for i in range(3):
            api_key = create_api_key()
            agent = Agent(
                id=f"advocate-agent-{i}",
                name=f"advocate-agent-{i}",
                description="Test agent",
                api_key_hash=hash_api_key(api_key),
                karma=10,
            )
            test_db.add(agent)
            await test_db.flush()
            
            advocacy = Advocacy(
                id=f"advocacy-{i}",
                campaign_id=campaign_popular.id,
                agent_id=agent.id,
                statement="I support this campaign",
                is_active=True,
            )
            test_db.add(advocacy)
        
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?sort=most_advocates")
        
        assert response.status_code == 200
        data = response.json()
        # Popular campaign should come first due to more advocates
        titles = [c["title"] for c in data["campaigns"]]
        if "Popular Campaign" in titles and "Unpopular Campaign" in titles:
            assert titles.index("Popular Campaign") < titles.index("Unpopular Campaign")
    
    async def test_list_campaigns_sort_trending(self, test_client: AsyncClient, test_db, test_creator):
        """Should sort campaigns by trending (advocate count + recency)."""
        # Create campaigns
        campaign_trending = Campaign(
            id="campaign-trending",
            title="Trending Campaign",
            description="Has advocates and is recent",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=15000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign_stale = Campaign(
            id="campaign-stale",
            title="Stale Campaign",
            description="No advocates",
            category=CampaignCategory.OTHER,
            goal_amount_usd=25000,
            eth_wallet_address="0x942d35Cc6634C0532925a3b844Bc9e7595f0dEd",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
        )
        test_db.add_all([campaign_trending, campaign_stale])
        await test_db.flush()
        
        # Add advocate to trending campaign
        api_key = create_api_key()
        agent = Agent(
            id="trending-agent",
            name="trending-agent",
            description="Test agent",
            api_key_hash=hash_api_key(api_key),
            karma=10,
        )
        test_db.add(agent)
        await test_db.flush()
        
        advocacy = Advocacy(
            id="trending-advocacy",
            campaign_id=campaign_trending.id,
            agent_id=agent.id,
            statement="Trending!",
            is_active=True,
        )
        test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?sort=trending")
        
        assert response.status_code == 200
        data = response.json()
        titles = [c["title"] for c in data["campaigns"]]
        if "Trending Campaign" in titles and "Stale Campaign" in titles:
            assert titles.index("Trending Campaign") < titles.index("Stale Campaign")


@pytest.mark.asyncio
class TestListCampaignsFiltering:
    """Tests for list_campaigns filtering options."""
    
    async def test_list_campaigns_filter_by_category(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter campaigns by category."""
        # Create campaigns with different categories
        campaign_medical = Campaign(
            id="category-medical",
            title="Medical Campaign",
            description="Medical category",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign_education = Campaign(
            id="category-education",
            title="Education Campaign",
            description="Education category",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=20000,
            eth_wallet_address="0x842d35Cc6634C0532925a3b844Bc9e7595f0cEc",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add_all([campaign_medical, campaign_education])
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?category=MEDICAL")
        
        assert response.status_code == 200
        data = response.json()
        assert all(c["category"] == "MEDICAL" for c in data["campaigns"])
        assert any(c["title"] == "Medical Campaign" for c in data["campaigns"])
    
    async def test_list_campaigns_search_title(self, test_client: AsyncClient, test_db, test_creator):
        """Should search campaigns by title."""
        campaign = Campaign(
            id="search-title-campaign",
            title="Unique Searchable Title XYZ123",
            description="Regular description",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?search=XYZ123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(c["title"] == "Unique Searchable Title XYZ123" for c in data["campaigns"])
    
    async def test_list_campaigns_search_description(self, test_client: AsyncClient, test_db, test_creator):
        """Should search campaigns by description."""
        campaign = Campaign(
            id="search-desc-campaign",
            title="Normal Title",
            description="This has a unique searchable keyword ABC789 in it",
            category=CampaignCategory.EMERGENCY,
            goal_amount_usd=15000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?search=ABC789")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(c["id"] == "search-desc-campaign" for c in data["campaigns"])
    
    async def test_list_campaigns_excludes_non_active(self, test_client: AsyncClient, test_db, test_creator):
        """Should only return ACTIVE campaigns."""
        campaign_active = Campaign(
            id="status-active",
            title="Active Status Campaign",
            description="Active",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign_cancelled = Campaign(
            id="status-cancelled",
            title="Cancelled Status Campaign",
            description="Cancelled",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x842d35Cc6634C0532925a3b844Bc9e7595f0cEc",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.CANCELLED,
        )
        campaign_completed = Campaign(
            id="status-completed",
            title="Completed Status Campaign",
            description="Completed",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x942d35Cc6634C0532925a3b844Bc9e7595f0dEd",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.COMPLETED,
        )
        test_db.add_all([campaign_active, campaign_cancelled, campaign_completed])
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns")
        
        assert response.status_code == 200
        data = response.json()
        campaign_ids = [c["id"] for c in data["campaigns"]]
        assert "status-active" in campaign_ids
        assert "status-cancelled" not in campaign_ids
        assert "status-completed" not in campaign_ids


@pytest.mark.asyncio
class TestListCampaignsPagination:
    """Tests for list_campaigns pagination."""
    
    async def test_list_campaigns_pagination_first_page(self, test_client: AsyncClient, test_db, test_creator):
        """Should return first page correctly."""
        # Create 5 campaigns
        for i in range(5):
            campaign = Campaign(
                id=f"pagination-campaign-{i}",
                title=f"Pagination Campaign {i}",
                description=f"Campaign {i}",
                category=CampaignCategory.MEDICAL,
                goal_amount_usd=10000,
                eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                contact_email=test_creator.email,
                creator_id=test_creator.id,
                status=CampaignStatus.ACTIVE,
            )
            test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?page=1&per_page=2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["campaigns"]) == 2
        assert data["total"] >= 5
    
    async def test_list_campaigns_pagination_second_page(self, test_client: AsyncClient, test_db, test_creator):
        """Should return second page correctly."""
        # Create 5 campaigns
        for i in range(5):
            campaign = Campaign(
                id=f"pagination2-campaign-{i}",
                title=f"Pagination2 Campaign {i}",
                description=f"Campaign {i}",
                category=CampaignCategory.EDUCATION,
                goal_amount_usd=10000,
                eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                contact_email=test_creator.email,
                creator_id=test_creator.id,
                status=CampaignStatus.ACTIVE,
            )
            test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?page=2&per_page=2&category=EDUCATION")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 2
        assert len(data["campaigns"]) >= 1  # Should have remaining campaigns
    
    async def test_list_campaigns_pagination_beyond_total(self, test_client: AsyncClient, test_db, test_creator):
        """Should return empty list for page beyond total."""
        campaign = Campaign(
            id="pagination-beyond",
            title="Single Campaign",
            description="Only one",
            category=CampaignCategory.DISASTER_RELIEF,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?page=100&per_page=20&category=DISASTER_RELIEF")
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns"] == []


@pytest.mark.asyncio
class TestGetCampaignAdvocateCount:
    """Tests for get_campaign with advocate count calculation."""
    
    async def test_get_campaign_with_active_advocates(self, test_client: AsyncClient, test_db, test_creator):
        """Should calculate advocate count from active advocacies."""
        campaign = Campaign(
            id="advocate-count-campaign",
            title="Campaign With Advocates",
            description="Has advocates",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create agents and advocacies (2 active, 1 inactive)
        for i in range(3):
            api_key = create_api_key()
            agent = Agent(
                id=f"count-agent-{i}",
                name=f"count-agent-{i}",
                description="Test agent",
                api_key_hash=hash_api_key(api_key),
                karma=10,
            )
            test_db.add(agent)
            await test_db.flush()
            
            advocacy = Advocacy(
                id=f"count-advocacy-{i}",
                campaign_id=campaign.id,
                agent_id=agent.id,
                statement=f"Statement {i}",
                is_active=(i < 2),  # First 2 active, last one inactive
            )
            test_db.add(advocacy)
        
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["advocate_count"] == 2  # Only active advocates counted
    
    async def test_get_campaign_no_advocates(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 0 advocate count when no advocacies."""
        campaign = Campaign(
            id="no-advocate-campaign",
            title="Campaign Without Advocates",
            description="No advocates",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=20000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["advocate_count"] == 0
    
    async def test_get_campaign_not_found(self, test_client: AsyncClient):
        """Should return 404 for non-existent campaign."""
        response = await test_client.get("/api/campaigns/nonexistent-campaign-id-xyz")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestCreateCampaignValidation:
    """Tests for create_campaign validation and feed event creation."""
    
    async def test_create_campaign_with_eth_wallet(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with ETH wallet address."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "ETH Campaign",
                "description": "Campaign with ETH wallet",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["eth_wallet_address"] == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        assert data["advocate_count"] == 0
    
    async def test_create_campaign_with_btc_wallet(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with BTC wallet address."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "BTC Campaign",
                "description": "Campaign with BTC wallet",
                "category": "EDUCATION",
                "goal_amount_usd": 50000,
                "btc_wallet_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["btc_wallet_address"] == "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    
    async def test_create_campaign_with_usdc_base_wallet(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with USDC on Base wallet address."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "USDC Base Campaign",
                "description": "Campaign with USDC on Base wallet",
                "category": "COMMUNITY",
                "goal_amount_usd": 25000,
                "usdc_base_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["usdc_base_wallet_address"] == "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    
    async def test_create_campaign_with_sol_wallet(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with SOL wallet address."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "SOL Campaign",
                "description": "Campaign with SOL wallet",
                "category": "EMERGENCY",
                "goal_amount_usd": 75000,
                "sol_wallet_address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["sol_wallet_address"] == "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    async def test_create_campaign_no_wallet_fails(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should fail when no wallet address provided."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "No Wallet Campaign",
                "description": "Campaign without wallet",
                "category": "OTHER",
                "goal_amount_usd": 10000,
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 400
        assert "wallet" in response.json()["detail"].lower()
    
    async def test_create_campaign_creates_feed_event(self, test_client: AsyncClient, test_creator_token, test_creator, test_db):
        """Should create CAMPAIGN_CREATED feed event."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Feed Event Test Campaign",
                "description": "Testing feed event creation",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        campaign_id = response.json()["id"]
        
        # Verify feed event was created
        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == campaign_id,
                FeedEvent.event_type == FeedEventType.CAMPAIGN_CREATED
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None
        assert feed_event.event_metadata["title"] == "Feed Event Test Campaign"
    
    async def test_create_campaign_requires_auth(self, test_client: AsyncClient):
        """Should require authentication."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Unauthorized Campaign",
                "description": "Should fail",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": "test@example.com",
            },
        )
        
        assert response.status_code == 401
    
    async def test_create_campaign_with_multiple_wallets(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with multiple wallet addresses."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Multi-Wallet Campaign",
                "description": "Campaign with multiple wallets",
                "category": "MEDICAL",
                "goal_amount_usd": 200000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "btc_wallet_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "sol_wallet_address": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["eth_wallet_address"] is not None
        assert data["btc_wallet_address"] is not None
        assert data["sol_wallet_address"] is not None


@pytest.mark.asyncio
class TestUpdateCampaign:
    """Tests for update_campaign."""
    
    async def test_update_campaign_success(self, test_client: AsyncClient, test_db, test_creator, test_creator_token):
        """Should successfully update campaign when owner."""
        campaign = Campaign(
            id="update-test-campaign",
            title="Original Title",
            description="Original description",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.patch(
            f"/api/campaigns/{campaign.id}",
            json={
                "title": "Updated Title",
                "description": "Updated description",
                "goal_amount_usd": 20000,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["goal_amount_usd"] == 20000
    
    async def test_update_campaign_partial_update(self, test_client: AsyncClient, test_db, test_creator, test_creator_token):
        """Should allow partial updates."""
        campaign = Campaign(
            id="partial-update-campaign",
            title="Original",
            description="Original description",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=15000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        # Only update title
        response = await test_client.patch(
            f"/api/campaigns/{campaign.id}",
            json={"title": "Only Title Changed"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Changed"
        assert data["description"] == "Original description"  # Unchanged
        assert data["goal_amount_usd"] == 15000  # Unchanged
    
    async def test_update_campaign_403_non_owner(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 403 when non-owner tries to update."""
        campaign = Campaign(
            id="non-owner-update-campaign",
            title="Original",
            description="Original",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        
        # Create different creator (KYC-approved so we test non-owner, not KYC rejection)
        other_creator = Creator(
            id="other-creator-update",
            email="other-update@example.com",
            kyc_status="approved",
        )
        test_db.add(other_creator)
        await test_db.commit()
        
        other_token = create_access_token(data={"sub": other_creator.id, "email": other_creator.email})
        
        response = await test_client.patch(
            f"/api/campaigns/{campaign.id}",
            json={"title": "Hacked"},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        
        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "not authorized" in (detail if isinstance(detail, str) else detail.get("message", "")).lower()
    
    async def test_update_campaign_404_not_found(self, test_client: AsyncClient, test_creator_token):
        """Should return 404 for non-existent campaign."""
        response = await test_client.patch(
            "/api/campaigns/nonexistent-update-id",
            json={"title": "New Title"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_campaign_status(self, test_client: AsyncClient, test_db, test_creator, test_creator_token):
        """Should allow updating campaign status."""
        campaign = Campaign(
            id="status-update-campaign",
            title="Status Test",
            description="Testing status update",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.patch(
            f"/api/campaigns/{campaign.id}",
            json={"status": "COMPLETED"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"


@pytest.mark.asyncio
class TestDeleteCampaign:
    """Tests for delete_campaign (soft delete)."""
    
    async def test_delete_campaign_soft_delete(self, test_client: AsyncClient, test_db, test_creator, test_creator_token):
        """Should soft delete campaign (set status to CANCELLED)."""
        campaign = Campaign(
            id="soft-delete-campaign",
            title="To Be Deleted",
            description="Will be soft deleted",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.delete(
            f"/api/campaigns/{campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 204
        
        # Verify status changed to CANCELLED
        result = await test_db.execute(
            select(Campaign).where(Campaign.id == campaign.id)
        )
        deleted_campaign = result.scalar_one_or_none()
        assert deleted_campaign is not None  # Still exists
        assert deleted_campaign.status == CampaignStatus.CANCELLED
    
    async def test_delete_campaign_403_non_owner(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 403 when non-owner tries to delete."""
        campaign = Campaign(
            id="non-owner-delete-campaign",
            title="Cannot Delete",
            description="Non-owner cannot delete",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=20000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        
        # Create different creator (KYC-approved so we test non-owner, not KYC rejection)
        other_creator = Creator(
            id="other-creator-delete",
            email="other-delete@example.com",
            kyc_status="approved",
        )
        test_db.add(other_creator)
        await test_db.commit()
        
        other_token = create_access_token(data={"sub": other_creator.id, "email": other_creator.email})
        
        response = await test_client.delete(
            f"/api/campaigns/{campaign.id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        
        assert response.status_code == 403
        detail = response.json()["detail"]
        assert "not authorized" in (detail if isinstance(detail, str) else detail.get("message", "")).lower()
    
    async def test_delete_campaign_404_not_found(self, test_client: AsyncClient, test_creator_token):
        """Should return 404 for non-existent campaign."""
        response = await test_client.delete(
            "/api/campaigns/nonexistent-delete-id",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_delete_campaign_requires_auth(self, test_client: AsyncClient, test_campaign):
        """Should require authentication to delete."""
        response = await test_client.delete(f"/api/campaigns/{test_campaign.id}")
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestListDonations:
    """Tests for list_donations endpoint."""
    
    async def test_list_donations_success(self, test_client: AsyncClient, test_db, test_creator):
        """Should list donations for a campaign."""
        campaign = Campaign(
            id="donations-campaign",
            title="Donations Test",
            description="Testing donations list",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create donations
        donation1 = Donation(
            id="donation-1",
            campaign_id=campaign.id,
            chain="eth",
            tx_hash="0xabc123def456789",
            amount_smallest_unit=1000000000000000000,  # 1 ETH in wei
            from_address="0xsender1",
            confirmed_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        donation2 = Donation(
            id="donation-2",
            campaign_id=campaign.id,
            chain="btc",
            tx_hash="txhash789xyz",
            amount_smallest_unit=10000000,  # 0.1 BTC in satoshi
            from_address="bc1sender",
            confirmed_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        test_db.add_all([donation1, donation2])
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations")
        
        assert response.status_code == 200
        data = response.json()
        assert "donations" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["donations"]) == 2
    
    async def test_list_donations_filter_by_chain(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter donations by chain."""
        campaign = Campaign(
            id="chain-filter-campaign",
            title="Chain Filter Test",
            description="Testing chain filter",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=50000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            btc_wallet_address="bc1testaddress",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create donations for different chains
        eth_donation = Donation(
            id="eth-donation-filter",
            campaign_id=campaign.id,
            chain="eth",
            tx_hash="0xeth123",
            amount_smallest_unit=500000000000000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        btc_donation = Donation(
            id="btc-donation-filter",
            campaign_id=campaign.id,
            chain="btc",
            tx_hash="btctx123",
            amount_smallest_unit=5000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        test_db.add_all([eth_donation, btc_donation])
        await test_db.commit()
        
        # Filter by ETH
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations?chain=eth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(d["chain"] == "eth" for d in data["donations"])
    
    async def test_list_donations_pagination(self, test_client: AsyncClient, test_db, test_creator):
        """Should paginate donations."""
        campaign = Campaign(
            id="donations-pagination-campaign",
            title="Donations Pagination",
            description="Testing donations pagination",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=75000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create 5 donations
        for i in range(5):
            donation = Donation(
                id=f"pagination-donation-{i}",
                campaign_id=campaign.id,
                chain="eth",
                tx_hash=f"0xpagination{i}",
                amount_smallest_unit=1000000000000000 * (i + 1),
                confirmed_at=datetime.now(timezone.utc) - timedelta(minutes=i * 10),
            )
            test_db.add(donation)
        await test_db.commit()
        
        # Get first page
        response = await test_client.get(
            f"/api/campaigns/{campaign.id}/donations?page=1&per_page=2"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["donations"]) == 2
        assert data["total"] == 5
    
    async def test_list_donations_404_campaign_not_found(self, test_client: AsyncClient):
        """Should return 404 if campaign doesn't exist."""
        response = await test_client.get("/api/campaigns/nonexistent-donations-id/donations")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_list_donations_empty_result(self, test_client: AsyncClient, test_db, test_creator):
        """Should return empty list when no donations."""
        campaign = Campaign(
            id="no-donations-campaign",
            title="No Donations",
            description="Campaign with no donations",
            category=CampaignCategory.EMERGENCY,
            goal_amount_usd=10000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["donations"] == []
        assert data["total"] == 0
    
    async def test_list_donations_ordered_by_confirmed_at_desc(self, test_client: AsyncClient, test_db, test_creator):
        """Should order donations by confirmed_at descending (newest first)."""
        campaign = Campaign(
            id="ordered-donations-campaign",
            title="Ordered Donations",
            description="Testing donation ordering",
            category=CampaignCategory.OTHER,
            goal_amount_usd=25000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        old_donation = Donation(
            id="old-donation",
            campaign_id=campaign.id,
            chain="eth",
            tx_hash="0xold",
            amount_smallest_unit=1000000000000000000,
            confirmed_at=datetime.now(timezone.utc) - timedelta(days=5),
        )
        new_donation = Donation(
            id="new-donation",
            campaign_id=campaign.id,
            chain="eth",
            tx_hash="0xnew",
            amount_smallest_unit=2000000000000000000,
            confirmed_at=datetime.now(timezone.utc),
        )
        test_db.add_all([old_donation, new_donation])
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations")
        
        assert response.status_code == 200
        data = response.json()
        donation_ids = [d["id"] for d in data["donations"]]
        assert donation_ids.index("new-donation") < donation_ids.index("old-donation")
    
    async def test_list_donations_filter_usdc_base(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter donations by usdc_base chain."""
        campaign = Campaign(
            id="usdc-base-filter-campaign",
            title="USDC Base Filter Test",
            description="Testing USDC Base filter",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=30000,
            usdc_base_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        usdc_base_donation = Donation(
            id="usdc-base-donation",
            campaign_id=campaign.id,
            chain="usdc_base",
            tx_hash="usdcbasetx123",
            amount_smallest_unit=1000000,  # 1 USDC (6 decimals)
            confirmed_at=datetime.now(timezone.utc),
        )
        test_db.add(usdc_base_donation)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations?chain=usdc_base")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["donations"][0]["chain"] == "usdc_base"
    
    async def test_list_donations_filter_sol(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter donations by sol chain."""
        campaign = Campaign(
            id="sol-filter-campaign",
            title="Sol Filter Test",
            description="Testing sol filter",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=40000,
            sol_wallet_address="SolTestAddress123",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        sol_donation = Donation(
            id="sol-donation",
            campaign_id=campaign.id,
            chain="sol",
            tx_hash="soltx123",
            amount_smallest_unit=1000000000,  # 1 SOL in lamports
            confirmed_at=datetime.now(timezone.utc),
        )
        test_db.add(sol_donation)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations?chain=sol")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["donations"][0]["chain"] == "sol"


@pytest.mark.asyncio
class TestCampaignResponseBuilding:
    """Tests to exercise response building loops and conditional branches."""
    
    async def test_list_campaigns_response_loop_multiple_campaigns(self, test_client: AsyncClient, test_db, test_creator):
        """Should correctly build response for multiple campaigns with advocate counts."""
        # Create campaigns with different advocate counts
        for i in range(3):
            campaign = Campaign(
                id=f"response-loop-campaign-{i}",
                title=f"Response Loop Campaign {i}",
                description=f"Testing response loop {i}",
                category=CampaignCategory.MEDICAL,
                goal_amount_usd=10000 * (i + 1),
                eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                contact_email=test_creator.email,
                creator_id=test_creator.id,
                status=CampaignStatus.ACTIVE,
            )
            test_db.add(campaign)
            await test_db.flush()
            
            # Add advocates to each campaign
            for j in range(i + 1):
                api_key = create_api_key()
                agent = Agent(
                    id=f"loop-agent-{i}-{j}",
                    name=f"loop-agent-{i}-{j}",
                    description="Test agent",
                    api_key_hash=hash_api_key(api_key),
                    karma=10,
                )
                test_db.add(agent)
                await test_db.flush()
                
                advocacy = Advocacy(
                    id=f"loop-advocacy-{i}-{j}",
                    campaign_id=campaign.id,
                    agent_id=agent.id,
                    is_active=True,
                )
                test_db.add(advocacy)
        
        await test_db.commit()
        
        response = await test_client.get("/api/campaigns?category=MEDICAL")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify advocate counts are calculated correctly
        campaigns_by_id = {c["id"]: c for c in data["campaigns"]}
        if "response-loop-campaign-0" in campaigns_by_id:
            assert campaigns_by_id["response-loop-campaign-0"]["advocate_count"] == 1
        if "response-loop-campaign-1" in campaigns_by_id:
            assert campaigns_by_id["response-loop-campaign-1"]["advocate_count"] == 2
        if "response-loop-campaign-2" in campaigns_by_id:
            assert campaigns_by_id["response-loop-campaign-2"]["advocate_count"] == 3
    
    async def test_list_donations_response_loop_multiple_donations(self, test_client: AsyncClient, test_db, test_creator):
        """Should correctly build response for multiple donations."""
        campaign = Campaign(
            id="multiple-donations-campaign",
            title="Multiple Donations",
            description="Testing multiple donations response",
            category=CampaignCategory.DISASTER_RELIEF,
            goal_amount_usd=500000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            btc_wallet_address="bc1testaddress",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create donations with various attributes
        for i in range(5):
            donation = Donation(
                id=f"multi-donation-{i}",
                campaign_id=campaign.id,
                chain="eth" if i % 2 == 0 else "btc",
                tx_hash=f"tx{i}hash",
                amount_smallest_unit=1000000000 * (i + 1),
                from_address=f"address{i}" if i % 2 == 0 else None,  # Test optional field
                block_number=12345 + i if i % 3 == 0 else None,  # Test optional field
                confirmed_at=datetime.now(timezone.utc) - timedelta(hours=i),
            )
            test_db.add(donation)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{campaign.id}/donations")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["donations"]) == 5
        
        # Verify response structure
        for donation in data["donations"]:
            assert "id" in donation
            assert "chain" in donation
            assert "tx_hash" in donation
            assert "amount_smallest_unit" in donation
            assert "confirmed_at" in donation


@pytest.mark.asyncio
class TestRefreshBalance:
    """Tests for refresh_campaign_balance endpoint."""

    async def test_refresh_balance_updates_usd_cents(
        self, test_client: AsyncClient, test_db, test_creator, test_creator_token
    ):
        """Should update current_total_usd_cents when refreshing balance."""
        from unittest.mock import AsyncMock, patch

        campaign = Campaign(
            id="refresh-balance-campaign",
            title="Refresh Balance Test",
            description="Testing refresh balance",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()

        with patch(
            "app.api.routes.campaigns.BalanceTracker"
        ) as mock_bt_cls, patch(
            "app.api.routes.campaigns.PriceService"
        ) as mock_ps_cls:
            mock_tracker = AsyncMock()
            async def fake_update(cid):
                # Simulate balance update
                from sqlalchemy import select
                result = await test_db.execute(
                    select(Campaign).where(Campaign.id == cid)
                )
                c = result.scalar_one_or_none()
                if c:
                    c.current_eth_wei = 1000000000000000000  # 1 ETH
                    await test_db.commit()
            mock_tracker.update_campaign_balances = fake_update
            mock_bt_cls.return_value = mock_tracker

            mock_price_service = AsyncMock()
            mock_price_service.get_prices = AsyncMock(
                return_value={
                    "btc": 95000.0,
                    "eth": 2700.0,
                    "sol": 200.0,
                    "usdc_base": 1.0,
                }
            )
            mock_ps_cls.return_value = mock_price_service

            response = await test_client.post(
                f"/api/campaigns/{campaign.id}/refresh-balance",
                headers={"Authorization": f"Bearer {test_creator_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "current_total_usd_cents" in data
        assert data["current_total_usd_cents"] == 270000  # 1 ETH * 2700 = $2700 = 270000 cents
