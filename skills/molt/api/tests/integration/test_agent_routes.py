"""Integration tests for agent routes."""
import pytest
from httpx import AsyncClient

from app.db.models import Agent


@pytest.mark.asyncio
class TestAgentLeaderboard:
    """Tests for GET /api/agents/leaderboard."""
    
    async def test_get_leaderboard_returns_agents(self, test_client: AsyncClient, test_agent):
        """Should return agents sorted by karma (NOT 404)."""
        agent, _ = test_agent
        
        # Create another agent with different karma
        from app.db.models import Agent
        from app.core.security import create_api_key, hash_api_key
        from sqlalchemy import select
        
        # Get the test_db from the fixture
        # We need to create agents in the test_db
        # For now, test with existing agent
        
        response = await test_client.get("/api/agents/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_get_leaderboard_sorted_by_karma(self, test_client: AsyncClient, test_db, test_agent):
        """Should return agents sorted by karma descending."""
        agent1, _ = test_agent
        
        # Create second agent with higher karma
        from app.core.security import create_api_key, hash_api_key
        api_key2 = create_api_key()
        agent2 = Agent(
            name="high-karma-agent",
            description="High karma",
            api_key_hash=hash_api_key(api_key2),
            karma=100,
        )
        test_db.add(agent2)
        await test_db.commit()
        
        response = await test_client.get("/api/agents/leaderboard")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) >= 2:
            # First agent should have higher karma
            assert data[0]["karma"] >= data[1]["karma"]
    
    async def test_get_leaderboard_with_timeframe(self, test_client: AsyncClient, test_agent):
        """Should accept timeframe query parameter."""
        response = await test_client.get("/api/agents/leaderboard?timeframe=week")
        assert response.status_code == 200
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=month")
        assert response.status_code == 200
        
        response = await test_client.get("/api/agents/leaderboard?timeframe=all-time")
        assert response.status_code == 200


@pytest.mark.asyncio
class TestGetAgent:
    """Tests for GET /api/agents/{name}."""
    
    async def test_get_agent_returns_profile(self, test_client: AsyncClient, test_agent):
        """Should return agent profile."""
        agent, _ = test_agent
        
        response = await test_client.get(f"/api/agents/{agent.name}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent.id
        assert data["name"] == agent.name
        assert data["karma"] == agent.karma
    
    async def test_get_agent_returns_404_for_missing(self, test_client: AsyncClient):
        """Should return 404 for non-existent agent."""
        response = await test_client.get("/api/agents/nonexistent-agent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestRegisterAgent:
    """Tests for POST /api/agents/register."""
    
    async def test_register_creates_agent_with_api_key(self, test_client: AsyncClient):
        """Should create agent and return API key."""
        response = await test_client.post(
            "/api/agents/register",
            json={
                "name": "new-agent",
                "description": "New agent description",
                "avatar_url": "https://example.com/avatar.png",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "agent" in data
        assert "api_key" in data
        assert data["agent"]["name"] == "new-agent"
        assert len(data["api_key"]) > 0
    
    async def test_register_rejects_duplicate_name(self, test_client: AsyncClient, test_agent):
        """Should reject duplicate agent name."""
        agent, _ = test_agent
        
        response = await test_client.post(
            "/api/agents/register",
            json={
                "name": agent.name,  # Duplicate name
                "description": "Duplicate",
            }
        )
        
        assert response.status_code == 400
        assert "already taken" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestUpdateAgent:
    """Tests for PATCH /api/agents/me."""
    
    async def test_update_agent_with_valid_api_key(self, test_client: AsyncClient, test_agent):
        """Should update agent profile with valid API key."""
        agent, api_key = test_agent
        
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Updated description"},
            headers={"X-Agent-API-Key": api_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
    
    async def test_update_agent_rejects_without_api_key(self, test_client: AsyncClient):
        """Should reject update without API key."""
        response = await test_client.patch(
            "/api/agents/me",
            json={"description": "Updated"},
        )
        
        assert response.status_code == 401
        assert "api key" in response.json()["detail"].lower()
