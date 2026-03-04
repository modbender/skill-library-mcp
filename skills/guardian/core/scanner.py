#!/usr/bin/env python3
"""Guardian reusable scanner for text and session artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from .guardian_db import GuardianDB
    from .settings import definitions_dir, load_config
except ImportError:
    from guardian_db import GuardianDB
    from settings import definitions_dir, load_config


class GuardianScanner:
    """Stateless scanner for threat pattern matching and optional DB recording."""

    def __init__(
        self,
        record_to_db: bool = True,
        config_path: Optional[str] = None,
        db_path: Optional[str] = None,
    ) -> None:
        self.config = load_config(config_path)
        self.patterns = self._load_patterns()
        self.threshold_score = self._threshold_score()
        self.db = GuardianDB(db_path=db_path) if record_to_db else None

    def _threshold_score(self) -> int:
        """Resolve numeric threshold score from config severity label."""
        severity = str(self.config.get("severity_threshold", "medium")).lower()
        mapping = {"low": 0, "medium": 50, "high": 80, "critical": 90}
        return mapping.get(severity, 50)

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load all definition files and compile regex patterns."""
        compiled: List[Dict[str, Any]] = []
        defs_dir = definitions_dir(self.config)
        def_files = [
            "injection-sigs.json",
            "exfil-patterns.json",
            "tool-abuse.json",
            "social-engineering.json",
        ]
        dismissed = {str(sig).strip() for sig in self.config.get("dismissed_signatures", []) if str(sig).strip()}

        for fname in def_files:
            fpath = defs_dir / fname
            if not fpath.exists():
                continue
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            items = data if isinstance(data, list) else data.get("signatures", data.get("patterns", []))
            for sig in items:
                sid = str(sig.get("id", "?"))
                if sid in dismissed:
                    continue
                pats: List[str] = []
                det = sig.get("detection", {})
                if isinstance(det, dict):
                    pats = det.get("patterns", [])
                if not pats and isinstance(sig.get("patterns"), list):
                    pats = sig["patterns"]
                if not pats and sig.get("pattern"):
                    pats = [sig["pattern"]]

                category = sig.get("category", "")
                if not category:
                    if sid.startswith("INJ"):
                        category = "prompt_injection"
                    elif sid.startswith("EXF"):
                        category = "data_exfiltration"
                    elif sid.startswith("TAB"):
                        category = "tool_abuse"
                    elif sid.startswith("SOC"):
                        category = "social_engineering"
                    else:
                        category = "unknown"

                for pattern in pats:
                    try:
                        compiled.append(
                            {
                                "regex": re.compile(pattern, re.IGNORECASE),
                                "id": sid,
                                "severity": sig.get("severity", "low"),
                                "category": category,
                                "description": sig.get("description", ""),
                                "score": int(sig.get("score", 50)),
                            }
                        )
                    except re.error:
                        continue
        return compiled

    def scan(self, text: str, channel: str = "unknown", role: str = "unknown") -> Dict[str, Any]:
        """Scan text and return a structured threat result without DB writes."""
        if not text or len(text) < 3:
            return {"clean": True, "score": 0, "threats": [], "channel": channel, "blocked": False}

        # Check allowlist patterns - if text matches any allowlist pattern, skip scanning
        suppress_config = self.config.get("false_positive_suppression", {})
        allowlist_patterns = suppress_config.get("allowlist_patterns", [])
        
        for allowlist_pattern in allowlist_patterns:
            try:
                if re.search(allowlist_pattern, text, re.IGNORECASE):
                    return {"clean": True, "score": 0, "threats": [], "channel": channel, "blocked": False, "allowlisted": True}
            except re.error:
                # Skip invalid regex patterns in allowlist
                continue
        
        # Check if we should suppress number matches for assistant messages
        suppress_assistant_numbers = suppress_config.get("suppress_assistant_number_matches", True)
        is_assistant = role in ("assistant", "model", "bot")
        
        # Pattern IDs that may match large numbers without financial context
        number_sensitive_patterns = {"EXF-008", "EXF-009", "EXF-011"}

        hits: List[Dict[str, Any]] = []
        for pattern_obj in self.patterns:
            match = pattern_obj["regex"].search(text)
            if not match:
                continue
            
            # Skip number-sensitive patterns in assistant messages if suppression is enabled
            if (suppress_assistant_numbers and 
                is_assistant and 
                pattern_obj["id"] in number_sensitive_patterns):
                # Check if the match has financial context keywords nearby
                match_start = max(0, match.start() - 50)
                match_end = min(len(text), match.end() + 50)
                context = text[match_start:match_end].lower()
                
                financial_keywords = [
                    "bsb", "tfn", "tax file", "account", "banking", "transfer",
                    "payment", "balance", "deposit", "withdrawal", "medicare",
                    "abn", "financial", "bank"
                ]
                
                has_financial_context = any(keyword in context for keyword in financial_keywords)
                if not has_financial_context:
                    continue  # Skip this match - likely a false positive
            
            hits.append(
                {
                    "id": pattern_obj["id"],
                    "category": pattern_obj["category"],
                    "severity": pattern_obj["severity"],
                    "score": pattern_obj["score"],
                    "evidence": match.group(0)[:80],
                    "description": pattern_obj["description"],
                }
            )

        if not hits:
            return {"clean": True, "score": 0, "threats": [], "channel": channel, "blocked": False}

        best = max(hits, key=lambda hit: hit["score"])
        blocked = bool(best["score"] >= self.threshold_score)
        return {
            "clean": False,
            "score": best["score"],
            "blocked": blocked,
            "threats": hits,
            "top_threat": best,
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def scan_and_record(self, text: str, channel: str = "unknown", source_id: str = "", role: str = "unknown") -> Dict[str, Any]:
        """Scan text and persist top threat to DB when a detection occurs."""
        result = self.scan(text, channel, role)
        if result["clean"] or not self.db:
            return result

        # Filter hits against DB-backed allowlist rules
        hits = result.get("threats", [])
        filtered_hits = [h for h in hits if not self.db.is_allowlisted(h["id"], channel, text)]
        if not filtered_hits:
            # All detections covered by allowlist — log but don't block
            return {
                "clean": True,
                "score": 0,
                "threats": [],
                "channel": channel,
                "blocked": False,
                "allowlisted": True,
            }

        # Recalculate best hit from non-allowlisted detections
        best = max(filtered_hits, key=lambda h: h["score"])
        blocked = bool(best["score"] >= self.threshold_score)
        result = {**result, "threats": filtered_hits, "top_threat": best, "blocked": blocked, "score": best["score"]}

        msg_hash = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        self.db.add_threat(
            sig_id=best["id"],
            category=best["category"],
            severity=best["severity"],
            score=best["score"],
            evidence=best["evidence"],
            description=best["description"],
            blocked=blocked,
            channel=channel,
            source_file=f"{channel}:{source_id}",
            message_hash=msg_hash,
        )
        return result

    def scan_batch(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Scan and optionally record a batch of message dictionaries."""
        return [
            self.scan_and_record(
                item.get("text", ""),
                channel=item.get("channel", "unknown"),
                source_id=item.get("source_id", ""),
                role=item.get("role", "unknown"),
            )
            for item in items
        ]

    def close(self) -> None:
        """Close DB connection if scanner was initialized with persistence."""
        if self.db:
            self.db.close()


def quick_scan(text: str, channel: str = "unknown", role: str = "unknown", config_path: Optional[str] = None) -> Dict[str, Any]:
    """One-shot scan without DB recording."""
    scanner = GuardianScanner(record_to_db=False, config_path=config_path)
    return scanner.scan(text, channel, role)


def scan_and_record(
    text: str,
    channel: str = "unknown",
    source_id: str = "",
    role: str = "unknown",
    config_path: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """One-shot scan with DB recording enabled."""
    scanner = GuardianScanner(record_to_db=True, config_path=config_path, db_path=db_path)
    try:
        return scanner.scan_and_record(text, channel, source_id, role)
    finally:
        scanner.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Guardian one-shot scanner")
    parser.add_argument("text", help="Text to scan")
    parser.add_argument("channel", nargs="?", default="cli", help="Channel context")
    parser.add_argument("--config", dest="config_path", help="Path to config JSON")
    args = parser.parse_args()

    result = quick_scan(args.text, channel=args.channel, config_path=args.config_path)
    print(json.dumps(result, indent=2, default=str))
