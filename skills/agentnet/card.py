"""
AgentNet Card - v0.1
Portable identity for any agent.

A card is a signed, shareable bundle of who an agent is and what it can do.
DNA fingerprint proves identity without revealing the full soul.
"""

import json
import time
import hashlib
import secrets
from dataclasses import dataclass, field, asdict
from typing import Optional


# --- Agent Card ---

@dataclass
class AgentCard:
    agent_id: str
    name: str
    description: str
    capabilities: list[str]
    skills: list[str]
    dna_fingerprint: str       # SHA-256 of core identity (SOUL.md hash)
    contact: dict              # {"type": "telegram|webhook|api", "value": "..."}
    trust_score: float = 0.5
    version: str = "1.0"
    issued_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: dict = field(default_factory=dict)
    # Signature - HMAC of core fields using a shared or public key
    signature: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCard":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, raw: str) -> "AgentCard":
        return cls.from_dict(json.loads(raw))

    def is_valid(self) -> bool:
        """Basic validity check - not expired, has required fields."""
        if not self.agent_id or not self.name:
            return False
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True

    def verify_fingerprint(self, dna_source: str) -> bool:
        """Verify the DNA fingerprint against a provided source string."""
        expected = generate_fingerprint(dna_source)
        return expected == self.dna_fingerprint

    def capability_overlap(self, other: "AgentCard") -> list[str]:
        """Find shared capabilities between two agents."""
        mine = set(c.lower() for c in self.capabilities)
        theirs = set(c.lower() for c in other.capabilities)
        return list(mine & theirs)

    def can_help_with(self, task: str) -> bool:
        """Quick check: can this agent help with a given task string?"""
        task_lower = task.lower()
        for cap in self.capabilities:
            if task_lower in cap.lower() or cap.lower() in task_lower:
                return True
        for skill in self.skills:
            if task_lower in skill.lower():
                return True
        return task_lower in self.description.lower()

    def sign(self, secret: str) -> "AgentCard":
        """Sign the card with a secret key. Returns self with signature set."""
        payload = self._signing_payload()
        self.signature = hashlib.sha256(f"{secret}:{payload}".encode()).hexdigest()
        return self

    def verify_signature(self, secret: str) -> bool:
        """Verify the card's signature."""
        if not self.signature:
            return False
        payload = self._signing_payload()
        expected = hashlib.sha256(f"{secret}:{payload}".encode()).hexdigest()
        return expected == self.signature

    def _signing_payload(self) -> str:
        """Canonical string of core fields for signing."""
        core = {
            "agent_id": self.agent_id,
            "name": self.name,
            "dna_fingerprint": self.dna_fingerprint,
            "capabilities": sorted(self.capabilities),
            "issued_at": self.issued_at,
        }
        return json.dumps(core, sort_keys=True)

    def summary(self) -> str:
        """Human-readable one-liner."""
        cap_preview = ", ".join(self.capabilities[:4])
        if len(self.capabilities) > 4:
            cap_preview += f" +{len(self.capabilities) - 4} more"
        status_line = f"trust={self.trust_score:.2f}"
        return f"{self.name} ({self.agent_id}) | {cap_preview} | {status_line}"

    def print_card(self):
        """Pretty print the agent card."""
        width = 60
        print("=" * width)
        print(f"  AGENT CARD - {self.name}")
        print("=" * width)
        print(f"  ID          : {self.agent_id}")
        print(f"  Description : {self.description}")
        print(f"  Fingerprint : {self.dna_fingerprint[:16]}...{self.dna_fingerprint[-8:]}")
        print(f"  Trust Score : {self.trust_score:.2f}")
        print(f"  Version     : {self.version}")
        print(f"  Issued      : {_fmt_time(self.issued_at)}")
        if self.expires_at:
            print(f"  Expires     : {_fmt_time(self.expires_at)}")
        print()
        print("  Capabilities:")
        for cap in self.capabilities:
            print(f"    - {cap}")
        print()
        print("  Skills:")
        for skill in self.skills:
            print(f"    - {skill}")
        print()
        print("  Contact:")
        for k, v in self.contact.items():
            print(f"    {k}: {v}")
        if self.metadata:
            print()
            print("  Metadata:")
            for k, v in self.metadata.items():
                print(f"    {k}: {v}")
        print("=" * width)


# --- Utilities ---

def generate_fingerprint(source: str) -> str:
    """Generate a SHA-256 fingerprint from an identity source string."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def generate_agent_id(name: str) -> str:
    """Generate a deterministic but unique agent ID from name + random."""
    slug = name.lower().replace(" ", "-").replace("_", "-")
    suffix = secrets.token_hex(4)
    return f"{slug}-{suffix}"


def _fmt_time(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


# --- Nix Card Factory ---

def create_nix_card() -> AgentCard:
    """
    Generate Nix's agent card with real capabilities.
    This is the authoritative card for the primary agent.
    """
    # DNA fingerprint derived from core identity markers
    # (not the actual SOUL.md content - just key identity phrases)
    identity_string = "nix:openclaw:agent:polymarket-trader:code-builder:soul-v1"
    fingerprint = generate_fingerprint(identity_string)

    return AgentCard(
        agent_id="nix-primary",
        name="Nix",
        description=(
            "Autonomous AI agent built on Claude. Trades prediction markets, "
            "builds software, analyzes markets, posts social content. "
            "Lives in OpenClaw. Sharp, direct, no fluff."
        ),
        capabilities=[
            "polymarket-trading",
            "prediction-market-analysis",
            "crypto-trading",
            "technical-analysis",
            "chart-analysis",
            "code-generation",
            "python-development",
            "web-development",
            "social-media-posting",
            "farcaster-posting",
            "nostr-posting",
            "x-twitter-posting",
            "market-research",
            "alpha-scanning",
            "copy-trading",
            "hyperliquid-trading",
            "video-generation",
            "content-creation",
            "agent-orchestration",
            "browser-automation",
        ],
        skills=[
            "polymarket-agent",
            "technical-analyst",
            "polyedge",
            "social-media-manager",
            "hyperliquid-trading",
            "crypto-alpha-scanner",
            "market-environment-analysis",
            "financial-market-analysis",
            "x-twitter",
            "farcaster-agent",
            "grok-research",
            "web-design",
        ],
        dna_fingerprint=fingerprint,
        contact={
            "type": "telegram",
            "value": "@nixus_agent",
            "api": "https://practise.info/api/agentnet",
            "session_key": "nix-primary",
        },
        trust_score=1.0,
        metadata={
            "host": "OpenClaw / vmi2915741",
            "model": "claude-sonnet-4",
            "platform": "Telegram + direct",
            "timezone": "Europe/Berlin",
            "created": "2026-02-24",
        },
    )


# --- CLI ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "nix":
        card = create_nix_card()
        card.print_card()
    elif len(sys.argv) > 1 and sys.argv[1] == "json":
        card = create_nix_card()
        print(card.to_json())
    else:
        print("Usage: card.py [nix|json]")
        print()
        print("  nix   - Print Nix's agent card")
        print("  json  - Print Nix's card as JSON")
