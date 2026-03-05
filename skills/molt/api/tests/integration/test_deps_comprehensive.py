"""Comprehensive integration tests for dependency injection."""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, create_api_key, hash_api_key
from app.db.models import Agent, Creator


@pytest.mark.asyncio
class TestDependencyInjection:
    """Comprehensive tests for dependency injection."""
    
    async def test_get_current_agent_invalid_key_format(self, test_client: AsyncClient):
        """Should handle invalid API key format."""
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Test"},
            headers={"X-Agent-API-Key": "invalid-format-key"},
        )
        
        assert response.status_code == 401
    
    async def test_get_current_agent_wrong_key(self, test_client: AsyncClient, test_agent):
        """Should reject wrong API key."""
        _, correct_key = test_agent
        wrong_key = create_api_key()  # Different key
        
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Test"},
            headers={"X-Agent-API-Key": wrong_key},
        )
        
        assert response.status_code == 401
    
    async def test_get_required_agent_missing_header(self, test_client: AsyncClient):
        """Should return 401 without API key header."""
        response = await test_client.post(
            "/api/campaigns/test-id/advocate",
            json={},
        )
        
        assert response.status_code == 401
    
    async def test_get_current_creator_invalid_token(self, test_client: AsyncClient):
        """Should handle invalid JWT token."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0xtest",
            },
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        
        assert response.status_code == 401
    
    async def test_get_current_creator_expired_token(self, test_client: AsyncClient):
        """Should handle expired JWT token."""
        from datetime import timedelta
        from app.core.security import create_access_token
        
        # Create expired token
        expired_token = create_access_token(
            data={"sub": "test-id", "email": "test@example.com"},
            expires_delta=timedelta(seconds=-1)  # Expired
        )
        
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0xtest",
            },
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == 401
    
    async def test_get_required_creator_missing_token(self, test_client: AsyncClient):
        """Should return 401 without token."""
        response = await test_client.post(
            "/api/campaigns",
            json={
                "title": "Test",
                "description": "Test",
                "category": "MEDICAL",
                "goal_amount_usd": 100000,
                "eth_wallet_address": "0xtest",
            },
        )
        
        assert response.status_code == 401
