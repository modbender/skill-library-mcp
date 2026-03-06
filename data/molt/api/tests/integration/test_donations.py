"""Integration tests for donations endpoint."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone

from app.db.models import Donation


@pytest.mark.asyncio
class TestListDonations:
    """Tests for GET /api/campaigns/{id}/donations."""
    
    async def test_list_donations(self, test_client: AsyncClient, test_campaign, test_db):
        """Should list donations for campaign."""
        # Create donations
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
        test_db.add(donation1)
        test_db.add(donation2)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/donations")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["donations"]) == 2
        assert data["total"] == 2
    
    async def test_list_donations_filter_by_chain(self, test_client: AsyncClient, test_campaign, test_db):
        """Should filter donations by chain."""
        # Create donations
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
        test_db.add(donation1)
        test_db.add(donation2)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/donations?chain=btc")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["donations"]) == 1
        assert data["donations"][0]["chain"] == "btc"
    
    async def test_list_donations_pagination(self, test_client: AsyncClient, test_campaign, test_db):
        """Should paginate donations."""
        # Create multiple donations
        for i in range(25):
            donation = Donation(
                campaign_id=test_campaign.id,
                chain="btc",
                tx_hash=f"tx{i}",
                amount_smallest_unit=1000000,
                confirmed_at=datetime.now(timezone.utc),
            )
            test_db.add(donation)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/donations?page=1&per_page=20")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["donations"]) == 20
        assert data["total"] == 25
    
    async def test_list_donations_campaign_not_found(self, test_client: AsyncClient):
        """Should return 404 for nonexistent campaign."""
        response = await test_client.get("/api/campaigns/nonexistent/donations")
        
        assert response.status_code == 404
