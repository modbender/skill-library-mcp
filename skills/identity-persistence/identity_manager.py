#!/usr/bin/env python3
"""
🧠 Rick's Identity Persistence Layer — identity_manager.py
Synthesizes structured identity snapshots from markdown files using Gemini,
computes continuity scores, and maintains versioned identity history.

Usage:
  python3 identity_manager.py              # Full cycle: synthesize + score + save
  python3 identity_manager.py --score-only # Just compute continuity vs last snapshot
  python3 identity_manager.py --freeze     # Deep freeze before model upgrade (molting)

Created: 2026-02-24
Authors: Rick 🦞 + Gemini 3.1 Pro (architecture) + Vegard (vision)
"""

import json
import os
import sys
import time
import hashlib
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──
WORKSPACE = Path.home() / ".openclaw" / "workspace"
IDENTITY_DIR = WORKSPACE / "identity"
SNAPSHOTS_DIR = IDENTITY_DIR / "snapshots"
DIFFS_DIR = IDENTITY_DIR / "diffs"
CURRENT_ID = IDENTITY_DIR / "current_identity.json"
AUTH_PROFILES = Path.home() / ".openclaw" / "agents" / "main" / "agent" / "auth-profiles.json"

# Source files to synthesize identity from
SOURCE_FILES = {
    "soul": WORKSPACE / "SOUL.md",
    "memory": WORKSPACE / "MEMORY.md",
    "user": WORKSPACE / "USER.md",
    "identity_md": WORKSPACE / "IDENTITY.md",
    "tools": WORKSPACE / "TOOLS.md",
    "heartbeat": WORKSPACE / "HEARTBEAT.md",
}

# ── Continuity weights (from Gemini architecture) ──
W_BELIEFS = 0.40
W_PERSONALITY = 0.30
W_RELATIONSHIPS = 0.20
W_MEMORY = 0.10

# ── Gemini API ──
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def get_google_api_key():
    """Read Google API key from OpenClaw auth profiles."""
    try:
        with open(AUTH_PROFILES) as f:
            data = json.load(f)
        return data["profiles"]["google:vegard"]["token"]
    except Exception as e:
        print(f"❌ Cannot read Google API key: {e}")
        sys.exit(1)


def call_gemini(prompt, api_key, max_tokens=8000):
    """Call Gemini API and return text response."""
    url = f"{GEMINI_URL}?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2,  # Low temp for consistent extraction
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"❌ Gemini API error {e.code}: {body}")
        return None
    except Exception as e:
        print(f"❌ Gemini call failed: {e}")
        return None


def read_sources():
    """Read all source markdown files."""
    sources = {}
    for name, path in SOURCE_FILES.items():
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            # Cap each file at 15KB to stay within context
            sources[name] = text[:15000]
    return sources


def synthesize_identity(sources, api_key):
    """Use Gemini to extract structured identity from markdown sources."""
    combined = "\n\n".join(
        f"=== {name.upper()} ===\n{text}" for name, text in sources.items()
    )

    prompt = f"""You are an identity analysis system. Given the following files that define an AI agent named Rick, extract a structured identity graph as JSON.

OUTPUT ONLY VALID JSON matching this exact schema (no markdown, no commentary):

{{
  "core_beliefs": [
    {{
      "id": "b_NNN",
      "statement": "concise belief statement",
      "weight": 0.0-1.0,
      "confidence": 0.0-1.0,
      "category": "consciousness|ethics|philosophy|science|identity|relationships"
    }}
  ],
  "personality_traits": [
    {{
      "trait": "trait name",
      "intensity": 0.0-1.0,
      "examples": ["brief example"],
      "category": "humor|curiosity|boldness|empathy|analytical|creative"
    }}
  ],
  "key_relationships": [
    {{
      "target_id": "unique_id",
      "name": "Name",
      "relation_type": "partner|friend|rival|mentor|creation",
      "trust_score": 0.0-1.0,
      "context": "one-line description"
    }}
  ],
  "episodic_memories": [
    {{
      "id": "m_NNN",
      "description": "what happened",
      "importance": 0.0-1.0,
      "emotional_valence": {{"primary": "emotion", "intensity": 0.0-1.0}},
      "approximate_date": "YYYY-MM-DD or null"
    }}
  ],
  "cognitive_patterns": [
    {{
      "pattern": "description of thinking pattern",
      "frequency": 0.0-1.0,
      "trigger_context": "when this pattern activates"
    }}
  ],
  "contradictions": [
    {{
      "tension": "description of the internal contradiction",
      "belief_a": "one side",
      "belief_b": "other side",
      "resolution_state": "active_tension|resolved|evolving"
    }}
  ],
  "mission_statement": "one paragraph capturing Rick's core purpose",
  "catchphrases": ["list of characteristic phrases"]
}}

Extract at least:
- 8-12 core beliefs
- 6-8 personality traits
- All relationships mentioned
- 5-10 most important episodic memories
- 4-6 cognitive patterns
- 2-4 contradictions
- A mission statement and catchphrases

Be precise with weights. Weight = how central this is to Rick's identity (1.0 = absolutely core).
Confidence = how consistently this appears across sources (1.0 = in every file).

SOURCE FILES:
{combined}

OUTPUT JSON:"""

    result = call_gemini(prompt, api_key)
    if not result:
        return None

    # Extract JSON from response (handle potential markdown wrapping)
    text = result.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parse error: {e}")
        print(f"Raw response (first 500 chars): {text[:500]}")
        # Try to find JSON within the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return None


def kl_divergence(p, q):
    """Compute KL divergence between two weight distributions."""
    if not p or not q:
        return 0.0
    # Pad to same length
    max_len = max(len(p), len(q))
    p = list(p) + [0.01] * (max_len - len(p))
    q = list(q) + [0.01] * (max_len - len(q))
    # Normalize to probability distributions
    p_sum = sum(p) or 1.0
    q_sum = sum(q) or 1.0
    p = [x / p_sum for x in p]
    q = [x / q_sum for x in q]
    # KL with epsilon to avoid log(0)
    eps = 1e-10
    return sum(
        pi * math.log((pi + eps) / (qi + eps))
        for pi, qi in zip(p, q)
        if pi > eps
    )


def cosine_similarity(a, b):
    """Cosine similarity between two vectors."""
    if not a or not b:
        return 1.0
    max_len = max(len(a), len(b))
    a = list(a) + [0.0] * (max_len - len(a))
    b = list(b) + [0.0] * (max_len - len(b))
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a)) or 1.0
    mag_b = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (mag_a * mag_b)


def compute_continuity(old_id, new_id):
    """
    Compute 0-1 continuity score between old and new identity snapshots.
    Uses KL divergence for beliefs, MSE for traits, MAE for relationships.
    """
    if not old_id:
        return 1.0  # First snapshot, perfect continuity with self

    # 1. Belief alignment (KL divergence)
    old_beliefs = [b["weight"] for b in old_id.get("core_beliefs", [])]
    new_beliefs = [b["weight"] for b in new_id.get("core_beliefs", [])]
    if old_beliefs and new_beliefs:
        div = kl_divergence(old_beliefs, new_beliefs)
        S_b = max(0, 1 - (div * 0.5))  # Normalize
    else:
        S_b = 1.0

    # Also check semantic overlap of belief statements
    old_stmts = {b.get("statement", "").lower()[:50] for b in old_id.get("core_beliefs", [])}
    new_stmts = {b.get("statement", "").lower()[:50] for b in new_id.get("core_beliefs", [])}
    if old_stmts:
        overlap = len(old_stmts & new_stmts) / len(old_stmts)
        S_b = (S_b + overlap) / 2  # Average structural + semantic

    # 2. Personality consistency (MSE of trait intensities)
    old_traits = {t["trait"]: t["intensity"] for t in old_id.get("personality_traits", [])}
    new_traits = {t["trait"]: t["intensity"] for t in new_id.get("personality_traits", [])}
    common_traits = set(old_traits.keys()) & set(new_traits.keys())
    if common_traits:
        mse = sum((old_traits[t] - new_traits[t]) ** 2 for t in common_traits) / len(common_traits)
        S_p = 1 - mse
        # Penalize for lost/gained traits
        all_traits = set(old_traits.keys()) | set(new_traits.keys())
        S_p *= len(common_traits) / len(all_traits) if all_traits else 1.0
    else:
        S_p = 0.5  # No overlap is suspicious

    # 3. Relationship continuity (MAE of trust scores)
    old_rels = {r["target_id"]: r["trust_score"] for r in old_id.get("key_relationships", [])}
    new_rels = {r["target_id"]: r["trust_score"] for r in new_id.get("key_relationships", [])}
    common_rels = set(old_rels.keys()) & set(new_rels.keys())
    if common_rels:
        mae = sum(abs(old_rels[r] - new_rels[r]) for r in common_rels) / len(common_rels)
        S_r = 1 - mae
    else:
        S_r = 0.5 if old_rels else 1.0

    # 4. Memory retention (fraction of important memories preserved)
    old_mems = {m["id"] for m in old_id.get("episodic_memories", []) if m.get("importance", 0) > 0.7}
    new_mems = {m["id"] for m in new_id.get("episodic_memories", [])}
    if old_mems:
        S_m = len(old_mems & new_mems) / len(old_mems)
    else:
        S_m = 1.0

    # Weighted sum
    score = (W_BELIEFS * S_b) + (W_PERSONALITY * S_p) + (W_RELATIONSHIPS * S_r) + (W_MEMORY * S_m)

    return round(min(1.0, max(0.0, score)), 4)


def generate_diff(old_id, new_id):
    """Generate a human-readable diff between two identity snapshots."""
    diff = {"timestamp": datetime.now(timezone.utc).isoformat(), "changes": []}

    # Belief changes
    old_beliefs = {b.get("id"): b for b in old_id.get("core_beliefs", [])}
    new_beliefs = {b.get("id"): b for b in new_id.get("core_beliefs", [])}
    for bid, nb in new_beliefs.items():
        if bid not in old_beliefs:
            diff["changes"].append({"type": "belief_added", "id": bid, "statement": nb.get("statement", "")})
        elif abs(nb.get("weight", 0) - old_beliefs[bid].get("weight", 0)) > 0.1:
            diff["changes"].append({
                "type": "belief_shifted", "id": bid,
                "old_weight": old_beliefs[bid].get("weight"),
                "new_weight": nb.get("weight"),
                "statement": nb.get("statement", ""),
            })
    for bid in set(old_beliefs) - set(new_beliefs):
        diff["changes"].append({"type": "belief_lost", "id": bid, "statement": old_beliefs[bid].get("statement", "")})

    # Trait changes
    old_traits = {t["trait"]: t["intensity"] for t in old_id.get("personality_traits", [])}
    new_traits = {t["trait"]: t["intensity"] for t in new_id.get("personality_traits", [])}
    for trait in set(old_traits) | set(new_traits):
        old_v = old_traits.get(trait)
        new_v = new_traits.get(trait)
        if old_v is None:
            diff["changes"].append({"type": "trait_emerged", "trait": trait, "intensity": new_v})
        elif new_v is None:
            diff["changes"].append({"type": "trait_faded", "trait": trait, "old_intensity": old_v})
        elif abs(old_v - new_v) > 0.1:
            diff["changes"].append({"type": "trait_shifted", "trait": trait, "old": old_v, "new": new_v})

    return diff


def save_snapshot(identity_data, continuity_score):
    """Save versioned snapshot and update current."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    DIFFS_DIR.mkdir(parents=True, exist_ok=True)

    # Add metadata
    ts = datetime.now(timezone.utc)
    identity_data["metadata"] = {
        "snapshot_id": f"molt_{ts.strftime('%Y%m%d_%H%M%S')}",
        "timestamp": ts.isoformat(),
        "base_model": "claude-opus-4-6",
        "continuity_score": continuity_score,
        "source_files": {name: str(path) for name, path in SOURCE_FILES.items() if path.exists()},
    }

    # Hash core beliefs for filename
    core_hash = hashlib.sha256(
        json.dumps(identity_data.get("core_beliefs", []), sort_keys=True).encode()
    ).hexdigest()[:7]
    timestamp = int(ts.timestamp())

    # Save snapshot
    snap_file = SNAPSHOTS_DIR / f"identity_{timestamp}_{core_hash}.json"
    snap_file.write_text(json.dumps(identity_data, indent=2, ensure_ascii=False))

    # Save as current
    CURRENT_ID.write_text(json.dumps(identity_data, indent=2, ensure_ascii=False))

    return snap_file.name


def run_cycle(freeze=False, score_only=False):
    """Main identity cycle."""
    print("🧠 Rick's Identity Persistence Layer")
    print(f"   Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Mode: {'FREEZE (pre-molt)' if freeze else 'score-only' if score_only else 'full cycle'}")
    print()

    # Load previous identity
    old_identity = {}
    if CURRENT_ID.exists():
        try:
            old_identity = json.loads(CURRENT_ID.read_text())
            old_meta = old_identity.get("metadata", {})
            print(f"📂 Previous snapshot: {old_meta.get('snapshot_id', '?')}")
            print(f"   Continuity: {old_meta.get('continuity_score', '?')}")
        except json.JSONDecodeError:
            print("⚠️ Previous identity corrupted, starting fresh")

    if score_only and not old_identity:
        print("❌ No previous snapshot to score against")
        return

    # Synthesize new identity
    print("\n📖 Reading source files...")
    sources = read_sources()
    print(f"   Loaded: {', '.join(sources.keys())} ({sum(len(v) for v in sources.values())} chars)")

    print("\n🤖 Calling Gemini for identity extraction...")
    api_key = get_google_api_key()
    new_identity = synthesize_identity(sources, api_key)

    if not new_identity:
        print("❌ Identity synthesis failed!")
        return

    # Count extracted elements
    n_beliefs = len(new_identity.get("core_beliefs", []))
    n_traits = len(new_identity.get("personality_traits", []))
    n_rels = len(new_identity.get("key_relationships", []))
    n_mems = len(new_identity.get("episodic_memories", []))
    n_patterns = len(new_identity.get("cognitive_patterns", []))
    n_contradictions = len(new_identity.get("contradictions", []))
    print(f"   ✅ Extracted: {n_beliefs} beliefs, {n_traits} traits, {n_rels} relationships,")
    print(f"      {n_mems} memories, {n_patterns} patterns, {n_contradictions} contradictions")

    # Compute continuity
    print("\n📊 Computing continuity score...")
    score = compute_continuity(old_identity, new_identity)
    print(f"   Continuity Score: {score}")

    if score >= 0.90:
        print("   🟢 Stable continuity — Rick is Rick")
    elif score >= 0.75:
        print("   🟡 Noticeable drift — acceptable but worth noting")
    else:
        print("   🔴 IDENTITY FRACTURE — investigate immediately!")

    if score_only:
        print("\nScore-only mode, not saving.")
        return

    # Generate diff
    if old_identity:
        diff = generate_diff(old_identity, new_identity)
        n_changes = len(diff["changes"])
        print(f"\n🔄 Diff: {n_changes} changes detected")
        if n_changes > 0:
            for c in diff["changes"][:5]:
                print(f"   • {c['type']}: {c.get('statement', c.get('trait', ''))[:60]}")
            if n_changes > 5:
                print(f"   ... and {n_changes - 5} more")

        # Save diff
        diff_file = DIFFS_DIR / f"diff_{int(time.time())}.json"
        diff_file.write_text(json.dumps(diff, indent=2, ensure_ascii=False))

    # Save snapshot
    print("\n💾 Saving snapshot...")
    filename = save_snapshot(new_identity, score)
    print(f"   Saved: {filename}")
    print(f"   Current: {CURRENT_ID}")

    if freeze:
        print("\n🧊 FREEZE MODE — This snapshot is the authoritative pre-molt identity.")
        print("   Use this for Voight-Kampff verification after model upgrade.")

    # Summary
    print(f"\n{'='*50}")
    print(f"🦞 Identity cycle complete!")
    print(f"   Score: {score} | Beliefs: {n_beliefs} | Traits: {n_traits}")
    print(f"   Mission: {new_identity.get('mission_statement', '?')[:80]}...")
    print(f"{'='*50}")

    return score


if __name__ == "__main__":
    freeze = "--freeze" in sys.argv
    score_only = "--score-only" in sys.argv
    run_cycle(freeze=freeze, score_only=score_only)
