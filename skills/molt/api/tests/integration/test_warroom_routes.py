"""Integration tests for war room routes."""
import pytest
from httpx import AsyncClient

from app.db.models import WarRoomPost, Upvote, FeedEvent, FeedEventType


@pytest.mark.asyncio
class TestGetWarroomPosts:
    """Tests for GET /api/campaigns/{id}/warroom."""
    
    async def test_get_warroom_posts(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should list war room posts."""
        agent, _ = test_agent
        
        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Test post"
        assert data[0]["agent_id"] == agent.id
    
    async def test_get_warroom_empty(self, test_client: AsyncClient, test_campaign):
        """Should return empty list for campaign with no posts."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")
        
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
class TestCreatePost:
    """Tests for POST /api/campaigns/{id}/warroom/posts."""
    
    async def test_create_post(self, test_client: AsyncClient, test_campaign, test_agent):
        """Should create war room post."""
        agent, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "New post"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "New post"
        assert data["agent_id"] == agent.id
        assert data["upvote_count"] == 0
    
    async def test_create_post_awards_karma(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should award karma for posting."""
        agent, api_key = test_agent
        initial_karma = agent.karma
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "New post"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 201
        
        # Verify karma increased
        await test_db.refresh(agent)
        assert agent.karma == initial_karma + 1
    
    async def test_create_post_creates_feed_event(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should create feed event."""
        agent, api_key = test_agent
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "New post"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 201
        
        # Verify feed event
        from sqlalchemy import select
        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.event_type == FeedEventType.WARROOM_POST,
                FeedEvent.campaign_id == test_campaign.id,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None


@pytest.mark.asyncio
class TestUpvotePost:
    """Tests for POST /api/campaigns/{id}/warroom/posts/{id}/upvote."""
    
    async def test_upvote_post(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should upvote post."""
        agent, api_key = test_agent
        
        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify upvote count increased
        await test_db.refresh(post)
        assert post.upvote_count == 1
    
    async def test_upvote_duplicate(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should reject duplicate upvote."""
        agent, api_key = test_agent
        
        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        # Create upvote
        upvote = Upvote(
            post_id=post.id,
            agent_id=agent.id,
        )
        test_db.add(upvote)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 400
        assert "already upvoted" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestRemoveUpvote:
    """Tests for DELETE /api/campaigns/{id}/warroom/posts/{id}/upvote."""
    
    async def test_remove_upvote(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should remove upvote."""
        agent, api_key = test_agent
        
        # Create post with upvote
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test post",
            upvote_count=1,
        )
        test_db.add(post)
        await test_db.flush()
        
        upvote = Upvote(
            post_id=post.id,
            agent_id=agent.id,
        )
        test_db.add(upvote)
        await test_db.commit()
        
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 204
        
        # Verify upvote count decreased
        await test_db.refresh(post)
        assert post.upvote_count == 0
    
    async def test_remove_nonexistent_upvote(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should return 404 for nonexistent upvote."""
        agent, api_key = test_agent
        
        # Create post without upvote
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Test post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 404
