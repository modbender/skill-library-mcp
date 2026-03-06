"""Integration tests for security headers middleware."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Tests that security headers are present on all responses."""

    async def test_x_content_type_options(self, test_client: AsyncClient):
        """Every response includes X-Content-Type-Options: nosniff."""
        response = await test_client.get("/api/campaigns")
        assert response.status_code == 200
        assert response.headers.get("x-content-type-options") == "nosniff"

    async def test_x_frame_options(self, test_client: AsyncClient):
        """Every response includes X-Frame-Options: DENY."""
        response = await test_client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("x-frame-options") == "DENY"

    async def test_referrer_policy(self, test_client: AsyncClient):
        """Every response includes Referrer-Policy: strict-origin-when-cross-origin."""
        response = await test_client.get("/")
        assert response.status_code == 200
        assert (
            response.headers.get("referrer-policy")
            == "strict-origin-when-cross-origin"
        )

    async def test_x_xss_protection(self, test_client: AsyncClient):
        """Every response includes X-XSS-Protection: 0."""
        response = await test_client.get("/api/campaigns")
        assert response.status_code == 200
        assert response.headers.get("x-xss-protection") == "0"

    async def test_content_security_policy_present(
        self, test_client: AsyncClient
    ):
        """Every response includes Content-Security-Policy header."""
        response = await test_client.get("/api/campaigns")
        assert response.status_code == 200
        csp = response.headers.get("content-security-policy")
        assert csp is not None
        assert len(csp) > 0

    async def test_permissions_policy_present(self, test_client: AsyncClient):
        """Every response includes Permissions-Policy header."""
        response = await test_client.get("/api/campaigns")
        assert response.status_code == 200
        pp = response.headers.get("permissions-policy")
        assert pp is not None
