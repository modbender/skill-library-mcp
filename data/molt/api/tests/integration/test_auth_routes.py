"""Integration tests for auth routes."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

from app.db.models import Creator, MagicLink
from app.core.security import create_magic_link_token


@pytest.mark.asyncio
class TestMagicLink:
    """Tests for POST /api/auth/magic-link."""
    
    async def test_request_magic_link(self, test_client: AsyncClient, test_db):
        """Should create magic link (dev mode: token in response when SMTP not configured)."""
        with patch("app.api.routes.auth.email_service") as mock_email:
            mock_email.is_configured.return_value = False  # Dev mode
            response = await test_client.post(
                "/api/auth/magic-link",
                json={"email": "newuser@example.com"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Token:" in data["message"] or "token" in data["message"].lower()
        
        # Verify magic link was created
        from sqlalchemy import select
        result = await test_db.execute(select(MagicLink).where(MagicLink.email == "newuser@example.com"))
        magic_link = result.scalar_one_or_none()
        assert magic_link is not None
        # Extract token from message (format: "Token: <token> (dev only...)")
        token_in_message = data["message"].split("Token:")[1].split()[0] if "Token:" in data["message"] else None
        if token_in_message:
            assert magic_link.token == token_in_message
    
    async def test_request_magic_link_creates_creator(self, test_client: AsyncClient, test_db):
        """Should create creator if doesn't exist."""
        response = await test_client.post(
            "/api/auth/magic-link",
            json={"email": "newcreator@example.com"},
        )
        
        assert response.status_code == 200
        
        # Verify creator was created
        from sqlalchemy import select
        result = await test_db.execute(select(Creator).where(Creator.email == "newcreator@example.com"))
        creator = result.scalar_one_or_none()
        assert creator is not None

    async def test_request_magic_link_returns_token_when_smtp_not_configured(
        self, test_client: AsyncClient
    ):
        """When SMTP not configured (dev mode), should return token in message."""
        with patch("app.api.routes.auth.email_service") as mock_email:
            mock_email.is_configured.return_value = False

            response = await test_client.post(
                "/api/auth/magic-link",
                json={"email": "dev@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Token:" in data["message"] or "token" in data["message"].lower()

    async def test_request_magic_link_sends_email_when_smtp_configured(
        self, test_client: AsyncClient
    ):
        """When SMTP configured, should send email and return generic success message."""
        with patch("app.api.routes.auth.email_service") as mock_email:
            mock_email.is_configured.return_value = True
            mock_email.send_magic_link = AsyncMock()

            response = await test_client.post(
                "/api/auth/magic-link",
                json={"email": "prod@example.com"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "Token:" not in data["message"]
            assert "email" in data["message"].lower() or "check" in data["message"].lower()
            mock_email.send_magic_link.assert_called_once()


@pytest.mark.asyncio
class TestVerifyToken:
    """Tests for GET /api/auth/verify."""
    
    async def test_verify_valid_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should verify valid token and return JWT."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["access_token"] is not None
    
    async def test_verify_invalid_token(self, test_client: AsyncClient):
        """Should return 401 for invalid token."""
        response = await test_client.get("/api/auth/verify?token=invalid-token")
        
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    async def test_verify_expired_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 401 for expired token."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    async def test_verify_used_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 401 for already used token."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
            used_at=datetime.now(timezone.utc),
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    """Tests for POST /api/auth/logout."""
    
    async def test_logout(self, test_client: AsyncClient):
        """Should return success."""
        response = await test_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
