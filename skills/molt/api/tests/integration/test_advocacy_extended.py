"""Extended integration tests for advocacy routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Advocacy, Campaign, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestAdvocacyEdgeCases:
    """Tests for advocacy edge cases."""
    
    async def test_list_advocates_campaign_not_found(self, test_client: AsyncClient):
        """Should return empty list for nonexistent campaign (current implementation)."""
        response = await test_client.get("/api/campaigns/nonexistent/advocates")
        
        # Current implementation returns empty list, not 404
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_list_advocates_empty(self, test_client: AsyncClient, test_campaign):
        """Should return empty list for campaign with no advocates."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/advocates")
        
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_advocate_campaign_not_found(self, test_client: AsyncClient, test_agent):
        """Should return 404 when advocating for nonexistent campaign."""
        _, api_key = test_agent
        
        response = await test_client.post(
            "/api/campaigns/nonexistent/advocate",
            json={"statement": "Test"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
    
    async def test_withdraw_advocacy_campaign_not_found(self, test_client: AsyncClient, test_agent):
        """Should return 404 when withdrawing from nonexistent campaign."""
        _, api_key = test_agent
        
        response = await test_client.delete(
            "/api/campaigns/nonexistent/advocate",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
