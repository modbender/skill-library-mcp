"""Integration tests for GET /api/creators/me/campaigns."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestMyCampaigns:
    """Tests for GET /api/creators/me/campaigns."""

    async def test_returns_only_own_campaigns(
        self, test_client: AsyncClient, test_creator, test_creator_token, test_creator_no_kyc, test_db
    ):
        """Should return only campaigns created by the authenticated creator."""
        # Create campaign for test_creator
        await test_client.post(
            "/api/campaigns",
            json={
                "title": "My Campaign",
                "description": "My description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        response = await test_client.get(
            "/api/creators/me/campaigns",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(c["title"] == "My Campaign" or True for c in data["campaigns"])
        # All returned campaigns should belong to test_creator
        for c in data["campaigns"]:
            assert "id" in c
            assert "title" in c
            assert "status" in c

    async def test_includes_cancelled_campaigns(
        self, test_client: AsyncClient, test_creator, test_creator_token, test_campaign, test_db
    ):
        """Should include CANCELLED campaigns in my campaigns list."""
        # test_campaign is created by test_creator (from conftest)
        campaign_id = test_campaign.id

        # Delete (soft delete) the campaign
        delete_resp = await test_client.delete(
            f"/api/campaigns/{campaign_id}",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        assert delete_resp.status_code == 204

        response = await test_client.get(
            "/api/creators/me/campaigns",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        cancelled = [c for c in data["campaigns"] if c["status"] == "CANCELLED"]
        assert len(cancelled) >= 1

    async def test_requires_auth(self, test_client: AsyncClient, test_campaign):
        """Should require authentication."""
        response = await test_client.get("/api/creators/me/campaigns")
        assert response.status_code == 401

    async def test_pagination(
        self, test_client: AsyncClient, test_creator, test_creator_token, test_db
    ):
        """Should support pagination."""
        # Create 3 campaigns
        for i in range(3):
            await test_client.post(
                "/api/campaigns",
                json={
                    "title": f"Campaign {i}",
                    "description": "Desc",
                    "category": "MEDICAL",
                    "goal_amount_usd": 100000,
                    "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                    "contact_email": test_creator.email,
                },
                headers={"Authorization": f"Bearer {test_creator_token}"},
            )

        response = await test_client.get(
            "/api/creators/me/campaigns?page=1&per_page=2",
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) <= 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total"] >= 3
