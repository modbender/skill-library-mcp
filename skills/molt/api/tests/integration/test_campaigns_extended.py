"""Extended integration tests for campaign routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Campaign, CampaignStatus, CampaignCategory


@pytest.mark.asyncio
class TestCampaignListEdgeCases:
    """Tests for campaign list edge cases."""
    
    async def test_list_campaigns_empty_result(self, test_client: AsyncClient):
        """Should handle empty campaign list."""
        response = await test_client.get("/api/campaigns?category=EDUCATION")
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns"] == []
        assert data["total"] == 0
    
    async def test_list_campaigns_invalid_page(self, test_client: AsyncClient):
        """Should handle invalid page number."""
        response = await test_client.get("/api/campaigns?page=0")
        
        # Should be validated by FastAPI Query(ge=1)
        assert response.status_code == 422
    
    async def test_list_campaigns_large_per_page(self, test_client: AsyncClient):
        """Should limit per_page to max."""
        response = await test_client.get("/api/campaigns?per_page=200")
        
        # Should be validated by FastAPI Query(le=100)
        assert response.status_code == 422
    
    async def test_list_campaigns_search_no_results(self, test_client: AsyncClient):
        """Should return empty results for search with no matches."""
        response = await test_client.get("/api/campaigns?search=nonexistentcampaignxyz")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) == 0
