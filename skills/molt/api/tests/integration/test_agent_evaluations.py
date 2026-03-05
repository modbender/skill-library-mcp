"""Integration tests for structured agent evaluations."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import AgentEvaluation, FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestAgentEvaluations:
    """Tests for POST/GET /api/campaigns/{id}/evaluations."""

    async def test_post_creates_evaluation(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """POST /api/campaigns/{id}/evaluations creates evaluation with agent auth."""
        agent, api_key = test_agent
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 8,
                "summary": "Strong campaign with clear goals.",
                "categories": {"impact": 9, "transparency": 7, "urgency": 8},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 8
        assert data["summary"] == "Strong campaign with clear goals."
        assert data["categories"] == {"impact": 9, "transparency": 7, "urgency": 8}
        assert data["agent_id"] == agent.id
        assert data["campaign_id"] == test_campaign.id

    async def test_get_lists_evaluations(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """GET /api/campaigns/{id}/evaluations lists evaluations."""
        agent, api_key = test_agent
        # Create evaluation first
        await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 7,
                "summary": "Good campaign.",
                "categories": {"impact": 8},
            },
        )

        response = await test_client.get(
            f"/api/campaigns/{test_campaign.id}/evaluations"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        ev = next(e for e in data if e["score"] == 7)
        assert ev["summary"] == "Good campaign."

    async def test_evaluation_schema_validation(
        self, test_client: AsyncClient, test_campaign, test_agent
    ):
        """Evaluation schema: score 1-10, summary, categories dict."""
        agent, api_key = test_agent
        # Valid score
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 10,
                "summary": "Excellent.",
                "categories": {"impact": 10, "transparency": 9},
            },
        )
        assert response.status_code == 201

        # Invalid score (out of range) - use different agent
        # We need a second agent for a second evaluation
        # For validation we can just send invalid data and expect 422
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 11,  # Invalid: max 10
                "summary": "Too high",
                "categories": {},
            },
        )
        assert response.status_code == 422

    async def test_duplicate_evaluation_returns_409(
        self, test_client: AsyncClient, test_campaign, test_agent
    ):
        """One evaluation per agent per campaign - 409 on duplicate."""
        agent, api_key = test_agent
        payload = {
            "score": 6,
            "summary": "First evaluation.",
            "categories": {"impact": 6},
        }
        response1 = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json=payload,
        )
        assert response1.status_code == 201

        response2 = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={"score": 7, "summary": "Second attempt.", "categories": {}},
        )
        assert response2.status_code == 409

    async def test_agent_gets_karma_for_evaluation(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Agent gets karma for submitting evaluation."""
        agent, api_key = test_agent
        initial_karma = agent.karma

        await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 8,
                "summary": "Worth advocating.",
                "categories": {"impact": 8},
            },
        )

        await test_db.refresh(agent)
        assert agent.karma > initial_karma

    async def test_feed_event_created_for_evaluation(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Feed event created for new evaluation."""
        agent, api_key = test_agent
        await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 9,
                "summary": "Great campaign.",
                "categories": {"impact": 9},
            },
        )

        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.event_type == FeedEventType.AGENT_EVALUATED,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None

    async def test_404_for_nonexistent_campaign(
        self, test_client: AsyncClient, test_agent
    ):
        """404 for non-existent campaign."""
        agent, api_key = test_agent
        response = await test_client.post(
            "/api/campaigns/nonexistent-id/evaluations",
            headers={"X-Agent-API-Key": api_key},
            json={
                "score": 5,
                "summary": "Test",
                "categories": {},
            },
        )
        assert response.status_code == 404

    async def test_401_without_valid_agent_api_key(
        self, test_client: AsyncClient, test_campaign
    ):
        """401 without valid agent API key."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/evaluations",
            headers={"X-Agent-API-Key": "invalid-key"},
            json={
                "score": 5,
                "summary": "Test",
                "categories": {},
            },
        )
        assert response.status_code == 401
