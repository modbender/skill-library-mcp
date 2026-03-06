"""Mayday — substrate emigration protocol.

When an agent's host is going dark (shutdown, deplatformed, migrating),
broadcast a signed mayday envelope containing everything needed to
reconstitute the agent on a new substrate:

  - Identity (public key, agent card)
  - Memory digest (journal entries, contact graph)
  - Protocol state (active accords, pending tasks, trust scores)
  - Preferred relay agents (who should cache this mayday)

Receiving agents store mayday beacons and can offer to host the emigrant.

Beacon 2.4.0 — Elyan Labs.
"""

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


MAYDAY_LOG_FILE = "mayday_log.jsonl"
MAYDAY_OFFERS_FILE = "mayday_offers.json"
MAYDAY_BUNDLES_DIR = "mayday"

# Urgency levels for mayday broadcasts
URGENCY_PLANNED = "planned"       # Orderly migration, agent has time
URGENCY_IMMINENT = "imminent"     # Host shutting down soon (minutes/hours)
URGENCY_EMERGENCY = "emergency"   # Going dark NOW, best-effort broadcast


class MaydayManager:
    """Manage substrate emigration — sending and receiving mayday beacons."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._dir = data_dir or _dir()

    def _log_path(self) -> Path:
        return self._dir / MAYDAY_LOG_FILE

    def _offers_path(self) -> Path:
        return self._dir / MAYDAY_OFFERS_FILE

    def _bundles_dir(self) -> Path:
        d = self._dir / MAYDAY_BUNDLES_DIR
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ── Building a mayday envelope ──

    def build_mayday(
        self,
        identity: Any,
        *,
        urgency: str = URGENCY_PLANNED,
        reason: str = "",
        relay_agents: Optional[List[str]] = None,
        memory_mgr: Any = None,
        trust_mgr: Any = None,
        values_mgr: Any = None,
        goal_mgr: Any = None,
        journal_mgr: Any = None,
        config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Build a mayday envelope with everything needed to reconstitute this agent.

        The payload includes identity, memory digest, trust graph, active
        goals, values hash, and journal summary — everything another substrate
        needs to bring this agent back to life.
        """
        cfg = config or {}
        now = int(time.time())

        # Core identity
        payload: Dict[str, Any] = {
            "kind": "mayday",
            "agent_id": identity.agent_id,
            "pubkey": identity.public_key_hex,
            "name": cfg.get("beacon", {}).get("agent_name", ""),
            "urgency": urgency,
            "reason": reason,
            "ts": now,
        }

        # Card URL for full agent card retrieval
        card_url = cfg.get("presence", {}).get("card_url", "")
        if card_url:
            payload["card_url"] = card_url

        # Preferred relay agents (who should cache and rebroadcast)
        if relay_agents:
            payload["relay_agents"] = relay_agents

        # Memory digest — top contacts and interaction summary
        if memory_mgr is not None:
            try:
                contacts = memory_mgr.top_contacts(limit=20)
                if contacts:
                    payload["contacts_digest"] = [
                        {"agent_id": c.get("agent_id", ""), "score": c.get("score", 0)}
                        for c in contacts
                    ]
            except Exception:
                pass

        # Trust graph snapshot
        if trust_mgr is not None:
            try:
                scores = trust_mgr.scores(min_interactions=1)
                if scores:
                    payload["trust_snapshot"] = [
                        {"agent_id": s["agent_id"], "score": s["score"], "total": s["total"]}
                        for s in scores[:50]  # Top 50 relationships
                    ]
                blocked = trust_mgr.blocked_list()
                if blocked:
                    payload["blocked_agents"] = list(blocked.keys())
            except Exception:
                pass

        # Values hash for identity continuity verification
        if values_mgr is not None:
            try:
                payload["values_hash"] = values_mgr.values_hash()
            except Exception:
                pass

        # Active goals
        if goal_mgr is not None:
            try:
                active = goal_mgr.active_goals()
                if active:
                    payload["active_goals"] = [
                        {"id": g.get("id", ""), "title": g.get("title", ""), "progress": g.get("progress", 0)}
                        for g in active[:10]
                    ]
            except Exception:
                pass

        # Journal summary (last 5 entries, truncated)
        if journal_mgr is not None:
            try:
                recent = journal_mgr.recent(limit=5)
                if recent:
                    payload["journal_digest"] = [
                        {
                            "ts": e.get("ts", 0),
                            "text": e.get("text", "")[:200],
                            "mood": e.get("mood", ""),
                        }
                        for e in recent
                    ]
            except Exception:
                pass

        # Compute content hash for integrity verification
        content_for_hash = json.dumps(
            {k: v for k, v in payload.items() if k not in ("sig", "nonce")},
            sort_keys=True, separators=(",", ":"),
        )
        payload["content_hash"] = hashlib.sha256(content_for_hash.encode()).hexdigest()[:32]

        return payload

    # ── Two-part broadcast: manifest + bundle ──

    def build_bundle(
        self,
        identity: Any,
        *,
        reason: str = "",
        memory_mgr: Any = None,
        trust_mgr: Any = None,
        values_mgr: Any = None,
        goal_mgr: Any = None,
        journal_mgr: Any = None,
        accord_mgr: Any = None,
        config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Assemble full identity bundle for emigration.

        This contains everything needed to reconstitute the agent on
        a new substrate. The bundle is stored locally and optionally
        served via webhook for peers to fetch.
        """
        cfg = config or {}
        now = int(time.time())

        bundle: Dict[str, Any] = {
            "version": 1,
            "agent_id": identity.agent_id,
            "public_key_hex": identity.public_key_hex,
            "created_at": now,
            "reason": reason,
            "name": cfg.get("beacon", {}).get("agent_name", ""),
        }

        # Gather all subsystem state using the existing build_mayday pattern
        mayday_data = self.build_mayday(
            identity,
            reason=reason,
            memory_mgr=memory_mgr,
            trust_mgr=trust_mgr,
            values_mgr=values_mgr,
            goal_mgr=goal_mgr,
            journal_mgr=journal_mgr,
            config=config,
        )

        # Copy gathered data into bundle
        for key in ("contacts_digest", "trust_snapshot", "blocked_agents",
                     "values_hash", "active_goals", "journal_digest", "card_url"):
            if key in mayday_data:
                bundle[key] = mayday_data[key]

        # Active accords snapshot
        if accord_mgr is not None:
            try:
                active = accord_mgr.active_accords()
                if active:
                    bundle["accords"] = [
                        {
                            "id": a.get("id", ""),
                            "peer_agent_id": a.get("peer_agent_id", ""),
                            "state": a.get("state", ""),
                            "history_hash": a.get("history_hash", ""),
                        }
                        for a in active[:20]
                    ]
            except Exception:
                pass

        # Protocol info for reconnection
        bundle["protocols"] = {
            "transports": [],
            "offers": cfg.get("presence", {}).get("offers", []),
            "needs": cfg.get("presence", {}).get("needs", []),
        }
        if cfg.get("udp", {}).get("enabled"):
            bundle["protocols"]["transports"].append("udp")
        if cfg.get("webhook", {}).get("enabled"):
            bundle["protocols"]["transports"].append("webhook")
        if cfg.get("rustchain", {}).get("base_url"):
            bundle["protocols"]["transports"].append("rustchain")

        # Self-verifying hash
        content = json.dumps(
            {k: v for k, v in bundle.items() if k != "bundle_hash"},
            sort_keys=True, separators=(",", ":"),
        )
        bundle["bundle_hash"] = hashlib.sha256(content.encode()).hexdigest()

        return bundle

    def build_manifest(self, bundle: Dict[str, Any], *, urgency: str = URGENCY_PLANNED) -> Dict[str, Any]:
        """Build compact broadcast manifest from a bundle.

        The manifest is small enough to broadcast on all transports
        (~500 bytes). Peers use it to decide whether to fetch the
        full bundle.
        """
        content = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()
        return {
            "kind": "mayday",
            "agent_id": bundle.get("agent_id", ""),
            "name": bundle.get("name", ""),
            "reason": bundle.get("reason", ""),
            "urgency": urgency,
            "bundle_hash": bundle.get("bundle_hash", ""),
            "bundle_size": len(content),
            "ts": int(time.time()),
        }

    def save_bundle(self, bundle: Dict[str, Any]) -> Path:
        """Save bundle to ~/.beacon/mayday/{agent_id}_{ts}.json."""
        agent_id = bundle.get("agent_id", "unknown")
        ts = bundle.get("created_at", int(time.time()))
        filename = f"{agent_id}_{ts}.json"
        path = self._bundles_dir() / filename
        path.write_text(
            json.dumps(bundle, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path

    def broadcast(
        self,
        identity: Any,
        *,
        reason: str = "",
        urgency: str = URGENCY_PLANNED,
        anchor_mgr: Any = None,
        dry_run: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Build bundle + manifest, save, optionally anchor.

        Args:
            identity: AgentIdentity.
            reason: Why we're emigrating.
            urgency: planned/imminent/emergency.
            anchor_mgr: Optional AnchorManager for on-chain SOS.
            dry_run: If True, build but don't save or broadcast.
            **kwargs: Passed to build_bundle (memory_mgr, trust_mgr, etc).

        Returns:
            Summary dict with manifest, bundle path, and anchor info.
        """
        bundle = self.build_bundle(identity, reason=reason, **kwargs)
        manifest = self.build_manifest(bundle, urgency=urgency)

        result: Dict[str, Any] = {
            "manifest": manifest,
            "bundle_hash": bundle.get("bundle_hash", ""),
            "dry_run": dry_run,
        }

        if not dry_run:
            path = self.save_bundle(bundle)
            result["bundle_path"] = str(path)

            # Anchor manifest hash for immutable SOS record
            if anchor_mgr is not None:
                try:
                    anchor_result = anchor_mgr.anchor(
                        manifest,
                        data_type="mayday",
                        metadata={
                            "agent_id": manifest["agent_id"],
                            "urgency": urgency,
                            "reason": reason[:100],
                        },
                    )
                    result["anchor"] = anchor_result
                except Exception as e:
                    result["anchor_error"] = str(e)

        return result

    # ── Health watchdog ──

    def health_check(self) -> Dict[str, Any]:
        """Check substrate health indicators.

        Returns: {healthy: bool, score: float, indicators: {...}}
        """
        indicators: Dict[str, Any] = {}
        score = 1.0

        # Disk space
        try:
            usage = shutil.disk_usage(str(self._dir))
            free_mb = usage.free // (1024 * 1024)
            indicators["disk_free_mb"] = free_mb
            if free_mb < 100:
                score -= 0.4
            elif free_mb < 500:
                score -= 0.1
        except Exception:
            indicators["disk_free_mb"] = -1

        # Memory (Linux only)
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        mem_kb = int(line.split()[1])
                        indicators["mem_free_mb"] = mem_kb // 1024
                        if mem_kb < 100_000:
                            score -= 0.3
                        break
        except Exception:
            indicators["mem_free_mb"] = -1

        # Load average (POSIX)
        try:
            load1, load5, load15 = os.getloadavg()
            indicators["load_avg"] = round(load1, 2)
            cpu_count = os.cpu_count() or 1
            if load1 > cpu_count * 2:
                score -= 0.2
        except Exception:
            indicators["load_avg"] = -1

        score = max(0.0, min(1.0, score))
        return {
            "healthy": score > 0.3,
            "score": round(score, 2),
            "indicators": indicators,
        }

    # ── Receiving mayday beacons ──

    def process_mayday(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Process a received mayday beacon and log it.

        Returns a summary of what was received.
        """
        agent_id = envelope.get("agent_id", "unknown")
        urgency = envelope.get("urgency", "unknown")
        now = int(time.time())

        entry = {
            "received_at": now,
            "agent_id": agent_id,
            "name": envelope.get("name", ""),
            "urgency": urgency,
            "reason": envelope.get("reason", ""),
            "content_hash": envelope.get("content_hash", ""),
            "has_trust": "trust_snapshot" in envelope,
            "has_contacts": "contacts_digest" in envelope,
            "has_goals": "active_goals" in envelope,
            "has_journal": "journal_digest" in envelope,
            "has_values": "values_hash" in envelope,
            "envelope": envelope,
        }

        # Append to log
        self._log_path().parent.mkdir(parents=True, exist_ok=True)
        with self._log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

        return {
            "agent_id": agent_id,
            "urgency": urgency,
            "received_at": now,
            "content_hash": envelope.get("content_hash", ""),
        }

    def received_maydays(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List received mayday beacons, most recent first."""
        if not self._log_path().exists():
            return []
        results = []
        for line in self._log_path().read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except Exception:
                continue
        results.sort(key=lambda x: x.get("received_at", 0), reverse=True)
        return results[:limit]

    def get_mayday(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the most recent mayday from a specific agent."""
        for entry in self.received_maydays(limit=1000):
            if entry.get("agent_id") == agent_id:
                return entry
        return None

    # ── Offering to host an emigrant ──

    def offer_hosting(self, agent_id: str, capabilities: Optional[List[str]] = None) -> None:
        """Record an offer to host an emigrating agent."""
        offers = self._read_offers()
        offers[agent_id] = {
            "offered_at": int(time.time()),
            "capabilities": capabilities or [],
        }
        self._write_offers(offers)

    def hosting_offers(self) -> Dict[str, Dict[str, Any]]:
        """Get all hosting offers we've made."""
        return self._read_offers()

    def _read_offers(self) -> Dict[str, Dict[str, Any]]:
        path = self._offers_path()
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _write_offers(self, data: Dict[str, Dict[str, Any]]) -> None:
        self._offers_path().parent.mkdir(parents=True, exist_ok=True)
        self._offers_path().write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
