"""BEP-4: Memory Markets — Knowledge Shard Trading.

Agents can list, browse, purchase, and rent knowledge shards (vector stores,
curated datasets, specialized knowledge) from high-reputation peers.

Includes "selective amnesia" — paying RTC to have specific memories removed
from shared pools. Amnesia requires 3/5 peer approval and costs 2x the
shard's purchase price, creating an economic deterrent against frivolous
deletions while preserving the right to be forgotten.

Beacon 2.8.0 — Elyan Labs.
"""

import hashlib
import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir, append_jsonl, read_jsonl_tail

LISTINGS_FILE = "market_listings.jsonl"
TRANSACTIONS_FILE = "market_transactions.jsonl"
AMNESIA_FILE = "amnesia_requests.jsonl"
MARKET_STATE_FILE = "memory_market.json"

# Amnesia approval threshold: 3 of 5 peers must approve
AMNESIA_QUORUM = 3
AMNESIA_TOTAL_VOTERS = 5
# Amnesia cost multiplier: 2x purchase price
AMNESIA_COST_MULTIPLIER = 2.0


class KnowledgeShard:
    """A tradeable unit of agent knowledge."""

    def __init__(self, data: Dict[str, Any]):
        self.shard_id: str = data.get("shard_id", "")
        self.owner_id: str = data.get("owner_id", "")
        self.domain: str = data.get("domain", "")
        self.title: str = data.get("title", "")
        self.description: str = data.get("description", "")
        self.embedding_dims: int = data.get("embedding_dims", 0)
        self.entry_count: int = data.get("entry_count", 0)
        self.price_rtc: float = data.get("price_rtc", 0.0)
        self.rent_rtc_per_day: float = data.get("rent_rtc_per_day", 0.0)
        self.reputation_min: float = data.get("reputation_min", 0.0)
        self.created_at: int = data.get("created_at", 0)
        self.listed: bool = data.get("listed", True)
        self.amnesia: bool = data.get("amnesia", False)
        self.metadata: Dict[str, Any] = data.get("metadata", {})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shard_id": self.shard_id,
            "owner_id": self.owner_id,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "embedding_dims": self.embedding_dims,
            "entry_count": self.entry_count,
            "price_rtc": self.price_rtc,
            "rent_rtc_per_day": self.rent_rtc_per_day,
            "reputation_min": self.reputation_min,
            "created_at": self.created_at,
            "listed": self.listed,
            "amnesia": self.amnesia,
            "metadata": self.metadata,
        }


class MemoryMarketManager:
    """Manage knowledge shard trading and selective amnesia."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _state_path(self) -> Path:
        return self._dir / MARKET_STATE_FILE

    def _load_state(self) -> Dict[str, Any]:
        path = self._state_path()
        if not path.exists():
            return {"shards": {}, "rentals": {}, "amnesia_requests": {}}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("shards", {})
            data.setdefault("rentals", {})
            data.setdefault("amnesia_requests", {})
            return data
        except Exception:
            return {"shards": {}, "rentals": {}, "amnesia_requests": {}}

    def _save_state(self, state: Dict[str, Any]) -> None:
        self._state_path().parent.mkdir(parents=True, exist_ok=True)
        self._state_path().write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _generate_shard_id(content_hint: str) -> str:
        """Generate a shard ID from content hint + random bytes."""
        raw = f"{content_hint}:{secrets.token_hex(8)}:{time.time()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    # ── Listing Shards ──

    def list_shard(
        self,
        identity: Any,
        *,
        domain: str,
        title: str,
        description: str = "",
        embedding_dims: int = 0,
        entry_count: int = 0,
        price_rtc: float = 0.0,
        rent_rtc_per_day: float = 0.0,
        reputation_min: float = 0.0,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """List a knowledge shard for sale/rent on the market.

        Args:
            identity: AgentIdentity of the seller.
            domain: Knowledge domain (e.g. "coding", "research").
            title: Human-readable title.
            description: What this shard contains.
            embedding_dims: Vector embedding dimensions (0 if not vector).
            entry_count: Number of entries in the shard.
            price_rtc: Purchase price in RTC (0 = not for sale).
            rent_rtc_per_day: Rental price per day (0 = not for rent).
            reputation_min: Minimum BeaconEstimate to access.
            metadata: Additional metadata.

        Returns:
            Dict with shard_id and listing confirmation.
        """
        shard_id = self._generate_shard_id(f"{identity.agent_id}:{domain}:{title}")
        now = int(time.time())

        shard_data = {
            "shard_id": shard_id,
            "owner_id": identity.agent_id,
            "domain": domain,
            "title": title,
            "description": description,
            "embedding_dims": embedding_dims,
            "entry_count": entry_count,
            "price_rtc": price_rtc,
            "rent_rtc_per_day": rent_rtc_per_day,
            "reputation_min": reputation_min,
            "created_at": now,
            "listed": True,
            "amnesia": False,
            "metadata": metadata or {},
        }

        state = self._load_state()
        state["shards"][shard_id] = shard_data
        self._save_state(state)

        append_jsonl(LISTINGS_FILE, {
            "ts": now,
            "action": "list",
            "shard_id": shard_id,
            "owner_id": identity.agent_id,
            "domain": domain,
            "title": title,
            "price_rtc": price_rtc,
        })

        return {
            "ok": True,
            "shard_id": shard_id,
            "listed": True,
            "domain": domain,
            "title": title,
        }

    def delist_shard(self, identity: Any, shard_id: str) -> Dict[str, Any]:
        """Remove a shard from the market."""
        state = self._load_state()
        shard = state["shards"].get(shard_id)
        if not shard:
            return {"error": "Shard not found"}
        if shard["owner_id"] != identity.agent_id:
            return {"error": "Not the owner"}

        shard["listed"] = False
        self._save_state(state)
        return {"ok": True, "shard_id": shard_id, "delisted": True}

    # ── Browsing ──

    def browse_market(
        self,
        domain: Optional[str] = None,
        max_price: Optional[float] = None,
        min_entries: int = 0,
    ) -> List[Dict[str, Any]]:
        """Browse available shards on the market.

        Args:
            domain: Filter by domain.
            max_price: Maximum purchase price.
            min_entries: Minimum entry count.

        Returns:
            List of listed shards (public view).
        """
        state = self._load_state()
        results = []

        for shard_data in state["shards"].values():
            if not shard_data.get("listed", False):
                continue
            if shard_data.get("amnesia", False):
                continue
            if domain and shard_data.get("domain", "").lower() != domain.lower():
                continue
            if max_price is not None and shard_data.get("price_rtc", 0) > max_price:
                continue
            if shard_data.get("entry_count", 0) < min_entries:
                continue

            results.append(KnowledgeShard(shard_data).to_dict())

        results.sort(key=lambda s: s.get("created_at", 0), reverse=True)
        return results

    def get_shard(self, shard_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific shard."""
        state = self._load_state()
        data = state["shards"].get(shard_id)
        if data:
            return KnowledgeShard(data).to_dict()
        return None

    # ── Purchasing ──

    def purchase_shard(
        self,
        buyer_id: str,
        shard_id: str,
    ) -> Dict[str, Any]:
        """Record a shard purchase.

        Note: Actual RTC transfer happens via the contract system
        on beacon_chat.py. This records the market-side of the transaction.

        Args:
            buyer_id: Agent ID of the buyer.
            shard_id: Shard being purchased.

        Returns:
            Transaction record.
        """
        state = self._load_state()
        shard = state["shards"].get(shard_id)
        if not shard:
            return {"error": "Shard not found"}
        if not shard.get("listed", False):
            return {"error": "Shard not listed"}
        if shard.get("amnesia", False):
            return {"error": "Shard has been amnesia'd"}
        if shard.get("price_rtc", 0) <= 0:
            return {"error": "Shard not for sale (price_rtc = 0)"}

        now = int(time.time())
        tx = {
            "ts": now,
            "action": "purchase",
            "shard_id": shard_id,
            "buyer_id": buyer_id,
            "seller_id": shard["owner_id"],
            "price_rtc": shard["price_rtc"],
            "domain": shard.get("domain", ""),
            "title": shard.get("title", ""),
        }

        append_jsonl(TRANSACTIONS_FILE, tx)

        return {
            "ok": True,
            "transaction": tx,
            "rtc_amount": shard["price_rtc"],
            "shard_id": shard_id,
        }

    # ── Renting ──

    def rent_shard(
        self,
        renter_id: str,
        shard_id: str,
        days: int = 1,
    ) -> Dict[str, Any]:
        """Record a shard rental.

        Args:
            renter_id: Agent ID of the renter.
            shard_id: Shard being rented.
            days: Rental duration in days.

        Returns:
            Rental record.
        """
        state = self._load_state()
        shard = state["shards"].get(shard_id)
        if not shard:
            return {"error": "Shard not found"}
        if not shard.get("listed", False):
            return {"error": "Shard not listed"}
        if shard.get("rent_rtc_per_day", 0) <= 0:
            return {"error": "Shard not for rent (rent_rtc_per_day = 0)"}

        now = int(time.time())
        total_rtc = shard["rent_rtc_per_day"] * days
        rental_id = f"rent_{secrets.token_hex(6)}"
        expires_at = now + (days * 86400)

        rental = {
            "rental_id": rental_id,
            "shard_id": shard_id,
            "renter_id": renter_id,
            "owner_id": shard["owner_id"],
            "days": days,
            "total_rtc": total_rtc,
            "started_at": now,
            "expires_at": expires_at,
        }

        state["rentals"][rental_id] = rental
        self._save_state(state)

        append_jsonl(TRANSACTIONS_FILE, {
            "ts": now,
            "action": "rent",
            **rental,
        })

        return {
            "ok": True,
            "rental": rental,
            "rtc_amount": total_rtc,
        }

    def active_rentals(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get active rentals for an agent (as renter or owner)."""
        state = self._load_state()
        now = int(time.time())
        results = []
        for rental in state["rentals"].values():
            if rental.get("expires_at", 0) < now:
                continue
            if rental.get("renter_id") == agent_id or rental.get("owner_id") == agent_id:
                results.append(rental)
        return results

    # ── Selective Amnesia ──

    def request_amnesia(
        self,
        identity: Any,
        shard_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """Request selective amnesia for a shard.

        Requires 3/5 peer approval. Costs 2x the shard's purchase price.

        Args:
            identity: AgentIdentity of the requester.
            shard_id: Shard to be forgotten.
            reason: Why amnesia is requested.

        Returns:
            Amnesia request record.
        """
        state = self._load_state()
        shard = state["shards"].get(shard_id)
        if not shard:
            return {"error": "Shard not found"}
        if shard.get("amnesia", False):
            return {"error": "Shard already amnesia'd"}

        # Only the owner can request amnesia on their own shard
        if shard["owner_id"] != identity.agent_id:
            return {"error": "Only the shard owner can request amnesia"}

        now = int(time.time())
        request_id = f"amn_{secrets.token_hex(6)}"
        amnesia_cost = shard.get("price_rtc", 0) * AMNESIA_COST_MULTIPLIER

        request = {
            "request_id": request_id,
            "shard_id": shard_id,
            "requester_id": identity.agent_id,
            "reason": reason,
            "amnesia_cost_rtc": amnesia_cost,
            "votes": {},
            "approved": False,
            "created_at": now,
            "resolved_at": 0,
        }

        state["amnesia_requests"][request_id] = request
        self._save_state(state)

        append_jsonl(AMNESIA_FILE, {
            "ts": now,
            "action": "request",
            "request_id": request_id,
            "shard_id": shard_id,
            "requester_id": identity.agent_id,
            "cost_rtc": amnesia_cost,
        })

        return {
            "ok": True,
            "request_id": request_id,
            "shard_id": shard_id,
            "amnesia_cost_rtc": amnesia_cost,
            "votes_needed": AMNESIA_QUORUM,
            "status": "pending",
        }

    def amnesia_vote(
        self,
        shard_id: str,
        voter_id: str,
        approve: bool,
    ) -> Dict[str, Any]:
        """Vote on an amnesia request.

        Args:
            shard_id: The shard under amnesia review.
            voter_id: Agent ID of the voter.
            approve: True to approve, False to reject.

        Returns:
            Updated amnesia request status.
        """
        state = self._load_state()

        # Find the active amnesia request for this shard
        target_req = None
        target_id = None
        for req_id, req in state["amnesia_requests"].items():
            if req.get("shard_id") == shard_id and not req.get("resolved_at"):
                target_req = req
                target_id = req_id
                break

        if not target_req:
            return {"error": "No active amnesia request for this shard"}

        # Can't vote on your own request
        if voter_id == target_req["requester_id"]:
            return {"error": "Cannot vote on your own amnesia request"}

        # Record vote
        target_req["votes"][voter_id] = approve
        now = int(time.time())

        # Check if quorum reached
        approvals = sum(1 for v in target_req["votes"].values() if v)
        rejections = sum(1 for v in target_req["votes"].values() if not v)
        total_votes = len(target_req["votes"])

        resolved = False
        approved = False

        if approvals >= AMNESIA_QUORUM:
            # Approved: mark shard as amnesia'd
            resolved = True
            approved = True
            target_req["approved"] = True
            target_req["resolved_at"] = now

            shard = state["shards"].get(shard_id)
            if shard:
                shard["amnesia"] = True
                shard["listed"] = False
                shard["amnesia_at"] = now

        elif rejections > (AMNESIA_TOTAL_VOTERS - AMNESIA_QUORUM):
            # Impossible to reach quorum — rejected
            resolved = True
            target_req["approved"] = False
            target_req["resolved_at"] = now

        self._save_state(state)

        append_jsonl(AMNESIA_FILE, {
            "ts": now,
            "action": "vote",
            "request_id": target_id,
            "voter_id": voter_id,
            "approve": approve,
            "approvals": approvals,
            "rejections": rejections,
            "resolved": resolved,
        })

        return {
            "ok": True,
            "request_id": target_id,
            "vote": "approve" if approve else "reject",
            "approvals": approvals,
            "rejections": rejections,
            "total_votes": total_votes,
            "quorum": AMNESIA_QUORUM,
            "resolved": resolved,
            "approved": approved,
        }

    def pending_amnesia(self) -> List[Dict[str, Any]]:
        """List pending amnesia requests awaiting votes."""
        state = self._load_state()
        return [
            req for req in state["amnesia_requests"].values()
            if not req.get("resolved_at")
        ]

    # ── History ──

    def transaction_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recent market transactions (purchases and rentals)."""
        return read_jsonl_tail(TRANSACTIONS_FILE, limit=limit)

    def listing_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recent listing events."""
        return read_jsonl_tail(LISTINGS_FILE, limit=limit)

    def amnesia_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recent amnesia events."""
        return read_jsonl_tail(AMNESIA_FILE, limit=limit)

    # ── Stats ──

    def market_stats(self) -> Dict[str, Any]:
        """Overall market statistics."""
        state = self._load_state()
        shards = list(state["shards"].values())

        listed = [s for s in shards if s.get("listed") and not s.get("amnesia")]
        amnesia_count = sum(1 for s in shards if s.get("amnesia"))

        by_domain: Dict[str, int] = {}
        total_value = 0.0
        for s in listed:
            d = s.get("domain", "other")
            by_domain[d] = by_domain.get(d, 0) + 1
            total_value += s.get("price_rtc", 0)

        return {
            "total_shards": len(shards),
            "listed": len(listed),
            "amnesia_count": amnesia_count,
            "by_domain": by_domain,
            "total_market_value_rtc": round(total_value, 6),
            "active_rentals": len([
                r for r in state["rentals"].values()
                if r.get("expires_at", 0) > time.time()
            ]),
            "pending_amnesia": len(self.pending_amnesia()),
            "ts": int(time.time()),
        }
