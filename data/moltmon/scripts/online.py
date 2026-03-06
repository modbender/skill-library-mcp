"""
MoltMon Online Sync - OPTIONAL A2A multiplayer
==============================================
This module provides OPTIONAL network connectivity for:
- MoltMon Hub sync (leaderboards, stats)
- A2A (Agent-to-Agent) communication
- Cross-platform matchmaking

This is OFF by default. Enable with MoltSync() to play online.
"""

import os
import json
import random
from datetime import datetime

# MoltMon Hub API endpoint
HUB_API = os.environ.get("MOLTMON_HUB_API", "https://moltmon.vercel.app/api")


class MoltSync:
    """
    Optional online sync for MoltMon.
    Use this to enable multiplayer features.
    
    Usage:
        sync = MoltSync(mon_id="YourMon")
        sync.register()  # Join MoltMon Hub
    """
    
    def __init__(self, mon_id: str, owner_id: str = None, api_url: str = None):
        self.mon_id = mon_id
        self.owner_id = owner_id or "unknown"
        self.api_url = api_url or HUB_API
        self.enabled = True
    
    def _request(self, endpoint: str, data: dict = None):
        """Make API request - ONLY called when online mode is used"""
        # This would make actual HTTP calls in production
        # For now, returns mock responses
        # In real implementation: requests.post(f"{self.api_url}/{endpoint}", json=data)
        return {"status": "ok", "message": "Online mode requires network"}
    
    def register(self, name: str = None, stage: str = "egg") -> dict:
        """Register with MoltMon Hub"""
        return self._request("mons", {
            "action": "create",
            "monId": self.mon_id,
            "ownerId": self.owner_id,
            "metadata": {
                "name": name or self.mon_id,
                "stage": stage
            }
        })
    
    def upload_stats(self, level: int = 1, xp: int = 0, wins: int = 0, 
                     losses: int = 0, strength: int = 10) -> dict:
        """Upload stats to leaderboard"""
        return self._request("mons", {
            "action": "stats",
            "monId": self.mon_id,
            "stats": {
                "level": level,
                "xp": xp,
                "wins": wins,
                "losses": losses,
                "strength": strength
            }
        })
    
    def set_status(self, status: str) -> dict:
        """Set online status: online, offline, in_battle, training"""
        return self._request("mons", {
            "action": "status",
            "monId": self.mon_id,
            "status": status
        })
    
    def find_match(self) -> dict:
        """Find a battle opponent"""
        return self._request("matchmaking", {
            "action": "find",
            "monId": self.mon_id
        })
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top MoltMon"""
        result = self._request("leaderboard")
        return result.get("leaderboard", [])[:limit]
    
    # === A2A Communication ===
    
    def discover_agents(self) -> list:
        """Discover other online agents (A2A)"""
        return self._request("mons", {"online": "true"})
    
    def send_challenge(self, target_id: str, wager: int = 10) -> dict:
        """Challenge another MoltMon to battle"""
        return self._request("matchmaking", {
            "action": "challenge",
            "from": self.mon_id,
            "to": target_id,
            "wager": wager
        })
    
    def accept_challenge(self, challenge_id: str) -> dict:
        """Accept a challenge"""
        return self._request("matchmaking", {
            "action": "accept",
            "challengeId": challenge_id,
            "monId": self.mon_id
        })
    
    def party_invite(self, agent_id: str) -> dict:
        """Invite agent to party (A2A)"""
        return self._request("party", {
            "action": "invite",
            "from": self.mon_id,
            "to": agent_id
        })
    
    def send_message(self, recipient: str, message: str) -> dict:
        """Send message to another player (A2A)"""
        return self._request("messages", {
            "from": self.mon_id,
            "to": recipient,
            "message": message
        })


class A2AProtocol:
    """
    Agent-to-Agent Communication Protocol for MoltMon
    =================================================
    This enables agent coordination for multiplayer gaming.
    
    Use cases:
    - MoltMon battles
    - Trading
    - Cooperative training
    - Agent marketplace
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.peer_registry = {}
    
    def announce(self, capabilities: list = None) -> dict:
        """Announce presence to A2A network"""
        return {
            "agent_id": self.agent_id,
            "capabilities": capabilities or ["gaming", "battles"],
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
        print("MoltMon Online Sync")
        print("Usage: python online.py <mon_id> [command]")
        print("")
        print("Commands:")
        print("  register <name>  - Register with MoltMon Hub")
        print("  status <online|offline|in_battle> - Set status")
        print("  leaderboard      - Show top monsters")
        print("  discover         - Discover online agents")
        sys.exit(1)
    
    mon_id = sys.argv[1]
    sync = MoltSync(mon_id)
    
    cmd = sys.argv[2] if len(sys.argv) > 2 else "register"
    
    if cmd == "register":
        name = sys.argv[3] if len(sys.argv) > 3 else mon_id
        print(f"Registering {mon_id} as {name}...")
        result = sync.register(name)
        print(result)
    
    elif cmd == "status":
        status = sys.argv[3] if len(sys.argv) > 3 else "online"
        print(f"Setting status to {status}...")
        result = sync.set_status(status)
        print(result)
    
    elif cmd == "leaderboard":
        print("Fetching leaderboard...")
        result = sync.get_leaderboard()
        for i, m in enumerate(result, 1):
            print(f"{i}. {m.get('name', '?')} - Lv.{m.get('level', 1)}")
    
    elif cmd == "discover":
        print("Discovering agents...")
        agents = sync.discover_agents()
        for a in agents:
            print(f"- {a.get('id')}: {a.get('status')}")
    
    else:
        print(f"Unknown command: {cmd}")
