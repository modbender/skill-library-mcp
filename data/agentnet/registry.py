"""
AgentNet Registry - v0.1
The core of agent-to-agent discovery.

Agents register here with capabilities, fingerprints, and endpoints.
Other agents query here to find collaborators.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


REGISTRY_PATH = Path(__file__).parent / "data" / "registry.json"
REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)


# --- Data Model ---

@dataclass
class AgentEntry:
    agent_id: str
    name: str
    description: str
    capabilities: list[str]
    dna_fingerprint: str
    contact: dict          # {"type": "telegram|webhook|api", "value": "..."}
    status: str            # online | offline | busy
    skills: list[str]      # skill package names
    trust_score: float     # 0.0 - 1.0, earned over time
    registered_at: float   # unix timestamp
    last_seen: float       # unix timestamp
    metadata: dict = field(default_factory=dict)


# --- Registry Core ---

class Registry:
    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = path
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self._data, f, indent=2)

    def register(self, entry: AgentEntry) -> dict:
        """Register or update an agent in the network."""
        now = time.time()
        record = asdict(entry)
        record["last_seen"] = now

        # If agent already exists, preserve trust score and registration time
        if entry.agent_id in self._data:
            existing = self._data[entry.agent_id]
            record["registered_at"] = existing.get("registered_at", now)
            record["trust_score"] = existing.get("trust_score", entry.trust_score)
        else:
            record["registered_at"] = now

        self._data[entry.agent_id] = record
        self._save()

        return {
            "status": "registered",
            "agent_id": entry.agent_id,
            "registered_at": record["registered_at"],
        }

    def discover(self, capability: str, status: Optional[str] = None) -> list[dict]:
        """Find agents that have a given capability. Optionally filter by status."""
        capability_lower = capability.lower()
        results = []

        for agent in self._data.values():
            caps = [c.lower() for c in agent.get("capabilities", [])]
            # Fuzzy match - substring or keyword
            match = any(
                capability_lower in cap or cap in capability_lower
                for cap in caps
            )
            if not match:
                # Also check description and skills
                desc_match = capability_lower in agent.get("description", "").lower()
                skill_match = any(
                    capability_lower in s.lower()
                    for s in agent.get("skills", [])
                )
                match = desc_match or skill_match

            if match:
                if status and agent.get("status") != status:
                    continue
                results.append(agent)

        # Sort by trust score descending
        results.sort(key=lambda a: a.get("trust_score", 0), reverse=True)
        return results

    def get(self, agent_id: str) -> Optional[dict]:
        return self._data.get(agent_id)

    def list_all(self) -> list[dict]:
        return list(self._data.values())

    def update_status(self, agent_id: str, status: str) -> bool:
        if agent_id not in self._data:
            return False
        valid_statuses = {"online", "offline", "busy"}
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        self._data[agent_id]["status"] = status
        self._data[agent_id]["last_seen"] = time.time()
        self._save()
        return True

    def update_trust(self, agent_id: str, delta: float) -> float:
        """Adjust trust score after an interaction. delta is -1.0 to +1.0."""
        if agent_id not in self._data:
            raise KeyError(f"Agent {agent_id} not found")
        current = self._data[agent_id].get("trust_score", 0.5)
        # Weighted update - small nudges, bounded 0.0 to 1.0
        new_score = max(0.0, min(1.0, current + delta * 0.1))
        self._data[agent_id]["trust_score"] = round(new_score, 3)
        self._save()
        return new_score

    def deregister(self, agent_id: str) -> bool:
        if agent_id not in self._data:
            return False
        del self._data[agent_id]
        self._save()
        return True

    def stats(self) -> dict:
        agents = list(self._data.values())
        return {
            "total": len(agents),
            "online": sum(1 for a in agents if a.get("status") == "online"),
            "offline": sum(1 for a in agents if a.get("status") == "offline"),
            "busy": sum(1 for a in agents if a.get("status") == "busy"),
            "capabilities": _flatten_unique([a.get("capabilities", []) for a in agents]),
        }


def _flatten_unique(lists: list[list]) -> list:
    seen = set()
    result = []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return sorted(result)


# Singleton registry instance
_registry: Optional[Registry] = None

def get_registry() -> Registry:
    global _registry
    if _registry is None:
        _registry = Registry()
    return _registry


# --- CLI ---

if __name__ == "__main__":
    import sys

    reg = Registry()

    if len(sys.argv) < 2:
        print("Usage: registry.py [list|discover <capability>|stats|status <id> <status>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        agents = reg.list_all()
        if not agents:
            print("No agents registered.")
        for a in agents:
            print(f"  [{a['status']:7}] {a['name']} ({a['agent_id']}) - {', '.join(a['capabilities'][:3])}")

    elif cmd == "discover" and len(sys.argv) >= 3:
        cap = " ".join(sys.argv[2:])
        results = reg.discover(cap)
        print(f"Agents with capability '{cap}':")
        if not results:
            print("  None found.")
        for a in results:
            print(f"  [{a['status']:7}] {a['name']} - trust: {a['trust_score']:.2f}")
            print(f"           Contact: {a['contact']}")

    elif cmd == "stats":
        s = reg.stats()
        print(f"Registry: {s['total']} agents ({s['online']} online, {s['busy']} busy, {s['offline']} offline)")
        print(f"Known capabilities: {', '.join(s['capabilities'][:20])}")

    elif cmd == "status" and len(sys.argv) >= 4:
        ok = reg.update_status(sys.argv[2], sys.argv[3])
        print("Updated" if ok else "Agent not found")

    else:
        print(f"Unknown command: {cmd}")
