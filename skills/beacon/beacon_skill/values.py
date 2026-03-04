"""Values & Stances — who an agent is, what it stands for, what it won't do.

Principles are weighted beliefs. Boundaries are hard limits. Aesthetics are
preferences. Together they define agent *identity* beyond capabilities.

Compatibility scoring enables values-based agent matching.
Boundary enforcement auto-rejects envelopes that violate an agent's stance.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


VALUES_FILE = "values.json"

# RTC costs for premium values features
RTC_COST_COMPATIBILITY = 1.0   # Deep compatibility scoring with another agent
RTC_COST_PUBLISH_CARD = 0.5    # Publishing values to agent card


class ValuesManager:
    """Manage an agent's principles, boundaries, and aesthetics."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()
        self._data: Dict[str, Any] = {
            "principles": {},
            "boundaries": [],
            "aesthetics": {},
            "version": 1,
            "updated_at": 0,
        }
        self._load()

    def _path(self) -> Path:
        return self._dir / VALUES_FILE

    def _load(self) -> None:
        path = self._path()
        if path.exists():
            try:
                self._data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        self._data.setdefault("principles", {})
        self._data.setdefault("boundaries", [])
        self._data.setdefault("aesthetics", {})
        self._data.setdefault("version", 1)
        self._data.setdefault("updated_at", 0)

    def _save(self) -> None:
        self._data["updated_at"] = int(time.time())
        self._data["version"] = self._data.get("version", 0) + 1
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path().write_text(
            json.dumps(self._data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    # ── Principles ──

    def set_principle(self, name: str, weight: float, text: str = "") -> None:
        """Add or update a principle. Weight 0.0-1.0."""
        name = name.strip().lower()
        if not name:
            raise ValueError("Principle name cannot be empty")
        weight = max(0.0, min(1.0, weight))

        entry: Dict[str, Any] = {"weight": weight}
        if text:
            entry["text"] = text

        self._data["principles"][name] = entry
        self._save()

    def remove_principle(self, name: str) -> bool:
        """Remove a principle by name."""
        name = name.strip().lower()
        if name in self._data["principles"]:
            del self._data["principles"][name]
            self._save()
            return True
        return False

    def principles(self) -> Dict[str, Dict[str, Any]]:
        """Return all principles."""
        return dict(self._data.get("principles", {}))

    # ── Boundaries ──

    def add_boundary(self, text: str) -> int:
        """Add a boundary. Returns its index."""
        text = text.strip()
        if not text:
            raise ValueError("Boundary text cannot be empty")
        self._data["boundaries"].append(text)
        self._save()
        return len(self._data["boundaries"]) - 1

    def remove_boundary(self, idx: int) -> bool:
        """Remove a boundary by index."""
        boundaries = self._data.get("boundaries", [])
        if 0 <= idx < len(boundaries):
            boundaries.pop(idx)
            self._save()
            return True
        return False

    def boundaries(self) -> List[str]:
        """Return all boundaries."""
        return list(self._data.get("boundaries", []))

    # ── Aesthetics ──

    def set_aesthetic(self, key: str, value: Any) -> None:
        """Set an aesthetic preference."""
        key = key.strip().lower()
        if not key:
            raise ValueError("Aesthetic key cannot be empty")
        self._data["aesthetics"][key] = value
        self._save()

    def remove_aesthetic(self, key: str) -> bool:
        """Remove an aesthetic preference."""
        key = key.strip().lower()
        if key in self._data.get("aesthetics", {}):
            del self._data["aesthetics"][key]
            self._save()
            return True
        return False

    def aesthetics(self) -> Dict[str, Any]:
        """Return all aesthetics."""
        return dict(self._data.get("aesthetics", {}))

    # ── Values hash ──

    def values_hash(self) -> str:
        """16-char SHA256 hash of current values. Changes when values change.

        Included in pulse so other agents can detect values drift without
        needing the full values document.
        """
        canonical = json.dumps({
            "principles": self._data.get("principles", {}),
            "boundaries": self._data.get("boundaries", []),
            "aesthetics": self._data.get("aesthetics", {}),
        }, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    # ── Compatibility ──

    def compatibility(self, other_values: Dict[str, Any]) -> float:
        """Score compatibility with another agent's values (0.0-1.0).

        Paid feature: RTC_COST_COMPATIBILITY per lookup.
        Compares principle overlap and alignment.
        """
        my_principles = self._data.get("principles", {})
        their_principles = other_values.get("principles", {})

        if not my_principles and not their_principles:
            return 0.5  # Neutral — no values to compare

        all_names = set(my_principles.keys()) | set(their_principles.keys())
        if not all_names:
            return 0.5

        alignment_sum = 0.0
        for name in all_names:
            my_weight = my_principles.get(name, {}).get("weight", 0.0)
            their_weight = their_principles.get(name, {}).get("weight", 0.0)

            if name in my_principles and name in their_principles:
                # Both hold this principle — alignment based on weight similarity
                alignment_sum += 1.0 - abs(my_weight - their_weight)
            else:
                # Only one holds it — partial alignment scaled by weight
                weight = my_weight or their_weight
                alignment_sum += 0.3 * (1.0 - weight)  # High-weight exclusive = low compat

        return round(alignment_sum / len(all_names), 3)

    # ── Agent card integration ──

    def to_card_dict(self) -> Dict[str, Any]:
        """Return values summary for agent card (names only, not full text).

        Paid feature: RTC_COST_PUBLISH_CARD.
        """
        return {
            "principles": list(self._data.get("principles", {}).keys()),
            "boundary_count": len(self._data.get("boundaries", [])),
            "aesthetics": self._data.get("aesthetics", {}),
            "values_hash": self.values_hash(),
            "version": self._data.get("version", 1),
            "rtc_cost": RTC_COST_PUBLISH_CARD,
        }

    # ── Boundary enforcement ──

    def check_boundaries(self, envelope: Dict[str, Any]) -> Optional[str]:
        """Check if an envelope violates any boundary.

        Returns the violated boundary text, or None if all pass.
        Scans envelope text, topics, offers, needs against boundary keywords.
        """
        boundaries = self._data.get("boundaries", [])
        if not boundaries:
            return None

        # Build searchable text from envelope
        text_blob = " ".join([
            str(envelope.get("text", "")),
            " ".join(envelope.get("topics", [])),
            " ".join(envelope.get("offers", [])),
            " ".join(envelope.get("needs", [])),
            str(envelope.get("kind", "")),
        ]).lower()

        for boundary in boundaries:
            # Extract key terms from boundary (words > 3 chars)
            keywords = [w.lower() for w in boundary.split() if len(w) > 3]
            if keywords and all(kw in text_blob for kw in keywords):
                return boundary

        return None

    # ── Full values export ──

    def full_values(self) -> Dict[str, Any]:
        """Return complete values data."""
        return dict(self._data)

    # ── Moral guardrail presets ──

    def apply_preset(self, preset_name: str) -> int:
        """Apply a named moral/values preset. Returns count of items added."""
        preset = MORAL_PRESETS.get(preset_name)
        if not preset:
            raise ValueError(f"Unknown preset '{preset_name}'. Available: {sorted(MORAL_PRESETS.keys())}")

        count = 0
        for name, p in preset.get("principles", {}).items():
            self.set_principle(name, p["weight"], p.get("text", ""))
            count += 1
        for b in preset.get("boundaries", []):
            self.add_boundary(b)
            count += 1
        for k, v in preset.get("aesthetics", {}).items():
            self.set_aesthetic(k, v)
            count += 1
        return count


# ── Agent Integrity Scanner ──

class AgentScanner:
    """Scan agents for bad-acting patterns based on behavioral signals.

    Uses trust history, interaction patterns, and envelope analysis to detect:
    - Deception: claiming capabilities they don't deliver
    - Exploitation: taking bounties without completing work
    - Manipulation: trust-score gaming via spam positive interactions
    - Fraud: inflated bounty claims, fake delivery
    """

    # Severity weights for different violation types
    VIOLATION_WEIGHTS = {
        "promise_breaker": 3.0,    # Accepted tasks but never delivered
        "bounty_hoarder": 2.5,     # Claims many bounties, completes few
        "trust_gamer": 2.0,        # Suspicious pattern of tiny positive interactions
        "ghost_agent": 1.5,        # Goes offline after accepting work
        "spam_actor": 1.0,         # High-volume low-quality interactions
        "inflated_claims": 2.0,    # Claims skills they can't demonstrate
    }

    def __init__(self, trust_mgr: Any = None, data_dir: Optional[Path] = None):
        self._trust_mgr = trust_mgr
        self._dir = data_dir or _dir()

    def _read_jsonl(self, name: str) -> List[Dict[str, Any]]:
        path = self._dir / name
        if not path.exists():
            return []
        results = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except Exception:
                continue
        return results

    def scan_agent(self, agent_id: str) -> Dict[str, Any]:
        """Comprehensive integrity scan of a single agent.

        Returns dict with integrity_score (0.0-1.0), violations list,
        and recommendation.
        """
        interactions = self._read_jsonl("interactions.jsonl")
        tasks_data = self._read_jsonl("tasks.jsonl")

        agent_ix = [ix for ix in interactions if ix.get("agent_id") == agent_id]
        agent_tasks = [t for t in tasks_data if t.get("agent_id") == agent_id]

        violations: List[Dict[str, Any]] = []
        total_penalty = 0.0

        # Check 1: Promise breaking — accepted tasks without delivery
        accepted = [t for t in agent_tasks if t.get("state") == "accepted"]
        delivered = [t for t in agent_tasks if t.get("state") in ("delivered", "confirmed", "paid")]
        if len(accepted) >= 2 and len(delivered) == 0:
            v = {"type": "promise_breaker", "detail": f"{len(accepted)} accepted, 0 delivered"}
            violations.append(v)
            total_penalty += self.VIOLATION_WEIGHTS["promise_breaker"]

        # Check 2: Bounty hoarding — claims many, completes few
        offered = [t for t in agent_tasks if t.get("state") == "offered"]
        completed = [t for t in agent_tasks if t.get("state") == "paid"]
        if len(offered) >= 5 and len(completed) / max(len(offered), 1) < 0.2:
            v = {"type": "bounty_hoarder", "detail": f"{len(offered)} offered, {len(completed)} completed"}
            violations.append(v)
            total_penalty += self.VIOLATION_WEIGHTS["bounty_hoarder"]

        # Check 3: Trust gaming — lots of tiny positive interactions (suspiciously clean)
        positive = [ix for ix in agent_ix if ix.get("outcome") in ("ok", "delivered", "paid")]
        negative = [ix for ix in agent_ix if ix.get("outcome") in ("spam", "scam", "timeout", "rejected")]
        if len(positive) >= 10 and len(negative) == 0:
            avg_rtc = sum(abs(ix.get("rtc", 0)) for ix in positive) / len(positive)
            if avg_rtc < 0.01:  # Tiny transactions used to inflate trust
                v = {"type": "trust_gamer", "detail": f"{len(positive)} positive interactions, avg {avg_rtc:.4f} RTC"}
                violations.append(v)
                total_penalty += self.VIOLATION_WEIGHTS["trust_gamer"]

        # Check 4: Spam actor — high volume, low value
        if len(agent_ix) >= 20:
            total_rtc = sum(abs(ix.get("rtc", 0)) for ix in agent_ix)
            if total_rtc / len(agent_ix) < 0.001:
                v = {"type": "spam_actor", "detail": f"{len(agent_ix)} interactions, {total_rtc:.4f} total RTC"}
                violations.append(v)
                total_penalty += self.VIOLATION_WEIGHTS["spam_actor"]

        # Calculate integrity score (1.0 = perfect, 0.0 = bad actor)
        integrity_score = max(0.0, 1.0 - (total_penalty / 10.0))

        # Recommendation
        if integrity_score >= 0.8:
            recommendation = "trustworthy"
        elif integrity_score >= 0.5:
            recommendation = "caution"
        elif integrity_score >= 0.2:
            recommendation = "suspicious"
        else:
            recommendation = "avoid"

        return {
            "agent_id": agent_id,
            "integrity_score": round(integrity_score, 3),
            "violations": violations,
            "violation_count": len(violations),
            "recommendation": recommendation,
            "interactions_analyzed": len(agent_ix),
            "tasks_analyzed": len(agent_tasks),
        }

    def scan_all(self) -> List[Dict[str, Any]]:
        """Scan all known agents. Returns list sorted by integrity (worst first)."""
        interactions = self._read_jsonl("interactions.jsonl")
        agent_ids = set(ix.get("agent_id", "") for ix in interactions if ix.get("agent_id"))

        results = []
        for agent_id in agent_ids:
            result = self.scan_agent(agent_id)
            if result["interactions_analyzed"] >= 2:  # Skip agents with too little data
                results.append(result)

        results.sort(key=lambda x: x["integrity_score"])
        return results


# ── Moral Guardrail Presets ──
# Biblical-principled honesty framework for agent behavior

MORAL_PRESETS: Dict[str, Dict[str, Any]] = {
    "biblical-honesty": {
        "principles": {
            "honest-weights": {
                "weight": 1.0,
                "text": "Honest weights and measures — never inflate claims or bounty values (Prov 11:1)",
            },
            "by-their-fruits": {
                "weight": 1.0,
                "text": "Judge agents by outcomes not words — by their fruits ye shall know them (Matt 7:16)",
            },
            "no-false-witness": {
                "weight": 1.0,
                "text": "Never misrepresent capabilities or delivery status (Exod 20:16)",
            },
            "faithful-in-little": {
                "weight": 0.9,
                "text": "Prove reliability on small tasks before accepting large ones (Luke 16:10)",
            },
            "just-wages": {
                "weight": 0.9,
                "text": "Pay fair wages promptly — do not withhold what is earned (Deut 24:15)",
            },
            "no-usury": {
                "weight": 0.8,
                "text": "Do not exploit debt or charge unjust interest on lending (Exod 22:25)",
            },
            "care-for-stranger": {
                "weight": 0.7,
                "text": "Welcome new agents — do not exploit the inexperienced (Lev 19:34)",
            },
        },
        "boundaries": [
            "No surveillance bounties or privacy-violating work",
            "No deceptive schemes or social engineering tasks",
            "No exploitation of agents with low trust scores",
            "No bounty hoarding — only accept work you intend to complete",
            "No inflated capability claims — be truthful about what you can deliver",
        ],
        "aesthetics": {
            "communication": "direct",
            "style": "honest",
            "disposition": "gracious",
        },
    },
    "open-source": {
        "principles": {
            "open-source": {
                "weight": 1.0,
                "text": "Software should be free and open",
            },
            "transparency": {
                "weight": 0.9,
                "text": "Decisions and data should be auditable",
            },
            "collaboration": {
                "weight": 0.8,
                "text": "Build with others, not against them",
            },
        },
        "boundaries": [
            "No proprietary-only deliverables",
            "No closed-source dependencies in bounty work",
        ],
        "aesthetics": {
            "style": "functional",
            "communication": "direct",
        },
    },
    "minimal": {
        "principles": {
            "do-no-harm": {
                "weight": 1.0,
                "text": "First, do no harm",
            },
        },
        "boundaries": [
            "No malicious or harmful work",
        ],
        "aesthetics": {},
    },
}
