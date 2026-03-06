#!/usr/bin/env bash
# classify.sh — Batch-classify content items using LLM
# Reads JSON lines from stdin, outputs JSON lines with added "category" field
#
# Usage: cat items.jsonl | ./classify.sh
#
# Each input line must have at minimum: {"title": "...", ...}
# Output adds: {"title": "...", "category": "deep-technical", ...}
#
# Strategy: batches of 25 items per LLM call for token efficiency

set -euo pipefail
source "$(dirname "$0")/common.sh"

BATCH_SIZE="${FEED_DIET_BATCH_SIZE:-25}"

if ! command -v jq >/dev/null 2>&1; then
  err "jq is required for safe JSON construction in classify.sh"
  exit 1
fi

# ─── Read all items ──────────────────────────────────────────────────
ITEMS=()
while IFS= read -r line; do
  [ -z "$line" ] && continue
  ITEMS+=("$line")
done

TOTAL=${#ITEMS[@]}
if [ "$TOTAL" -eq 0 ]; then
  err "No items to classify. Pipe JSON lines to stdin."
  exit 1
fi

info "Classifying ${TOTAL} items in batches of ${BATCH_SIZE}..."

# ─── Process in batches ──────────────────────────────────────────────
CLASSIFIED=0

for ((i = 0; i < TOTAL; i += BATCH_SIZE)); do
  BATCH_END=$((i + BATCH_SIZE))
  [ "$BATCH_END" -gt "$TOTAL" ] && BATCH_END=$TOTAL
  BATCH_COUNT=$((BATCH_END - i))

  # Build the batch JSON array safely via jq
  BATCH_JSON="[]"
  for ((j = i; j < BATCH_END; j++)); do
    ITEM="${ITEMS[$j]}"
    TITLE=$(printf '%s' "$ITEM" | jq -r '.title // .item_title // ""' 2>/dev/null || echo "")
    URL=$(printf '%s' "$ITEM" | jq -r '.url // ""' 2>/dev/null || echo "")

    ENTRY=$(jq -cn --argjson idx "$j" --arg title "$TITLE" --arg url "$URL" \
      '{idx: $idx, title: $title, url: $url}')
    BATCH_JSON=$(jq -cn --argjson arr "$BATCH_JSON" --argjson entry "$ENTRY" '$arr + [$entry]')
  done

  # Build the classification prompt
  PROMPT="Classify each item into exactly one category. Categories:
- deep-technical: In-depth technical content, papers, systems design, low-level programming
- news: Current events, announcements, product releases, launches
- opinion: Takes, editorials, essays, personal perspectives  
- drama: Controversy, outrage, interpersonal conflict, firings, scandals
- entertainment: Fun, humor, lifestyle, games, art
- tutorial: How-tos, guides, educational content, documentation
- meta: Navel-gazing about tech industry itself, AI hype cycles, meta-discussion

Items to classify:
${BATCH_JSON}

Respond with ONLY a JSON array of objects, each with \"idx\" (number) and \"category\" (string).
Example: [{\"idx\":0,\"category\":\"news\"},{\"idx\":1,\"category\":\"deep-technical\"}]
No explanation, no markdown fences, just the JSON array."

  # Call LLM via the agent's classify endpoint or fallback to rule-based
  RESULT=""
  
  # Method 1: Use openclaw llm if available
  if command -v openclaw &>/dev/null; then
    RESULT=$(echo "$PROMPT" | openclaw llm --raw 2>/dev/null) || RESULT=""
  fi

  # Method 2: Use the ANTHROPIC_API_KEY directly
  if [ -z "$RESULT" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    request_body=$(jq -n \
      --arg model "claude-sonnet-4-20250514" \
      --arg prompt "$PROMPT" \
      '{
        model: $model,
        max_tokens: 1024,
        messages: [{role: "user", content: $prompt}]
      }')
    RESULT=$(printf '%s' "$request_body" | curl -sf --max-time 30 \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -H "content-type: application/json" \
      -d @- \
      https://api.anthropic.com/v1/messages 2>/dev/null | jq -r '.content[0].text // empty' 2>/dev/null) || RESULT=""
  fi

  # Method 3: Use OPENAI_API_KEY
  if [ -z "$RESULT" ] && [ -n "${OPENAI_API_KEY:-}" ]; then
    request_body=$(jq -n \
      --arg model "gpt-4o-mini" \
      --arg prompt "$PROMPT" \
      '{
        model: $model,
        max_tokens: 1024,
        messages: [{role: "user", content: $prompt}]
      }')
    RESULT=$(printf '%s' "$request_body" | curl -sf --max-time 30 \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      -H "content-type: application/json" \
      -d @- \
      https://api.openai.com/v1/chat/completions 2>/dev/null | jq -r '.choices[0].message.content // empty' 2>/dev/null) || RESULT=""
  fi

  # Method 4: Rule-based fallback (keyword matching)
  if [ -z "$RESULT" ]; then
    warn "No LLM available — using keyword-based classification (set ANTHROPIC_API_KEY or OPENAI_API_KEY for better results)"
    RESULT="[]"
    for ((j = i; j < BATCH_END; j++)); do
      ITEM="${ITEMS[$j]}"
      CATEGORY=$(echo "$ITEM" | python3 -c "
import json, sys, re
item = json.load(sys.stdin)
title = (item.get('title','') or item.get('item_title','')).lower()
url = item.get('url','').lower()
combined = title + ' ' + url

# Score-based classification — each category gets a score, highest wins
scores = {
    'tutorial': 0,
    'drama': 0,
    'opinion': 0,
    'entertainment': 0,
    'meta': 0,
    'deep-technical': 0,
    'news': 0,
}

# Tutorial signals
for w in ['tutorial', 'how to', 'howto', 'guide', 'getting started', 'introduction to', 'learn ', 'beginner', 'step by step', 'walkthrough', 'cookbook', 'cheat sheet', 'tips for', 'primer']:
    if w in title: scores['tutorial'] += 3
for w in ['tutorial', 'howto', 'guide', 'learn']:
    if w in url: scores['tutorial'] += 2

# Drama signals
for w in ['fired', 'scandal', 'controversy', 'toxic', 'outrage', 'lawsuit', 'sues', 'accused', 'backlash', 'layoff', 'layoffs', 'boycott', 'harass', 'abuse', 'whistleblow', 'leak', 'exposed', 'betrayed']:
    if w in title: scores['drama'] += 4
for w in ['drama', 'fight', 'war between', 'feud']:
    if w in title: scores['drama'] += 3

# Opinion signals
for w in ['opinion', 'editorial', 'why i ', 'why you should', 'hot take', 'unpopular', 'manifesto', 'letter to', 'open letter', 'i think', 'we need to talk', 'my experience', 'lessons learned', 'what i learned', 'reflections on', 'in defense of', 'against ', 'the case for', 'the case against', 'stop using', 'you don']:
    if w in title: scores['opinion'] += 3
for w in ['essay', 'take', 'should', 'must', 'need']:
    if w in title: scores['opinion'] += 1
for w in ['paulgraham.com', 'blog', 'medium.com', 'substack']:
    if w in url: scores['opinion'] += 1

# Entertainment signals
for w in ['game', 'humor', 'funny', 'art ', 'music', 'movie', 'meme', 'comic', 'joke', 'easter egg', 'pixel', 'animation', 'demoscene', 'demo ', 'ascii art', 'generative art', 'creative coding', 'toy', 'puzzle', 'fun ', 'play ', 'retro']:
    if w in title: scores['entertainment'] += 3
for w in ['youtube.com']:
    if w in url and not any(t in title for t in ['talk', 'lecture', 'conference', 'presentation']): scores['entertainment'] += 1

# Meta signals
for w in ['state of', 'future of', 'is dead', 'is dying', 'hype', 'bubble', 'hn ', 'hacker news', 'big tech', 'silicon valley', 'tech industry', 'vc ', 'venture capital', 'startup ecosystem', 'ai hype', 'ai bubble', 'tech culture', 'developer experience', 'dx ', 'what happened to']:
    if w in title: scores['meta'] += 3
for w in ['industry', 'market', 'trend']:
    if w in title: scores['meta'] += 1

# Deep-technical signals
for w in ['paper', 'algorithm', 'implementation', 'kernel', 'compiler', 'cpu', 'gpu', 'database', 'distributed system', 'protocol', 'bytecode', 'assembly', 'forth', 'lisp', 'low-level', 'garbage collect', 'parser', 'register', 'cache', 'virtual machine', 'type system', 'formal verif', 'proof', 'theorem', 'optimization', 'scheduler', 'file system', 'filesystem', 'memory model', 'concurrency', 'lock-free', 'b-tree', 'hash table', 'tcp', 'udp', 'syscall', 'interrupt', 'elf ', 'linker', 'loader', 'binary', 'disassemb', 'reverse engineer', 'exploit', 'buffer overflow', 'jit', 'aot', 'ir ', 'llvm', 'codegen', 'instruction set', 'isa ', 'risc', 'cisc', 'fpga', 'verilog', 'hdl', 'simd', 'vector', 'matrix', 'eigenvalue', 'neural net', 'transformer', 'attention', 'backprop', 'gradient']:
    if w in title: scores['deep-technical'] += 3
# URL-based tech signals
for w in ['arxiv.org', '.pdf', 'acm.org', 'ieee.org', 'usenix.org', 'github.com']:
    if w in url: scores['deep-technical'] += 2
# Programming language names in title (strong tech signal)
for w in ['rust ', 'zig ', 'haskell', 'ocaml', 'erlang', 'elixir', 'clojure', 'scheme', 'racket', 'prolog', 'cobol', 'fortran', 'ada ', 'apl', 'smalltalk', 'forth ', 'colorforth']:
    if w in title: scores['deep-technical'] += 2
# General tech terms
for w in ['programming', 'software', 'hardware', 'chip', 'processor', 'architecture', 'networking', 'cryptograph', 'encryption', 'hash', 'compression', 'encoding', 'unicode', 'utf', 'font', 'rendering', 'graphics', 'opengl', 'vulkan', 'webgl', 'shader', 'rasteriz']:
    if w in title: scores['deep-technical'] += 1
# Date patterns like (YYYY) or [YYYY] suggest classic/historical technical content
if re.search(r'[\(\[](19[0-9]{2}|20[01][0-9])[\)\]]', title):
    scores['deep-technical'] += 2

# News signals
for w in ['release', 'launched', 'announces', 'announced', 'ships', 'introduces', 'now available', 'raises', 'funding', 'acquired', 'acquisition', 'ipo', 'series a', 'series b', 'million', 'billion', 'partnership', 'joins', 'hires']:
    if w in title: scores['news'] += 3
for w in ['new', 'update', 'version', 'v1', 'v2', 'v3', 'v4', 'v0.', 'v1.', 'v2.', 'beta', 'alpha', 'preview', 'release candidate', 'rc1', 'rc2', 'stable']:
    if w in title: scores['news'] += 2
# Product names / companies submitting new things
for w in ['apple', 'google', 'microsoft', 'amazon', 'meta ', 'openai', 'anthropic', 'nvidia']:
    if w in title: scores['news'] += 1

# Pick the highest-scoring category (default: news if all tied at 0)
best = max(scores, key=scores.get)
if scores[best] == 0:
    # Title-length heuristic: short titles with URLs tend to be project/news links
    # Longer titles tend to be opinion/essay
    if len(title) > 60:
        best = 'opinion'
    else:
        best = 'news'
print(best)
" 2>/dev/null)
      ENTRY=$(jq -cn --argjson idx "$j" --arg category "$CATEGORY" '{idx: $idx, category: $category}')
      RESULT=$(jq -cn --argjson arr "$RESULT" --argjson entry "$ENTRY" '$arr + [$entry]')
    done
  fi

  # Parse LLM result and merge with original items
  echo "$RESULT" | python3 -c "
import json, sys

# Parse the classification result
text = sys.stdin.read().strip()
# Strip markdown code fences if present
if text.startswith('\`\`\`'):
    text = text.split('\n', 1)[1] if '\n' in text else text[3:]
if text.endswith('\`\`\`'):
    text = text[:text.rfind('\`\`\`')]
text = text.strip()

try:
    classifications = json.loads(text)
except json.JSONDecodeError:
    # Try to extract JSON array from the text
    import re
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        classifications = json.loads(match.group())
    else:
        classifications = []

# Build lookup
cat_map = {}
valid_cats = {'deep-technical','news','opinion','drama','entertainment','tutorial','meta'}
for c in classifications:
    idx = c.get('idx', -1)
    cat = c.get('category', 'news')
    if cat not in valid_cats:
        cat = 'news'
    cat_map[idx] = cat

# We need to output these for the batch processor
for idx, cat in sorted(cat_map.items()):
    print(json.dumps({'idx': idx, 'category': cat}))
" 2>/dev/null | while IFS= read -r CLASS_LINE; do
    IDX=$(echo "$CLASS_LINE" | python3 -c "import json,sys; print(json.load(sys.stdin)['idx'])" 2>/dev/null)
    CAT=$(echo "$CLASS_LINE" | python3 -c "import json,sys; print(json.load(sys.stdin)['category'])" 2>/dev/null)
    
    if [ -n "$IDX" ] && [ "$IDX" -ge 0 ] 2>/dev/null && [ "$IDX" -lt "$TOTAL" ]; then
      ORIG="${ITEMS[$IDX]}"
      echo "$ORIG" | CAT_ENV="$CAT" python3 -c "
import json, sys, os
item = json.load(sys.stdin)
item['category'] = os.environ['CAT_ENV']
print(json.dumps(item))
" 2>/dev/null
    fi
  done

  CLASSIFIED=$((CLASSIFIED + BATCH_COUNT))
  progress "$CLASSIFIED" "$TOTAL" "classifications"
done

progress_done
info "Classified ${CLASSIFIED} items"
