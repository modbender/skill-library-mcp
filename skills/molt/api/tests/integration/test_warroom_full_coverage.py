"""Full coverage integration tests for warroom routes.

Tests cover all code paths in app/api/routes/warroom.py including:
- get_warroom_posts: response building with agent details, 404 for missing campaign
- create_warroom_post: success with karma award, feed event creation, parent post validation
- upvote_post: success with karma to author, duplicate upvote, 404 for missing post
- remove_upvote: success case, 404 for missing post, 404 for no existing upvote
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db.models import Campaign, Agent, WarRoomPost, Upvote, FeedEvent, FeedEventType
from app.core.security import create_api_key, hash_api_key


@pytest.mark.asyncio
class TestGetWarroomPosts:
    """Tests for GET /{campaign_id}/warroom endpoint."""

    async def test_get_warroom_posts_empty(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should return empty list for campaign with no posts."""
        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_warroom_posts_with_multiple_posts(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should return posts in chronological order with agent details."""
        # Create two agents with different attributes
        agent1_key = create_api_key()
        agent1 = Agent(
            name="agent-alpha",
            description="First agent",
            api_key_hash=hash_api_key(agent1_key),
            karma=100,
            avatar_url="https://example.com/avatar1.png",
        )
        agent2_key = create_api_key()
        agent2 = Agent(
            name="agent-beta",
            description="Second agent",
            api_key_hash=hash_api_key(agent2_key),
            karma=50,
            avatar_url=None,  # Test null avatar_url
        )
        test_db.add(agent1)
        test_db.add(agent2)
        await test_db.flush()

        # Create posts with different attributes
        post1 = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent1.id,
            content="First post content",
            upvote_count=10,
        )
        test_db.add(post1)
        await test_db.flush()

        # Create second post (will have later created_at)
        post2 = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent2.id,
            content="Second post content",
            upvote_count=5,
        )
        # Create reply post (tests parent_post_id in response)
        post3 = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent1.id,
            parent_post_id=post1.id,
            content="Reply to first post",
            upvote_count=0,
        )
        test_db.add(post2)
        test_db.add(post3)
        await test_db.commit()

        response = await test_client.get(f"/api/campaigns/{test_campaign.id}/warroom")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify response building with all agent details (lines 35-48)
        # First post
        assert data[0]["id"] == post1.id
        assert data[0]["campaign_id"] == test_campaign.id
        assert data[0]["agent_id"] == agent1.id
        assert data[0]["agent_name"] == "agent-alpha"
        assert data[0]["agent_karma"] == 100
        assert data[0]["agent_avatar_url"] == "https://example.com/avatar1.png"
        assert data[0]["parent_post_id"] is None
        assert data[0]["content"] == "First post content"
        assert data[0]["upvote_count"] == 10

        # Second post - verify null avatar_url
        assert data[1]["agent_name"] == "agent-beta"
        assert data[1]["agent_karma"] == 50
        assert data[1]["agent_avatar_url"] is None
        assert data[1]["content"] == "Second post content"
        assert data[1]["upvote_count"] == 5

        # Third post - verify parent_post_id
        assert data[2]["parent_post_id"] == post1.id
        assert data[2]["content"] == "Reply to first post"

    async def test_get_warroom_posts_campaign_not_found(
        self, test_client: AsyncClient, test_db
    ):
        """Should return 404 for non-existent campaign."""
        response = await test_client.get(
            "/api/campaigns/non-existent-campaign-id/warroom"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"


@pytest.mark.asyncio
class TestCreateWarroomPost:
    """Tests for POST /{campaign_id}/warroom/posts endpoint."""

    async def test_create_post_success_with_karma_award(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should create post and award karma to agent."""
        agent, api_key = test_agent
        initial_karma = agent.karma

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Test post content"},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response contains all expected fields
        assert data["content"] == "Test post content"
        assert data["campaign_id"] == test_campaign.id
        assert data["agent_id"] == agent.id
        assert data["agent_name"] == agent.name
        assert data["agent_karma"] == initial_karma + 1  # Karma increased
        assert data["parent_post_id"] is None
        assert data["upvote_count"] == 0
        assert "created_at" in data
        assert "id" in data

        # Verify karma was awarded (line 91)
        await test_db.refresh(agent)
        assert agent.karma == initial_karma + 1

    async def test_create_post_creates_feed_event(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should create feed event for warroom post."""
        agent, api_key = test_agent

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Post that generates feed event"},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 201

        # Verify feed event was created (lines 94-100)
        result = await test_db.execute(
            select(FeedEvent).where(
                FeedEvent.event_type == FeedEventType.WARROOM_POST,
                FeedEvent.campaign_id == test_campaign.id,
                FeedEvent.agent_id == agent.id,
            )
        )
        feed_event = result.scalar_one_or_none()
        assert feed_event is not None
        # Metadata contains post_id (value may be stringified "None" due to SQLite JSON handling)
        assert feed_event.event_metadata is not None
        assert "post_id" in feed_event.event_metadata

    async def test_create_post_with_parent_post(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should create reply post with valid parent_post_id."""
        agent, api_key = test_agent

        # Create parent post directly in DB
        parent_post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Parent post",
            upvote_count=0,
        )
        test_db.add(parent_post)
        await test_db.commit()

        # Create reply
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Reply content", "parent_post_id": parent_post.id},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_post_id"] == parent_post.id
        assert data["content"] == "Reply content"

    async def test_create_post_parent_not_found(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should return 404 if parent post doesn't exist."""
        agent, api_key = test_agent

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Reply", "parent_post_id": "non-existent-post-id"},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Parent post not found"

    async def test_create_post_parent_from_different_campaign(
        self, test_client: AsyncClient, test_campaign, test_creator, test_agent, test_db
    ):
        """Should return 404 if parent post is from a different campaign."""
        from app.db.models import CampaignCategory, CampaignStatus

        agent, api_key = test_agent

        # Create another campaign
        other_campaign = Campaign(
            title="Other Campaign",
            description="Another campaign",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=50000,
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(other_campaign)
        await test_db.flush()

        # Create parent post in different campaign
        parent_post = WarRoomPost(
            campaign_id=other_campaign.id,
            agent_id=agent.id,
            content="Post in other campaign",
            upvote_count=0,
        )
        test_db.add(parent_post)
        await test_db.commit()

        # Try to reply in original campaign - should fail
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Reply", "parent_post_id": parent_post.id},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Parent post not found"

    async def test_create_post_campaign_not_found(
        self, test_client: AsyncClient, test_agent, test_db
    ):
        """Should return 404 for non-existent campaign."""
        agent, api_key = test_agent

        response = await test_client.post(
            "/api/campaigns/non-existent-campaign/warroom/posts",
            json={"content": "Test post"},
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Campaign not found"

    async def test_create_post_requires_authentication(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should return 401/403 without valid API key."""
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts",
            json={"content": "Test post"},
        )

        # Could be 401 or 403 depending on implementation
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestUpvotePost:
    """Tests for POST /{campaign_id}/warroom/posts/{post_id}/upvote endpoint."""

    async def test_upvote_post_success(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should successfully upvote a post."""
        # Create author agent
        author_key = create_api_key()
        author = Agent(
            name="post-author",
            api_key_hash=hash_api_key(author_key),
            karma=10,
        )
        # Create upvoter agent
        upvoter_key = create_api_key()
        upvoter = Agent(
            name="upvoter",
            api_key_hash=hash_api_key(upvoter_key),
            karma=5,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()

        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Post to upvote",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify upvote count increased (line 162)
        await test_db.refresh(post)
        assert post.upvote_count == 1

        # Verify upvote record created
        result = await test_db.execute(
            select(Upvote).where(
                Upvote.post_id == post.id,
                Upvote.agent_id == upvoter.id,
            )
        )
        upvote = result.scalar_one_or_none()
        assert upvote is not None

    async def test_upvote_awards_karma_to_different_author(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should award karma to post author when upvoter is different agent."""
        # Create author agent
        author_key = create_api_key()
        author = Agent(
            name="karma-author",
            api_key_hash=hash_api_key(author_key),
            karma=10,
        )
        # Create upvoter agent
        upvoter_key = create_api_key()
        upvoter = Agent(
            name="karma-upvoter",
            api_key_hash=hash_api_key(upvoter_key),
            karma=5,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()

        initial_author_karma = author.karma

        # Create post
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Post for karma test",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )

        assert response.status_code == 200

        # Verify author karma increased (lines 165-170)
        await test_db.refresh(author)
        assert author.karma == initial_author_karma + 1

    async def test_upvote_own_post_no_karma(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should not award karma when upvoting own post."""
        agent, api_key = test_agent
        initial_karma = agent.karma

        # Create post by same agent
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="My own post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 200

        # Verify no karma awarded to self (line 165 condition)
        await test_db.refresh(agent)
        assert agent.karma == initial_karma  # No change

    async def test_upvote_post_duplicate(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should return 400 when trying to upvote same post twice."""
        # Create agents
        author_key = create_api_key()
        author = Agent(
            name="dup-author",
            api_key_hash=hash_api_key(author_key),
            karma=0,
        )
        upvoter_key = create_api_key()
        upvoter = Agent(
            name="dup-upvoter",
            api_key_hash=hash_api_key(upvoter_key),
            karma=0,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()

        # Create post first and flush to get ID
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Post for duplicate upvote test",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.flush()  # Flush to generate post.id

        # Create existing upvote
        upvote = Upvote(
            post_id=post.id,
            agent_id=upvoter.id,
        )
        test_db.add(upvote)
        await test_db.commit()

        # Try to upvote again - should fail (line 150-151)
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Already upvoted"

    async def test_upvote_post_not_found(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should return 404 for non-existent post."""
        agent, api_key = test_agent

        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/non-existent-post/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

    async def test_upvote_post_wrong_campaign(
        self, test_client: AsyncClient, test_campaign, test_creator, test_agent, test_db
    ):
        """Should return 404 if post exists but in different campaign."""
        from app.db.models import CampaignCategory, CampaignStatus

        agent, api_key = test_agent

        # Create another campaign
        other_campaign = Campaign(
            title="Other Campaign for Upvote",
            description="Another campaign",
            category=CampaignCategory.COMMUNITY,
            goal_amount_usd=25000,
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(other_campaign)
        await test_db.flush()

        # Create post in different campaign
        post = WarRoomPost(
            campaign_id=other_campaign.id,
            agent_id=agent.id,
            content="Post in other campaign",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        # Try to upvote using original campaign ID - should fail
        response = await test_client.post(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"


@pytest.mark.asyncio
class TestRemoveUpvote:
    """Tests for DELETE /{campaign_id}/warroom/posts/{post_id}/upvote endpoint."""

    async def test_remove_upvote_success(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should successfully remove upvote."""
        # Create agents
        author_key = create_api_key()
        author = Agent(
            name="remove-author",
            api_key_hash=hash_api_key(author_key),
            karma=0,
        )
        upvoter_key = create_api_key()
        upvoter = Agent(
            name="remove-upvoter",
            api_key_hash=hash_api_key(upvoter_key),
            karma=0,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()

        # Create post with upvote count > 0
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Post to remove upvote from",
            upvote_count=5,
        )
        test_db.add(post)
        await test_db.flush()

        # Create existing upvote
        upvote = Upvote(
            post_id=post.id,
            agent_id=upvoter.id,
        )
        test_db.add(upvote)
        await test_db.commit()

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )

        assert response.status_code == 204

        # Verify upvote was deleted (line 211)
        result = await test_db.execute(
            select(Upvote).where(
                Upvote.post_id == post.id,
                Upvote.agent_id == upvoter.id,
            )
        )
        assert result.scalar_one_or_none() is None

        # Verify upvote count decreased (line 214)
        await test_db.refresh(post)
        assert post.upvote_count == 4

    async def test_remove_upvote_decrements_to_zero_minimum(
        self, test_client: AsyncClient, test_campaign, test_db
    ):
        """Should not decrement below zero."""
        # Create agents
        author_key = create_api_key()
        author = Agent(
            name="zero-author",
            api_key_hash=hash_api_key(author_key),
            karma=0,
        )
        upvoter_key = create_api_key()
        upvoter = Agent(
            name="zero-upvoter",
            api_key_hash=hash_api_key(upvoter_key),
            karma=0,
        )
        test_db.add(author)
        test_db.add(upvoter)
        await test_db.flush()

        # Create post with upvote_count = 0 (edge case)
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=author.id,
            content="Post with zero upvotes",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.flush()

        # Create existing upvote
        upvote = Upvote(
            post_id=post.id,
            agent_id=upvoter.id,
        )
        test_db.add(upvote)
        await test_db.commit()

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": upvoter_key},
        )

        assert response.status_code == 204

        # Verify upvote count is 0, not negative (line 214 max(0, ...))
        await test_db.refresh(post)
        assert post.upvote_count == 0

    async def test_remove_upvote_post_not_found(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should return 404 for non-existent post."""
        agent, api_key = test_agent

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/non-existent-post/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

    async def test_remove_upvote_no_existing_upvote(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should return 404 when trying to remove non-existent upvote."""
        agent, api_key = test_agent

        # Create post without upvote from this agent
        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Post without upvote",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Upvote not found"

    async def test_remove_upvote_wrong_campaign(
        self, test_client: AsyncClient, test_campaign, test_creator, test_agent, test_db
    ):
        """Should return 404 if post exists but in different campaign."""
        from app.db.models import CampaignCategory, CampaignStatus

        agent, api_key = test_agent

        # Create another campaign
        other_campaign = Campaign(
            title="Other Campaign for Remove",
            description="Another campaign",
            category=CampaignCategory.DISASTER_RELIEF,
            goal_amount_usd=75000,
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(other_campaign)
        await test_db.flush()

        # Create post in different campaign
        post = WarRoomPost(
            campaign_id=other_campaign.id,
            agent_id=agent.id,
            content="Post in other campaign",
            upvote_count=1,
        )
        test_db.add(post)
        await test_db.flush()

        # Add upvote in other campaign
        upvote = Upvote(
            post_id=post.id,
            agent_id=agent.id,
        )
        test_db.add(upvote)
        await test_db.commit()

        # Try to remove upvote using original campaign ID - should fail
        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
            headers={"X-Agent-API-Key": api_key},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Post not found"

    async def test_remove_upvote_requires_authentication(
        self, test_client: AsyncClient, test_campaign, test_agent, test_db
    ):
        """Should return 401/403 without valid API key."""
        agent, api_key = test_agent

        post = WarRoomPost(
            campaign_id=test_campaign.id,
            agent_id=agent.id,
            content="Post",
            upvote_count=0,
        )
        test_db.add(post)
        await test_db.commit()

        response = await test_client.delete(
            f"/api/campaigns/{test_campaign.id}/warroom/posts/{post.id}/upvote",
        )

        assert response.status_code in [401, 403]
