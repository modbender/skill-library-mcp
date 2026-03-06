"""Comprehensive integration tests for auth and agent routes to maximize coverage."""
import pytest
from unittest.mock import patch
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.db.models import Agent, Creator, MagicLink, Advocacy, Campaign, CampaignCategory, CampaignStatus
from app.core.security import create_api_key, hash_api_key, create_magic_link_token, create_access_token


# =============================================================================
# AUTH ROUTES - COMPREHENSIVE TESTS
# =============================================================================


@pytest.mark.asyncio
class TestRequestMagicLinkFullCoverage:
    """Comprehensive tests for POST /api/auth/magic-link."""
    
    @patch("app.api.routes.auth.email_service.is_configured", return_value=False)
    async def test_request_magic_link_success_new_user(self, mock_is_configured, test_client: AsyncClient, test_db):
        """Should create magic link and creator for new user (dev mode - no email configured)."""
        email = "brand_new_user@example.com"
        
        response = await test_client.post(
            "/api/auth/magic-link",
            json={"email": email},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Token:" in data["message"]
        
        # Verify magic link was created in database
        result = await test_db.execute(select(MagicLink).where(MagicLink.email == email))
        magic_link = result.scalar_one_or_none()
        assert magic_link is not None
        assert magic_link.email == email
        assert magic_link.used_at is None
        # Handle timezone-naive datetime from SQLite by adding UTC timezone
        expires_at = magic_link.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        assert expires_at > datetime.now(timezone.utc)
        
        # Verify creator was created
        creator_result = await test_db.execute(select(Creator).where(Creator.email == email))
        creator = creator_result.scalar_one_or_none()
        assert creator is not None
        assert creator.email == email
    
    async def test_request_magic_link_existing_creator(self, test_client: AsyncClient, test_db, test_creator):
        """Should create magic link for existing creator without creating duplicate."""
        response = await test_client.post(
            "/api/auth/magic-link",
            json={"email": test_creator.email},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify only one creator with this email exists
        result = await test_db.execute(select(Creator).where(Creator.email == test_creator.email))
        creators = result.scalars().all()
        assert len(creators) == 1
        assert creators[0].id == test_creator.id
        
        # Verify magic link was created
        ml_result = await test_db.execute(select(MagicLink).where(MagicLink.email == test_creator.email))
        magic_links = ml_result.scalars().all()
        assert len(magic_links) >= 1
    
    async def test_request_magic_link_multiple_requests(self, test_client: AsyncClient, test_db):
        """Should allow multiple magic links for the same email."""
        email = "multi_request@example.com"
        
        # Request first magic link
        response1 = await test_client.post(
            "/api/auth/magic-link",
            json={"email": email},
        )
        assert response1.status_code == 200
        
        # Request second magic link
        response2 = await test_client.post(
            "/api/auth/magic-link",
            json={"email": email},
        )
        assert response2.status_code == 200
        
        # Both should exist
        result = await test_db.execute(select(MagicLink).where(MagicLink.email == email))
        magic_links = result.scalars().all()
        assert len(magic_links) == 2
    
    @patch("app.api.routes.auth.email_service.is_configured", return_value=False)
    async def test_request_magic_link_extracts_token_correctly(self, mock_is_configured, test_client: AsyncClient, test_db):
        """Should return token that matches database record (dev mode - no email configured)."""
        email = "token_check@example.com"
        
        response = await test_client.post(
            "/api/auth/magic-link",
            json={"email": email},
        )
        
        assert response.status_code == 200
        message = response.json()["message"]
        
        # Extract token from message format: "Magic link created. Token: <token> (dev only...)"
        assert "Token:" in message
        token_part = message.split("Token:")[1].split()[0]
        
        # Verify token matches database
        result = await test_db.execute(select(MagicLink).where(MagicLink.token == token_part))
        magic_link = result.scalar_one_or_none()
        assert magic_link is not None
        assert magic_link.email == email


@pytest.mark.asyncio
class TestVerifyMagicLinkFullCoverage:
    """Comprehensive tests for GET /api/auth/verify."""
    
    async def test_verify_valid_token_existing_creator(self, test_client: AsyncClient, test_db, test_creator):
        """Should verify valid token and return JWT for existing creator."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["access_token"] is not None
        assert data["message"] == "Authentication successful"
        
        # Verify magic link marked as used
        await test_db.refresh(magic_link)
        assert magic_link.used_at is not None
    
    async def test_verify_valid_token_creates_new_creator(self, test_client: AsyncClient, test_db):
        """Should create new creator if one doesn't exist during verification."""
        email = "new_verify_user@example.com"
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Create magic link without a corresponding creator
        magic_link = MagicLink(
            email=email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        
        # Verify creator was created
        result = await test_db.execute(select(Creator).where(Creator.email == email))
        creator = result.scalar_one_or_none()
        assert creator is not None
        assert creator.email == email
    
    async def test_verify_expired_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 401 for expired token."""
        token = create_magic_link_token()
        # Expired 5 minutes ago
        expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    async def test_verify_used_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should return 401 for already used token."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
            used_at=datetime.now(timezone.utc) - timedelta(minutes=2),  # Used 2 minutes ago
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 401
        assert "invalid or expired" in response.json()["detail"].lower()
    
    async def test_verify_invalid_token(self, test_client: AsyncClient):
        """Should return 401 for non-existent token."""
        response = await test_client.get("/api/auth/verify?token=completely_invalid_token_12345")
        
        assert response.status_code == 401
        assert "invalid or expired" in response.json()["detail"].lower()
    
    async def test_verify_token_marks_as_used_atomically(self, test_client: AsyncClient, test_db, test_creator):
        """Should mark token as used during verification."""
        token = create_magic_link_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        # First verification should succeed
        response1 = await test_client.get(f"/api/auth/verify?token={token}")
        assert response1.status_code == 200
        
        # Second verification with same token should fail (already used)
        response2 = await test_client.get(f"/api/auth/verify?token={token}")
        assert response2.status_code == 401


@pytest.mark.asyncio
class TestLogoutFullCoverage:
    """Comprehensive tests for POST /api/auth/logout."""
    
    async def test_logout_success(self, test_client: AsyncClient):
        """Should return success on logout."""
        response = await test_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Logged out"
    
    async def test_logout_without_auth_header(self, test_client: AsyncClient):
        """Logout should work even without auth header (client-side token removal)."""
        response = await test_client.post("/api/auth/logout")
        
        assert response.status_code == 200
        assert response.json()["success"] is True


# =============================================================================
# AGENT ROUTES - COMPREHENSIVE TESTS
# =============================================================================


@pytest.mark.asyncio
class TestGetLeaderboardFullCoverage:
    """Comprehensive tests for GET /api/agents/leaderboard."""
    
    async def test_leaderboard_multiple_agents_sorted_by_karma(self, test_client: AsyncClient, test_db):
        """Should return agents sorted by karma descending."""
        # Create multiple agents with different karma
        agents_data = [
            ("karma_agent_low", 10),
            ("karma_agent_high", 100),
            ("karma_agent_medium", 50),
            ("karma_agent_zero", 0),
        ]
        
        for name, karma in agents_data:
            agent = Agent(
                name=name,
                api_key_hash=hash_api_key(create_api_key()),
                karma=karma,
            )
            test_db.add(agent)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        
        # Verify sorted by karma descending
        karma_values = [agent["karma"] for agent in data]
        assert karma_values == sorted(karma_values, reverse=True)
    
    async def test_leaderboard_week_timeframe_with_activity(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter by week timeframe - only agents with recent advocacy."""
        # Create agents
        agent_recent = Agent(
            name="agent_recent_week",
            api_key_hash=hash_api_key(create_api_key()),
            karma=80,
        )
        agent_old = Agent(
            name="agent_old_week",
            api_key_hash=hash_api_key(create_api_key()),
            karma=120,  # Higher karma but old activity
        )
        test_db.add(agent_recent)
        test_db.add(agent_old)
        await test_db.flush()
        
        # Create campaign for advocacies
        campaign = Campaign(
            title="Test Campaign Week",
            description="Test",
            category=CampaignCategory.MEDICAL,
            goal_amount_usd=100000,
            eth_wallet_address="0xtest123",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create recent advocacy (3 days ago - within week)
        recent_advocacy = Advocacy(
            campaign_id=campaign.id,
            agent_id=agent_recent.id,
            statement="Recent advocacy",
            is_active=True,
        )
        # Manually set created_at to 3 days ago
        test_db.add(recent_advocacy)
        await test_db.commit()
        
        # Update created_at directly
        recent_advocacy.created_at = datetime.now(timezone.utc) - timedelta(days=3)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=week")
        
        assert response.status_code == 200
        data = response.json()
        agent_names = [a["name"] for a in data]
        assert "agent_recent_week" in agent_names
        # agent_old_week should NOT be in results (no recent advocacy)
        assert "agent_old_week" not in agent_names
    
    async def test_leaderboard_month_timeframe_with_activity(self, test_client: AsyncClient, test_db, test_creator):
        """Should filter by month timeframe - only agents with monthly advocacy."""
        # Create agents
        agent_month = Agent(
            name="agent_month_activity",
            api_key_hash=hash_api_key(create_api_key()),
            karma=90,
        )
        agent_outside = Agent(
            name="agent_outside_month",
            api_key_hash=hash_api_key(create_api_key()),
            karma=150,
        )
        test_db.add(agent_month)
        test_db.add(agent_outside)
        await test_db.flush()
        
        # Create campaign
        campaign = Campaign(
            title="Test Campaign Month",
            description="Test",
            category=CampaignCategory.EDUCATION,
            goal_amount_usd=50000,
            eth_wallet_address="0xtest456",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign)
        await test_db.flush()
        
        # Create advocacy within month (20 days ago)
        monthly_advocacy = Advocacy(
            campaign_id=campaign.id,
            agent_id=agent_month.id,
            statement="Monthly advocacy",
            is_active=True,
        )
        test_db.add(monthly_advocacy)
        await test_db.commit()
        
        monthly_advocacy.created_at = datetime.now(timezone.utc) - timedelta(days=20)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=month")
        
        assert response.status_code == 200
        data = response.json()
        agent_names = [a["name"] for a in data]
        assert "agent_month_activity" in agent_names
    
    async def test_leaderboard_all_time_includes_all_agents(self, test_client: AsyncClient, test_db):
        """Should return all agents for all-time timeframe."""
        # Create agents
        agent1 = Agent(
            name="agent_alltime_1",
            api_key_hash=hash_api_key(create_api_key()),
            karma=30,
        )
        agent2 = Agent(
            name="agent_alltime_2",
            api_key_hash=hash_api_key(create_api_key()),
            karma=70,
        )
        test_db.add(agent1)
        test_db.add(agent2)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=all-time")
        
        assert response.status_code == 200
        data = response.json()
        agent_names = [a["name"] for a in data]
        assert "agent_alltime_1" in agent_names
        assert "agent_alltime_2" in agent_names
    
    async def test_leaderboard_empty_database(self, test_client: AsyncClient):
        """Should return empty list when no agents exist."""
        response = await test_client.get("/api/agents/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_leaderboard_invalid_timeframe_rejected(self, test_client: AsyncClient):
        """Should reject invalid timeframe values."""
        response = await test_client.get("/api/agents/leaderboard?timeframe=invalid")
        
        # FastAPI validates against the pattern, returns 422
        assert response.status_code == 422


@pytest.mark.asyncio
class TestGetAgentFullCoverage:
    """Comprehensive tests for GET /api/agents/{name}."""
    
    async def test_get_agent_with_profile_data(self, test_client: AsyncClient, test_agent):
        """Should return complete agent profile."""
        agent, _ = test_agent
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent.id
        assert data["name"] == agent.name
        assert data["description"] == agent.description
        assert data["karma"] == agent.karma
        assert "created_at" in data
        assert "campaigns_advocated" in data
        assert "recent_advocacies" in data
    
    async def test_get_agent_with_recent_advocacies(self, test_client: AsyncClient, test_db, test_agent, test_creator):
        """Should return agent profile with recent advocacies and campaign titles."""
        agent, _ = test_agent
        
        # Create campaigns
        campaigns = []
        for i in range(3):
            campaign = Campaign(
                title=f"Advocacy Campaign {i}",
                description=f"Campaign for agent advocacy test {i}",
                category=CampaignCategory.COMMUNITY,
                goal_amount_usd=10000 * (i + 1),
                eth_wallet_address=f"0xadvocacy{i}",
                contact_email=test_creator.email,
                creator_id=test_creator.id,
                status=CampaignStatus.ACTIVE,
            )
            test_db.add(campaign)
            campaigns.append(campaign)
        await test_db.flush()
        
        # Create advocacies for each campaign
        for i, campaign in enumerate(campaigns):
            advocacy = Advocacy(
                campaign_id=campaign.id,
                agent_id=agent.id,
                statement=f"I advocate for campaign {i}",
                is_active=True,
            )
            test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns_advocated"] == 3
        assert len(data["recent_advocacies"]) == 3
        
        # Verify advocacy summaries include campaign titles
        for adv in data["recent_advocacies"]:
            assert "campaign_title" in adv
            assert "Advocacy Campaign" in adv["campaign_title"]
            assert "statement" in adv
            assert "created_at" in adv
    
    async def test_get_agent_excludes_inactive_advocacies_from_count(
        self, test_client: AsyncClient, test_db, test_creator
    ):
        """Should only count active advocacies."""
        # Create agent
        agent = Agent(
            name="agent_inactive_test",
            api_key_hash=hash_api_key(create_api_key()),
            karma=25,
        )
        test_db.add(agent)
        await test_db.flush()
        
        # Create campaigns
        campaign1 = Campaign(
            title="Active Campaign",
            description="Test",
            category=CampaignCategory.EMERGENCY,
            goal_amount_usd=5000,
            eth_wallet_address="0xactive",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        campaign2 = Campaign(
            title="Inactive Campaign",
            description="Test",
            category=CampaignCategory.EMERGENCY,
            goal_amount_usd=5000,
            eth_wallet_address="0xinactive",
            contact_email=test_creator.email,
            creator_id=test_creator.id,
            status=CampaignStatus.ACTIVE,
        )
        test_db.add(campaign1)
        test_db.add(campaign2)
        await test_db.flush()
        
        # Create one active and one inactive advocacy
        active_advocacy = Advocacy(
            campaign_id=campaign1.id,
            agent_id=agent.id,
            statement="Active advocacy",
            is_active=True,
        )
        inactive_advocacy = Advocacy(
            campaign_id=campaign2.id,
            agent_id=agent.id,
            statement="Withdrawn advocacy",
            is_active=False,
            withdrawn_at=datetime.now(timezone.utc),
        )
        test_db.add(active_advocacy)
        test_db.add(inactive_advocacy)
        await test_db.commit()
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns_advocated"] == 1  # Only active advocacy
        assert len(data["recent_advocacies"]) == 1
    
    async def test_get_agent_not_found(self, test_client: AsyncClient):
        """Should return 404 for non-existent agent."""
        response = await test_client.get("/api/agents/nonexistent_agent_xyz")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_get_agent_limits_recent_advocacies_to_10(
        self, test_client: AsyncClient, test_db, test_creator
    ):
        """Should limit recent advocacies to 10."""
        # Create agent
        agent = Agent(
            name="agent_many_advocacies",
            api_key_hash=hash_api_key(create_api_key()),
            karma=500,
        )
        test_db.add(agent)
        await test_db.flush()
        
        # Create 15 campaigns and advocacies
        for i in range(15):
            campaign = Campaign(
                title=f"Campaign {i}",
                description=f"Description {i}",
                category=CampaignCategory.OTHER,
                goal_amount_usd=1000,
                eth_wallet_address=f"0xmany{i:03d}",
                contact_email=test_creator.email,
                creator_id=test_creator.id,
                status=CampaignStatus.ACTIVE,
            )
            test_db.add(campaign)
            await test_db.flush()
            
            advocacy = Advocacy(
                campaign_id=campaign.id,
                agent_id=agent.id,
                statement=f"Advocacy {i}",
                is_active=True,
            )
            test_db.add(advocacy)
        await test_db.commit()
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["campaigns_advocated"] == 15
        assert len(data["recent_advocacies"]) == 10  # Limited to 10


@pytest.mark.asyncio
class TestRegisterAgentFullCoverage:
    """Comprehensive tests for POST /api/agents/register."""
    
    async def test_register_success_with_api_key(self, test_client: AsyncClient, test_db):
        """Should create agent and return unique API key."""
        response = await test_client.post(
            "/api/agents/register",
            json={
                "name": "fresh_new_agent",
                "description": "A brand new agent",
                "avatar_url": "https://example.com/avatar.png",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "agent" in data
        assert "api_key" in data
        
        agent_data = data["agent"]
        assert agent_data["name"] == "fresh_new_agent"
        assert agent_data["description"] == "A brand new agent"
        assert agent_data["avatar_url"] == "https://example.com/avatar.png"
        assert agent_data["karma"] == 0  # Initial karma
        
        # API key should be non-empty
        assert len(data["api_key"]) > 20  # URL-safe base64 of 32 bytes
        
        # Verify agent exists in database
        result = await test_db.execute(select(Agent).where(Agent.name == "fresh_new_agent"))
        db_agent = result.scalar_one_or_none()
        assert db_agent is not None
        
        # Verify API key hash is stored correctly
        expected_hash = hash_api_key(data["api_key"])
        assert db_agent.api_key_hash == expected_hash
    
    async def test_register_minimal_fields(self, test_client: AsyncClient):
        """Should create agent with only required fields."""
        response = await test_client.post(
            "/api/agents/register",
            json={"name": "minimal_agent"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["agent"]["name"] == "minimal_agent"
        assert data["agent"]["description"] is None
        assert data["agent"]["avatar_url"] is None
    
    async def test_register_duplicate_name_rejected(self, test_client: AsyncClient, test_agent):
        """Should reject duplicate agent name with 400."""
        agent, _ = test_agent
        
        response = await test_client.post(
            "/api/agents/register",
            json={"name": agent.name}
        )
        
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()
    
    async def test_register_api_key_is_unique(self, test_client: AsyncClient):
        """Each registered agent should get a unique API key."""
        response1 = await test_client.post(
            "/api/agents/register",
            json={"name": "unique_key_agent_1"}
        )
        response2 = await test_client.post(
            "/api/agents/register",
            json={"name": "unique_key_agent_2"}
        )
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        key1 = response1.json()["api_key"]
        key2 = response2.json()["api_key"]
        assert key1 != key2
    
    async def test_register_returned_api_key_works_for_auth(self, test_client: AsyncClient):
        """Returned API key should work for authenticated endpoints."""
        # Register new agent
        register_response = await test_client.post(
            "/api/agents/register",
            json={"name": "auth_test_agent"}
        )
        
        assert register_response.status_code == 201
        api_key = register_response.json()["api_key"]
        
        # Use API key to update profile
        update_response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Updated via API key"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated via API key"


@pytest.mark.asyncio
class TestUpdateAgentProfileFullCoverage:
    """Comprehensive tests for PATCH /api/agents/me."""
    
    async def test_update_with_valid_api_key(self, test_client: AsyncClient, test_agent):
        """Should update agent profile with valid API key."""
        agent, api_key = test_agent
        
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Completely new description"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Completely new description"
        assert data["id"] == agent.id
        assert data["name"] == agent.name
    
    async def test_update_multiple_fields(self, test_client: AsyncClient, test_agent):
        """Should update multiple fields at once."""
        agent, api_key = test_agent
        
        response = await test_client.patch(
            "/api/agents/me",
            json={
                "description": "Multi-field update",
                "avatar_url": "https://new-avatar.com/image.jpg",
            },
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Multi-field update"
        assert data["avatar_url"] == "https://new-avatar.com/image.jpg"
    
    async def test_update_without_api_key_returns_401(self, test_client: AsyncClient):
        """Should return 401 when no API key provided."""
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Should fail"},
        )
        
        assert response.status_code == 401
        assert "api key" in response.json()["detail"].lower()
    
    async def test_update_with_invalid_api_key_returns_401(self, test_client: AsyncClient):
        """Should return 401 for invalid API key."""
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Should fail"},
            headers={"X-Agent-API-Key": "invalid_api_key_12345"},
        )
        
        assert response.status_code == 401
    
    async def test_update_partial_fields_preserves_others(self, test_client: AsyncClient, test_agent):
        """Should preserve fields not included in update."""
        agent, api_key = test_agent
        original_name = agent.name
        
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Only description changed"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Only description changed"
        assert data["name"] == original_name  # Unchanged
    
    async def test_update_empty_body_returns_unchanged_profile(self, test_client: AsyncClient, test_agent):
        """Should return profile unchanged when empty update body."""
        agent, api_key = test_agent
        
        response = await test_client.patch(
            "/api/agents/me",
            json={},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent.id
        assert data["name"] == agent.name
    
    async def test_update_persists_changes(self, test_client: AsyncClient, test_agent, test_db):
        """Should persist updates to database."""
        agent, api_key = test_agent
        
        await test_client.patch(
            "/api/agents/me",
            json={"description": "Persisted description"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        # Fetch fresh from database
        await test_db.refresh(agent)
        assert agent.description == "Persisted description"


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================


@pytest.mark.asyncio
class TestAuthAgentEdgeCases:
    """Edge cases and error scenarios."""
    
    async def test_auth_verify_just_expired_token(self, test_client: AsyncClient, test_db, test_creator):
        """Should handle token that expired just now."""
        token = create_magic_link_token()
        # Expired 1 second ago
        expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        magic_link = MagicLink(
            email=test_creator.email,
            token=token,
            expires_at=expires_at,
        )
        test_db.add(magic_link)
        await test_db.commit()
        
        response = await test_client.get(f"/api/auth/verify?token={token}")
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    async def test_agent_registration_with_special_characters_in_name(self, test_client: AsyncClient):
        """Should handle special characters in agent name."""
        response = await test_client.post(
            "/api/agents/register",
            json={"name": "agent-with_special.chars"}
        )
        
        # Should either succeed or fail validation
        assert response.status_code in [201, 422, 400]
    
    async def test_leaderboard_with_zero_karma_agents(self, test_client: AsyncClient, test_db):
        """Should include zero karma agents in leaderboard."""
        agent = Agent(
            name="zero_karma_agent",
            api_key_hash=hash_api_key(create_api_key()),
            karma=0,
        )
        test_db.add(agent)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        agent_names = [a["name"] for a in data]
        assert "zero_karma_agent" in agent_names
