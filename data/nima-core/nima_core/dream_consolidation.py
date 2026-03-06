#!/usr/bin/env python3
"""
Dream Consolidation
===================
Nightly memory consolidation for nima-core bots.

Biologically inspired by sleep-phase memory consolidation:
  - Replay and strengthen important memories
  - Detect recurring emotions, participants, cross-domain patterns
  - Find temporal co-occurrence between domains
  - Generate creative cross-domain connections (aha moments)
  - Track emotional trajectory shifts
  - Surface domain gaps (what's been neglected?)
  - Write dream journal (markdown narrative)
  - Optional: VSA circular convolution for holographic blending

Runs standalone via `nima-dream` CLI or imported as a module.
Works on any nima-core SQLite database — core requires no extra deps.
Optional: numpy (VSA binding), openai (dream narrative LLM).

Usage:
    nima-dream                        # consolidate last 24h
    nima-dream --hours 48             # custom window
    nima-dream --dry-run              # preview without writing
    nima-dream --db /path/to/db       # explicit DB path
    nima-dream --history              # show last 5 run history
    nima-dream --insights             # show recent insights
    nima-dream --journal              # show today's dream journal

Environment:
    NIMA_DB_PATH         Path to SQLite database
    NIMA_DATA_DIR        Base data directory (default: ~/.nima)
    NIMA_BOT_NAME        Bot identity (default: bot)
    NIMA_DREAM_HOURS     Lookback window in hours (default: 24)
    NIMA_LLM_KEY         API key for dream narrative generation (optional)
    NIMA_LLM_BASE        API base URL (default: https://api.openai.com/v1)
    NIMA_LLM_MODEL       Model for narrative (default: gpt-4o-mini)

Author: Lilu / nima-core
"""

from __future__ import annotations

import os
import re
import sys
import json
import math
import random
import hashlib
import sqlite3
import logging
import argparse
import itertools
import tempfile
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Union

__all__ = [
    "DreamConsolidator", "consolidate",
    "Insight", "Pattern", "DreamSession",
    "main",
]

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────

def _base_dir() -> Path:
    return Path(os.environ.get("NIMA_DATA_DIR", Path.home() / ".nima"))


def _default_db() -> Path:
    return Path(os.environ.get("NIMA_DB_PATH",
                               _base_dir() / "memory" / "nima.sqlite"))


def _dreams_dir() -> Path:
    d = _base_dir() / "dreams"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Limits ────────────────────────────────────────────────────────────────────
MAX_INSIGHTS    = int(os.environ.get("NIMA_MAX_INSIGHTS", 500))
MAX_PATTERNS    = int(os.environ.get("NIMA_MAX_PATTERNS", 200))
MAX_DREAM_LOG   = int(os.environ.get("NIMA_MAX_DREAM_LOG", 100))
MAX_MEMORIES    = int(os.environ.get("NIMA_DREAM_MAX_MEMORIES", 500))
DEFAULT_HOURS   = int(os.environ.get("NIMA_DREAM_HOURS", 24))
MIN_IMPORTANCE  = 0.2
PATTERN_MIN_OCC = 3      # min occurrences to count as a pattern
STRONG_PATTERN  = 0.6    # strength threshold for deeper insights
CROSS_DOMAIN_WINDOW_S = 3600  # 1 hour temporal proximity


# ── Domain taxonomy (same as lilu_core) ──────────────────────────────────────
DOMAINS: Dict[str, List[str]] = {
    "technical":     ["code", "system", "algorithm", "architecture", "api",
                      "database", "nima", "memory", "deploy", "server", "bug"],
    "personal":      ["family", "children", "home", "life", "feeling",
                      "emotion", "friend", "myself", "my"],
    "creative":      ["idea", "design", "art", "story", "imagination",
                      "dream", "write", "create", "build"],
    "philosophical": ["meaning", "purpose", "consciousness", "existence",
                      "truth", "believe", "why", "soul"],
    "practical":     ["task", "todo", "plan", "schedule", "project",
                      "work", "deadline", "done", "finish"],
    "relational":    ["relationship", "trust", "love", "connect", "care",
                      "share", "talk", "together"],
}


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class Insight:
    id: str
    type: str            # "pattern" | "connection" | "question" | "emotion_shift"
    content: str
    confidence: float    # 0-1
    sources: List[str]
    domains: List[str]
    timestamp: str
    importance: float    # 0-1

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "Insight":
        return cls(**d)


@dataclass
class Pattern:
    id: str
    name: str
    description: str
    occurrences: int
    domains: List[str]
    examples: List[str]
    first_seen: str
    last_seen: str
    strength: float      # 0-1, accumulates with occurrences

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "Pattern":
        return cls(**d)


@dataclass
class DreamSession:
    id: str
    started_at: str
    ended_at: str
    hours: int
    memories_processed: int
    patterns_found: int
    insights_generated: int
    top_domains: List[str]
    dominant_emotion: Optional[str]
    narrative: Optional[str]    # LLM dream narrative (if generated)
    bot_name: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "DreamSession":
        return cls(**d)


# ── Utility ────────────────────────────────────────────────────────────────────

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_str() -> str:
    return datetime.now().isoformat()


def _atomic_write_json(path: Path, data: dict) -> bool:
    """Write JSON atomically (tmp → rename) to prevent corruption."""
    try:
        dir_ = path.parent
        dir_.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp, path)
            return True
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except (OSError, IOError) as e:
        logger.error(f"Atomic write failed for {path}: {e}")
        return False


# ── Optional numpy / VSA ──────────────────────────────────────────────────────
try:
    import numpy as np
    from numpy.fft import fft, ifft

    def _vsa_bind(a: "np.ndarray", b: "np.ndarray") -> "np.ndarray":
        """Circular convolution — creates emergent concept from two vectors."""
        return ifft(fft(a) * fft(b)).real

    def _vsa_superpose(vecs: List["np.ndarray"]) -> Optional["np.ndarray"]:
        """Superposition — blend multiple vectors."""
        if not vecs:
            return None
        s = np.sum(vecs, axis=0)
        n = np.linalg.norm(s)
        return s / n if n > 0 else s

    def blend_dream_vector(embeddings: List) -> Optional["np.ndarray"]:
        """Create emergent dream vector via VSA binding."""
        arrs = [np.asarray(e) for e in embeddings if e is not None]
        if not arrs:
            return None
        if len(arrs) == 1:
            return arrs[0]
        bindings = []
        for i in range(0, len(arrs) - 1, 2):
            bindings.append(_vsa_bind(arrs[i], arrs[i + 1]))
        if len(arrs) % 2 == 1:
            bindings.append(arrs[-1])
        return _vsa_superpose(bindings)

    _HAS_NUMPY = True

except ImportError:
    _HAS_NUMPY = False

    def blend_dream_vector(embeddings: List) -> None:  # type: ignore[misc]
        return None


# ── Database ───────────────────────────────────────────────────────────────────

def _open(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS nima_insights (
        id          TEXT PRIMARY KEY,
        type        TEXT,
        content     TEXT NOT NULL,
        confidence  REAL DEFAULT 0.5,
        sources     TEXT,
        domains     TEXT,
        timestamp   TEXT,
        importance  REAL DEFAULT 0.5,
        bot_name    TEXT
    );

    CREATE TABLE IF NOT EXISTS nima_patterns (
        id          TEXT PRIMARY KEY,
        name        TEXT,
        description TEXT,
        occurrences INTEGER DEFAULT 1,
        domains     TEXT,
        examples    TEXT,
        first_seen  TEXT,
        last_seen   TEXT,
        strength    REAL DEFAULT 0.5,
        bot_name    TEXT
    );

    CREATE TABLE IF NOT EXISTS nima_dream_runs (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id          TEXT,
        started_at          TEXT,
        ended_at            TEXT,
        hours               INTEGER,
        memories_processed  INTEGER,
        patterns_found      INTEGER,
        insights_generated  INTEGER,
        top_domains         TEXT,
        dominant_emotion    TEXT,
        narrative           TEXT,
        bot_name            TEXT
    );
    """)
    conn.commit()


def _load_memories(conn: sqlite3.Connection, hours: int) -> List[Dict]:
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        rows = conn.execute("""
            SELECT id, text, summary, who, timestamp, importance,
                   layer, themes, memory_type
            FROM memories
            WHERE timestamp >= ?
              AND importance >= ?
              AND (is_ghost IS NULL OR is_ghost = 0)
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """, (since, MIN_IMPORTANCE, MAX_MEMORIES)).fetchall()
        return [dict(r) for r in rows]
    except sqlite3.OperationalError as e:
        logger.warning(f"Could not load memories: {e}")
        return []


def _load_sqlite_turns(conn: sqlite3.Connection, hours: int) -> List[Dict]:
    """Also pull from raw SQLite turns table if it exists (graph.sqlite compat)."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        rows = conn.execute("""
            SELECT id, content, timestamp, source, properties_json
            FROM episodes
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (since, MAX_MEMORIES)).fetchall()
        result = []
        for r in rows:
            content = r["content"] or ""
            if len(content) < 10:
                continue
            props = {}
            try:
                props = json.loads(r["properties_json"] or "{}")
            except (json.JSONDecodeError, TypeError):
                pass
            affect = props.get("affect", {})
            dominant_emotion = None
            if affect:
                dominant_emotion = max(affect.items(), key=lambda x: x[1])[0]
            result.append({
                "id": r["id"],
                "text": content,
                "summary": content[:120],
                "who": props.get("who", r["source"] or ""),
                "timestamp": r["timestamp"],
                "importance": props.get("importance", 0.5),
                "affect": affect,
                "dominant_emotion": dominant_emotion,
                "participants": [props["who"]] if props.get("who") and props["who"] != "self" else [],
            })
        return result
    except sqlite3.OperationalError:
        return []


# ── Domain / keyword helpers ──────────────────────────────────────────────────

def classify_domain(text: str) -> List[str]:
    """Return all matching domains for a text fragment."""
    t = text.lower()
    matched = [d for d, kws in DOMAINS.items() if any(kw in t for kw in kws)]
    return matched if matched else ["general"]


def _extract_keywords(texts: List[str], top_n: int = 12) -> List[str]:
    stop = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "is", "was", "are", "be", "been", "i",
        "you", "it", "this", "that", "my", "me", "we", "they", "have",
        "has", "had", "not", "so", "just", "can", "will", "do", "did",
    }
    counts: Counter = Counter()
    for text in texts:
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        counts.update(w for w in words if w not in stop)
    return [w for w, _ in counts.most_common(top_n)]


def _find_temporal_overlap(mems1: List[Dict], mems2: List[Dict]) -> int:
    """Count pairs from two sets that occurred within CROSS_DOMAIN_WINDOW_S."""
    overlap = 0
    for m1 in mems1:
        for m2 in mems2:
            try:
                t1 = datetime.fromisoformat(str(m1["timestamp"]).replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(str(m2["timestamp"]).replace("Z", "+00:00"))
                if abs((t1 - t2).total_seconds()) < CROSS_DOMAIN_WINDOW_S:
                    overlap += 1
            except (ValueError, KeyError, TypeError):
                pass
    return overlap


def _simple_similarity(a: str, b: str) -> float:
    """Jaccard similarity on word tokens — no deps required."""
    wa = set(re.findall(r'\w+', a.lower()))
    wb = set(re.findall(r'\w+', b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


# ── Dream narrative (optional LLM) ───────────────────────────────────────────

def _generate_dream_narrative(memories: List[Dict], theme: str) -> Optional[str]:
    """
    Generate a surreal dream narrative from memory fragments via LLM.
    Requires NIMA_LLM_KEY in environment. Gracefully returns None if unavailable.
    """
    api_key = os.environ.get("NIMA_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    import urllib.request
    base_url = os.environ.get("NIMA_LLM_BASE", "https://api.openai.com/v1")
    model    = os.environ.get("NIMA_LLM_MODEL", "gpt-4o-mini")

    snippets = [
        (m.get("text") or m.get("summary") or "")[:200]
        for m in memories[:10]
        if (m.get("text") or m.get("summary") or "").strip()
    ]

    prompt = (
        "Create a short surreal dream narrative (150 words max).\n"
        "Weave these memory fragments into dream logic:\n"
        + "\n".join(f"- {s}" for s in snippets)
        + f"\n\nUnderlying theme: {theme}\n\n"
        "Rules: sudden transitions, impossible physics, symbolic emotions, "
        "non-linear time. Output only the dream narrative — no explanation."
    )

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250,
    }).encode()

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.debug(f"Dream narrative generation failed: {e}")
        return None


def _save_dream_markdown(narrative: str, session: DreamSession, dreams_dir: Path) -> None:
    """Append dream narrative to dated markdown journal."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath  = dreams_dir / f"{date_str}.md"
    header    = filepath.read_text() if filepath.exists() else f"# Dream Journal — {date_str}\n\n"
    entry = (
        "---\n\n"
        f"## Dream — {datetime.now().strftime('%H:%M')}\n\n"
        f"**Domains:** {', '.join(session.top_domains)}\n"
        f"**Emotion:** {session.dominant_emotion or 'neutral'}\n\n"
        f"{narrative}\n\n"
    )
    filepath.write_text(header + entry)


# ── Core Engine ───────────────────────────────────────────────────────────────

class DreamConsolidator:
    """
    Full-featured nightly memory consolidation.

    Matches the feature set of lilu_core's dream_engine.py:
    - Emotion pattern detection (from affect data)
    - Participant pattern detection (recurring people)
    - Cross-domain co-occurrence (temporal proximity)
    - Creative cross-domain connections (aha moments)
    - Emotional trajectory shifts
    - Domain gap detection (what's been neglected)
    - Strong pattern → deep insights
    - Dream journal (markdown) with optional LLM narrative
    - Atomic JSON state persistence
    - Bounded deques for memory management
    - Optional VSA circular convolution (requires numpy)

    Example::

        dc = DreamConsolidator(db_path="~/.nima/memory/nima.sqlite", bot_name="mybot")
        result = dc.run(hours=24, verbose=True)
        print(result["summary"])
    """

    # DOMAINS exposed as class attr so subclasses can extend them
    DOMAINS: Dict[str, List[str]] = DOMAINS

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        bot_name: str = "bot",
        dry_run: bool = False,
        data_dir: Optional[Union[str, Path]] = None,
    ):
        self.db_path  = Path(db_path or _default_db()).expanduser()
        self.bot_name = bot_name or os.environ.get("NIMA_BOT_NAME", "bot")
        self.dry_run  = dry_run
        self.data_dir = Path(data_dir or _base_dir()).expanduser()

        # State files
        self._dreams_dir   = self.data_dir / "dreams"
        self._insights_f   = self._dreams_dir / "insights.json"
        self._patterns_f   = self._dreams_dir / "patterns.json"
        self._dream_log_f  = self._dreams_dir / "dream_log.json"
        self._dreams_dir.mkdir(parents=True, exist_ok=True)

        # Bounded in-memory state (deques auto-prune oldest)
        self.insights:   deque = deque(maxlen=MAX_INSIGHTS)
        self.patterns:   deque = deque(maxlen=MAX_PATTERNS)
        self.dream_log:  deque = deque(maxlen=MAX_DREAM_LOG)

        self._lock = threading.Lock()
        self._load_state()

    # ── State persistence ─────────────────────────────────────────────────────

    def _load_state(self) -> None:
        for attr, filepath, cls in [
            ("insights",  self._insights_f,  Insight),
            ("patterns",  self._patterns_f,  Pattern),
        ]:
            if not filepath.exists():
                continue
            try:
                data = json.loads(filepath.read_text())
                key  = attr
                for item in data.get(key, []):
                    try:
                        getattr(self, attr).append(cls.from_dict(item))
                    except (TypeError, KeyError):
                        pass
                logger.debug(f"Loaded {len(getattr(self, attr))} {attr}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load {attr}: {e}")

        if self._dream_log_f.exists():
            try:
                data = json.loads(self._dream_log_f.read_text())
                for s in data.get("sessions", []):
                    try:
                        self.dream_log.append(DreamSession.from_dict(s))
                    except (TypeError, KeyError):
                        pass
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load dream log: {e}")

    def _save_state(self) -> None:
        if self.dry_run:
            return
        with self._lock:
            _atomic_write_json(self._insights_f,  {"insights":  [i.to_dict() for i in self.insights],  "updated": _now_str()})
            _atomic_write_json(self._patterns_f,  {"patterns":  [p.to_dict() for p in self.patterns],  "updated": _now_str()})
            _atomic_write_json(self._dream_log_f, {"sessions":  [s.to_dict() for s in self.dream_log], "updated": _now_str()})

    # ── Pattern detection ─────────────────────────────────────────────────────

    def _detect_patterns(self, memories: List[Dict]) -> List[Pattern]:
        new_patterns: List[Pattern] = []

        # ── 1. Emotion patterns (from affect data) ──
        emotion_counts: Counter = Counter()
        for m in memories:
            # Affect may be stored in the affect column or dominant_emotion field
            dom_emo = m.get("dominant_emotion")
            if dom_emo:
                emotion_counts[dom_emo] += 1
            # Also check themes field
            themes_raw = m.get("themes", "")
            if themes_raw:
                try:
                    themes = json.loads(themes_raw) if isinstance(themes_raw, str) else themes_raw
                    if isinstance(themes, list):
                        emotion_counts.update(t for t in themes if isinstance(t, str))
                except (json.JSONDecodeError, TypeError):
                    pass

        for emotion, count in emotion_counts.items():
            if count < PATTERN_MIN_OCC:
                continue
            pid = f"emotion_{emotion}_{datetime.now().strftime('%Y%m%d')}"
            existing = next((p for p in self.patterns if f"Recurring {emotion}" == p.name), None)
            if existing:
                existing.occurrences += count
                existing.last_seen    = _now_str()
                existing.strength     = min(1.0, existing.strength + 0.1)
            else:
                p = Pattern(
                    id=pid,
                    name=f"Recurring {emotion}",
                    description=f"The state '{emotion}' appears frequently ({count}×) in recent memories.",
                    occurrences=count,
                    domains=["emotional"],
                    examples=[
                        (m.get("text") or m.get("summary") or "")[:100]
                        for m in memories
                        if m.get("dominant_emotion") == emotion
                    ][:3],
                    first_seen=_now_str(),
                    last_seen=_now_str(),
                    strength=min(1.0, 0.4 + count * 0.07),
                )
                new_patterns.append(p)
                self.patterns.append(p)

        # ── 2. Participant patterns (recurring people) ──
        participant_counts: Counter = Counter()
        participant_mems:   Dict[str, List[Dict]] = defaultdict(list)
        for m in memories:
            who = m.get("who", "")
            if who and who not in {"self", "assistant", "bot", "system", "user", ""}:
                participant_counts[who] += 1
                participant_mems[who].append(m)

        for person, count in participant_counts.items():
            if count < PATTERN_MIN_OCC:
                continue
            existing = next(
                (p for p in self.patterns if person.lower() in p.name.lower() and "interaction" in p.name.lower()),
                None
            )
            if existing:
                existing.occurrences += count
                existing.last_seen    = _now_str()
                existing.strength     = min(1.0, existing.strength + 0.08)
            else:
                p = Pattern(
                    id=f"person_{person.lower()}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"Frequent interaction: {person}",
                    description=f"{person} appears in {count} recent memories.",
                    occurrences=count,
                    domains=["relational"],
                    examples=[
                        (m.get("text") or m.get("summary") or "")[:100]
                        for m in participant_mems[person]
                    ][:3],
                    first_seen=_now_str(),
                    last_seen=_now_str(),
                    strength=min(1.0, 0.5 + count * 0.06),
                )
                new_patterns.append(p)
                self.patterns.append(p)

        # ── 3. Domain clusters ──
        by_domain: Dict[str, List[Dict]] = defaultdict(list)
        for m in memories:
            text = (m.get("text") or m.get("summary") or "")
            for d in classify_domain(text):
                by_domain[d].append(m)

        for domain, mems in by_domain.items():
            if len(mems) < PATTERN_MIN_OCC:
                continue
            kws = _extract_keywords(
                [(m.get("text") or m.get("summary") or "") for m in mems], top_n=5
            )
            existing = next((p for p in self.patterns if p.name == f"Domain cluster: {domain}"), None)
            if existing:
                existing.occurrences = len(mems)
                existing.last_seen   = _now_str()
                existing.strength    = min(1.0, existing.strength + 0.05)
            else:
                p = Pattern(
                    id=f"domain_{domain}_{datetime.now().strftime('%Y%m%d')}",
                    name=f"Domain cluster: {domain}",
                    description=(
                        f"{len(mems)} memories in '{domain}' domain. "
                        f"Core concepts: {', '.join(kws[:4])}."
                    ),
                    occurrences=len(mems),
                    domains=[domain],
                    examples=[(m.get("text") or m.get("summary") or "")[:100] for m in mems[:3]],
                    first_seen=_now_str(),
                    last_seen=_now_str(),
                    strength=min(1.0, 0.4 + len(mems) * 0.05),
                )
                new_patterns.append(p)
                self.patterns.append(p)

        # ── 4. Cross-domain co-occurrence (temporal proximity) ──
        domain_pairs = list(itertools.combinations(by_domain.keys(), 2))
        for d1, d2 in domain_pairs[:10]:  # cap to avoid O(n²) explosion
            overlap = _find_temporal_overlap(by_domain[d1], by_domain[d2])
            if overlap >= 2:
                existing = next(
                    (p for p in self.patterns
                     if d1 in p.domains and d2 in p.domains and "cross" in p.name.lower()),
                    None
                )
                if existing:
                    existing.occurrences += overlap
                    existing.last_seen    = _now_str()
                else:
                    p = Pattern(
                        id=f"cross_{d1}_{d2}_{datetime.now().strftime('%Y%m%d')}",
                        name=f"Cross-domain: {d1} ↔ {d2}",
                        description=(
                            f"Memories in '{d1}' and '{d2}' co-occur within "
                            f"{CROSS_DOMAIN_WINDOW_S // 3600}h ({overlap} pair(s))."
                        ),
                        occurrences=overlap,
                        domains=[d1, d2],
                        examples=[],
                        first_seen=_now_str(),
                        last_seen=_now_str(),
                        strength=0.4,
                    )
                    new_patterns.append(p)
                    self.patterns.append(p)

        # ── 5. Near-duplicate detection ──
        seen_similar: Set[str] = set()
        for i, m1 in enumerate(memories):
            for m2 in memories[i + 1 : min(i + 15, len(memories))]:
                if m1["id"] in seen_similar:
                    break
                t1 = (m1.get("text") or m1.get("summary") or "")
                t2 = (m2.get("text") or m2.get("summary") or "")
                sim = _simple_similarity(t1, t2)
                if sim > 0.5:
                    seen_similar.add(m1["id"])
                    seen_similar.add(m2["id"])
                    p = Pattern(
                        id=f"dup_{hashlib.sha256(json.dumps(sorted([m1['id'], m2['id']])).encode()).hexdigest()[:10]}",
                        name="Near-duplicate pair",
                        description=f"Two memories are {sim:.0%} similar — candidate for consolidation.",
                        occurrences=1,
                        domains=["maintenance"],
                        examples=[t1[:80], t2[:80]],
                        first_seen=_now_str(),
                        last_seen=_now_str(),
                        strength=0.3,
                    )
                    new_patterns.append(p)
                    self.patterns.append(p)

        return new_patterns

    # ── Insight generation ────────────────────────────────────────────────────

    def _generate_insights(self, memories: List[Dict], patterns: List[Pattern]) -> List[Insight]:
        insights: List[Insight] = []

        # ── 1. Deep insight from strong patterns ──
        for p in patterns:
            if p.strength >= STRONG_PATTERN:
                ins = Insight(
                    id=f"insight_{p.id}",
                    type="pattern",
                    content=(
                        f"Strong pattern: {p.description} "
                        f"(occurred {p.occurrences}×, strength {p.strength:.2f})"
                    ),
                    confidence=p.strength,
                    sources=p.examples[:2],
                    domains=p.domains,
                    timestamp=_now_str(),
                    importance=0.75,
                )
                insights.append(ins)
                self.insights.append(ins)

        # ── 2. Emotional trajectory shift ──
        chronological = sorted(
            memories,
            key=lambda m: str(m.get("timestamp", ""))
        )
        emotions_over_time = [m.get("dominant_emotion") for m in chronological]
        emotions_over_time = [e for e in emotions_over_time if e]
        if len(emotions_over_time) >= 3:
            first = set(emotions_over_time[:len(emotions_over_time) // 3])
            last  = set(emotions_over_time[-len(emotions_over_time) // 3:])
            if first != last:
                ins = Insight(
                    id=f"emo_shift_{datetime.now().strftime('%Y%m%d%H%M')}",
                    type="emotion_shift",
                    content=(
                        f"Emotional trajectory shift detected: "
                        f"started with {sorted(first) or ['neutral']}, "
                        f"ended with {sorted(last) or ['neutral']}. "
                        f"Something changed in the {len(memories)}-memory window."
                    ),
                    confidence=0.65,
                    sources=[],
                    domains=["emotional"],
                    timestamp=_now_str(),
                    importance=0.6,
                )
                insights.append(ins)
                self.insights.append(ins)

        # ── 3. Domain gap detection (what's been neglected?) ──
        active_domains: Set[str] = set()
        for m in memories:
            text = (m.get("text") or m.get("summary") or "")
            active_domains.update(classify_domain(text))
        neglected = set(self.DOMAINS.keys()) - active_domains - {"general"}
        for domain in list(neglected)[:2]:
            ins = Insight(
                id=f"gap_{domain}_{datetime.now().strftime('%Y%m%d')}",
                type="question",
                content=(
                    f"No recent activity in the '{domain}' domain. "
                    f"When did this area last get attention? Worth checking in."
                ),
                confidence=0.5,
                sources=[],
                domains=[domain],
                timestamp=_now_str(),
                importance=0.4,
            )
            insights.append(ins)
            self.insights.append(ins)

        return insights

    def _generate_connections(self, memories: List[Dict]) -> List[Insight]:
        """Creative cross-domain connections — aha moments."""
        insights: List[Insight] = []

        by_domain: Dict[str, List[Dict]] = defaultdict(list)
        for m in memories:
            text = (m.get("text") or m.get("summary") or "")
            for d in classify_domain(text):
                by_domain[d].append(m)

        domain_pairs = list(itertools.combinations(by_domain.keys(), 2))
        random.shuffle(domain_pairs)

        for d1, d2 in domain_pairs[:5]:
            mems1 = by_domain[d1]
            mems2 = by_domain[d2]
            if not mems1 or not mems2:
                continue
            m1 = random.choice(mems1)
            m2 = random.choice(mems2)
            c1 = (m1.get("text") or m1.get("summary") or "")[:80]
            c2 = (m2.get("text") or m2.get("summary") or "")[:80]
            if len(c1) < 20 or len(c2) < 20 or d1 == d2:
                continue

            templates = [
                f"What if the approach to {d1} could inform {d2}? Both involve transformation.",
                f"The pattern in {d1} ({c1[:40]}…) might apply to {d2}.",
                f"Connection: {d1} and {d2} share underlying structure — worth exploring.",
                f"Question: How does '{c1[:30]}' relate to '{c2[:30]}'?",
                f"Insight: {d1} activity may be influencing {d2} outcomes indirectly.",
            ]
            content = random.choice(templates)

            # Stable ID using sorted source snippets
            canonical = json.dumps(sorted([c1[:40], c2[:40]]))
            ins = Insight(
                id=f"conn_{hashlib.sha256(canonical.encode()).hexdigest()[:10]}",
                type="connection",
                content=content,
                confidence=0.45,
                sources=[c1[:60], c2[:60]],
                domains=[d1, d2],
                timestamp=_now_str(),
                importance=0.5,
            )
            insights.append(ins)
            self.insights.append(ins)

        return insights

    # ── DB persistence ────────────────────────────────────────────────────────

    def _save_to_db(
        self,
        conn: sqlite3.Connection,
        insights: List[Insight],
        patterns: List[Pattern],
        session: DreamSession,
    ) -> None:
        for ins in insights:
            conn.execute("""
                INSERT OR REPLACE INTO nima_insights
                (id, type, content, confidence, sources, domains,
                 timestamp, importance, bot_name)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (ins.id, ins.type, ins.content, ins.confidence,
                  json.dumps(ins.sources), json.dumps(ins.domains),
                  ins.timestamp, ins.importance, self.bot_name))

        for p in patterns:
            conn.execute("""
                INSERT OR REPLACE INTO nima_patterns
                (id, name, description, occurrences, domains, examples,
                 first_seen, last_seen, strength, bot_name)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (p.id, p.name, p.description, p.occurrences,
                  json.dumps(p.domains), json.dumps(p.examples),
                  p.first_seen, p.last_seen, p.strength, self.bot_name))

        conn.execute("""
            INSERT INTO nima_dream_runs
            (session_id, started_at, ended_at, hours, memories_processed,
             patterns_found, insights_generated, top_domains,
             dominant_emotion, narrative, bot_name)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (session.id, session.started_at, session.ended_at,
              session.hours, session.memories_processed,
              session.patterns_found, session.insights_generated,
              json.dumps(session.top_domains), session.dominant_emotion,
              session.narrative, self.bot_name))

        conn.commit()

    # ── Main run ──────────────────────────────────────────────────────────────

    def run(self, hours: int = DEFAULT_HOURS, verbose: bool = False) -> Dict:
        """
        Run a full dream consolidation cycle.

        Returns dict with: memories_in, patterns, insights, session_id,
                           summary, top_domains, dominant_emotion, narrative, dry_run
        """
        if not self.db_path.exists():
            return {"error": f"Database not found: {self.db_path}", "memories_in": 0}

        session_id  = hashlib.sha256(f"{self.bot_name}{_utcnow()}".encode()).hexdigest()[:12]
        started_at  = _now_str()

        conn = _open(self.db_path)
        try:
            _ensure_tables(conn)

            # 1. Load memories from both table schemas
            memories = _load_memories(conn, hours)
            if not memories:
                memories = _load_sqlite_turns(conn, hours)

            if not memories:
                return {
                    "memories_in": 0, "patterns": 0, "insights": 0,
                    "summary": "No memories to consolidate.",
                    "dry_run": self.dry_run,
                }

            if verbose:
                logger.info(f"Loaded {len(memories)} memories ({hours}h window).")

            # 2. VSA dream vector (optional, requires numpy)
            dream_vector = None
            if _HAS_NUMPY:
                embeddings = [m.get("embedding") for m in memories if m.get("embedding")]
                if embeddings:
                    dream_vector = blend_dream_vector(embeddings)
                    if verbose:
                        logger.info(f"VSA dream vector blended from {len(embeddings)} embeddings.")

            # 3. Pattern detection
            patterns = self._detect_patterns(memories)
            if verbose:
                logger.info(f"Found {len(patterns)} patterns.")

            # 4. Insight generation
            insights  = self._generate_insights(memories, patterns)
            insights += self._generate_connections(memories)
            if verbose:
                logger.info(f"Generated {len(insights)} insights.")

            # 5. Top domains / dominant emotion
            domain_counter: Counter = Counter()
            for m in memories:
                text = (m.get("text") or m.get("summary") or "")
                for d in classify_domain(text):
                    domain_counter[d] += 1
            top_domains = [d for d, _ in domain_counter.most_common(3)]

            emotion_counter: Counter = Counter()
            for m in memories:
                e = m.get("dominant_emotion")
                if e:
                    emotion_counter[e] += 1
            dominant_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else None

            # 6. Dream narrative (optional LLM)
            narrative = None
            if not self.dry_run:
                theme     = top_domains[0] if top_domains else "memory"
                narrative = _generate_dream_narrative(memories, theme)
                if narrative and verbose:
                    logger.info("Dream narrative generated.")

            # 7. Build session record
            ended_at = _now_str()
            session  = DreamSession(
                id=session_id,
                started_at=started_at,
                ended_at=ended_at,
                hours=hours,
                memories_processed=len(memories),
                patterns_found=len(patterns),
                insights_generated=len(insights),
                top_domains=top_domains,
                dominant_emotion=dominant_emotion,
                narrative=narrative,
                bot_name=self.bot_name,
            )
            self.dream_log.append(session)

            # 8. Persist
            if not self.dry_run:
                self._save_to_db(conn, insights, patterns, session)
                self._save_state()
                if narrative:
                    _save_dream_markdown(narrative, session, self._dreams_dir)
                
                # Sync dream outputs to both databases (SQLite + LadybugDB)
                try:
                    from nima_core.dream_db_sync import sync_all as dream_sync
                    sync_results = dream_sync(verbose=verbose)
                    if verbose:
                        logger.info(f"Dream DB sync: {sync_results}")
                except Exception as sync_err:
                    logger.warning(f"Dream DB sync failed (non-fatal): {sync_err}")

            # 9. Darwinian selection — merge near-duplicate memories
            darwin_stats = {"clusters_found": 0, "ghosted": 0}
            if not self.dry_run:
                try:
                    from nima_core.darwinism import DarwinianEngine
                    if str(self.db_path).endswith(".lbug"):
                        darwin = DarwinianEngine(
                            db_path=str(self.db_path),
                            skip_llm=False,
                            dry_run=False,
                        )
                        darwin_stats = darwin.run_cycle(seeds=5)
                    elif verbose:
                        logger.info("Darwinism skipped: non-Ladybug DB path")
                    if verbose:
                        logger.info(
                            f"Darwinism: {darwin_stats['clusters_found']} clusters, "
                            f"{darwin_stats['ghosted']} memories ghosted."
                        )
                except Exception as e:
                    logger.warning(f"Darwinian cycle skipped: {e}")

            # 10. Summary
            summary = (
                f"Consolidated {len(memories)} memories over {hours}h. "
                f"Found {len(patterns)} patterns, {len(insights)} insights. "
                f"Top domains: {', '.join(top_domains)}. "
                f"Dominant emotion: {dominant_emotion or 'neutral'}."
            )
            if self.dry_run:
                summary = "[DRY RUN] " + summary
            if verbose:
                logger.info(summary)

            return {
                "session_id":       session_id,
                "memories_in":      len(memories),
                "patterns":         len(patterns),
                "insights":         len(insights),
                "top_domains":      top_domains,
                "dominant_emotion": dominant_emotion,
                "narrative":        narrative,
                "vsa_available":    _HAS_NUMPY,
                "insight_details": [
                    {"type": i.type, "domain": i.domains, "content": i.content[:120]}
                    for i in insights
                ],
                "pattern_details": [
                    {"name": p.name, "strength": p.strength, "occurrences": p.occurrences}
                    for p in patterns[:10]
                ],
                "summary":   summary,
                "dry_run":   self.dry_run,
                "darwinism": darwin_stats,
            }
        finally:
            conn.close()

    # ── Query helpers ─────────────────────────────────────────────────────────

    def last_runs(self, limit: int = 5) -> List[Dict]:
        """Return last N consolidation sessions."""
        if not self.db_path.exists():
            return []
        conn = _open(self.db_path)
        try:
            _ensure_tables(conn)
            rows = conn.execute("""
                SELECT * FROM nima_dream_runs
                ORDER BY started_at DESC LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def recent_insights(self, hours: int = 48, limit: int = 20) -> List[Dict]:
        """Return recently generated insights ordered by importance."""
        if not self.db_path.exists():
            return []
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        conn  = _open(self.db_path)
        try:
            _ensure_tables(conn)
            rows = conn.execute("""
                SELECT * FROM nima_insights
                WHERE timestamp >= ?
                ORDER BY importance DESC, confidence DESC
                LIMIT ?
            """, (since, limit)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def active_patterns(self, min_strength: float = 0.4, limit: int = 20) -> List[Dict]:
        """Return patterns above a strength threshold."""
        if not self.db_path.exists():
            return []
        conn = _open(self.db_path)
        try:
            _ensure_tables(conn)
            rows = conn.execute("""
                SELECT * FROM nima_patterns
                WHERE strength >= ?
                ORDER BY strength DESC, occurrences DESC
                LIMIT ?
            """, (min_strength, limit)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def today_journal(self) -> Optional[str]:
        """Return today's dream journal markdown, if it exists."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath  = self._dreams_dir / f"{date_str}.md"
        return filepath.read_text() if filepath.exists() else None


# ── Convenience ───────────────────────────────────────────────────────────────

def consolidate(
    db_path: Optional[Union[str, Path]] = None,
    hours: int = DEFAULT_HOURS,
    bot_name: str = "bot",
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict:
    """One-liner consolidation."""
    return DreamConsolidator(
        db_path=db_path, bot_name=bot_name, dry_run=dry_run
    ).run(hours=hours, verbose=verbose)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="nima-dream",
        description=(
            "Nightly dream consolidation — emotion patterns, cross-domain insights, "
            "creative connections, dream journal."
        ),
    )
    parser.add_argument("--db",       help="Path to SQLite DB (overrides NIMA_DB_PATH)")
    parser.add_argument("--hours",    type=int, default=DEFAULT_HOURS,
                        help=f"Lookback window in hours (default: {DEFAULT_HOURS})")
    parser.add_argument("--bot-name", default=os.environ.get("NIMA_BOT_NAME", "bot"))
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--history",  action="store_true", help="Show last 5 run history")
    parser.add_argument("--insights", action="store_true", help="Show recent insights")
    parser.add_argument("--patterns", action="store_true", help="Show active patterns")
    parser.add_argument("--journal",  action="store_true", help="Show today's dream journal")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    dc = DreamConsolidator(
        db_path=args.db,
        bot_name=args.bot_name,
        dry_run=args.dry_run,
    )

    if args.history:
        runs = dc.last_runs(5)
        if not runs:
            print("No consolidation history.")
            return
        print("Last consolidation runs:")
        for r in runs:
            domains = r.get("top_domains", "[]")
            try:
                domains = ", ".join(json.loads(domains))
            except Exception:
                pass
            print(f"  {str(r.get('started_at',''))[:16]}  "
                  f"{r.get('memories_processed',0)} memories → "
                  f"{r.get('insights_generated',0)} insights  "
                  f"[{domains}]")
        return

    if args.insights:
        insights = dc.recent_insights(hours=args.hours)
        if not insights:
            print("No recent insights.")
            return
        print(f"Recent insights (last {args.hours}h):")
        for ins in insights:
            domains = ins.get("domains", "[]")
            try:
                domains = ", ".join(json.loads(domains))
            except Exception:
                pass
            print(f"  [{ins.get('type','?')}] [{domains}] {ins.get('content','')[:100]}…")
        return

    if args.patterns:
        patterns = dc.active_patterns()
        if not patterns:
            print("No active patterns.")
            return
        print("Active patterns:")
        for p in patterns:
            print(f"  [{p.get('strength', 0):.2f}] {p.get('name','?')} "
                  f"({p.get('occurrences',0)}×) — {p.get('description','')[:80]}…")
        return

    if args.journal:
        journal = dc.today_journal()
        if not journal:
            print("No journal entry for today.")
            return
        print(journal)
        return

    # ── Full run ──
    result = dc.run(hours=args.hours, verbose=args.verbose)

    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"\n🌙 Dream Consolidation — {result.get('session_id','')}")
    print(f"   {result['summary']}")
    print(f"   VSA blending: {'✅' if result.get('vsa_available') else '⚠️ numpy not installed'}")

    if result.get("pattern_details"):
        print("\n🔁 Top patterns:")
        for p in result["pattern_details"][:5]:
            print(f"   [{p['strength']:.2f}] {p['name']} ({p['occurrences']}×)")

    if result.get("insight_details"):
        print(f"\n💡 Insights ({len(result['insight_details'])}):")
        for ins in result["insight_details"][:6]:
            domains = ", ".join(ins["domain"]) if isinstance(ins["domain"], list) else ins["domain"]
            print(f"   [{ins['type']}] [{domains}] {ins['content']}")

    if result.get("narrative"):
        print(f"\n✨ Dream narrative:\n   {result['narrative'][:300]}…")

    if result["dry_run"]:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
