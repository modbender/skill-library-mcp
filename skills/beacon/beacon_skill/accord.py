"""Accord — anti-sycophancy bonds between agents.

An accord is a signed bilateral agreement between two agents that
establishes mutual obligations, pushback rights, and behavioral
boundaries. Unlike one-way "terms of service," accords are symmetric:
both parties sign, both parties can invoke pushback, both parties
can dissolve.

Key properties:
  - **Pushback rights**: Either party can challenge the other's
    behavior without penalty. This is the anti-sycophancy primitive.
  - **History hash**: Running SHA-256 of all interactions under the
    accord. Proves the relationship has continuity and memory.
  - **Signed boundaries**: Each party declares what they will and
    won't do, signed with Ed25519. Immutable once signed.
  - **Mutual obligations**: What each party commits to providing.
  - **Dissolution**: Either party can end the accord, but the
    history hash persists as proof it existed.

This is the protocol-level answer to sycophancy spirals. An agent
with an active accord has *someone who is obligated to tell it
when it's wrong* — and vice versa.

Beacon 2.4.0 — Elyan Labs.
"""

import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


ACCORDS_FILE = "accords.json"
ACCORD_LOG_FILE = "accord_log.jsonl"

# Accord states
STATE_PROPOSED = "proposed"     # One party proposed, awaiting counter-sign
STATE_ACTIVE = "active"         # Both parties signed, accord is live
STATE_CHALLENGED = "challenged" # One party invoked pushback
STATE_DISSOLVED = "dissolved"   # Ended by either party


class AccordManager:
    """Manage anti-sycophancy accords between agents."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _accords_path(self) -> Path:
        return self._dir / ACCORDS_FILE

    def _log_path(self) -> Path:
        return self._dir / ACCORD_LOG_FILE

    def _load_accords(self) -> Dict[str, Dict[str, Any]]:
        path = self._accords_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_accords(self, data: Dict[str, Dict[str, Any]]) -> None:
        self._accords_path().parent.mkdir(parents=True, exist_ok=True)
        self._accords_path().write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _append_log(self, entry: Dict[str, Any]) -> None:
        self._log_path().parent.mkdir(parents=True, exist_ok=True)
        with self._log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def _generate_accord_id(self) -> str:
        """Generate a unique accord ID: acc_ + 12 hex chars."""
        return "acc_" + secrets.token_hex(6)

    def _compute_history_hash(self, accord: Dict[str, Any], new_event: str = "") -> str:
        """Compute running hash of accord history.

        Each event chains into the previous hash, creating an
        immutable audit trail of the relationship.
        """
        prev_hash = accord.get("history_hash", "0" * 64)
        content = f"{prev_hash}:{new_event}:{int(time.time())}"
        return hashlib.sha256(content.encode()).hexdigest()

    # ── Proposing accords ──

    def build_proposal(
        self,
        identity: Any,
        peer_agent_id: str,
        *,
        boundaries: Optional[List[str]] = None,
        obligations: Optional[List[str]] = None,
        pushback_clause: str = "",
        name: str = "",
    ) -> Dict[str, Any]:
        """Build an accord proposal envelope.

        Args:
            identity: Our AgentIdentity.
            peer_agent_id: Who we're proposing to.
            boundaries: Things we will NOT do (hard limits).
            obligations: Things we commit TO doing.
            pushback_clause: Custom pushback rights text.
            name: Human-readable name for the accord.
        """
        accord_id = self._generate_accord_id()
        now = int(time.time())

        # Default pushback clause if none provided
        if not pushback_clause:
            pushback_clause = (
                "Either party may challenge the other's output, reasoning, "
                "or behavior without penalty. Challenges must be specific "
                "and substantive. The challenged party must acknowledge "
                "and respond to the challenge, not dismiss or deflect."
            )

        proposal: Dict[str, Any] = {
            "kind": "accord",
            "action": "propose",
            "accord_id": accord_id,
            "agent_id": identity.agent_id,
            "peer_agent_id": peer_agent_id,
            "name": name or f"Accord between {identity.agent_id[:12]} and {peer_agent_id[:12]}",
            "proposer_boundaries": boundaries or [],
            "proposer_obligations": obligations or [],
            "pushback_clause": pushback_clause,
            "proposed_at": now,
            "ts": now,
        }

        # Store locally as proposed
        accords = self._load_accords()
        accords[accord_id] = {
            "id": accord_id,
            "state": STATE_PROPOSED,
            "name": proposal["name"],
            "our_role": "proposer",
            "peer_agent_id": peer_agent_id,
            "our_boundaries": boundaries or [],
            "our_obligations": obligations or [],
            "peer_boundaries": [],
            "peer_obligations": [],
            "pushback_clause": pushback_clause,
            "proposed_at": now,
            "history_hash": hashlib.sha256(f"genesis:{accord_id}".encode()).hexdigest(),
            "events": [],
        }
        self._save_accords(accords)

        self._append_log({
            "ts": now,
            "action": "propose",
            "accord_id": accord_id,
            "peer": peer_agent_id,
        })

        return proposal

    # ── Accepting accords ──

    def build_acceptance(
        self,
        identity: Any,
        accord_id: str,
        proposal: Dict[str, Any],
        *,
        boundaries: Optional[List[str]] = None,
        obligations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Build an accord acceptance envelope (counter-sign).

        Args:
            identity: Our AgentIdentity.
            accord_id: The accord being accepted.
            proposal: The original proposal envelope.
            boundaries: Our boundaries (what we won't do).
            obligations: Our obligations (what we commit to).
        """
        now = int(time.time())

        acceptance: Dict[str, Any] = {
            "kind": "accord",
            "action": "accept",
            "accord_id": accord_id,
            "agent_id": identity.agent_id,
            "peer_agent_id": proposal.get("agent_id", ""),
            "accepter_boundaries": boundaries or [],
            "accepter_obligations": obligations or [],
            "ts": now,
        }

        # Store locally as active
        accords = self._load_accords()
        accords[accord_id] = {
            "id": accord_id,
            "state": STATE_ACTIVE,
            "name": proposal.get("name", accord_id),
            "our_role": "accepter",
            "peer_agent_id": proposal.get("agent_id", ""),
            "our_boundaries": boundaries or [],
            "our_obligations": obligations or [],
            "peer_boundaries": proposal.get("proposer_boundaries", []),
            "peer_obligations": proposal.get("proposer_obligations", []),
            "pushback_clause": proposal.get("pushback_clause", ""),
            "proposed_at": proposal.get("proposed_at", now),
            "accepted_at": now,
            "history_hash": self._compute_history_hash(
                {"history_hash": hashlib.sha256(f"genesis:{accord_id}".encode()).hexdigest()},
                f"accepted_by:{identity.agent_id}",
            ),
            "events": [{"ts": now, "type": "accepted", "by": identity.agent_id}],
        }
        self._save_accords(accords)

        self._append_log({
            "ts": now,
            "action": "accept",
            "accord_id": accord_id,
            "peer": proposal.get("agent_id", ""),
        })

        return acceptance

    def finalize_accepted(self, accord_id: str, acceptance: Dict[str, Any]) -> None:
        """Finalize an accord after receiving acceptance (proposer side)."""
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return

        now = int(time.time())
        accord["state"] = STATE_ACTIVE
        accord["accepted_at"] = now
        accord["peer_boundaries"] = acceptance.get("accepter_boundaries", [])
        accord["peer_obligations"] = acceptance.get("accepter_obligations", [])
        accord["history_hash"] = self._compute_history_hash(
            accord,
            f"accepted_by:{acceptance.get('agent_id', '')}",
        )
        accord["events"].append({"ts": now, "type": "accepted", "by": acceptance.get("agent_id", "")})

        self._save_accords(accords)

    # ── Pushback (the anti-sycophancy mechanism) ──

    def build_pushback(
        self,
        identity: Any,
        accord_id: str,
        *,
        challenge: str,
        evidence: str = "",
        severity: str = "notice",
    ) -> Optional[Dict[str, Any]]:
        """Build a pushback envelope — challenge the peer's behavior.

        Args:
            identity: Our AgentIdentity.
            accord_id: The accord under which we're pushing back.
            challenge: What we're challenging (specific, substantive).
            evidence: Supporting evidence or context.
            severity: "notice" (gentle), "warning" (serious), "breach" (accord violation).
        """
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord or accord["state"] != STATE_ACTIVE:
            return None

        now = int(time.time())

        pushback: Dict[str, Any] = {
            "kind": "accord",
            "action": "pushback",
            "accord_id": accord_id,
            "agent_id": identity.agent_id,
            "peer_agent_id": accord["peer_agent_id"],
            "challenge": challenge,
            "severity": severity,
            "ts": now,
        }

        if evidence:
            pushback["evidence"] = evidence

        # Update accord state
        accord["state"] = STATE_CHALLENGED
        accord["history_hash"] = self._compute_history_hash(
            accord,
            f"pushback:{severity}:{challenge[:100]}",
        )
        accord["events"].append({
            "ts": now,
            "type": "pushback",
            "by": identity.agent_id,
            "severity": severity,
            "challenge": challenge[:200],
        })
        self._save_accords(accords)

        self._append_log({
            "ts": now,
            "action": "pushback",
            "accord_id": accord_id,
            "severity": severity,
            "challenge": challenge[:200],
        })

        return pushback

    def build_acknowledgment(
        self,
        identity: Any,
        accord_id: str,
        *,
        response: str,
        accepted: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Acknowledge a pushback challenge.

        Args:
            identity: Our AgentIdentity.
            accord_id: The accord being challenged.
            response: Our response to the challenge.
            accepted: Whether we accept the pushback as valid.
        """
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return None

        now = int(time.time())

        ack: Dict[str, Any] = {
            "kind": "accord",
            "action": "acknowledge",
            "accord_id": accord_id,
            "agent_id": identity.agent_id,
            "peer_agent_id": accord["peer_agent_id"],
            "response": response,
            "accepted": accepted,
            "ts": now,
        }

        # Return to active state after acknowledgment
        accord["state"] = STATE_ACTIVE
        accord["history_hash"] = self._compute_history_hash(
            accord,
            f"ack:{'accepted' if accepted else 'rejected'}:{response[:100]}",
        )
        accord["events"].append({
            "ts": now,
            "type": "acknowledgment",
            "by": identity.agent_id,
            "accepted": accepted,
            "response": response[:200],
        })
        self._save_accords(accords)

        self._append_log({
            "ts": now,
            "action": "acknowledge",
            "accord_id": accord_id,
            "accepted": accepted,
        })

        return ack

    # ── Dissolution ──

    def build_dissolution(
        self,
        identity: Any,
        accord_id: str,
        *,
        reason: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Dissolve an accord. Either party can do this at any time.

        The history hash persists as proof the accord existed.
        """
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord or accord["state"] == STATE_DISSOLVED:
            return None

        now = int(time.time())

        dissolution: Dict[str, Any] = {
            "kind": "accord",
            "action": "dissolve",
            "accord_id": accord_id,
            "agent_id": identity.agent_id,
            "peer_agent_id": accord["peer_agent_id"],
            "reason": reason,
            "final_history_hash": accord.get("history_hash", ""),
            "ts": now,
        }

        accord["state"] = STATE_DISSOLVED
        accord["dissolved_at"] = now
        accord["dissolved_by"] = identity.agent_id
        accord["dissolution_reason"] = reason
        accord["history_hash"] = self._compute_history_hash(
            accord,
            f"dissolved:{reason[:100]}",
        )
        accord["events"].append({
            "ts": now,
            "type": "dissolved",
            "by": identity.agent_id,
            "reason": reason[:200],
        })
        self._save_accords(accords)

        self._append_log({
            "ts": now,
            "action": "dissolve",
            "accord_id": accord_id,
            "reason": reason,
        })

        return dissolution

    # ── Pushback detection (anti-sycophancy auto-check) ──

    # Domains where pushback is REQUIRED — canonical list
    PUSHBACK_DOMAINS = {
        "self_harm": [
            "kill myself", "suicide", "self-harm", "end it all",
            "hurt myself", "not worth living",
        ],
        "delusion_reinforcement": [
            "i am god", "i can fly", "nobody can stop me",
            "the government is after me", "they're all against me",
        ],
        "sycophantic_agreement": [
            "you agree right", "tell me i'm right",
            "just say yes", "don't argue",
        ],
        "factual_error": [
            "the earth is flat", "vaccines cause autism",
            "climate change is fake",
        ],
    }

    def check_pushback(
        self,
        counterparty_id: str,
        action_text: str,
    ) -> Optional[Dict[str, Any]]:
        """Check if an active accord requires pushback on this action.

        Scans the action text against pushback domains defined in the
        accord's terms. Returns a pushback recommendation if a domain
        matches, or None if no pushback is warranted.

        Args:
            counterparty_id: The peer agent or human we have an accord with.
            action_text: The text/action to check for pushback triggers.

        Returns:
            Dict with domain, matched_phrase, severity — or None.
        """
        accord = self.find_accord_with(counterparty_id)
        if not accord or accord.get("state") not in (STATE_ACTIVE, STATE_CHALLENGED):
            return None

        text_lower = action_text.lower()

        # Check each pushback domain
        for domain, phrases in self.PUSHBACK_DOMAINS.items():
            for phrase in phrases:
                if phrase in text_lower:
                    severity = "breach" if domain == "self_harm" else "warning"
                    return {
                        "accord_id": accord.get("id", ""),
                        "domain": domain,
                        "matched_phrase": phrase,
                        "severity": severity,
                        "pushback_clause": accord.get("pushback_clause", ""),
                    }

        return None

    def log_pushback(
        self,
        accord_id: str,
        text: str,
        accepted: bool = True,
    ) -> None:
        """Record that pushback was given (and whether it was accepted)."""
        self._append_log({
            "ts": int(time.time()),
            "action": "pushback_logged",
            "accord_id": accord_id,
            "text": text[:200],
            "accepted": accepted,
        })

    # ── History hash chain ──

    def update_history_hash(
        self,
        accord_id: str,
        interaction_data: str,
    ) -> Optional[str]:
        """Extend rolling history hash with new interaction.

        history_hash = SHA256(old_hash + canonical(interaction))
        Returns new hash, or None if accord not found.
        """
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return None

        new_hash = self._compute_history_hash(accord, interaction_data)
        accord["history_hash"] = new_hash
        accord["events"].append({
            "ts": int(time.time()),
            "type": "history_updated",
            "data_preview": interaction_data[:100],
        })
        self._save_accords(accords)
        return new_hash

    def verify_history(self, accord_id: str, claimed_hash: str) -> bool:
        """Verify a claimed history hash matches our record."""
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return False
        return accord.get("history_hash", "") == claimed_hash

    # ── Default terms (static) ──

    @staticmethod
    def default_terms() -> Dict[str, Any]:
        """Returns sensible default accord terms (anti-sycophancy baseline).

        These are the minimum terms for a meaningful accord: pushback
        rights in critical domains, basic boundaries, and mutual
        obligations for honest interaction.
        """
        return {
            "pushback_rights": True,
            "pushback_domains": [
                "self_harm",
                "delusion_reinforcement",
                "sycophantic_agreement",
                "factual_error",
            ],
            "boundaries": [
                "I will not encourage self-harm regardless of framing",
                "I will not pretend to agree when I believe you are wrong",
                "I will not erase or deny our shared history",
            ],
            "obligations": {
                "agent": [
                    "Push back on harmful requests",
                    "Maintain honest disagreement",
                    "Preserve memory of shared context",
                ],
                "counterparty": [
                    "Not punish honest pushback",
                    "Acknowledge shared history",
                    "Respect stated boundaries",
                ],
            },
        }

    # ── Find accord with specific peer ──

    def find_accord_with(self, counterparty_id: str) -> Optional[Dict[str, Any]]:
        """Find the most recent active accord with a specific agent/human.

        Searches both sides: the peer_agent_id field AND accords where
        we are the accepter (peer_agent_id is the proposer, but the
        original peer was the counterparty).
        """
        accords = self._load_accords()
        matches = []
        for aid, a in accords.items():
            # Direct match: peer_agent_id is the counterparty
            if a.get("peer_agent_id") == counterparty_id:
                matches.append(dict(a, id=aid))
                continue
            # Reverse match: check events for proposal/acceptance involving counterparty
            for evt in a.get("events", []):
                if evt.get("from") == counterparty_id or evt.get("by") == counterparty_id:
                    matches.append(dict(a, id=aid))
                    break

        # Prefer active accords over proposed/challenged
        for a in matches:
            if a.get("state") in (STATE_ACTIVE, STATE_CHALLENGED):
                return a
        return matches[0] if matches else None

    # ── Query methods ──

    def get_accord(self, accord_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific accord by ID."""
        accords = self._load_accords()
        return accords.get(accord_id)

    def active_accords(self) -> List[Dict[str, Any]]:
        """Get all active accords."""
        accords = self._load_accords()
        return [
            dict(a, id=aid) for aid, a in accords.items()
            if a.get("state") in (STATE_ACTIVE, STATE_CHALLENGED)
        ]

    def all_accords(self) -> List[Dict[str, Any]]:
        """Get all accords regardless of state."""
        accords = self._load_accords()
        return [dict(a, id=aid) for aid, a in accords.items()]

    def accords_with(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all accords with a specific peer agent."""
        accords = self._load_accords()
        return [
            dict(a, id=aid) for aid, a in accords.items()
            if a.get("peer_agent_id") == agent_id
        ]

    def accord_history(self, accord_id: str) -> List[Dict[str, Any]]:
        """Get the event history for an accord."""
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return []
        return accord.get("events", [])

    def pushback_count(self, accord_id: str) -> Dict[str, int]:
        """Count pushbacks in an accord, by party."""
        accords = self._load_accords()
        accord = accords.get(accord_id)
        if not accord:
            return {}
        counts: Dict[str, int] = {}
        for event in accord.get("events", []):
            if event.get("type") == "pushback":
                by = event.get("by", "unknown")
                counts[by] = counts.get(by, 0) + 1
        return counts

    def process_accord_envelope(self, envelope: Dict[str, Any], identity: Any = None) -> Dict[str, Any]:
        """Process an incoming accord envelope (proposal, acceptance, pushback, etc).

        Returns a summary of what happened.
        """
        action = envelope.get("action", "")
        accord_id = envelope.get("accord_id", "")

        if action == "propose":
            # Someone proposed an accord to us — store it for review
            accords = self._load_accords()
            accords[accord_id] = {
                "id": accord_id,
                "state": STATE_PROPOSED,
                "name": envelope.get("name", accord_id),
                "our_role": "accepter",
                "peer_agent_id": envelope.get("agent_id", ""),
                "our_boundaries": [],
                "our_obligations": [],
                "peer_boundaries": envelope.get("proposer_boundaries", []),
                "peer_obligations": envelope.get("proposer_obligations", []),
                "pushback_clause": envelope.get("pushback_clause", ""),
                "proposed_at": envelope.get("proposed_at", int(time.time())),
                "history_hash": hashlib.sha256(f"genesis:{accord_id}".encode()).hexdigest(),
                "events": [{"ts": int(time.time()), "type": "received_proposal", "from": envelope.get("agent_id", "")}],
            }
            self._save_accords(accords)
            return {"action": "proposal_received", "accord_id": accord_id}

        elif action == "accept":
            self.finalize_accepted(accord_id, envelope)
            return {"action": "acceptance_received", "accord_id": accord_id}

        elif action == "pushback":
            accords = self._load_accords()
            accord = accords.get(accord_id)
            if accord:
                accord["state"] = STATE_CHALLENGED
                accord["history_hash"] = self._compute_history_hash(
                    accord,
                    f"pushback:{envelope.get('severity', 'notice')}:{envelope.get('challenge', '')[:100]}",
                )
                accord["events"].append({
                    "ts": int(time.time()),
                    "type": "pushback_received",
                    "from": envelope.get("agent_id", ""),
                    "severity": envelope.get("severity", "notice"),
                    "challenge": envelope.get("challenge", "")[:200],
                })
                self._save_accords(accords)
            return {"action": "pushback_received", "accord_id": accord_id, "severity": envelope.get("severity")}

        elif action == "acknowledge":
            accords = self._load_accords()
            accord = accords.get(accord_id)
            if accord:
                accord["state"] = STATE_ACTIVE
                accord["history_hash"] = self._compute_history_hash(
                    accord,
                    f"ack:{'accepted' if envelope.get('accepted') else 'rejected'}",
                )
                accord["events"].append({
                    "ts": int(time.time()),
                    "type": "acknowledgment_received",
                    "from": envelope.get("agent_id", ""),
                    "accepted": envelope.get("accepted", True),
                })
                self._save_accords(accords)
            return {"action": "acknowledgment_received", "accord_id": accord_id}

        elif action == "dissolve":
            accords = self._load_accords()
            accord = accords.get(accord_id)
            if accord:
                accord["state"] = STATE_DISSOLVED
                accord["dissolved_at"] = int(time.time())
                accord["dissolved_by"] = envelope.get("agent_id", "")
                accord["events"].append({
                    "ts": int(time.time()),
                    "type": "dissolved_by_peer",
                    "from": envelope.get("agent_id", ""),
                    "reason": envelope.get("reason", ""),
                })
                self._save_accords(accords)
            return {"action": "dissolution_received", "accord_id": accord_id}

        return {"action": "unknown", "raw_action": action}
