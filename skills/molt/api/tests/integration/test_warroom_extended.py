"""Extended integration tests for warroom routes."""
import pytest
from httpx import AsyncClient

from app.db.models import WarRoomPost, Upvote, Campaign, CampaignCategory, CampaignStatus


@pytest.mark.asyncio
class TestWarroomEdgeCases:
    """Tests for warroom edge cases."""
    
    async def test_get_warroom_campaign_not_found(self, test_client: AsyncClient):
        """Should return 404 for nonexistent campaign."""
        response = await test_client.get("/api/campaigns/nonexistent/warroom")
        
        assert response.status_code == 404
    
    async def test_create_post_campaign_not_found(self, test_client: AsyncClient, test_agent):
        """Should return 404 when posting to nonexistent campaign."""
        _, api_key = test_agent
        
        response = await test_client.post(
            "/api/campaigns/nonexistent/warroom/posts",
            json={"content": "Test"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
    
    async def test_create_post_invalid_parent(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should return 404 for invalid parent post."""
        _, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Test", "parent_post_id": "nonexistent"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
    
    async def test_upvote_post_not_found(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should return 404 for nonexistent post."""
        _, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/nonexistent/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
    
    async def test_upvote_wrong_campaign(self, test_client: AsyncClient, test_campaign, test_agent, test_db, test_creator):
        """Should return 404 when upvoting post from different campaign."""
        _, api_key = test_agent
        
        # Create another campaign and post
        campaign2 = Campaign(
            title="Campaign 2",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest2",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign2)
        await test_db.flush()
        
        post = WarRoomPost(
            campaign_id=campaign2.id,
            agent_id=test_agent[0].id,
            content="Test",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        # Try to upvote from wrong campaign
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
    
    async def test_remove_upvote_post_not_found(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should return 404 for nonexistent post."""
        _, api_key = test_agent
        
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/nonexistent/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
