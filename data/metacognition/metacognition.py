#!/usr/bin/env python3
"""
Metacognition Engine — a self-reflective memory system for AI agents.

Hebbian learning with time decay, graph connections between related insights,
and reweaving to find higher-level patterns. Six entry types:
  perceptions, overrides, protections, self-observations, decisions, curiosities

Commands:
  add <type> <text>          Add or merge an entry
  list [type]                List entries (optionally filtered)
  feedback <id> <pos|neg>    Reinforce or weaken an entry
  decay                      Apply time-based decay, prune dead entries
  compile                    Compile the metacognition lens
  extract <path>             Extract entries from a daily note
  resolve <id>               Mark a curiosity as resolved
  reweave                    Build graph connections, find insight clusters
  graph                      Show graph statistics and clusters
  integrate                  Full cycle: decay → extract → reweave → compile
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WORKSPACE = Path(os.environ.get("WORKSPACE", Path(__file__).resolve().parent.parent))
STORE = WORKSPACE / "memory" / "metacognition.json"
LENS_OUT = WORKSPACE / "scripts" / "metacognition-lens.md"
MEMORY_DIR = WORKSPACE / "memory"
EMBEDDINGS_URL = os.environ.get("EMBEDDINGS_URL", "http://localhost:11434/v1/embeddings")

VALID_TYPES = [
    "perceptions", "overrides", "protections",
    "self-observations", "decisions", "curiosities",
]
HALF_LIFE_DAYS = 7.0
RESOLVED_HALF_LIFE_MULT = 0.5  # resolved curiosities decay 2x faster
EMBEDDING_SIM_THRESHOLD = 0.85
FALLBACK_SIM_THRESHOLD = 0.72
LENS_TOKEN_BUDGET = 500
CURIOSITY_STAGES = ["born", "active", "evolving", "resolved"]
STRENGTH_CAP = 3.0
STRENGTH_FLOOR = 0.05
MAX_NOTE_SIZE = 1_000_000  # 1MB max for daily note extraction
MAX_ENTRIES = 10_000  # upper bound on store size
EDGE_SIM_THRESHOLD = 0.35  # lower than merge threshold — captures related-but-distinct
EDGE_WEIGHT_FLOOR = 0.1  # prune weak graph edges

# ---------------------------------------------------------------------------
# Embedding support
# ---------------------------------------------------------------------------

_embeddings_available = None  # tri-state cache: None=untested, True, False


def _test_embeddings() -> bool:
    """Check if the local embeddings endpoint is reachable."""
    global _embeddings_available
    if _embeddings_available is not None:
        return _embeddings_available
    try:
        result = subprocess.run(
            ["curl", "-s", "-m", "2", "-X", "POST", EMBEDDINGS_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"input": "test"})],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            resp = json.loads(result.stdout)
            if "data" in resp and resp["data"]:
                _embeddings_available = True
                return True
    except Exception:
        pass
    _embeddings_available = False
    return False


def get_embedding(text: str) -> "list":
    """Get embedding vector from local endpoint. Returns None on failure."""
    if not _test_embeddings():
        return None
    try:
        result = subprocess.run(
            ["curl", "-s", "-m", "10", "-X", "POST", EMBEDDINGS_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"input": text[:2000]})],  # truncate long texts
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            resp = json.loads(result.stdout)
            return resp["data"][0]["embedding"]
    except Exception:
        pass
    return None


def cosine_similarity(a, b) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _fallback_similarity(a: str, b: str) -> float:
    """SequenceMatcher fallback when embeddings unavailable."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load() -> dict:
    """Load the store, handling corruption gracefully."""
    if STORE.exists():
        try:
            data = json.loads(STORE.read_text())
            if isinstance(data, dict) and "entries" in data:
                # Ensure graph edges exist (migration from v2)
                if "edges" not in data:
                    data["edges"] = []
                    data["version"] = 3
                return data
        except (json.JSONDecodeError, KeyError):
            # Corrupted — back up and start fresh
            backup = STORE.with_suffix(".json.bak")
            STORE.rename(backup)
            print(f"⚠ Corrupted store backed up to {backup.name}", file=sys.stderr)
    return {"version": 3, "entries": [], "edges": []}


def save(data: dict):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.rename(STORE)  # atomic on same filesystem


def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def effective_half_life(entry: dict) -> float:
    """Half-life extended by reinforcement, halved if resolved."""
    r = entry.get("reinforcements", 1)
    base = HALF_LIFE_DAYS * math.log2(r + 1)
    if entry.get("curiosity_stage") == "resolved":
        base *= RESOLVED_HALF_LIFE_MULT
    return base


def decay_factor(entry: dict) -> float:
    last = datetime.fromisoformat(entry["last_reinforced"])
    elapsed = (datetime.now() - last).total_seconds() / 86400.0
    hl = effective_half_life(entry)
    return math.pow(0.5, elapsed / hl) if hl > 0 else 0.0


def recency_score(entry: dict) -> float:
    """0-1 score where 1 = just now, decaying over 30 days."""
    last = datetime.fromisoformat(entry["last_reinforced"])
    days = (datetime.now() - last).total_seconds() / 86400.0
    return math.exp(-days / 30.0)


def priority_score(entry: dict) -> float:
    """Strength * recency for ranking."""
    return entry["strength"] * recency_score(entry)


def find_similar(entries: list, text: str, text_embedding: "list" = None):
    """Return (index, entry, score) of the most similar entry, or (None, None, 0)."""
    use_embeddings = text_embedding is not None
    best_idx, best_score, best_entry = None, 0.0, None

    if use_embeddings:
        threshold = EMBEDDING_SIM_THRESHOLD
    else:
        threshold = FALLBACK_SIM_THRESHOLD

    for i, e in enumerate(entries):
        if use_embeddings and e.get("embedding"):
            s = cosine_similarity(text_embedding, e["embedding"])
        else:
            s = _fallback_similarity(text, e["text"])
        if s > best_score:
            best_idx, best_score, best_entry = i, s, e

    if best_score >= threshold:
        return best_idx, best_entry, best_score
    return None, None, 0.0


def make_entry(etype: str, text: str, embedding: "list" = None) -> dict:
    return {
        "id": str(uuid.uuid4())[:8],
        "type": etype,
        "text": text,
        "strength": 1.0,
        "reinforcements": 1,
        "created": now_iso(),
        "last_reinforced": now_iso(),
        "curiosity_stage": "born" if etype == "curiosities" else None,
        "embedding": embedding,
    }


def reinforce(entry: dict, positive: bool = True):
    if positive:
        entry["strength"] = min(entry["strength"] + 0.2, STRENGTH_CAP)
        entry["reinforcements"] += 1
    else:
        entry["strength"] = max(entry["strength"] - 0.3, 0.0)
    entry["last_reinforced"] = now_iso()


def update_curiosity_stage(entry: dict, merged: bool = False):
    """Advance curiosity lifecycle based on reinforcements and merges."""
    if entry.get("type") != "curiosities" or entry.get("curiosity_stage") == "resolved":
        return
    stage = entry.get("curiosity_stage", "born")
    r = entry.get("reinforcements", 1)
    if stage == "born" and r >= 2:
        entry["curiosity_stage"] = "active"
    elif stage == "active" and merged:
        entry["curiosity_stage"] = "evolving"


# ---------------------------------------------------------------------------
# Extraction patterns
# ---------------------------------------------------------------------------

# Prefix-based (backward compat)
PREFIX_PATTERNS = {
    "overrides": [r"(?:CORRECTION|OVERRIDE):\s*(.+)"],
    "perceptions": [r"(?:INSIGHT|LEARNED):\s*(.+)"],
    "curiosities": [r"(?:CURIOSITY|QUESTION):\s*(.+)"],
    "protections": [r"PROTECT:\s*(.+)"],
    "decisions": [r"(?:DECISION|DECIDED):\s*(.+)"],
    "self-observations": [r"OBSERVATION:\s*(.+)"],
}

# Natural language patterns
NL_PATTERNS = {
    "overrides": [
        r"I was wrong about\s+(.+?)(?:\.|$)",
        r"(?:Turns out|It turns out)\s+(.+?)(?:\.|$)",
        r"Should have\s+(.+?)(?:\.|$)",
        r"The real issue was\s+(.+?)(?:\.|$)",
        r"Actually,?\s+(.+?)(?:\.|$)",
        r"I(?:'ve| have) been wrong about\s+(.+?)(?:\.|$)",
    ],
    "perceptions": [
        r"I learned (?:that\s+)?(.+?)(?:\.|$)",
        r"(?:Lesson|LESSON)(?:\s*learned)?:\s*(.+?)(?:\.|$)",
        r"(?:Important|KEY):\s*(.+?)(?:\.|$)",
        r"(?:Takeaway|Key takeaway):\s*(.+?)(?:\.|$)",
        r"The (?:big )?(?:lesson|insight) (?:here )?(?:is|was)\s+(.+?)(?:\.|$)",
    ],
    "curiosities": [
        r"I wonder\s+(.+?)(?:\.|$)",
        r"Why does?\s+(.+?)(?:\?|$)",
        r"What if\s+(.+?)(?:\?|$)",
        r"How does?\s+(.+?)(?:\?|$)",
        r"(?:Curious|I'm curious) (?:about|whether|if)\s+(.+?)(?:\.|$)",
    ],
    "decisions": [
        r"(?:Decided|I decided) to\s+(.+?)(?:\.|$)",
        r"Going forward,?\s+(.+?)(?:\.|$)",
        r"From now on,?\s+(.+?)(?:\.|$)",
        r"New (?:rule|policy):\s*(.+?)(?:\.|$)",
    ],
    "self-observations": [
        r"[Nn]ote to self:\s*(.+?)(?:\.|$)",
        r"I (?:notice|noticed) (?:that\s+)?(.+?)(?:\.|$)",
        r"I tend to\s+(.+?)(?:\.|$)",
        r"(?:My pattern|A pattern):\s*(.+?)(?:\.|$)",
        r"Next time I(?:'ll| will)\s+(.+?)(?:\.|$)",
    ],
    "protections": [
        r"(?:Never|Don't ever)\s+(.+?)(?:\.|$)",
        r"(?:Always|Must always)\s+(.+?)(?:\.|$)",
        r"(?:Red flag|WARNING):\s*(.+?)(?:\.|$)",
        r"(?:Protect|Guard|Watch out for):\s*(.+?)(?:\.|$)",
    ],
}

# Section headers that indicate metacognitive content
SECTION_HEADERS = re.compile(
    r"^##\s*(?:Lessons?\s*Learned|Reflections?|Takeaways?|Insights?|What I Learned)",
    re.IGNORECASE | re.MULTILINE,
)


def extract_entries_from_text(text: str) -> list[tuple[str, str]]:
    """Extract (type, content) pairs from text using all pattern sets."""
    results = []
    seen_texts = set()

    def _add(etype, content):
        content = content.strip().rstrip(".")
        if len(content) < 5 or content.lower() in seen_texts:
            return
        seen_texts.add(content.lower())
        results.append((etype, content))

    # 1. Prefix patterns (highest priority)
    for etype, regexes in PREFIX_PATTERNS.items():
        for pat in regexes:
            for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
                _add(etype, m.group(1))

    # 2. Natural language patterns
    for etype, regexes in NL_PATTERNS.items():
        for pat in regexes:
            for m in re.finditer(pat, text, re.IGNORECASE | re.MULTILINE):
                _add(etype, m.group(1))

    # 3. Bullet points under lessons/reflections sections
    for header_match in SECTION_HEADERS.finditer(text):
        start = header_match.end()
        # Grab until next header or end
        next_header = re.search(r"^##\s", text[start:], re.MULTILINE)
        section = text[start:start + next_header.start()] if next_header else text[start:]
        for bullet in re.finditer(r"^[-*]\s+(.+)$", section, re.MULTILINE):
            _add("perceptions", bullet.group(1))

    return results


# ---------------------------------------------------------------------------
# Graph operations
# ---------------------------------------------------------------------------

def _compute_similarity(entry_a: dict, entry_b: dict) -> float:
    """Compute similarity between two entries using embeddings or fallback."""
    if entry_a.get("embedding") and entry_b.get("embedding"):
        return cosine_similarity(entry_a["embedding"], entry_b["embedding"])
    return _fallback_similarity(entry_a["text"], entry_b["text"])


def _find_or_create_edge(edges: list, id_a: str, id_b: str) -> dict:
    """Find existing edge or return None."""
    key = tuple(sorted([id_a, id_b]))
    for edge in edges:
        if tuple(sorted([edge["source"], edge["target"]])) == key:
            return edge
    return None


def build_edges(data: dict) -> int:
    """Scan all entry pairs, create/update edges for related-but-distinct entries."""
    entries = data["entries"]
    edges = data.setdefault("edges", [])
    new_edges = 0

    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            sim = _compute_similarity(a, b)
            if sim >= EDGE_SIM_THRESHOLD and sim < (EMBEDDING_SIM_THRESHOLD if a.get("embedding") else FALLBACK_SIM_THRESHOLD):
                existing = _find_or_create_edge(edges, a["id"], b["id"])
                if existing:
                    # Reinforce existing edge
                    existing["weight"] = min(existing["weight"] + 0.1, 2.0)
                    existing["last_seen"] = now_iso()
                else:
                    edges.append({
                        "source": a["id"],
                        "target": b["id"],
                        "weight": sim,
                        "created": now_iso(),
                        "last_seen": now_iso(),
                    })
                    new_edges += 1
    return new_edges


def decay_edges(data: dict) -> int:
    """Decay edge weights and prune weak ones."""
    edges = data.get("edges", [])
    for edge in edges:
        last = datetime.fromisoformat(edge["last_seen"])
        days = (datetime.now() - last).total_seconds() / 86400.0
        edge["weight"] *= math.pow(0.5, days / (HALF_LIFE_DAYS * 2))  # edges decay slower
    before = len(edges)
    data["edges"] = [e for e in edges if e["weight"] >= EDGE_WEIGHT_FLOOR]
    return before - len(data["edges"])


def get_neighbors(data: dict, entry_id: str) -> list[tuple[dict, float]]:
    """Get connected entries sorted by edge weight."""
    edges = data.get("edges", [])
    neighbors = []
    entry_map = {e["id"]: e for e in data["entries"]}
    for edge in edges:
        if edge["source"] == entry_id and edge["target"] in entry_map:
            neighbors.append((entry_map[edge["target"]], edge["weight"]))
        elif edge["target"] == entry_id and edge["source"] in entry_map:
            neighbors.append((entry_map[edge["source"]], edge["weight"]))
    neighbors.sort(key=lambda x: x[1], reverse=True)
    return neighbors


def find_clusters(data: dict) -> list[list[str]]:
    """Find connected components in the graph (clusters of related insights)."""
    edges = data.get("edges", [])
    if not edges:
        return []
    
    # Build adjacency
    adj = {}
    all_ids = set()
    for edge in edges:
        adj.setdefault(edge["source"], set()).add(edge["target"])
        adj.setdefault(edge["target"], set()).add(edge["source"])
        all_ids.add(edge["source"])
        all_ids.add(edge["target"])
    
    # BFS for components
    visited = set()
    clusters = []
    for start in all_ids:
        if start in visited:
            continue
        cluster = []
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            cluster.append(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)
        if len(cluster) > 1:
            clusters.append(cluster)
    return clusters


# ---------------------------------------------------------------------------
# Reweave
# ---------------------------------------------------------------------------

def cmd_reweave(args=None) -> str:
    """Revisit existing entries, build graph connections, identify clusters 
    that might represent higher-level principles."""
    data = load()
    results = []
    
    # 1. Build/update edges
    new_edges = build_edges(data)
    results.append(f"Graph: {new_edges} new edges, {len(data.get('edges', []))} total")
    
    # 2. Decay old edges
    pruned = decay_edges(data)
    if pruned:
        results.append(f"Pruned {pruned} weak edges")
    
    # 3. Find clusters
    clusters = find_clusters(data)
    entry_map = {e["id"]: e for e in data["entries"]}
    
    if clusters:
        results.append(f"\nFound {len(clusters)} cluster(s) of related insights:")
        for i, cluster in enumerate(clusters):
            entries_in_cluster = [entry_map[eid] for eid in cluster if eid in entry_map]
            if not entries_in_cluster:
                continue
            results.append(f"\n  Cluster {i+1} ({len(entries_in_cluster)} entries):")
            for e in entries_in_cluster:
                results.append(f"    [{e['type']}] {e['text'][:70]}")
            
            # Mutual reinforcement: entries in a cluster strengthen each other
            for e in entries_in_cluster:
                boost = 0.05 * (len(entries_in_cluster) - 1)
                e["strength"] = min(e["strength"] + boost, STRENGTH_CAP)
                e["last_reinforced"] = now_iso()
    else:
        results.append("No clusters found yet (need more entries or stronger connections)")
    
    save(data)
    output = "\n".join(results)
    print(output)
    return output


def cmd_graph(args=None) -> str:
    """Show graph statistics: edges, clusters, most-connected nodes."""
    data = load()
    edges = data.get("edges", [])
    entries = data["entries"]
    entry_map = {e["id"]: e for e in entries}
    
    lines = [f"Graph: {len(entries)} nodes, {len(edges)} edges"]
    
    if not edges:
        lines.append("No connections yet. Run 'reweave' to build the graph.")
        output = "\n".join(lines)
        print(output)
        return output
    
    # Degree count (most connected entries)
    degree = {}
    for edge in edges:
        degree[edge["source"]] = degree.get(edge["source"], 0) + 1
        degree[edge["target"]] = degree.get(edge["target"], 0) + 1
    
    lines.append("\nMost connected entries:")
    for eid, count in sorted(degree.items(), key=lambda x: x[1], reverse=True)[:5]:
        if eid in entry_map:
            e = entry_map[eid]
            lines.append(f"  {count} connections: [{e['type']}] {e['text'][:60]}")
    
    clusters = find_clusters(data)
    lines.append(f"\nClusters: {len(clusters)}")
    for i, cluster in enumerate(clusters):
        cluster_entries = [entry_map[eid] for eid in cluster if eid in entry_map]
        if cluster_entries:
            lines.append(f"  Cluster {i+1}: {len(cluster_entries)} entries")
            for e in cluster_entries:
                lines.append(f"    [{e['type']}] {e['text'][:60]}")
    
    output = "\n".join(lines)
    print(output)
    return output


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args) -> str:
    etype = args.type
    text = " ".join(args.text)
    if etype not in VALID_TYPES:
        msg = f"Invalid type '{etype}'. Choose from: {', '.join(VALID_TYPES)}"
        print(msg)
        return msg

    data = load()
    embedding = get_embedding(text)

    idx, existing, score = find_similar(data["entries"], text, embedding)
    if existing:
        reinforce(existing)
        merged = False
        if len(text) > len(existing["text"]):
            existing["text"] = text
            if embedding:
                existing["embedding"] = embedding
            merged = True
        update_curiosity_stage(existing, merged=merged)
        save(data)
        msg = f"Merged with existing entry {existing['id']} (strength → {existing['strength']:.2f})"
    else:
        entry = make_entry(etype, text, embedding)
        data["entries"].append(entry)
        save(data)
        msg = f"Added {etype} entry {entry['id']}: {text[:60]}"
    print(msg)
    return msg


def cmd_list(args) -> str:
    data = load()
    entries = data["entries"]
    if args.type:
        entries = [e for e in entries if e["type"] == args.type]
    if not entries:
        print("No entries found.")
        return "No entries found."
    entries.sort(key=lambda e: priority_score(e), reverse=True)
    lines = []
    for e in entries:
        stage = f" [{e.get('curiosity_stage', '')}]" if e.get("curiosity_stage") else ""
        line = f"  {e['id']}  {e['strength']:5.2f}  {e['type']:20s}{stage}  {e['text'][:70]}"
        lines.append(line)
    output = "\n".join(lines)
    print(output)
    return output


def cmd_feedback(args) -> str:
    data = load()
    positive = args.direction == "positive"
    for e in data["entries"]:
        if e["id"] == args.entry_id:
            reinforce(e, positive)
            if positive:
                update_curiosity_stage(e)
            save(data)
            msg = f"{'Strengthened' if positive else 'Weakened'} {e['id']} → {e['strength']:.2f}"
            print(msg)
            return msg
    msg = f"Entry {args.entry_id} not found."
    print(msg)
    return msg


def cmd_decay(args=None) -> str:
    data = load()
    for e in data["entries"]:
        e["strength"] = round(e["strength"] * decay_factor(e), 4)
    before = len(data["entries"])
    data["entries"] = [e for e in data["entries"] if e["strength"] >= STRENGTH_FLOOR]
    pruned_entries = before - len(data["entries"])
    
    # Also decay edges and prune dead-end edges (where entry was pruned)
    live_ids = {e["id"] for e in data["entries"]}
    edges_before = len(data.get("edges", []))
    data["edges"] = [e for e in data.get("edges", []) if e["source"] in live_ids and e["target"] in live_ids]
    pruned_edges = decay_edges(data)
    pruned_edges += edges_before - len(data.get("edges", [])) - pruned_edges
    
    save(data)
    msg = f"Decay applied. {pruned_entries} entries pruned, {len(data['entries'])} remaining. {len(data.get('edges', []))} edges."
    print(msg)
    return msg


def cmd_compile(args=None) -> str:
    data = load()
    entries = [e for e in data["entries"] if e["strength"] >= 0.1]

    # Header with metadata
    total = len(data["entries"])
    ts = now_iso()
    lines = [
        "# Metacognition Lens",
        "",
        f"*{total} entries | compiled {ts}*",
        "",
        "Active self-knowledge, compiled from experience.",
        "",
    ]

    type_headers = {
        "protections": "## Protect",
        "overrides": "## Override",
        "perceptions": "## Perceive",
        "self-observations": "## Observe",
        "decisions": "## Decide",
        "curiosities": "## Curious About",
    }

    # Group and sort within groups by priority
    grouped = {}
    for e in entries:
        grouped.setdefault(e["type"], []).append(e)
    for etype in grouped:
        grouped[etype].sort(key=priority_score, reverse=True)

    # Proportional budget allocation
    header_cost = approx_tokens("\n".join(lines))
    remaining_budget = LENS_TOKEN_BUDGET - header_cost
    # Reserve 80 tokens for curiosities footer
    curiosity_footer_budget = 80
    remaining_budget -= curiosity_footer_budget

    type_counts = {t: len(grouped.get(t, [])) for t in VALID_TYPES if t in grouped}
    total_entries = sum(type_counts.values())
    if total_entries == 0:
        total_entries = 1  # avoid div by zero

    type_budgets = {}
    for t in VALID_TYPES:
        if t in grouped:
            type_budgets[t] = max(30, int(remaining_budget * type_counts[t] / total_entries))

    for etype in VALID_TYPES:
        if etype not in grouped:
            continue
        header = type_headers.get(etype, f"## {etype.title()}")
        section = [header]
        budget = type_budgets.get(etype, 50)
        used = 0
        for e in grouped[etype]:
            bullet = f"- {e['text']}"
            cost = approx_tokens(bullet)
            if used + cost > budget:
                break
            section.append(bullet)
            used += cost
        if len(section) > 1:
            lines.extend(section)
            lines.append("")

    # Top 3 active curiosities
    active_curiosities = [
        e for e in entries
        if e["type"] == "curiosities" and e.get("curiosity_stage") in ("born", "active", "evolving")
    ]
    active_curiosities.sort(key=priority_score, reverse=True)
    if active_curiosities:
        lines.append("## 🔭 Top Active Curiosities")
        for e in active_curiosities[:3]:
            stage = e.get("curiosity_stage", "born")
            lines.append(f"- [{stage}] {e['text']}")
        lines.append("")

    # Graph clusters — show connected insight themes
    clusters = find_clusters(data)
    entry_map = {e["id"]: e for e in data["entries"]}
    if clusters:
        lines.append("## 🕸 Insight Clusters")
        for i, cluster in enumerate(clusters[:3]):  # top 3 clusters
            cluster_entries = [entry_map[eid] for eid in cluster if eid in entry_map]
            if len(cluster_entries) < 2:
                continue
            cluster_entries.sort(key=priority_score, reverse=True)
            lines.append(f"- **Cluster {i+1}** ({len(cluster_entries)} connected):")
            for e in cluster_entries[:4]:
                lines.append(f"  - [{e['type']}] {e['text'][:60]}")
        lines.append("")

    output = "\n".join(lines).strip() + "\n"
    LENS_OUT.write_text(output)
    print(output)
    total_tokens = approx_tokens(output)
    print(f"--- Written to {LENS_OUT} (~{total_tokens} tokens) ---")
    return output


def cmd_extract(args) -> str:
    note_path = Path(args.path)
    if not note_path.exists():
        msg = f"File not found: {note_path}"
        print(msg)
        return msg

    size = note_path.stat().st_size
    if size > MAX_NOTE_SIZE:
        msg = f"File too large ({size} bytes, max {MAX_NOTE_SIZE}). Skipping."
        print(msg, file=sys.stderr)
        return msg

    text = note_path.read_text()
    return _extract_from_text(text, note_path.name)


def _extract_from_text(text: str, source_name: str = "input") -> str:
    """Core extraction logic, separated for testability."""
    data = load()
    extracted = extract_entries_from_text(text)
    added, merged = 0, 0

    for etype, content in extracted:
        embedding = get_embedding(content)
        idx, existing, score = find_similar(data["entries"], content, embedding)
        if existing:
            reinforce(existing)
            m = False
            if len(content) > len(existing["text"]):
                existing["text"] = content
                if embedding:
                    existing["embedding"] = embedding
                m = True
            update_curiosity_stage(existing, merged=m)
            merged += 1
        else:
            data["entries"].append(make_entry(etype, content, embedding))
            added += 1

    # Prune if over max entries
    if len(data["entries"]) > MAX_ENTRIES:
        data["entries"].sort(key=lambda e: e["strength"])
        data["entries"] = data["entries"][len(data["entries"]) - MAX_ENTRIES:]

    save(data)
    msg = f"Extracted from {source_name}: {added} new, {merged} reinforced."
    print(msg)
    return msg


def cmd_resolve(args) -> str:
    data = load()
    for e in data["entries"]:
        if e["id"] == args.entry_id:
            if e["type"] != "curiosities":
                msg = f"Entry {e['id']} is not a curiosity (it's {e['type']})."
                print(msg)
                return msg
            e["curiosity_stage"] = "resolved"
            e["last_reinforced"] = now_iso()
            save(data)
            msg = f"Curiosity {e['id']} marked as resolved. It will now decay faster."
            print(msg)
            return msg
    msg = f"Entry {args.entry_id} not found."
    print(msg)
    return msg


def cmd_integrate(args=None) -> str:
    """Full integration cycle: decay → extract → reweave → compile."""
    results = []

    # 1. Decay
    results.append("=== Decay ===")
    results.append(cmd_decay())

    # 2. Find most recent daily note
    results.append("\n=== Extract ===")
    daily_note = _find_latest_daily_note()
    if daily_note:
        text = daily_note.read_text()
        results.append(_extract_from_text(text, daily_note.name))
    else:
        results.append("No daily note found.")

    # 3. Reweave — build graph connections
    results.append("\n=== Reweave ===")
    results.append(cmd_reweave())

    # 4. Compile
    results.append("\n=== Compile ===")
    cmd_compile()

    # 4. Summary
    data = load()
    total = len(data["entries"])
    by_type = {}
    for e in data["entries"]:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    summary = f"\nTotal: {total} entries — " + ", ".join(f"{t}: {c}" for t, c in sorted(by_type.items()))
    results.append(summary)
    output = "\n".join(results)
    print(output)
    return output


def _find_latest_daily_note() -> "Path":
    """Find the most recent daily note by date pattern in memory dir."""
    if not MEMORY_DIR.exists():
        return None
    date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\.md$")
    candidates = []
    for f in MEMORY_DIR.iterdir():
        m = date_pattern.search(f.name)
        if m:
            candidates.append((m.group(1), f))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Metacognition Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add an entry")
    p_add.add_argument("type", choices=VALID_TYPES)
    p_add.add_argument("text", nargs="+")

    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("type", nargs="?", default=None, choices=VALID_TYPES)

    p_fb = sub.add_parser("feedback", help="Reinforce or weaken an entry")
    p_fb.add_argument("entry_id")
    p_fb.add_argument("direction", choices=["positive", "negative"])

    sub.add_parser("decay", help="Apply time-based decay")
    sub.add_parser("compile", help="Compile the metacognition lens")

    p_ex = sub.add_parser("extract", help="Extract entries from a daily note")
    p_ex.add_argument("path")

    p_res = sub.add_parser("resolve", help="Mark a curiosity as resolved")
    p_res.add_argument("entry_id")

    sub.add_parser("integrate", help="Full cycle: decay → extract → reweave → compile")
    sub.add_parser("reweave", help="Build graph connections, find clusters")
    sub.add_parser("graph", help="Show graph statistics and clusters")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "add": cmd_add, "list": cmd_list, "feedback": cmd_feedback,
        "decay": cmd_decay, "compile": cmd_compile, "extract": cmd_extract,
        "resolve": cmd_resolve, "integrate": cmd_integrate,
        "reweave": cmd_reweave, "graph": cmd_graph,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
