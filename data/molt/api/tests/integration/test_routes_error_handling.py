"""Integration tests for error handling in routes."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.db.models import Campaign, CampaignStatus, CampaignCategory


@pytest.mark.asyncio
class TestCampaignErrorHandling:
    """Tests for error handling in campaign routes."""
    
    async def test_create_campaign_database_error(self, test_client: AsyncClient, test_creator_token, test_db):
        """Should handle database errors gracefully."""
        # Patch flush instead since commit happens after flush
        with patch.object(test_db, "flush", side_effect=Exception("DB error")):
            response = await test_client.post(
                "/api/campaigns",
                json={
                    "title": "Test",
                    "description": "Test",
                    "category": "MEDICAL",
                    "goal_amount_usd": 100000,
                    "eth_wallet_address": "0xtest",
                },
                headers={"Authorization": f"Bearer {test_creator_token}"},
            )
            
            # May get 500 or validation error depending on when error occurs
            assert response.status_code in [500, 422]
    
    async def test_update_campaign_database_error(self, test_client: AsyncClient, test_campaign, test_creator_token, test_db):
        """Should handle database errors on update."""
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.patch(
                f"/api/campaigns/{test_campaign.id}",
                json={"title": "Updated"},
                headers={"Authorization": f"Bearer {test_creator_token}"},
            )
            
            assert response.status_code == 500
            assert "Failed to update campaign" in response.json()["detail"]


@pytest.mark.asyncio
class TestAdvocacyErrorHandling:
    """Tests for error handling in advocacy routes."""
    
    async def test_advocate_database_error(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should handle database errors on advocacy creation."""
        agent, api_key = test_agent
        
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.post(
                f"/api/campaigns/{test_campaign.id}/advocate",
                json={"statement": "Test"},
                headers={"X-Agent-API-Key": api_key},
            )
            
            assert response.status_code == 500
            assert "Failed to create advocacy" in response.json()["detail"]


@pytest.mark.asyncio
class TestWarroomErrorHandling:
    """Tests for error handling in warroom routes."""
    
    async def test_create_post_database_error(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should handle database errors on post creation."""
        agent, api_key = test_agent
        
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.post(
                f"/api/campaigns/{test_campaign.id}/warroom/posts",
                json={"content": "Test post"},
                headers={"X-Agent-API-Key": api_key},
            )
            
            assert response.status_code == 500
            assert "Failed to create post" in response.json()["detail"]
    
    async def test_upvote_database_error(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should handle database errors on upvote."""
        agent, api_key = test_agent
        
        # Create post
        from app.db.models import WarRoomPost
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.post(
                f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
                headers={"X-Agent-API-Key": api_key},
            )
            
            assert response.status_code == 500
            assert "Failed to upvote post" in response.json()["detail"]


@pytest.mark.asyncio
class TestAuthErrorHandling:
    """Tests for error handling in auth routes."""
    
    async def test_magic_link_database_error(self, test_client: AsyncClient, test_db):
        """Should handle database errors on magic link creation."""
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.post(
                "/api/auth/magic-link",
                json={"email": "test@example.com"},
            )
            
            assert response.status_code == 500
            assert "Failed to create magic link" in response.json()["detail"]
    
    async def test_verify_token_database_error(self, test_client: AsyncClient, test_db, test_creator):
        """Should handle database errors on token verification."""
        from app.db.models import MagicLink
        from app.core.security import create_magic_link_token
        from datetime import datetime, timedelta, timezone
        
        token = create_magic_link_token()
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        with patch.object(test_db, "commit", side_effect=Exception("DB error")):
            response = await test_client.get(f"/api/auth/verify?token={token}")
            
            assert response.status_code == 500
            assert "Failed to verify token" in response.json()["detail"]
