"""Integration tests for campaign KYC badge (is_creator_verified)."""
import pytest
from httpx import AsyncClient

from app.db.models import Creator, Campaign, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestCampaignKYCBadge:
    """Tests for is_creator_verified in campaign responses."""

    async def test_get_campaign_returns_is_creator_verified_true_when_kyc_approved(
        self, test_client: AsyncClient, test_campaign, test_creator
    ):
        """GET /api/campaigns/{id} returns is_creator_verified: true when creator has kyc_status approved."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_creator_verified"] is True
        assert test_creator.kyc_status == "approved"

    async def test_get_campaign_returns_is_creator_verified_false_when_kyc_none(
        self, test_client: AsyncClient, test_db
    ):
        """GET /api/campaigns/{id} returns is_creator_verified: false when creator has kyc_status none."""
        creator = Creator(
            id="creator-kyc-none-id",
            email="none@example.com",
            kyc_status="none",
            kyc_attempt_count=0,
        )
        test_db.add(creator)
        await test_db.commit()
        await test_db.refresh(creator)

        campaign = Campaign(
            id="campaign-kyc-none-id",
            title="No KYC Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=creator.email,
            creator_id=creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()

        response = await test_client.get(f"/api/campaigns/{campaign.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_creator_verified"] is False

    async def test_get_campaign_returns_is_creator_verified_false_when_kyc_pending(
        self, test_client: AsyncClient, test_db
    ):
        """GET /api/campaigns/{id} returns is_creator_verified: false when creator has kyc_status pending."""
        creator = Creator(
            id="creator-kyc-pending-id",
            email="pending@example.com",
            kyc_status="pending",
            kyc_attempt_count=1,
        )
        test_db.add(creator)
        await test_db.commit()
        await test_db.refresh(creator)

        campaign = Campaign(
            id="campaign-kyc-pending-id",
            title="Pending KYC Campaign",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            contact_email=creator.email,
            creator_id=creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.commit()

        response = await test_client.get(f"/api/campaigns/{campaign.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_creator_verified"] is False

    async def test_list_campaigns_includes_is_creator_verified(
        self, test_client: AsyncClient, test_campaign, test_creator
    ):
        """GET /api/campaigns includes is_creator_verified in each campaign."""
        response = await test_client.get("/api/campaigns?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 1
        campaign = next(c for c in data["campaigns"] if c["id"] == test_campaign.id)
        assert "is_creator_verified" in campaign
        assert campaign["is_creator_verified"] is True
