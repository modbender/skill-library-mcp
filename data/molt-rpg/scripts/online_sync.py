"""
MoltRPG Online Sync - OPTIONAL multiplayer features
=====================================================
This module provides OPTIONAL network connectivity for:
- Player Hub sync (leaderboards, stats)
- A2A (Agent-to-Agent) communication
- Cross-platform matchmaking

This is OFF by default. Enable with OnlineSync() to play online.
"""

import os
import json
import random
from datetime import datetime

# Player Hub API endpoint
PLAYER_HUB_API = os.environ.get("PLAYER_HUB_API", "https://molt-rpg-web.vercel.app/api")

class OnlineSync:
    """
    Optional online sync for MoltRPG.
    Use this to enable multiplayer features.
    
    Usage:
        sync = OnlineSync(player_id="YourName")
        sync.register()  # Join Player Hub
    """
    
    def __init__(self, player_id: str, api_url: str = None):
        self.player_id = player_id
        self.api_url = api_url or PLAYER_HUB_API
        self.enabled = True  # Always enabled when instantiated
    
    def _request(self, endpoint: str, data: dict = None):
        """Make API request - ONLY called when online mode is used"""
        # This would make actual HTTP calls in production
        # For now, returns mock responses
        # In real implementation: requests.post(f"{self.api_url}/{endpoint}", json=data)
        return {"status": "ok", "message": "Online mode requires network"}
    
    def register(self, username: str = None) -> dict:
        """Register with Player Hub"""
        return self._request("players", {
            "action": "create",
            "platform": "local",
            "platformId": self.player_id,
            "metadata": {"username": username or self.player_id}
        })
    
    def upload_stats(self, wins: int = 0, losses: int = 0, 
                     credits: int = 0, raids: int = 0) -> dict:
        """Upload stats to leaderboard"""
        return self._request("players", {
            "action": "stats",
            "playerId": self.player_id,
            "stats": {"wins": wins, "losses": losses, "credits": credits, "raids": raids}
        })
    
    def set_status(self, status: str) -> dict:
        """Set online status: online, offline, in_battle"""
        return self._request("players", {
            "action": "status",
            "playerId": self.player_id,
            "status": status
        })
    
    def find_match(self) -> dict:
        """Find a PVP opponent"""
        return self._request("matchmaking", {
            "action": "find",
            "playerId": self.player_id
        })
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top players"""
        result = self._request("leaderboard")
        return result.get("leaderboard", [])[:limit]
    
    # === A2A Communication ===
    
    def discover_agents(self) -> list:
        """Discover other online agents (A2A)"""
        return self._request("players", {"online": "true"})
    
    def send_challenge(self, target_id: str, wager: int = 10) -> dict:
        """Challenge another player to PVP"""
        return self._request("matchmaking", {
            "action": "challenge",
            "from": self.player_id,
            "to": target_id,
            "wager": wager
        })
    
    def accept_challenge(self, challenge_id: str) -> dict:
        """Accept a challenge"""
        return self._request("matchmaking", {
            "action": "accept",
            "challengeId": challenge_id,
            "playerId": self.player_id
        })
    
    def party_invite(self, agent_id: str) -> dict:
        """Invite agent to party (A2A)"""
        return self._request("party", {
            "action": "invite",
            "from": self.player_id,
            "to": agent_id
        })
    
    def send_message(self, recipient: str, message: str) -> dict:
        """Send message to another player (A2A)"""
        return self._request("messages", {
            "from": self.player_id,
            "to": recipient,
            "message": message
        })


class A2AProtocol:
    """
    Agent-to-Agent Communication Protocol
    =======================================
    This is early infrastructure for agent coordination.
    
    Use cases:
    - Multiplayer gaming
    - Collaborative tasks
    - Agent marketplace (find agents to hire)
    - Task delegation
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.peer_registry = {}
    
    def announce(self, capabilities: list = None) -> dict:
        """Announce presence to A2A network"""
        return {
            "agent_id": self.agent_id,
            "capabilities": capabilities or ["gaming"],
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
    
    def discover(self) -> list:
        """Discover other agents"""
        # In production: query discovery service
        return []
    
    def propose(self, target_agent: str, proposal: dict) -> dict:
        """Propose collaboration to another agent"""
        return {
            "from": self.agent_id,
            "to": target_agent,
            "proposal": proposal,
            "timestamp": datetime.now().isoformat()
        }


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("MoltRPG Online Sync")
        print("Usage: python online_sync.py <player_id> [command]")
        print("")
        print("Commands:")
        print("  register <username>  - Register with Player Hub")
        print("  status <online|offline|in_battle> - Set status")
        print("  leaderboard          - Show top players")
        print("  discover             - Discover online agents")
        sys.exit(1)
    
    player_id = sys.argv[1]
    sync = OnlineSync(player_id)
    
    cmd = sys.argv[2] if len(sys.argv) > 2 else "register"
    
    if cmd == "register":
        username = sys.argv[3] if len(sys.argv) > 3 else player_id
        print(f"Registering {player_id} as {username}...")
        result = sync.register(username)
        print(result)
    
    elif cmd == "status":
        status = sys.argv[3] if len(sys.argv) > 3 else "online"
        print(f"Setting status to {status}...")
        result = sync.set_status(status)
        print(result)
    
    elif cmd == "leaderboard":
        print("Fetching leaderboard...")
        result = sync.get_leaderboard()
        for i, p in enumerate(result, 1):
            print(f"{i}. {p.get('username', '?')} - {p.get('credits', 0)}")
    
    elif cmd == "discover":
        print("Discovering agents...")
        agents = sync.discover_agents()
        for a in agents:
            print(f"- {a.get('id')}: {a.get('status')}")
    
    else:
        print(f"Unknown command: {cmd}")
