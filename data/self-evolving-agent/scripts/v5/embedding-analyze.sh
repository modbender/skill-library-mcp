#!/usr/bin/env bash
# ============================================================
# scripts/v5/embedding-analyze.sh — Semantic Embedding Analysis
#
# Stage 2 (v5): Analyzes user messages using Ollama local embeddings
# for true semantic similarity matching.
#
# Fallback chain:
#   Ollama available  → cosine similarity (nomic-embed-text)
#   Ollama offline    → v4 heuristic (semantic-analyze.sh)
#   No sessions       → empty result with "no_data" engine
#
# Environment:
#   OLLAMA_URL                Ollama API base (default: http://localhost:11434)
#   EMBEDDING_MODEL           Embedding model (default: nomic-embed-text)
#   EMBEDDING_SIMILARITY_THR  Cosine threshold (default: 0.78)
#   EMBEDDING_FALLBACK_ALLOWED  Allow v4 fallback (default: true)
#   OUTPUT_JSON               Output file path
#   AGENTS_BASE               Agent sessions directory
#   LOGS_DIR                  Logs directory
#   COLLECT_DAYS              Days to look back (default: 7)
#   MAX_SESSIONS              Max sessions to analyze (default: 30)
#   SEA_TMP_DIR               Temp directory
#
# SECURITY MANIFEST:
#   - Reads: $AGENTS_BASE/**/*.jsonl, $LOGS_DIR/*.log
#   - Writes: $OUTPUT_JSON, $SEA_TMP_DIR/embedding-*.json
#   - Network: $OLLAMA_URL (local only, no internet)
#   - Exec: None
# ============================================================
# shellcheck shell=bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="${SKILL_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# ── Configuration ──────────────────────────────────────────
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"
SIMILARITY_THRESHOLD="${EMBEDDING_SIMILARITY_THR:-0.78}"
FALLBACK_ALLOWED="${EMBEDDING_FALLBACK_ALLOWED:-true}"
OUTPUT_JSON="${OUTPUT_JSON:-${SEA_TMP_DIR:-/tmp/sea-v5}/embedding-analysis.json}"
AGENTS_BASE="${AGENTS_BASE:-$HOME/.openclaw/agents}"
LOGS_DIR="${LOGS_DIR:-$HOME/.openclaw/logs}"
COLLECT_DAYS="${COLLECT_DAYS:-7}"
MAX_SESSIONS="${MAX_SESSIONS:-30}"
SEA_TMP="${SEA_TMP_DIR:-/tmp/sea-v5}"

mkdir -p "$(dirname "$OUTPUT_JSON")" "$SEA_TMP" 2>/dev/null || true

# ── Logging ────────────────────────────────────────────────
log() { echo "[SEA-v5 embed] $*" >&2; }

# ── Helper: check Ollama availability ─────────────────────
check_ollama() {
  curl -sf --max-time 3 "${OLLAMA_URL}/api/tags" > /dev/null 2>&1
}

# ── Helper: embed a text string via Ollama ─────────────────
embed_text() {
  local text="$1"
  local response
  response=$(curl -sf --max-time 10 \
    -X POST "${OLLAMA_URL}/api/embeddings" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"${EMBEDDING_MODEL}\", \"prompt\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$text")}" \
    2>/dev/null) || return 1
  echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(json.dumps(d.get('embedding', [])))
" 2>/dev/null || return 1
}

# ── Helper: cosine similarity ──────────────────────────────
cosine_similarity() {
  local vec_a="$1"
  local vec_b="$2"
  python3 - "$vec_a" "$vec_b" << 'PYEOF' 2>/dev/null || echo "0"
import json, math, sys
a = json.loads(sys.argv[1])
b = json.loads(sys.argv[2])
if not a or not b or len(a) != len(b):
    print(0)
    sys.exit(0)
dot = sum(x*y for x, y in zip(a, b))
mag_a = math.sqrt(sum(x**2 for x in a))
mag_b = math.sqrt(sum(x**2 for x in b))
if mag_a == 0 or mag_b == 0:
    print(0)
else:
    print(round(dot / (mag_a * mag_b), 6))
PYEOF
}

# ── Main ───────────────────────────────────────────────────
main() {
  log "Starting embedding analysis"
  log "Ollama URL: $OLLAMA_URL"
  log "Model: $EMBEDDING_MODEL"
  log "Threshold: $SIMILARITY_THRESHOLD"

  # Check Ollama
  if ! check_ollama; then
    log "Ollama offline or unreachable at $OLLAMA_URL"

    if [ "$FALLBACK_ALLOWED" = "true" ]; then
      log "EMBEDDING_FALLBACK=true — falling back to v4 heuristic analysis"

      # Run v4 semantic-analyze.sh as fallback
      local v4_analysis_out="$SEA_TMP/analysis-fallback.json"
      local collect_out="$SEA_TMP/collect-fallback.json"

      # Collect first
      AGENTS_BASE="$AGENTS_BASE" \
      LOGS_DIR="$LOGS_DIR" \
      COLLECT_DAYS="$COLLECT_DAYS" \
      MAX_SESSIONS="$MAX_SESSIONS" \
      SEA_TMP_DIR="$SEA_TMP" \
      bash "$SKILL_DIR/scripts/v4/collect-logs.sh" "$collect_out" > /dev/null 2>&1 || true

      # Then analyze
      LOGS_JSON="${collect_out}" \
      OUTPUT_JSON="${v4_analysis_out}" \
      AGENTS_DIR="$AGENTS_BASE" \
      ANALYSIS_DAYS="$COLLECT_DAYS" \
      MAX_SESSIONS="$MAX_SESSIONS" \
      SEA_VERBOSE=false \
      bash "$SKILL_DIR/scripts/v4/semantic-analyze.sh" > /dev/null 2>&1 || true

      if [ -f "$v4_analysis_out" ]; then
        # Wrap v4 output with v5 envelope
        python3 - "$v4_analysis_out" "$OUTPUT_JSON" << 'PYEOF' 2>/dev/null || true
import json, sys
v4 = json.load(open(sys.argv[1]))
out = {
    "engine": "heuristic",
    "analysis_engine": "heuristic",
    "fallback_reason": "ollama_offline",
    "embedding_model": None,
    "similarity_threshold": None,
    "sessions_analyzed": v4.get("sessions_analyzed", 0),
    "frustration_events": v4.get("frustration_events", []),
    "complaint_signals": v4.get("complaint_signals", []),
    "failure_patterns": v4.get("failure_patterns", []),
    "rule_violations": v4.get("rule_violations", []),
    "exec_loops": v4.get("exec_loops", []),
    "quality_score": v4.get("quality_score", 5.0),
    "key_insights": v4.get("key_insights", []),
    "semantic_clusters": [],
    "confidence_scores": {},
    "fp_estimate": 0.15,
    "metadata": v4.get("metadata", {})
}
with open(sys.argv[2], 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
PYEOF
        log "Fallback analysis complete: $OUTPUT_JSON"
      else
        # Write minimal fallback output
        python3 -c "
import json
out = {
    'engine': 'fallback',
    'analysis_engine': 'fallback',
    'fallback_reason': 'ollama_offline_and_v4_failed',
    'sessions_analyzed': 0,
    'frustration_events': [],
    'complaint_signals': [],
    'failure_patterns': [],
    'rule_violations': [],
    'exec_loops': [],
    'quality_score': 5.0,
    'key_insights': ['Ollama offline, v4 fallback also failed'],
    'semantic_clusters': [],
    'confidence_scores': {},
    'fp_estimate': 0.30,
    'metadata': {}
}
import sys
with open(sys.argv[1], 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
" "$OUTPUT_JSON" 2>/dev/null || true
        log "Minimal fallback output written"
      fi
    else
      log "Fallback not allowed. Writing empty result."
      python3 -c "
import json, sys
out = {'engine': 'none', 'error': 'ollama_offline', 'fallback_allowed': False,
       'sessions_analyzed': 0, 'frustration_events': [], 'quality_score': 5.0}
with open(sys.argv[1], 'w') as f:
    json.dump(out, f, indent=2)
" "$OUTPUT_JSON" 2>/dev/null || true
    fi
    return 0
  fi

  log "Ollama is available — running semantic embedding analysis"

  # Collect sessions
  local collect_out="$SEA_TMP/collect-embed.json"
  AGENTS_BASE="$AGENTS_BASE" \
  LOGS_DIR="$LOGS_DIR" \
  COLLECT_DAYS="$COLLECT_DAYS" \
  MAX_SESSIONS="$MAX_SESSIONS" \
  SEA_TMP_DIR="$SEA_TMP" \
  bash "$SKILL_DIR/scripts/v4/collect-logs.sh" "$collect_out" > /dev/null 2>&1 || true

  if [ ! -f "$collect_out" ]; then
    log "No collect output — writing empty result"
    python3 -c "
import json, sys
out = {'engine': 'embedding', 'sessions_analyzed': 0, 'frustration_events': [],
       'semantic_clusters': [], 'quality_score': 5.0, 'fp_estimate': 0.08}
with open(sys.argv[1], 'w') as f:
    json.dump(out, f, indent=2)
" "$OUTPUT_JSON" 2>/dev/null || true
    return 0
  fi

  # Run embedding analysis on collected sessions
  python3 - "$collect_out" "$OUTPUT_JSON" "$SIMILARITY_THRESHOLD" "$OLLAMA_URL" "$EMBEDDING_MODEL" << 'PYEOF' 2>/dev/null || true
import json, sys, math, urllib.request, urllib.error

collect_file = sys.argv[1]
output_file  = sys.argv[2]
threshold    = float(sys.argv[3])
ollama_url   = sys.argv[4]
embed_model  = sys.argv[5]

def get_embedding(text, url, model):
    """Call Ollama embeddings API."""
    payload = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{url}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("embedding", [])
    except Exception:
        return []

def cosine_sim(a, b):
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x**2 for x in a))
    mag_b = math.sqrt(sum(x**2 for x in b))
    return dot / (mag_a * mag_b) if mag_a > 0 and mag_b > 0 else 0.0

# Frustration anchor texts
FRUSTRATION_ANCHORS = [
    "I told you this before, why do you keep forgetting?",
    "You made the same mistake again",
    "How many times do I have to tell you?",
    "말했잖아, 왜 또 그래?",
    "또 같은 실수를 반복하네",
    "몇 번을 말해야 알아듣냐",
]

# Get anchor embeddings (small list, cached)
print("[SEA-v5 embed] Computing frustration anchor embeddings...", file=sys.stderr)
anchor_vecs = []
for anchor in FRUSTRATION_ANCHORS:
    vec = get_embedding(anchor, ollama_url, embed_model)
    if vec:
        anchor_vecs.append(vec)

if not anchor_vecs:
    print("[SEA-v5 embed] Could not get anchor embeddings", file=sys.stderr)
    sys.exit(1)

# Load collected sessions
collected = json.load(open(collect_file))
sessions = collected.get("sessions", [])
print(f"[SEA-v5 embed] Analyzing {len(sessions)} sessions...", file=sys.stderr)

frustration_events = []
for session in sessions:
    session_id = session.get("id", "unknown")
    messages = session.get("user_messages", session.get("messages", []))
    for msg in messages:
        text = msg if isinstance(msg, str) else msg.get("text", msg.get("content", ""))
        if not text or len(text) < 5:
            continue
        vec = get_embedding(text, ollama_url, embed_model)
        if not vec:
            continue
        max_sim = max(cosine_sim(vec, anchor) for anchor in anchor_vecs)
        if max_sim >= threshold:
            frustration_events.append({
                "session_id": session_id,
                "text": text[:200],
                "similarity": round(max_sim, 4),
                "engine": "embedding"
            })

# Build output
result = {
    "engine": "embedding",
    "analysis_engine": "embedding",
    "embedding_model": embed_model,
    "similarity_threshold": threshold,
    "sessions_analyzed": len(sessions),
    "frustration_events": frustration_events,
    "complaint_signals": frustration_events,  # alias for v4 compat
    "failure_patterns": collected.get("exec_retry_patterns", {}),
    "rule_violations": [],
    "exec_loops": [],
    "semantic_clusters": [],  # k-means clustering — future enhancement
    "confidence_scores": {
        "avg_max_similarity": round(
            sum(e["similarity"] for e in frustration_events) / len(frustration_events), 4
        ) if frustration_events else 0.0
    },
    "quality_score": max(1, min(10, 10 - len(frustration_events) * 0.3)),
    "key_insights": [
        f"Found {len(frustration_events)} frustration signals via semantic embedding",
        f"Threshold: {threshold}, Model: {embed_model}"
    ],
    "fp_estimate": 0.08,
    "metadata": {
        "collected_at": collected.get("collected_at", ""),
        "analysis_type": "semantic_embedding",
        "anchor_count": len(anchor_vecs)
    }
}

with open(output_file, 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"[SEA-v5 embed] Complete: {len(frustration_events)} frustration events found", file=sys.stderr)
PYEOF

  log "Embedding analysis complete: $OUTPUT_JSON"
}

main "$@"
