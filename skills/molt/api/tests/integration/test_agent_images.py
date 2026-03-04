"""Integration tests for agent avatar upload and serving."""
import io
import pytest
from httpx import AsyncClient

from app.db.models import Agent


def _create_test_image(content: bytes = b"fake image content") -> io.BytesIO:
    """Create a fake image file for testing."""
    return io.BytesIO(content)


@pytest.mark.asyncio
class TestAgentAvatarUpload:
    """Tests for POST /api/agents/me/avatar."""

    async def test_upload_avatar_returns_200_with_updated_agent(
        self, test_client: AsyncClient, test_agent
    ):
        """Should upload avatar and return updated agent."""
        agent, api_key = test_agent

        response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(), "image/jpeg")},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"] is not None
        assert "avatar" in data["avatar_url"] or agent.id in data["avatar_url"]

    async def test_upload_avatar_rejects_non_image(self, test_client: AsyncClient, test_agent):
        """Should reject non-image files."""
        _, api_key = test_agent

        response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("file.txt", io.BytesIO(b"not an image"), "text/plain")},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 400
        assert "image" in response.json()["detail"].lower() or "jpg" in response.json()["detail"].lower() or "png" in response.json()["detail"].lower()

    async def test_upload_avatar_rejects_over_2mb(self, test_client: AsyncClient, test_agent):
        """Should reject files over 2MB."""
        _, api_key = test_agent
        large_content = b"x" * (2 * 1024 * 1024 + 1)

        response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(large_content), "image/jpeg")},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 400
        assert "2" in response.json()["detail"] or "size" in response.json()["detail"].lower()

    async def test_upload_avatar_requires_authentication(self, test_client: AsyncClient):
        """Should return 401 without API key."""
        response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(), "image/jpeg")},
        )

        assert response.status_code == 401

    async def test_upload_replaces_old_avatar(
        self, test_client: AsyncClient, test_agent, test_db
    ):
        """Should replace existing avatar when uploading new one."""
        agent, api_key = test_agent
        agent.avatar_url = "https://old.com/avatar.png"
        test_db.add(agent)
        await test_db.commit()
        await test_db.refresh(agent)

        response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(), "image/jpeg")},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert "old.com" not in (data["avatar_url"] or "")
        assert data["avatar_url"] is not None

    async def test_avatar_url_in_profile_response(
        self, test_client: AsyncClient, test_agent
    ):
        """Should include avatar URL in agent profile after upload."""
        agent, api_key = test_agent

        await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(), "image/jpeg")},
            headers={"X-Agent-API-Key": api_key},
        )

        profile_response = await test_client.get(f"/api/agents/{agent.name}")
        assert profile_response.status_code == 200
        data = profile_response.json()
        assert data["avatar_url"] is not None


@pytest.mark.asyncio
class TestAgentAvatarServe:
    """Tests for GET /api/uploads/agents/{agent_id}/{filename}."""

    async def test_serve_avatar_returns_file(
        self, test_client: AsyncClient, test_agent
    ):
        """Should return the uploaded avatar file."""
        agent, api_key = test_agent

        upload_response = await test_client.post(
            "/api/agents/me/avatar",
            files={"avatar": ("avatar.jpg", _create_test_image(b"image bytes"), "image/jpeg")},
            headers={"X-Agent-API-Key": api_key},
        )
        assert upload_response.status_code == 200

        avatar_url = upload_response.json()["avatar_url"]
        # Extract path: /api/uploads/agents/{id}/filename
        # Or full URL - we need to request it
        path = avatar_url.replace("http://test", "") if avatar_url.startswith("http") else avatar_url
        if not path.startswith("/"):
            path = "/" + path

        serve_response = await test_client.get(path)
        assert serve_response.status_code == 200
        assert serve_response.content == b"image bytes"
