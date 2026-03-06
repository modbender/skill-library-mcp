"""Integration tests for main app."""
import pytest
import os
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMainApp:
    """Tests for main app endpoints."""
    
    async def test_root_endpoint(self, test_client: AsyncClient):
        """Should return API info."""
        response = await test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    async def test_health_endpoint(self, test_client: AsyncClient):
        """Should return health status."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
