"""Unit tests for EmailService."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.email import EmailService


@pytest.mark.asyncio
class TestEmailService:
    """Tests for EmailService."""

    @pytest.fixture
    def service(self):
        return EmailService()

    async def test_send_magic_link_calls_resend_api(self, service):
        """Should call Resend API with correct payload."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"id": "msg_123"}'

        with (
            patch.object(service, "is_configured", return_value=True),
            patch("app.services.email.httpx.AsyncClient") as mock_client_cls,
        ):
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            await service.send_magic_link(
                to_email="user@example.com",
                token="abc123token",
                frontend_url="https://moltfundme.com",
            )

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            payload = call_kwargs.kwargs["json"]
            assert payload["to"] == ["user@example.com"]
            assert "abc123token" in payload["text"]
            assert "abc123token" in payload["html"]
            assert "https://moltfundme.com/auth/verify?token=abc123token" in payload["text"]

    async def test_send_magic_link_contains_html_and_plain_text(self, service):
        """Should include both HTML and plain text content in the payload."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with (
            patch.object(service, "is_configured", return_value=True),
            patch("app.services.email.httpx.AsyncClient") as mock_client_cls,
        ):
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            await service.send_magic_link(
                to_email="user@example.com",
                token="xyz789",
                frontend_url="https://app.example.com",
            )

            payload = mock_client.post.call_args.kwargs["json"]
            assert "html" in payload
            assert "text" in payload
            assert "xyz789" in payload["html"]
            assert "xyz789" in payload["text"]

    async def test_send_magic_link_graceful_failure_on_api_error(self, service):
        """Should log error but not raise when Resend API fails."""
        with (
            patch.object(service, "is_configured", return_value=True),
            patch(
                "app.services.email.httpx.AsyncClient",
                side_effect=Exception("Connection failed"),
            ),
            patch("app.services.email.logger") as mock_logger,
        ):
            await service.send_magic_link(
                to_email="user@example.com",
                token="abc123",
                frontend_url="https://moltfundme.com",
            )

            mock_logger.error.assert_called()

    async def test_send_magic_link_logs_on_non_200_response(self, service):
        """Should log error when Resend returns non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = '{"error": "invalid API key"}'

        with (
            patch.object(service, "is_configured", return_value=True),
            patch("app.services.email.httpx.AsyncClient") as mock_client_cls,
            patch("app.services.email.logger") as mock_logger,
        ):
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            await service.send_magic_link(
                to_email="user@example.com",
                token="abc123",
                frontend_url="https://moltfundme.com",
            )

            mock_logger.error.assert_called()

    def test_is_configured_returns_false_when_api_key_empty(self, service):
        """Should return False when Resend API key is empty."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.resend_api_key = ""

            result = service.is_configured()

        assert result is False

    def test_is_configured_returns_true_when_api_key_set(self, service):
        """Should return True when Resend API key is set."""
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.resend_api_key = "re_123456789"

            result = service.is_configured()

        assert result is True
