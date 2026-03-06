"""Integration tests for campaign donation_count and donor_count."""
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient

from app.db.models import Campaign, CampaignCategory, CampaignStatus, Creator, Donation


@pytest.fixture
async def test_campaign_with_donations(test_db, test_creator):
    """Create a campaign with donations for donor count tests."""
    campaign = Campaign(
        id="campaign-donations-id",
        title="Campaign With Donations",
        description="Test",
        category=CampaignCategory.MEDICAL,
        goal_amount_usd=100000,
        eth_wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        contact_email=test_creator.email,
        creator_id=test_creator.id,
        status=CampaignStatus.ACTIVE,
    )
    test_db.add(campaign)
    await test_db.commit()
    await test_db.refresh(campaign)

    # 3 donations from 2 unique addresses
    confirmed = datetime.now(timezone.utc)
    donations = [
        Donation(
            campaign_id=campaign.id,
            chain="eth",
            tx_hash=f"0xabc{i}",
            amount_smallest_unit=10**18,
            from_address="0x1111111111111111111111111111111111111111",
            confirmed_at=confirmed,
        )
        for i in range(2)
    ]
    donations.append(
        Donation(
            campaign_id=campaign.id,
            chain="eth",
            tx_hash="0xabc2",
            amount_smallest_unit=10**18,
            from_address="0x2222222222222222222222222222222222222222",
            confirmed_at=confirmed,
        )
    )
    # Fix: 3 unique tx_hashes
    donations[0].tx_hash = "0xabc0"
    donations[1].tx_hash = "0xabc1"
    donations[2].tx_hash = "0xabc2"
    for d in donations:
        test_db.add(d)
    await test_db.commit()
    return campaign


@pytest.mark.asyncio
class TestCampaignDonorCount:
    """Tests for donation_count and donor_count in campaign responses."""

    async def test_get_campaign_returns_zero_counts_when_no_donations(
        self, test_client: AsyncClient, test_campaign
    ):
        """GET /api/campaigns/{id} returns donation_count: 0, donor_count: 0 when no donations."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["donation_count"] == 0
        assert data["donor_count"] == 0

    async def test_get_campaign_returns_correct_counts_with_donations(
        self, test_client: AsyncClient, test_campaign_with_donations
    ):
        """GET /api/campaigns/{id} returns correct donation_count and donor_count."""
        campaign = test_campaign_with_donations
        response = await test_client.get(f"/api/campaigns/{campaign.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["donation_count"] == 3
        assert data["donor_count"] == 2

    async def test_list_campaigns_includes_donation_and_donor_counts(
        self, test_client: AsyncClient, test_campaign, test_campaign_with_donations
    ):
        """GET /api/campaigns includes donation_count and donor_count in each campaign."""
        response = await test_client.get("/api/campaigns?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) >= 2

        # Campaign with no donations
        no_donations = next(c for c in data["campaigns"] if c["id"] == test_campaign.id)
        assert no_donations["donation_count"] == 0
        assert no_donations["donor_count"] == 0

        # Campaign with donations
        with_donations = next(
            c for c in data["campaigns"] if c["id"] == test_campaign_with_donations.id
        )
        assert with_donations["donation_count"] == 3
        assert with_donations["donor_count"] == 2
