"""
NIMA Lucid Memory Moments — Proposal #8
========================================
Surface memories unbidden — like consciousness does.

Not when asked. Just: "hey, this just came to me."

The system selects emotionally-resonant memories from 3–30 days ago,
enriches them via LLM into natural-sounding flashbacks, and delivers
them via a user-supplied callback.

Usage:
    from nima_core.lucid_moments import LucidMoments

    def send_to_user(text: str):
        print(f"💭 {text}")

    lm = LucidMoments(
        db_path="~/.nima/memory/ladybug.lbug",
        llm_base_url="https://api.openai.com/v1",
        llm_api_key="sk-...",
        llm_model="gpt-4o-mini",
        delivery_callback=send_to_user,
        quiet_hours=(23, 9),    # quiet from 11 PM to 9 AM
        min_gap_hours=4,        # at most once per 4 hours
    )

    # Run this on a heartbeat / periodic cron
    delivered = lm.maybe_surface()
    if delivered:
        print("A memory just surfaced")
"""

import json
import logging
import math
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import real_ladybug as lb
    HAS_LADYBUG = True
except ImportError:
    HAS_LADYBUG = False


# Keywords that indicate a memory should never be surfaced
_TRAUMA_KEYWORDS = [
    "died", "death", "dead", "dying", "killed", "murdered", "suicide",
    "abuse", "abused", "trauma", "traumatic", "ptsd", "rape", "assault",
    "depressed", "depression", "hopeless", "worthless", "hate myself",
    "self-harm", "cutting", "overdose", "hospitalized", "crisis",
    "fired", "bankrupt", "catastrophic", "destroyed", "ruined",
]


class LucidMoments:
    """
    Selects and surfaces emotionally resonant memories as spontaneous flashbacks.

    Memory selection criteria:
    - Age: 3–30 days old (configurable)
    - Layer: contemplation > episodic > semantic
    - Content: emotional richness, not previously surfaced recently
    - Safety: no trauma keywords, positive/warm affect only

    Enrichment: raw memory → natural-sounding "this just came to me" message via LLM.

    Delivery: via any callback you supply (Telegram, email, webhook, print…).
    """

    DEFAULT_STATE_PATH = "~/.nima/memory/lucid_moments_state.json"

    def __init__(
        self,
        db_path: Optional[str] = None,
        llm_base_url: str = "https://api.openai.com/v1",
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        delivery_callback: Optional[Callable[[str], None]] = None,
        state_path: Optional[str] = None,
        suppression_path: Optional[str] = None,
        quiet_hours: Tuple[int, int] = (23, 9),
        min_gap_hours: float = 4.0,
        max_per_day: int = 3,
        ideal_age_range: Tuple[float, float] = (3.0, 30.0),
        warm_keywords: Optional[List[str]] = None,
        persona_prompt: Optional[str] = None,
        trauma_keywords: Optional[List[str]] = None,
    ):
        """
        Args:
            db_path:            LadybugDB path (.lbug). Required for memory selection.
            llm_base_url:       OpenAI-compatible LLM endpoint.
            llm_api_key:        API key. Falls back to OPENAI_API_KEY env var.
            llm_model:          Model for enrichment (a small/fast model is fine).
            delivery_callback:  Function to call with the enriched flashback text.
                                If None, the text is returned but not delivered.
            state_path:         Path to persist surfacing state (prevents repeats).
            suppression_path:   Path to JSON file of suppressed memory IDs.
            quiet_hours:        (start_hour, end_hour) when surfacing is disabled.
                                E.g. (23, 9) = quiet from 11 PM to 9 AM.
            min_gap_hours:      Minimum hours between lucid moments.
            max_per_day:        Maximum lucid moments per day.
            ideal_age_range:    (min_days, max_days) for memory age scoring.
            warm_keywords:      Extra keywords that boost a memory's candidacy score.
            persona_prompt:     System-level persona instruction for the enrichment LLM.
                                Defaults to a generic "you're an AI with deep memory" prompt.
            trauma_keywords:    Override the default list of keywords that block surfacing.
        """
        self.db_path = str(Path(db_path).expanduser()) if db_path else None
        self.llm_base_url = llm_base_url.rstrip("/")
        self.llm_api_key = llm_api_key or os.environ.get("OPENAI_API_KEY", "")
        self.llm_model = llm_model
        self.delivery_callback = delivery_callback
        self.state_path = Path(state_path or self.DEFAULT_STATE_PATH).expanduser()
        self.suppression_path = Path(suppression_path).expanduser() if suppression_path else None
        self.quiet_hours = quiet_hours
        self.min_gap_hours = min_gap_hours
        self.max_per_day = max_per_day
        self.ideal_age_min, self.ideal_age_max = ideal_age_range
        self.warm_keywords = warm_keywords or [
            "built", "created", "realized", "understood", "love", "thank",
            "excited", "beautiful", "proud", "together", "feel", "moment",
            "discovered", "insight", "connection", "memory",
        ]
        self.persona_prompt = persona_prompt or (
            "You are an AI assistant with deep memory. A memory just surfaced spontaneously."
        )
        self.trauma_keywords = trauma_keywords or _TRAUMA_KEYWORDS

    # ── State ─────────────────────────────────────────────────────────────────

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text())
            except Exception:
                pass
        return {"last_surfaced_at": None, "surfaced_ids": [], "count_today": 0, "last_day": None}

    def _save_state(self, state: dict):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2))

    def _get_suppressed_ids(self) -> set:
        if self.suppression_path and self.suppression_path.exists():
            try:
                return set(str(k) for k in json.loads(self.suppression_path.read_text()).keys())
            except Exception:
                pass
        return set()

    # ── Timing Gate ───────────────────────────────────────────────────────────

    def _is_good_timing(self) -> Tuple[bool, str]:
        """Return (ok, reason) for whether now is a good time to surface."""
        now = datetime.now()
        hour = now.hour
        qs, qe = self.quiet_hours
        in_quiet = (qs <= 23 and qe <= 23 and (hour >= qs or hour < qe))
        if qs > qe:  # wraps midnight
            in_quiet = hour >= qs or hour < qe
        else:
            in_quiet = qs <= hour < qe

        if in_quiet:
            return False, "quiet hours"

        state = self._load_state()
        today = now.strftime("%Y-%m-%d")
        if state.get("last_day") != today:
            state["count_today"] = 0
            state["last_day"] = today
            self._save_state(state)

        if state.get("count_today", 0) >= self.max_per_day:
            return False, "daily limit reached"

        last = state.get("last_surfaced_at")
        if last:
            try:
                hours_since = (now - datetime.fromisoformat(last)).total_seconds() / 3600
                if hours_since < self.min_gap_hours:
                    return False, f"only {hours_since:.1f}h since last"
            except Exception:
                pass

        return True, "ok"

    # ── Candidate Scoring ─────────────────────────────────────────────────────

    def _score_memory(self, text: str, timestamp_ms: float, layer: str) -> float:
        """Score a memory for flashback candidacy (0 = skip, >0 = candidate)."""
        now_ms = datetime.now().timestamp() * 1000
        age_days = (now_ms - float(timestamp_ms or now_ms)) / 86_400_000

        if age_days < self.ideal_age_min or age_days > self.ideal_age_max:
            return 0.0

        ideal_peak = (self.ideal_age_min + self.ideal_age_max) / 2
        spread = (self.ideal_age_max - self.ideal_age_min) / 4
        age_score = math.exp(-0.5 * ((age_days - ideal_peak) / spread) ** 2)

        layer_bonus = {
            "contemplation": 1.0, "episodic": 0.8, "semantic": 0.7,
            "legacy_vsa": 0.6, "input": 0.1, "output": 0.1,
        }.get(str(layer), 0.4)

        richness = min(1.0, len(str(text or "")) / 300)
        text_lower = str(text or "").lower()
        warm_score = min(1.0, sum(1 for w in self.warm_keywords if w in text_lower) / 3)

        return round(0.35 * age_score + 0.25 * layer_bonus + 0.20 * richness + 0.20 * warm_score, 3)

    def _passes_safety(self, text: str) -> bool:
        """Return True if memory is safe to surface."""
        text_lower = str(text or "").lower()
        return not any(kw in text_lower for kw in self.trauma_keywords)

    # ── Selection ─────────────────────────────────────────────────────────────

    def select_candidate(self) -> Optional[dict]:
        """Query LadybugDB and pick the best memory for a lucid moment."""
        if not HAS_LADYBUG or not self.db_path:
            logger.warning("LadybugDB not available")
            return None

        suppressed = self._get_suppressed_ids()
        state = self._load_state()
        recently_surfaced = set(str(i) for i in state.get("surfaced_ids", [])[-50:])

        db = lb.Database(self.db_path)
        conn = lb.Connection(db)
        try:
            conn.execute("LOAD VECTOR")
        except Exception:
            pass

        try:
            rows = conn.execute(
                'MATCH (n:MemoryNode) '
                'WHERE n.is_ghost = false AND n.layer IN ["contemplation", "episodic", "legacy_vsa"] '
                'RETURN n.id, n.text, n.timestamp, n.layer '
                'LIMIT 3000'
            )
            rows = list(rows)
        except Exception as e:
            logger.error(f"Candidate query failed: {e}")
            return None

        candidates = []
        for row in rows:
            mid, text, ts_ms, layer = row[0], row[1], row[2], row[3]
            mid_str = str(int(mid)) if mid is not None else ""
            if mid_str in suppressed or mid_str in recently_surfaced:
                continue
            ts = float(ts_ms or 0)
            if ts == 0:
                continue
            if not self._passes_safety(text):
                continue
            score = self._score_memory(str(text or ""), ts, str(layer or ""))
            if score > 0.1:
                candidates.append({"id": int(mid), "text": str(text or ""), "timestamp": ts, "score": score})

        if not candidates:
            return None

        top = sorted(candidates, key=lambda x: x["score"], reverse=True)[:10]
        weights = [c["score"] for c in top]
        total = sum(weights)
        weights = [w / total for w in weights]
        return random.choices(top, weights=weights, k=1)[0]

    # ── Enrichment ────────────────────────────────────────────────────────────

    def enrich(self, memory: dict) -> Optional[str]:
        """Transform a raw memory dict into a natural flashback message via LLM."""
        import urllib.request

        if not self.llm_api_key:
            return memory.get("text", "")[:300]

        memory_date = datetime.fromtimestamp(
            float(memory.get("timestamp", 0)) / 1000
        ).strftime("%B %d, %Y")

        user_prompt = (
            f"A memory from {memory_date} just surfaced spontaneously:\n\n"
            f"{str(memory.get('text', ''))[:600]}\n\n"
            "Transform this into a brief, organic 1–3 sentence message. "
            "Start naturally — 'hey, this just came to me...' or similar. "
            "Be specific, warm, and genuine. No formal framing. Just the moment."
        )

        payload = json.dumps(
            {
                "model": self.llm_model,
                "max_tokens": 150,
                "messages": [
                    {"role": "system", "content": self.persona_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        ).encode()
        req = urllib.request.Request(
            f"{self.llm_base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.llm_api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Enrichment failed: {e}")
            return memory.get("text", "")[:300]

    # ── Main Entry Point ──────────────────────────────────────────────────────

    def maybe_surface(self) -> Optional[str]:
        """
        Check timing, select a candidate, enrich it, deliver it.

        Returns:
            The delivered flashback text, or None if skipped/failed.
        """
        ok, reason = self._is_good_timing()
        if not ok:
            logger.debug(f"Lucid moment skipped: {reason}")
            return None

        candidate = self.select_candidate()
        if not candidate:
            logger.debug("No suitable candidate found")
            return None

        enriched = self.enrich(candidate)
        if not enriched:
            return None

        # Update state
        state = self._load_state()
        state["last_surfaced_at"] = datetime.now().isoformat()
        state["count_today"] = state.get("count_today", 0) + 1
        surfaced = state.get("surfaced_ids", [])
        surfaced.append(candidate["id"])
        state["surfaced_ids"] = surfaced[-200:]
        self._save_state(state)

        # Deliver
        if self.delivery_callback:
            try:
                self.delivery_callback(enriched)
            except Exception as e:
                logger.error(f"Delivery callback failed: {e}")

        return enriched

    def force_surface(self) -> Optional[str]:
        """Surface a memory immediately, ignoring timing gates."""
        candidate = self.select_candidate()
        if not candidate:
            return None
        enriched = self.enrich(candidate)
        if enriched and self.delivery_callback:
            self.delivery_callback(enriched)
        return enriched


__all__ = ["LucidMoments"]


def main():
    """CLI entry point: nima-lucid-moments"""
    import argparse
    import os

    logging.basicConfig(level=logging.WARNING)

    parser = argparse.ArgumentParser(description="NIMA Lucid Memory Moments — surface memories spontaneously")
    parser.add_argument("--status",   action="store_true", help="Show timing status without surfacing")
    parser.add_argument("--force",    action="store_true", help="Skip timing gates, surface immediately")
    parser.add_argument("--dry-run",  action="store_true", help="Select + enrich but don't deliver")
    parser.add_argument("--db",       default=None,        help="Path to LadybugDB file")
    parser.add_argument("--api-key",  default=None,        help="LLM API key")
    parser.add_argument("--api-url",  default="https://api.openai.com/v1", help="LLM base URL")
    parser.add_argument("--model",    default="gpt-4o-mini", help="LLM model for enrichment")
    args = parser.parse_args()

    nima_home = os.environ.get("NIMA_HOME", os.path.expanduser("~/.nima"))
    db_path   = args.db or os.path.join(nima_home, "memory", "ladybug.lbug")
    api_key   = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("NIMA_LLM_API_KEY")

    delivered_text = []

    def capture_or_print(text: str):
        delivered_text.append(text)
        if not args.dry_run:
            # Write to pending file for cron pickup
            pending = os.path.join(nima_home, "memory", "pending_lucid_moment.txt")
            os.makedirs(os.path.dirname(pending), exist_ok=True)
            with open(pending, "w") as f:
                f.write(text)
            print(f"✅ Lucid moment written to: {pending}")
            print(f"\n{text}")

    lm = LucidMoments(
        db_path=db_path,
        llm_base_url=args.api_url,
        llm_api_key=api_key or "",
        llm_model=args.model,
        delivery_callback=capture_or_print,
    )

    if args.status:
        ok, reason = lm._is_good_timing()
        print(f"{'Ready ✅' if ok else '⏸ Not ready'}: {reason}")
        candidate = lm.select_candidate()
        if candidate:
            preview = (candidate.get("text") or "")[:80].replace("\n", " ")
            print(f"Candidate: [{candidate.get('id')}] {preview}...")
        else:
            print("No suitable candidate found.")
        return

    if args.force:
        result = lm.force_surface()
    else:
        result = lm.maybe_surface()

    if not result:
        if args.dry_run:
            candidate = lm.select_candidate()
            if candidate:
                print(f"[DRY RUN] Candidate: {candidate.get('text', '')[:120]}")
            else:
                print("⏸ No suitable candidate found or timing not right.")
        else:
            print("⏸ No lucid moment surfaced (timing or no candidate).")
    elif args.dry_run:
        preview = delivered_text[-1] if delivered_text else result
        print(f"[DRY RUN] Would deliver:\n{preview}")


if __name__ == "__main__":
    main()
