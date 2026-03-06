#!/usr/bin/env bash
# clean_transcript.sh — Split transcript into chunks, clean each via opencode + MiniMax M2.5 (free)
# Chunks are processed IN PARALLEL
# Usage: clean_transcript.sh <input.txt> <output.txt> [chunk_lines] [concurrency]
set -euo pipefail

INPUT="$1"
OUTPUT="$2"
CHUNK_LINES="${3:-80}"
CONCURRENCY="${4:-0}"  # 0 = all chunks in parallel
MAX_RETRIES=3
RETRY_DELAY=3

OPENCODE="${OPENCODE_BIN:-$HOME/.opencode/bin/opencode}"
MODEL="${CLEAN_MODEL:-opencode/minimax-m2.5-free}"

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "[1/3] Splitting transcript into chunks of $CHUNK_LINES lines..."
split -l "$CHUNK_LINES" "$INPUT" "$TMPDIR/chunk_"

CHUNKS=("$TMPDIR"/chunk_*)
TOTAL=${#CHUNKS[@]}
echo "  → $TOTAL chunks to clean ($CONCURRENCY parallel)"

PROMPT='You are a Chinese ASR proofreader. Fix obvious speech recognition errors in the text below. Rules: 1) Fix clear homophones and garbled words 2) Add punctuation 3) Your output MUST be in Simplified Chinese (简体中文), regardless of the input language 4) If you are NOT confident about a correction (e.g. product names, brand names, technical terms, proper nouns), KEEP THE ORIGINAL text unchanged 5) Do NOT substitute one real term for another similar term 6) Output ONLY the corrected text, no explanations.'

# Write the cleaning function as a standalone script so xargs can call it
cat > "$TMPDIR/clean_one_chunk.sh" << 'CLEANEOF'
#!/usr/bin/env bash
set -euo pipefail
CHUNK="$1"
TMPDIR="$2"
OPENCODE="$3"
MODEL="$4"
PROMPT="$5"
MAX_RETRIES="$6"
RETRY_DELAY="$7"

BASENAME=$(basename "$CHUNK")
# Extract sequence number for ordered output
OUTFILE="$TMPDIR/clean_${BASENAME#chunk_}.txt"
JSONOUT="$TMPDIR/response_${BASENAME}.json"

CHUNK_TEXT=$(cat "$CHUNK")
SUCCESS=false

for attempt in $(seq 1 $MAX_RETRIES); do
  "$OPENCODE" run -m "$MODEL" --format json "${PROMPT}

${CHUNK_TEXT}" > "$JSONOUT" 2>/dev/null || true

  RESULT=$(python3 -c "
import json, sys
texts = []
for line in open('$JSONOUT'):
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        if obj.get('type') == 'text':
            texts.append(obj['part']['text'])
    except: pass
print('\n'.join(texts))
" 2>/dev/null) || true

  if [ -n "$RESULT" ]; then
    echo "$RESULT" > "$OUTFILE"
    SUCCESS=true
    break
  fi

  [ "$attempt" -lt "$MAX_RETRIES" ] && sleep "$RETRY_DELAY"
done

if [ "$SUCCESS" = false ]; then
  cp "$CHUNK" "$OUTFILE"
  echo "WARNING: Failed on $BASENAME" >&2
fi
CLEANEOF
chmod +x "$TMPDIR/clean_one_chunk.sh"

echo "[2/3] Cleaning $TOTAL chunks via $MODEL (all parallel)..."
if [ "$CONCURRENCY" -eq 0 ]; then
  CONCURRENCY=$TOTAL
fi
printf '%s\n' "${CHUNKS[@]}" | xargs -P "$CONCURRENCY" -I {} \
  "$TMPDIR/clean_one_chunk.sh" "{}" "$TMPDIR" "$OPENCODE" "$MODEL" "$PROMPT" "$MAX_RETRIES" "$RETRY_DELAY"

echo "[3/3] Merging cleaned chunks..."
# Sort to maintain order, then cat
ls "$TMPDIR"/clean_*.txt 2>/dev/null | sort | xargs cat > "$OUTPUT"

WORDCOUNT=$(wc -c < "$OUTPUT")
echo "Done: $OUTPUT ($WORDCOUNT bytes)"
