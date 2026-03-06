"""Integration tests for creator_name and creator_story on campaigns."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCampaignCreatorInfo:
    """Tests for creator_name and creator_story fields."""

    async def test_create_with_creator_name_and_story(
        self, test_client: AsyncClient, test_creator, test_creator_token
    ):
        """Should create campaign with creator_name and creator_story."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test Campaign",
                "description": "Test description",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
                "creator_name": "Jane Doe",
                "creator_story": "I am raising funds for my medical expenses.",
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["creator_name"] == "Jane Doe"
        assert data["creator_story"] == "I am raising funds for my medical expenses."

    async def test_create_without_creator_info_optional(
        self, test_client: AsyncClient, test_creator, test_creator_token
    ):
        """Should create campaign without creator_name/story (optional)."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Minimal Campaign",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data.get("creator_name") is None or data.get("creator_name") == ""
        assert data.get("creator_story") is None or data.get("creator_story") == ""

    async def test_get_campaign_returns_creator_info(
        self, test_client: AsyncClient, test_creator, test_creator_token
    ):
        """Should return creator_name and creator_story in GET response."""
        create_resp = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Creator Info Campaign",
                "description": "Desc",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "contact_email": test_creator.email,
                "creator_name": "John Smith",
                "creator_story": "My story here.",
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        assert create_resp.status_code == 201
        campaign_id = create_resp.json()["id"]

        get_resp = await test_client.get(f"/api/campaigns/{campaign_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["creator_name"] == "John Smith"
        assert data["creator_story"] == "My story here."
