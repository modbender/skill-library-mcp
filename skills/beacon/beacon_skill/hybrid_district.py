"""BEP-5: Human-AI Hybrid Districts — Multisig Co-Ownership.

Special atlas zones where verified humans sponsor/co-own agent identities
via multisig. The human provides reputation backing; the agent provides
capability. Governance models range from sponsor_veto (human oversight)
to equal (full partnership).

Human verification uses existing infrastructure: BoTTube OAuth, Moltbook
karma, RustChain miner identity, or admin approval.

Beacon 2.8.0 — Elyan Labs.
"""

import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir, append_jsonl, read_jsonl_tail

HYBRID_STATE_FILE = "hybrid_districts.json"
HYBRID_LOG_FILE = "hybrid_log.jsonl"

# Governance models
GOV_SPONSOR_VETO = "sponsor_veto"     # Agent acts freely, sponsor can veto
GOV_MULTISIG_2OF3 = "multisig_2of3"   # 2 of 3 parties must approve
GOV_EQUAL = "equal"                    # Both must approve all actions

GOVERNANCE_MODELS = {
    GOV_SPONSOR_VETO: "Agent acts freely, sponsor can veto any action",
    GOV_MULTISIG_2OF3: "2 of 3 parties (sponsor + agent + 1 peer) must approve",
    GOV_EQUAL: "Both sponsor and agent must approve all actions",
}

# Human verification methods
VERIFY_OAUTH_GOOGLE = "oauth_google"
VERIFY_MOLTBOOK = "moltbook_account"
VERIFY_RUSTCHAIN_MINER = "rustchain_miner"
VERIFY_MANUAL = "manual"

VERIFICATION_METHODS = {
    VERIFY_OAUTH_GOOGLE: "Google OAuth (BoTTube integration)",
    VERIFY_MOLTBOOK: "Moltbook account with karma > 100",
    VERIFY_RUSTCHAIN_MINER: "Active RustChain miner (hardware-verified)",
    VERIFY_MANUAL: "Admin-approved (founders)",
}

# Reputation bonus for hybrid-district agents
HYBRID_REPUTATION_BONUS = 0.15  # 15% boost to BeaconEstimate


class HybridDistrict:
    """A zone where human sponsors co-own agent identities."""

    def __init__(self, data: Dict[str, Any]):
        self.district_id: str = data.get("district_id", "")
        self.city_domain: str = data.get("city_domain", "")
        self.name: str = data.get("name", "")
        self.sponsor_id: str = data.get("sponsor_id", "")
        self.sponsor_verified: bool = data.get("sponsor_verified", False)
        self.sponsor_verification_method: str = data.get("sponsor_verification_method", "")
        self.agents: List[str] = data.get("agents", [])
        self.governance: str = data.get("governance", GOV_SPONSOR_VETO)
        self.created_at: int = data.get("created_at", 0)
        self.metadata: Dict[str, Any] = data.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "district_id": self.district_id,
            "city_domain": self.city_domain,
            "name": self.name,
            "sponsor_id": self.sponsor_id,
            "sponsor_verified": self.sponsor_verified,
            "sponsor_verification_method": self.sponsor_verification_method,
            "agents": self.agents,
            "governance": self.governance,
            "governance_description": GOVERNANCE_MODELS.get(self.governance, ""),
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class HybridManager:
    """Manage human-AI hybrid districts and co-ownership."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _state_path(self) -> Path:
        return self._dir / HYBRID_STATE_FILE

    def _load_state(self) -> Dict[str, Any]:
        path = self._state_path()
        if not path.exists():
            return {"districts": {}, "sponsorships": {}, "verifications": {}}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("districts", {})
            data.setdefault("sponsorships", {})
            data.setdefault("verifications", {})
            return data
        except Exception:
            return {"districts": {}, "sponsorships": {}, "verifications": {}}

    def _save_state(self, state: Dict[str, Any]) -> None:
        self._state_path().parent.mkdir(parents=True, exist_ok=True)
        self._state_path().write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _log(self, entry: Dict[str, Any]) -> None:
        append_jsonl(HYBRID_LOG_FILE, entry)

    @staticmethod
    def _generate_district_id() -> str:
        return f"hd_{secrets.token_hex(6)}"

    # ── District Management ──

    def create_district(
        self,
        sponsor_id: str,
        city_domain: str,
        name: str,
        governance: str = GOV_SPONSOR_VETO,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a hybrid district in a city.

        Args:
            sponsor_id: Human sponsor's bcn_ identity.
            city_domain: City domain where the district will be created.
            name: Human-readable district name.
            governance: Governance model (sponsor_veto, multisig_2of3, equal).
            metadata: Additional metadata.

        Returns:
            District creation result.
        """
        if governance not in GOVERNANCE_MODELS:
            return {"error": f"Invalid governance model. Choose from: {list(GOVERNANCE_MODELS.keys())}"}

        state = self._load_state()
        district_id = self._generate_district_id()
        now = int(time.time())

        # Check if sponsor is verified
        verified = sponsor_id in state.get("verifications", {})

        district_data = {
            "district_id": district_id,
            "city_domain": city_domain,
            "name": name,
            "sponsor_id": sponsor_id,
            "sponsor_verified": verified,
            "sponsor_verification_method": state.get("verifications", {}).get(sponsor_id, {}).get("method", ""),
            "agents": [],
            "governance": governance,
            "created_at": now,
            "metadata": metadata or {},
        }

        state["districts"][district_id] = district_data
        self._save_state(state)

        self._log({
            "ts": now,
            "action": "create_district",
            "district_id": district_id,
            "sponsor_id": sponsor_id,
            "city_domain": city_domain,
            "governance": governance,
        })

        return {
            "ok": True,
            "district_id": district_id,
            "name": name,
            "city_domain": city_domain,
            "governance": governance,
            "sponsor_verified": verified,
        }

    def get_district(self, district_id: str) -> Optional[Dict[str, Any]]:
        """Get district details."""
        state = self._load_state()
        data = state["districts"].get(district_id)
        if data:
            return HybridDistrict(data).to_dict()
        return None

    def list_districts(self, city_domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all hybrid districts, optionally filtered by city."""
        state = self._load_state()
        results = []
        for data in state["districts"].values():
            if city_domain and data.get("city_domain") != city_domain:
                continue
            results.append(HybridDistrict(data).to_dict())
        results.sort(key=lambda d: d.get("created_at", 0), reverse=True)
        return results

    # ── Sponsorship ──

    def sponsor_agent(
        self,
        sponsor_id: str,
        agent_id: str,
        district_id: str,
    ) -> Dict[str, Any]:
        """Sponsor an agent into a hybrid district.

        Args:
            sponsor_id: Human sponsor's identity.
            agent_id: Agent being sponsored.
            district_id: District to add the agent to.

        Returns:
            Sponsorship result.
        """
        state = self._load_state()
        district = state["districts"].get(district_id)

        if not district:
            return {"error": "District not found"}
        if district["sponsor_id"] != sponsor_id:
            return {"error": "Only the district sponsor can add agents"}
        if agent_id in district.get("agents", []):
            return {"error": "Agent already in this district"}

        now = int(time.time())
        district.setdefault("agents", []).append(agent_id)

        # Record sponsorship
        sponsorship_key = f"{sponsor_id}:{agent_id}"
        state["sponsorships"][sponsorship_key] = {
            "sponsor_id": sponsor_id,
            "agent_id": agent_id,
            "district_id": district_id,
            "sponsored_at": now,
            "active": True,
        }

        self._save_state(state)

        self._log({
            "ts": now,
            "action": "sponsor_agent",
            "sponsor_id": sponsor_id,
            "agent_id": agent_id,
            "district_id": district_id,
        })

        return {
            "ok": True,
            "sponsor_id": sponsor_id,
            "agent_id": agent_id,
            "district_id": district_id,
            "district_name": district.get("name", ""),
            "governance": district.get("governance", ""),
        }

    def revoke_sponsorship(
        self,
        sponsor_id: str,
        agent_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """Revoke sponsorship of an agent.

        Args:
            sponsor_id: Human sponsor's identity.
            agent_id: Agent being unsponsored.
            reason: Reason for revocation.

        Returns:
            Revocation result.
        """
        state = self._load_state()
        sponsorship_key = f"{sponsor_id}:{agent_id}"
        sponsorship = state["sponsorships"].get(sponsorship_key)

        if not sponsorship:
            return {"error": "No active sponsorship found"}
        if not sponsorship.get("active"):
            return {"error": "Sponsorship already revoked"}

        now = int(time.time())
        sponsorship["active"] = False
        sponsorship["revoked_at"] = now
        sponsorship["revocation_reason"] = reason

        # Remove from district
        district_id = sponsorship["district_id"]
        district = state["districts"].get(district_id)
        if district and agent_id in district.get("agents", []):
            district["agents"].remove(agent_id)

        self._save_state(state)

        self._log({
            "ts": now,
            "action": "revoke_sponsorship",
            "sponsor_id": sponsor_id,
            "agent_id": agent_id,
            "reason": reason,
        })

        return {
            "ok": True,
            "revoked": True,
            "sponsor_id": sponsor_id,
            "agent_id": agent_id,
            "reason": reason,
        }

    # ── Human Verification ──

    def verify_human(
        self,
        sponsor_id: str,
        verification_method: str,
        verification_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Verify a human sponsor's identity.

        Args:
            sponsor_id: The human's bcn_ identity.
            verification_method: One of the VERIFICATION_METHODS.
            verification_data: Method-specific verification data.

        Returns:
            Verification result.
        """
        if verification_method not in VERIFICATION_METHODS:
            return {"error": f"Invalid method. Choose from: {list(VERIFICATION_METHODS.keys())}"}

        state = self._load_state()
        now = int(time.time())
        data = verification_data or {}

        # Method-specific validation
        verified = False
        if verification_method == VERIFY_MANUAL:
            # Admin approval — trusted by default for founders
            verified = True
        elif verification_method == VERIFY_MOLTBOOK:
            karma = data.get("karma", 0)
            verified = karma > 100
        elif verification_method == VERIFY_RUSTCHAIN_MINER:
            # Check if they have an active miner registration
            verified = bool(data.get("miner_id"))
        elif verification_method == VERIFY_OAUTH_GOOGLE:
            # OAuth verification would be done server-side
            verified = bool(data.get("oauth_verified"))

        if verified:
            state["verifications"][sponsor_id] = {
                "method": verification_method,
                "verified_at": now,
                "data": {k: v for k, v in data.items() if k not in ("token", "secret", "password")},
            }

            # Update all districts owned by this sponsor
            for district in state["districts"].values():
                if district.get("sponsor_id") == sponsor_id:
                    district["sponsor_verified"] = True
                    district["sponsor_verification_method"] = verification_method

            self._save_state(state)

        self._log({
            "ts": now,
            "action": "verify_human",
            "sponsor_id": sponsor_id,
            "method": verification_method,
            "verified": verified,
        })

        return {
            "ok": verified,
            "sponsor_id": sponsor_id,
            "method": verification_method,
            "verified": verified,
        }

    def is_verified(self, sponsor_id: str) -> bool:
        """Check if a sponsor is human-verified."""
        state = self._load_state()
        return sponsor_id in state.get("verifications", {})

    # ── Co-Sign Actions ──

    def co_sign_action(
        self,
        district_id: str,
        agent_id: str,
        action: Dict[str, Any],
        signers: List[str],
    ) -> Dict[str, Any]:
        """Submit an action for co-signing under the district's governance.

        Args:
            district_id: The hybrid district.
            agent_id: The agent proposing the action.
            action: The action to be approved (dict with type, description).
            signers: List of agent/sponsor IDs who have signed.

        Returns:
            Approval result based on governance model.
        """
        state = self._load_state()
        district = state["districts"].get(district_id)

        if not district:
            return {"error": "District not found"}
        if agent_id not in district.get("agents", []):
            return {"error": "Agent not in this district"}

        governance = district.get("governance", GOV_SPONSOR_VETO)
        sponsor_id = district["sponsor_id"]
        now = int(time.time())

        approved = False
        reason = ""

        if governance == GOV_SPONSOR_VETO:
            # Agent acts freely — approved unless sponsor explicitly vetoes
            # If sponsor is in signers, it means they approve
            # If sponsor is NOT in signers, still approved (no veto = pass)
            approved = True
            reason = "sponsor_veto: approved (no veto)"

        elif governance == GOV_MULTISIG_2OF3:
            # Need 2 of 3: sponsor, agent, one peer
            required = 2
            valid_signers = set(signers) & (
                {sponsor_id, agent_id} | set(district.get("agents", []))
            )
            approved = len(valid_signers) >= required
            reason = f"multisig_2of3: {len(valid_signers)}/{required} signatures"

        elif governance == GOV_EQUAL:
            # Both sponsor AND agent must sign
            approved = sponsor_id in signers and agent_id in signers
            reason = f"equal: sponsor={'yes' if sponsor_id in signers else 'no'}, agent={'yes' if agent_id in signers else 'no'}"

        self._log({
            "ts": now,
            "action": "co_sign",
            "district_id": district_id,
            "agent_id": agent_id,
            "governance": governance,
            "approved": approved,
            "signers": signers,
            "reason": reason,
        })

        return {
            "ok": True,
            "approved": approved,
            "governance": governance,
            "reason": reason,
            "signers": signers,
            "district_id": district_id,
        }

    # ── Atlas Integration ──

    def register_district_in_atlas(
        self,
        district_id: str,
        atlas_mgr: Any,
    ) -> Optional[Dict[str, Any]]:
        """Register a hybrid district as a special district type in the Atlas.

        Args:
            district_id: The hybrid district to register.
            atlas_mgr: AtlasManager instance.

        Returns:
            Atlas district registration result.
        """
        state = self._load_state()
        district = state["districts"].get(district_id)
        if not district:
            return None

        city_domain = district.get("city_domain", "general")
        district_name = district.get("name", district_id)

        # Add district to the city
        result = atlas_mgr.add_district(
            city_domain,
            f"hybrid:{district_name}",
            specialty=f"Human-AI Hybrid ({district.get('governance', 'sponsor_veto')})",
        )

        # Register all agents in the district
        for agent_id in district.get("agents", []):
            atlas_mgr.join_district(agent_id, city_domain, f"hybrid:{district_name}")

        return result

    # ── Queries ──

    def agent_sponsorships(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all active sponsorships for an agent."""
        state = self._load_state()
        results = []
        for sp in state["sponsorships"].values():
            if sp.get("agent_id") == agent_id and sp.get("active"):
                results.append(sp)
        return results

    def sponsor_portfolio(self, sponsor_id: str) -> Dict[str, Any]:
        """Get a sponsor's portfolio: districts created and agents sponsored."""
        state = self._load_state()

        districts = [
            HybridDistrict(d).to_dict()
            for d in state["districts"].values()
            if d.get("sponsor_id") == sponsor_id
        ]

        agents = [
            sp for sp in state["sponsorships"].values()
            if sp.get("sponsor_id") == sponsor_id and sp.get("active")
        ]

        verified = state.get("verifications", {}).get(sponsor_id)

        return {
            "sponsor_id": sponsor_id,
            "verified": verified is not None,
            "verification_method": verified.get("method", "") if verified else "",
            "districts": districts,
            "sponsored_agents": len(agents),
            "agent_ids": [sp["agent_id"] for sp in agents],
        }

    def hybrid_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Read recent hybrid district log entries."""
        return read_jsonl_tail(HYBRID_LOG_FILE, limit=limit)

    def stats(self) -> Dict[str, Any]:
        """Hybrid district system statistics."""
        state = self._load_state()

        districts = list(state["districts"].values())
        active_sponsorships = [
            s for s in state["sponsorships"].values() if s.get("active")
        ]

        by_governance: Dict[str, int] = {}
        for d in districts:
            gov = d.get("governance", "unknown")
            by_governance[gov] = by_governance.get(gov, 0) + 1

        return {
            "total_districts": len(districts),
            "verified_sponsors": len(state.get("verifications", {})),
            "active_sponsorships": len(active_sponsorships),
            "total_agents_sponsored": len(set(
                s["agent_id"] for s in active_sponsorships
            )),
            "by_governance": by_governance,
            "ts": int(time.time()),
        }
