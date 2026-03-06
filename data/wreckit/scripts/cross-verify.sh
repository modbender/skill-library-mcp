#!/usr/bin/env bash
# wreckit — Cross-Verify scaffold (BUILD mode only)
# Sets up environment for AI-driven independent regeneration
# Usage: ./cross-verify.sh [project-path] [original-impl-path] [regenerated-impl-path]
# Without regenerated path: prints the AI prompt template to use for regeneration
# With regenerated path: diffs the two implementations structurally

set -euo pipefail
PROJECT="${1:-.}"
ORIGINAL="${2:-}"
REGENERATED="${3:-}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"

TEMP_DIR="$(mktemp -d "/tmp/wreckit-cross-verify.XXXXXX")"
mkdir -p "$TEMP_DIR"

if [ -d "tests" ]; then
  cp -R "tests" "$TEMP_DIR/"
fi
if [ -d "test" ]; then
  cp -R "test" "$TEMP_DIR/"
fi

PRD_CANDIDATE=""
for candidate in "PRD.md" "docs/PRD.md" "spec.md" "SPEC.md" "requirements.md" "docs/spec.md" "docs/requirements.md"; do
  if [ -f "$candidate" ]; then
    PRD_CANDIDATE="$candidate"
    break
  fi
done

if [ -n "$PRD_CANDIDATE" ]; then
  cp "$PRD_CANDIDATE" "$TEMP_DIR/"
fi

echo "Cross-verify workspace: $TEMP_DIR"

if [ -z "$REGENERATED" ]; then
  echo "=== Cross-Verify AI Prompt Template ==="
  cat <<PROMPT
You are an independent regenerator for a wreckit BUILD.

You have ONLY: the tests and PRD/spec in:
$TEMP_DIR

Instructions:
- Do NOT look at the original implementation.
- Regenerate the implementation from scratch.
- Match the external API expected by the tests.
- Return the regenerated implementation in a clean, minimal form.

Output:
- Provide the regenerated source code and any required project files.
PROMPT
  exit 0
fi

if [ -z "$ORIGINAL" ]; then
  echo "{\"status\":\"WARN\",\"symbol_match\":false,\"line_delta\":0,\"missing_in_regen\":[],\"extra_in_regen\":[],\"message\":\"Original implementation path required.\"}"
  exit 0
fi

if [ ! -f "$ORIGINAL" ] || [ ! -f "$REGENERATED" ]; then
  echo "{\"status\":\"WARN\",\"symbol_match\":false,\"line_delta\":0,\"missing_in_regen\":[],\"extra_in_regen\":[],\"message\":\"One or both implementation files not found.\"}"
  exit 0
fi

LINE_ORIG=$(wc -l < "$ORIGINAL" | tr -d ' ')
LINE_REGEN=$(wc -l < "$REGENERATED" | tr -d ' ')
if [ "$LINE_ORIG" -ge "$LINE_REGEN" ]; then
  LINE_DELTA=$((LINE_ORIG - LINE_REGEN))
else
  LINE_DELTA=$((LINE_REGEN - LINE_ORIG))
fi

SYMBOLS_JSON=$(python3 - "$ORIGINAL" "$REGENERATED" <<'PYEOF'
import json, re, sys

orig_path, regen_path = sys.argv[1:]

export_re = re.compile(r"^\\s*export\\s+(?:async\\s+)?(function|class|const|let)\\s+([A-Za-z_][A-Za-z0-9_]*)")
export_list_re = re.compile(r"^\\s*export\\s*\\{([^}]*)\\}")

def extract_symbols(path):
    symbols = set()
    try:
        with open(path, "r", errors="ignore") as f:
            for line in f:
                m = export_re.search(line)
                if m:
                    symbols.add(m.group(2))
                    continue
                m = export_list_re.search(line)
                if m:
                    parts = m.group(1).split(",")
                    for part in parts:
                        name = part.strip().split(" as ")[0].strip()
                        if name:
                            symbols.add(name)
    except FileNotFoundError:
        return set()
    return symbols

orig_symbols = extract_symbols(orig_path)
regen_symbols = extract_symbols(regen_path)

missing = sorted([s for s in orig_symbols if s not in regen_symbols])
extra = sorted([s for s in regen_symbols if s not in orig_symbols])

print(json.dumps({
    "orig": sorted(orig_symbols),
    "regen": sorted(regen_symbols),
    "missing": missing,
    "extra": extra,
}))
PYEOF
)

SYMBOL_MATCH=$(echo "$SYMBOLS_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print('true' if not d['missing'] else 'false')")
MISSING=$(echo "$SYMBOLS_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['missing']))")
EXTRA=$(echo "$SYMBOLS_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['extra']))")

STATUS="PASS"
if [ "$SYMBOL_MATCH" != "true" ]; then
  STATUS="FAIL"
elif [ "$EXTRA" != "[]" ]; then
  STATUS="WARN"
fi

python3 - "$STATUS" "$SYMBOL_MATCH" "$LINE_DELTA" "$MISSING" "$EXTRA" <<'PYEOF'
import json, sys
status = sys.argv[1]
symbol_match = True if sys.argv[2] == "true" else False
line_delta = int(sys.argv[3])
missing = json.loads(sys.argv[4])
extra = json.loads(sys.argv[5])

print(json.dumps({
  "status": status,
  "symbol_match": symbol_match,
  "line_delta": line_delta,
  "missing_in_regen": missing,
  "extra_in_regen": extra
}))
PYEOF
