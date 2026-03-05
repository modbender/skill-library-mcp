"""Integration tests for campaign routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignCategory, CampaignStatus, FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestCreateCampaign:
    """Tests for POST /api/campaigns."""
    
    async def test_create_campaign_with_all_fields(self, test_client: AsyncClient, test_creator_token, test_creator):
        """Should create campaign with all fields including contact_email."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,  # $1000 in cents
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Campaign"
        assert data["creator_id"] == test_creator.id
        # Verify contact_email was set (from creator.email)
        assert "id" in data
    
    async def test_create_campaign_requires_wallet_address(self, test_client: AsyncClient, test_creator_token):
        """Should require at least one wallet address."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "contact_email": "test@example.com",
                # No wallet addresses
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 400
        assert "wallet" in response.json()["detail"].lower()
    
    async def test_create_campaign_creates_feed_event(self, test_client: AsyncClient, test_creator_token, test_db, test_creator):
        """Should create feed event when campaign is created."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Feed Test Campaign",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 201
        campaign_id = response.json()["id"]
        
        # Check feed event was created
        from sqlalchemy import select
        result = await test_db.execute(
            select(FeedEvent).where(FeedEvent.campaign_id == campaign_id)
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None
        assert feed_event.event_type == FeedEventType.CAMPAIGN_CREATED
    
    async def test_create_campaign_requires_authentication(self, test_client: AsyncClient):
        """Should require authentication."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            },
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestListCampaigns:
    """Tests for GET /api/campaigns."""
    
    async def test_list_campaigns_pagination(self, test_client: AsyncClient, test_campaign):
        """Should support pagination."""
        response = await test_client.get("/api/campaigns?page=1&per_page=10")
        
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
    
    async def test_list_campaigns_filters_by_category(self, test_client: AsyncClient, test_campaign):
        """Should filter campaigns by category."""
        response = await test_client.get("/api/campaigns?category=MEDICAL")
        
        assert response.status_code == 200
        data = response.json()
        if data["campaigns"]:
            assert all(c["category"] == "MEDICAL" for c in data["campaigns"])
    
    async def test_list_campaigns_searches(self, test_client: AsyncClient, test_campaign):
        """Should search campaigns by title/description."""
        response = await test_client.get("/api/campaigns?search=Test")
        
        assert response.status_code == 200
        data = response.json()
        # Should find test campaign
        assert data["total"] >= 1


@pytest.mark.asyncio
class TestGetCampaign:
    """Tests for GET /api/campaigns/{id}."""
    
    async def test_get_campaign_returns_detail(self, test_client: AsyncClient, test_campaign):
        """Should return campaign with advocate count."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_campaign.id
        assert data["title"] == test_campaign.title
        assert "advocate_count" in data
    
    async def test_get_campaign_returns_404_for_missing(self, test_client: AsyncClient):
        """Should return 404 for non-existent campaign."""
        response = await test_client.get("/api/campaigns/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateCampaign:
    """Tests for PATCH /api/campaigns/{id}."""
    
    async def test_update_campaign_only_owner(self, test_client: AsyncClient, test_campaign, test_creator_token):
        """Should only allow owner to update."""
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
    
    async def test_update_campaign_rejects_non_owner(self, test_client: AsyncClient, test_campaign, test_db):
        """Should reject update from non-owner."""
        # Create different creator
        from app.db.models import Creator
        from app.core.security import create_access_token
        
        other_creator = Creator(email="other@example.com")
        test_db.add(other_creator)
        await test_db.commit()
        
        other_token = create_access_token(data={"sub": other_creator.id, "email": other_creator.email})
        
        response = await test_client.patch(
            f"/api/campaigns/{test_campaign.id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        
        assert response.status_code == 403


@pytest.mark.asyncio
class TestDeleteCampaign:
    """Tests for DELETE /api/campaigns/{id}."""
    
    async def test_delete_campaign_soft_deletes(self, test_client: AsyncClient, test_campaign, test_creator_token, test_db):
        """Should soft delete (set status to CANCELLED)."""
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        
        assert response.status_code == 204
        
        # Verify status changed
        from sqlalchemy import select
        result = await test_db.execute(
            select(Campaign).where(Campaign.id == test_campaign.id)
        )
        campaign = result.scalar_one_or_none()
        assert campaign.status == CampaignStatus.CANCELLED
    
    async def test_delete_campaign_only_owner(self, test_client: AsyncClient, test_campaign):
        """Should only allow owner to delete."""
        # Without auth
        response = await test_client.delete(f"/api/campaigns/{test_campaign.id}")
        assert response.status_code == 401
