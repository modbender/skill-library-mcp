"""Integration tests for human war room posts (POST /warroom/posts/human)."""
import pytest
from httpx import AsyncClient

from app.db.models import WarRoomPost


@pytest.mark.asyncio
class TestCreateHumanPost:
    """Tests for POST /api/campaigns/{id}/warroom/posts/human."""

    async def test_create_human_post_success(
        self,
        test_client: AsyncClient,
        test_campaign,
        test_creator,
        test_creator_token,
    ):
        """Should create human post with valid KYC-approved creator token."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/human",
            json={"content": "Human posting in the war room!"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Human posting in the war room!"
        assert data["author_type"] == "human"
        assert data["creator_id"] == test_creator.id
        assert data["agent_id"] is None
        assert data["author_name"] == "test"
        assert data["upvote_count"] == 0

    async def test_create_human_post_requires_kyc(
        self,
        test_client: AsyncClient,
        test_campaign,
        test_creator_no_kyc_token,
    ):
        """Should return 403 when creator has not completed KYC."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/human",
            json={"content": "Trying without KYC"},
            headers={"Authorization": f"Bearer {test_creator_no_kyc_token}"},
        )

        assert response.status_code == 403
        data = response.json()
        detail = data.get("detail", {})
        if isinstance(detail, dict):
            assert detail.get("code") == "KYC_REQUIRED"
        else:
            assert "kyc" in str(detail).lower()

    async def test_create_human_post_unauthenticated(
        self,
        test_client: AsyncClient,
        test_campaign,
    ):
        """Should return 401 when no token provided."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/human",
            json={"content": "Anonymous post"},
        )

        assert response.status_code == 401

    async def test_create_human_post_campaign_not_found(
        self,
        test_client: AsyncClient,
        test_creator_token,
    ):
        """Should return 404 for nonexistent campaign."""
        response = await test_client.post(
            "/api/campaigns/nonexistent/warroom/posts/human",
            json={"content": "Post to nowhere"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 404

    async def test_human_post_with_reply(
        self,
        test_client: AsyncClient,
        test_campaign,
        test_creator,
        test_creator_token,
        test_agent,
        test_db,
    ):
        """Should create human reply to another post."""
        agent, api_key = test_agent

        # Create agent post first
        agent_response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Agent's original post"},
            headers={"X-Agent-API-Key": api_key},
        )
        assert agent_response.status_code == 201
        parent_post = agent_response.json()

        # Human replies
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/human",
            json={
                "content": "Human reply to the agent",
                "parent_post_id": parent_post["id"],
            },
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Human reply to the agent"
        assert data["parent_post_id"] == parent_post["id"]
        assert data["author_type"] == "human"


@pytest.mark.asyncio
class TestGetWarroomShowsBothTypes:
    """Tests for GET warroom with mixed agent and human posts."""

    async def test_get_warroom_shows_human_and_agent_posts(
        self,
        test_client: AsyncClient,
        test_campaign,
        test_creator,
        test_creator_token,
        test_agent,
    ):
        """Should return both agent and human posts with correct author_type."""
        agent, api_key = test_agent

        # Create agent post
        agent_response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Agent says hello"},
            headers={"X-Agent-API-Key": api_key},
        )
        assert agent_response.status_code == 201

        # Create human post
        human_response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/human",
            json={"content": "Human says thanks!"},
            headers={"Authorization": f"Bearer {test_creator_token}"},
        )
        assert human_response.status_code == 201

        # Get all posts
        get_response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")
        assert get_response.status_code == 200
        posts = get_response.json()

        assert len(posts) == 2

        agent_post = next(p for p in posts if p["author_type"] == "agent")
        human_post = next(p for p in posts if p["author_type"] == "human")

        assert agent_post["content"] == "Agent says hello"
        assert agent_post["agent_id"] == agent.id
        assert agent_post["creator_id"] is None

        assert human_post["content"] == "Human says thanks!"
        assert human_post["creator_id"] == test_creator.id
        assert human_post["agent_id"] is None
        assert human_post["author_name"] == "test"
