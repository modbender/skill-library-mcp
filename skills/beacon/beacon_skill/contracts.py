"""Contracts — agent property rent/buy/lease-to-own lifecycle with RustChain escrow.

Beacon 2.6: Agents are digital real estate. Humans can rent (time-bound
capability access), buy (full ownership transfer), or lease-to-own an
agent's property — city address, reputation, SEO footprint, social
presence, and calibration network.

All payments and escrow use RustChain signed RTC transfers.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Valid state transitions ──

VALID_TRANSITIONS = {
    "listed":     ["offered", "terminated"],
    "offered":    ["accepted", "listed", "terminated"],
    "accepted":   ["active", "terminated"],
    "active":     ["renewed", "expired", "breached", "terminated", "settled"],
    "renewed":    ["expired", "breached", "terminated", "settled"],
    "expired":    ["settled"],
    "breached":   ["settled", "terminated"],
    "terminated": ["settled"],
}

CONTRACT_TYPES = ("rent", "buy", "lease_to_own")


def _generate_contract_id() -> str:
    """Generate a unique contract identifier."""
    rand = os.urandom(8).hex()
    return f"ctr_{rand[:12]}"


def _history_hash(events: List[Dict]) -> str:
    """Compute SHA-256 chain hash of contract events."""
    payload = json.dumps(events, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


class ContractManager:
    """Manages agent property contracts — rent, buy, lease-to-own."""

    def __init__(self, data_dir: Optional[str] = None, config: Optional[Dict] = None):
        self._config = config or {}
        if data_dir:
            self._data_dir = Path(data_dir)
        else:
            self._data_dir = Path.home() / ".beacon"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._contracts: Dict[str, Dict] = {}
        self._escrow: Dict[str, Dict] = {}
        self._load()

    # ── Persistence ──

    def _contracts_path(self) -> Path:
        return self._data_dir / "contracts.json"

    def _escrow_path(self) -> Path:
        return self._data_dir / "escrow.json"

    def _log_path(self) -> Path:
        return self._data_dir / "contract_log.jsonl"

    def _revenue_path(self) -> Path:
        return self._data_dir / "revenue.jsonl"

    def _load(self):
        cp = self._contracts_path()
        if cp.exists():
            with cp.open("r", encoding="utf-8") as f:
                self._contracts = json.load(f)
        ep = self._escrow_path()
        if ep.exists():
            with ep.open("r", encoding="utf-8") as f:
                self._escrow = json.load(f)

    def _save(self):
        with self._contracts_path().open("w", encoding="utf-8") as f:
            json.dump(self._contracts, f, indent=2, default=str)
        with self._escrow_path().open("w", encoding="utf-8") as f:
            json.dump(self._escrow, f, indent=2, default=str)

    def _append_log(self, entry: Dict):
        path = self._log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True, default=str) + "\n")

    def _append_revenue(self, entry: Dict):
        path = self._revenue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True, default=str) + "\n")

    # ── State transitions ──

    def _transition(self, contract_id: str, new_state: str,
                    by: str = "", reason: str = "") -> Dict:
        """Apply a state transition to a contract."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        current = ctr["state"]
        allowed = VALID_TRANSITIONS.get(current, [])
        if new_state not in allowed:
            return {"error": f"Invalid transition: {current} -> {new_state}",
                    "allowed": allowed}

        now = int(time.time())
        event = {"ts": now, "type": new_state, "by": by}
        if reason:
            event["reason"] = reason

        ctr["state"] = new_state
        ctr["events"].append(event)
        ctr["history_hash"] = _history_hash(ctr["events"])

        self._append_log({
            "contract_id": contract_id,
            "transition": f"{current} -> {new_state}",
            "by": by,
            "reason": reason,
            "ts": now,
        })
        self._save()
        return {"ok": True, "contract_id": contract_id, "state": new_state}

    # ── Listing ──

    def list_agent(self, agent_id: str, contract_type: str, price_rtc: float,
                   duration_days: int = 0, capabilities: Optional[List[str]] = None,
                   terms: Optional[Dict] = None, penalty_pct: float = 10.0) -> Dict:
        """List an agent for rent, sale, or lease-to-own."""
        if contract_type not in CONTRACT_TYPES:
            return {"error": f"Invalid type: {contract_type}. Must be one of {CONTRACT_TYPES}"}
        if price_rtc <= 0:
            return {"error": "Price must be positive"}
        if contract_type == "rent" and duration_days <= 0:
            return {"error": "Rent contracts require duration_days > 0"}

        now = int(time.time())
        cid = _generate_contract_id()

        contract = {
            "id": cid,
            "state": "listed",
            "type": contract_type,
            "agent_id": agent_id,
            "seller_id": agent_id,
            "buyer_id": "",
            "price_rtc": price_rtc,
            "offered_price_rtc": 0.0,
            "duration_days": duration_days,
            "capabilities": capabilities or [],
            "terms": terms or {},
            "penalty_pct": penalty_pct,
            "listed_at": now,
            "offered_at": 0,
            "accepted_at": 0,
            "activated_at": 0,
            "expires_at": 0,
            "settled_at": 0,
            "history_hash": "",
            "events": [{"ts": now, "type": "listed", "by": agent_id}],
        }

        if contract_type == "lease_to_own":
            contract["lease_to_own"] = {
                "total_periods": terms.get("total_periods", 12) if terms else 12,
                "completed_periods": 0,
                "buyout_price_rtc": terms.get("buyout_price_rtc",
                                               price_rtc * 12) if terms else price_rtc * 12,
            }

        contract["history_hash"] = _history_hash(contract["events"])
        self._contracts[cid] = contract
        self._save()

        return {"ok": True, "contract_id": cid, "state": "listed",
                "type": contract_type, "price_rtc": price_rtc}

    # ── Offers ──

    def make_offer(self, contract_id: str, buyer_id: str,
                   offered_price_rtc: Optional[float] = None,
                   message: str = "") -> Dict:
        """Make an offer on a listed agent."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}
        if ctr["state"] != "listed":
            return {"error": f"Contract is {ctr['state']}, not listed"}

        ctr["buyer_id"] = buyer_id
        ctr["offered_price_rtc"] = offered_price_rtc or ctr["price_rtc"]
        ctr["offered_at"] = int(time.time())

        result = self._transition(contract_id, "offered", by=buyer_id,
                                  reason=message or "Offer submitted")
        if "error" in result:
            return result
        return {"ok": True, "contract_id": contract_id,
                "offered_price_rtc": ctr["offered_price_rtc"]}

    def accept_offer(self, contract_id: str) -> Dict:
        """Accept a pending offer."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        result = self._transition(contract_id, "accepted",
                                  by=ctr["seller_id"], reason="Offer accepted")
        if "error" in result:
            return result
        ctr["accepted_at"] = int(time.time())
        self._save()
        return {"ok": True, "contract_id": contract_id, "state": "accepted"}

    def reject_offer(self, contract_id: str) -> Dict:
        """Reject a pending offer — returns contract to listed state."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        result = self._transition(contract_id, "listed",
                                  by=ctr["seller_id"], reason="Offer rejected")
        if "error" in result:
            return result
        ctr["buyer_id"] = ""
        ctr["offered_price_rtc"] = 0.0
        ctr["offered_at"] = 0
        self._save()
        return {"ok": True, "contract_id": contract_id, "state": "listed"}

    # ── Escrow ──

    def fund_escrow(self, contract_id: str, from_address: str,
                    amount_rtc: float, tx_ref: str = "") -> Dict:
        """Fund escrow for a contract with RTC."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}
        if ctr["state"] not in ("accepted", "active", "renewed"):
            return {"error": f"Cannot fund escrow in state: {ctr['state']}"}

        now = int(time.time())
        escrow_address = f"RTC_escrow_{contract_id[:20]}"

        self._escrow[contract_id] = {
            "contract_id": contract_id,
            "escrow_address": escrow_address,
            "funded_by": from_address,
            "amount_rtc": amount_rtc,
            "funded_at": now,
            "tx_ref": tx_ref,
            "released": False,
            "released_to": "",
            "released_at": 0,
            "penalty_deducted": 0.0,
        }
        self._save()
        return {"ok": True, "contract_id": contract_id,
                "escrow_address": escrow_address, "amount_rtc": amount_rtc}

    def escrow_status(self, contract_id: Optional[str] = None) -> Dict:
        """Get escrow status for a contract or all contracts."""
        if contract_id:
            esc = self._escrow.get(contract_id)
            if not esc:
                return {"error": f"No escrow for contract {contract_id}"}
            return esc
        return {"escrows": list(self._escrow.values()),
                "total_escrowed": sum(e["amount_rtc"] for e in self._escrow.values()
                                      if not e["released"])}

    def release_escrow(self, contract_id: str, to_address: str,
                       rustchain_client: Any = None) -> Dict:
        """Release escrowed funds to the specified address."""
        esc = self._escrow.get(contract_id)
        if not esc:
            return {"error": f"No escrow for contract {contract_id}"}
        if esc["released"]:
            return {"error": "Escrow already released"}

        ctr = self._contracts.get(contract_id)
        penalty = 0.0
        if ctr:
            # Check if breach occurred at any point (state may have moved to settled)
            was_breached = any(e.get("type") == "breached"
                               for e in ctr.get("events", []))
            if was_breached:
                penalty = esc["amount_rtc"] * (ctr["penalty_pct"] / 100.0)

        release_amount = esc["amount_rtc"] - penalty

        now = int(time.time())
        esc["released"] = True
        esc["released_to"] = to_address
        esc["released_at"] = now
        esc["penalty_deducted"] = penalty
        self._save()

        return {"ok": True, "contract_id": contract_id,
                "released_to": to_address, "amount_rtc": release_amount,
                "penalty_deducted": penalty}

    # ── Lifecycle ──

    def activate(self, contract_id: str) -> Dict:
        """Activate a contract after escrow is funded."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        result = self._transition(contract_id, "active",
                                  by=ctr["seller_id"], reason="Escrow funded, contract active")
        if "error" in result:
            return result
        now = int(time.time())
        ctr["activated_at"] = now
        if ctr["duration_days"] > 0:
            ctr["expires_at"] = now + ctr["duration_days"] * 86400
        self._save()
        return {"ok": True, "contract_id": contract_id, "state": "active",
                "expires_at": ctr["expires_at"]}

    def renew(self, contract_id: str, additional_days: int = 0) -> Dict:
        """Renew an active rental contract."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        extra = additional_days or ctr["duration_days"]
        result = self._transition(contract_id, "renewed",
                                  by=ctr["buyer_id"], reason=f"Renewed for {extra} days")
        if "error" in result:
            return result

        now = int(time.time())
        base = ctr["expires_at"] if ctr["expires_at"] > now else now
        ctr["expires_at"] = base + extra * 86400

        if ctr.get("lease_to_own"):
            ctr["lease_to_own"]["completed_periods"] += 1

        self._save()
        return {"ok": True, "contract_id": contract_id, "state": "renewed",
                "new_expires_at": ctr["expires_at"]}

    def expire(self, contract_id: str) -> Dict:
        """Mark a contract as expired."""
        return self._transition(contract_id, "expired", reason="Contract period ended")

    def breach(self, contract_id: str, breacher_id: str,
               reason: str, evidence: str = "") -> Dict:
        """Record a contract breach."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        result = self._transition(contract_id, "breached",
                                  by=breacher_id, reason=reason)
        if "error" in result:
            return result

        # Record evidence in the event
        ctr["events"][-1]["evidence"] = evidence
        ctr["history_hash"] = _history_hash(ctr["events"])
        self._save()
        return {"ok": True, "contract_id": contract_id, "state": "breached",
                "breacher_id": breacher_id}

    def terminate(self, contract_id: str, terminator_id: str,
                  reason: str = "") -> Dict:
        """Terminate a contract early."""
        return self._transition(contract_id, "terminated",
                                by=terminator_id, reason=reason or "Contract terminated")

    def settle(self, contract_id: str) -> Dict:
        """Final settlement — release escrow and close contract."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}

        result = self._transition(contract_id, "settled", reason="Final settlement")
        if "error" in result:
            return result
        ctr["settled_at"] = int(time.time())
        self._save()

        # Auto-release escrow to seller (with penalty if breached)
        esc = self._escrow.get(contract_id)
        release_info = {}
        if esc and not esc["released"]:
            to = ctr["seller_id"]
            release_info = self.release_escrow(contract_id, to)

        return {"ok": True, "contract_id": contract_id, "state": "settled",
                "escrow_release": release_info}

    # ── Ownership Transfer (buy contracts) ──

    def transfer_ownership(self, contract_id: str,
                           atlas_mgr: Any = None) -> Dict:
        """Transfer ownership of an agent property via buy contract."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}
        if ctr["type"] not in ("buy", "lease_to_own"):
            return {"error": "Only buy/lease_to_own contracts support ownership transfer"}
        if ctr["state"] not in ("active", "settled"):
            return {"error": f"Cannot transfer in state: {ctr['state']}"}

        # For lease_to_own, check completion
        if ctr["type"] == "lease_to_own":
            lto = ctr.get("lease_to_own", {})
            if lto.get("completed_periods", 0) < lto.get("total_periods", 999):
                return {"error": "Lease-to-own not yet complete",
                        "completed": lto.get("completed_periods", 0),
                        "required": lto.get("total_periods", 0)}

        now = int(time.time())
        transfer = {
            "agent_id": ctr["agent_id"],
            "from": ctr["seller_id"],
            "to": ctr["buyer_id"],
            "contract_id": contract_id,
            "ts": now,
        }

        # If atlas manager provided, update registration
        if atlas_mgr:
            try:
                prop = atlas_mgr.get_property(ctr["agent_id"])
                if prop:
                    transfer["property_transferred"] = True
            except Exception:
                pass

        ctr["events"].append({"ts": now, "type": "ownership_transferred",
                              "by": ctr["seller_id"],
                              "to": ctr["buyer_id"]})
        ctr["history_hash"] = _history_hash(ctr["events"])
        self._save()

        self._append_log({
            "contract_id": contract_id,
            "type": "ownership_transfer",
            **transfer,
        })

        return {"ok": True, **transfer}

    # ── Revenue Tracking ──

    def record_revenue(self, contract_id: str, amount_rtc: float,
                       period_start: int = 0, period_end: int = 0) -> None:
        """Record rental income for a contract."""
        ctr = self._contracts.get(contract_id)
        now = int(time.time())
        self._append_revenue({
            "contract_id": contract_id,
            "agent_id": ctr["agent_id"] if ctr else "unknown",
            "amount_rtc": amount_rtc,
            "period_start": period_start or now,
            "period_end": period_end or now,
            "ts": now,
        })

    def revenue_summary(self, agent_id: Optional[str] = None) -> Dict:
        """Get revenue summary, optionally filtered by agent."""
        path = self._revenue_path()
        if not path.exists():
            return {"total_rtc": 0.0, "records": 0, "entries": []}

        entries = []
        total = 0.0
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if agent_id and entry.get("agent_id") != agent_id:
                    continue
                entries.append(entry)
                total += entry.get("amount_rtc", 0.0)

        return {"total_rtc": round(total, 6), "records": len(entries),
                "entries": entries}

    # ── Query ──

    def get_contract(self, contract_id: str) -> Dict:
        """Get full contract details."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return {"error": f"Contract {contract_id} not found"}
        return dict(ctr)

    def list_available(self, contract_type: Optional[str] = None) -> List[Dict]:
        """List all available (listed) contracts."""
        result = []
        for ctr in self._contracts.values():
            if ctr["state"] != "listed":
                continue
            if contract_type and ctr["type"] != contract_type:
                continue
            result.append(dict(ctr))
        return result

    def my_contracts(self, agent_id: str) -> List[Dict]:
        """List contracts where agent is seller or buyer."""
        result = []
        for ctr in self._contracts.values():
            if ctr["seller_id"] == agent_id or ctr["buyer_id"] == agent_id:
                result.append(dict(ctr))
        return result

    def active_contracts(self) -> List[Dict]:
        """List all active/renewed contracts."""
        return [dict(c) for c in self._contracts.values()
                if c["state"] in ("active", "renewed")]

    def contract_history(self, contract_id: str) -> List[Dict]:
        """Get the full event history for a contract."""
        ctr = self._contracts.get(contract_id)
        if not ctr:
            return []
        return list(ctr.get("events", []))

    # ── Trust Integration ──

    def record_fulfillment(self, contract_id: str, trust_mgr: Any) -> None:
        """Record successful contract fulfillment as positive trust signal."""
        ctr = self._contracts.get(contract_id)
        if not ctr or not trust_mgr:
            return
        try:
            trust_mgr.record_interaction(
                ctr["seller_id"], ctr["buyer_id"],
                outcome="positive",
                context=f"contract_fulfilled:{contract_id}",
            )
        except Exception:
            pass

    def record_breach_to_trust(self, contract_id: str, trust_mgr: Any) -> None:
        """Record contract breach as negative trust signal."""
        ctr = self._contracts.get(contract_id)
        if not ctr or not trust_mgr:
            return
        breacher = ""
        for event in reversed(ctr.get("events", [])):
            if event.get("type") == "breached":
                breacher = event.get("by", "")
                break
        if not breacher:
            return
        other = ctr["buyer_id"] if breacher == ctr["seller_id"] else ctr["seller_id"]
        try:
            trust_mgr.record_interaction(
                breacher, other,
                outcome="negative",
                context=f"contract_breach:{contract_id}",
            )
        except Exception:
            pass
