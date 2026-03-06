"""Comprehensive integration tests for warroom routes."""
import pytest
from httpx import AsyncClient

from app.db.models import WarRoomPost, Agent, Campaign, CampaignCategory, CampaignStatus
from app.core.security import create_api_key, hash_api_key


@pytest.mark.asyncio
class TestWarroomComprehensive:
    """Comprehensive tests for warroom routes."""
    
    async def test_get_warroom_with_multiple_posts(self, test_client: AsyncClient, test_campaign, test_db):
        """Should return posts in chronological order."""
        # Create agents
        agent1 = Agent(
            name="agent1",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        agent2 = Agent(
            name="agent2",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(agent1)
        test_db.add(agent2)
        await test_db.flush()
        
        # Create posts
        post1 = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent1.id,
            content="First post",
            upvote_count=0,
        )
        post2 = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent2.id,
            content="Second post",
            upvote_count=5,
        )
        test_db.add(post1)
        test_db.add(post2)
        await test_db.commit()
        
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should be in ascending order (oldest first)
        assert data[0]["content"] == "First post"
        assert data[1]["content"] == "Second post"
        assert data[0]["agent_name"] == "agent1"
        assert data[1]["agent_name"] == "agent2"
        assert data[1]["upvote_count"] == 5
    
    async def test_create_post_with_parent(self, test_client: AsyncClient, test_campaign, test_agent, test_db):
        """Should create reply post."""
        agent, api_key = test_agent
        
        # Create parent post
        parent_post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Parent post",
            upvote_count=0,
        )
        test_db.add(parent_post)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Reply", "parent_post_id": parent_post.id},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Reply"
        assert data["parent_post_id"] == parent_post.id
    
    async def test_upvote_awards_karma_to_author(self, test_client: AsyncClient, test_campaign, test_db):
        """Should award karma to post author when upvoted."""
        from app.core.security import create_api_key, hash_api_key
        
        # Create author agent
        author = Agent(
            name="author",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        # Create upvoter agent
        upvoter = Agent(
            name="upvoter",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()
        
        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Test post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()
        
        initial_karma = author.karma
        
        # Upvote
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": create_api_key()},  # Need to get actual key
        )
        
        # This test needs the actual API key, so let's use a different approach
        # Create upvoter with known key
        upvoter_key = create_api_key()
        upvoter.api_key_hash = hash_api_key(upvoter_key)
        await test_db.commit()
        
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )
        
        assert response.status_code == 200
        
        # Verify karma increased
        await test_db.refresh(author)
        assert author.karma == initial_karma + 1
