"""Integration tests for rate limiting on agent registration."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAgentRegistrationRateLimit:
    """Tests for POST /api/agents/register rate limiting."""

    async def test_returns_429_after_limit_exceeded(
        self, test_client: AsyncClient
    ):
        """POST /api/agents/register returns 429 after N requests from same IP."""
        # Limit is 5 per hour (config). Make 6 requests with unique names.
        for i in range(6):
            response = await test_client.post(
                "/api/agents/register",
                json={
                    "name": f"rate-limit-agent-{i}",
                    "description": "Test agent",
                },
            )
            if i < 5:
                assert response.status_code == 201, (
                    f"Request {i + 1} should succeed, got {response.status_code}"
                )
            else:
                assert response.status_code == 429, (
                    f"Request 6 should be rate limited, got {response.status_code}"
                )
                data = response.json()
                assert "rate" in data["detail"].lower() or "limit" in data["detail"].lower()

    async def test_different_ips_have_independent_limits(
        self, test_client: AsyncClient
    ):
        """Different IPs (via X-Forwarded-For) have independent rate limits."""
        # Make 5 requests from IP 1.1.1.1 - all succeed
        for i in range(5):
            response = await test_client.post(
                "/api/agents/register",
                json={"name": f"ip1-agent-{i}", "description": "Test"},
                headers={"X-Forwarded-For": "1.1.1.1"},
            )
            assert response.status_code == 201

        # 6th from 1.1.1.1 - rate limited
        response = await test_client.post(
            "/api/agents/register",
            json={"name": "ip1-agent-6", "description": "Test"},
            headers={"X-Forwarded-For": "1.1.1.1"},
        )
        assert response.status_code == 429

        # First request from 2.2.2.2 - should succeed (different IP)
        response = await test_client.post(
            "/api/agents/register",
            json={"name": "ip2-agent-0", "description": "Test"},
            headers={"X-Forwarded-For": "2.2.2.2"},
        )
        assert response.status_code == 201

    async def test_other_endpoints_not_rate_limited(
        self, test_client: AsyncClient
    ):
        """Other endpoints (e.g. GET /api/campaigns) are not rate limited."""
        for _ in range(20):
            response = await test_client.get("/api/campaigns")
            assert response.status_code == 200
