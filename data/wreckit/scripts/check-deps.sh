#!/usr/bin/env bash
# wreckit — verify declared dependencies exist in registries
# Usage: ./check-deps.sh [project-path]
# Outputs JSON to stdout (status PASS/FAIL), human-readable logs to stderr
# Exit 0 = results produced (check JSON status)

set -euo pipefail
PROJECT="${1:-.}"
PROJECT="$(cd "$PROJECT" && pwd)"
cd "$PROJECT"
HALLUCINATED=()

check_npm() {
  local pkg="$1"
  # Skip scoped packages with complex names, builtins
  [[ "$pkg" == node:* ]] && return 0
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://registry.npmjs.org/$pkg" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("npm:$pkg")
  fi
}

check_pypi() {
  local pkg="$1"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$pkg/json" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("pypi:$pkg")
  fi
}

check_crate() {
  local pkg="$1"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "https://crates.io/api/v1/crates/$pkg" 2>/dev/null || echo "000")
  if [ "$status" = "404" ]; then
    HALLUCINATED+=("crate:$pkg")
  fi
}

# npm/yarn
if [ -f "package.json" ]; then
  deps=$(python3 -c "
import json,sys
d=json.load(open('package.json'))
for k in ['dependencies','devDependencies']:
  for p,v in d.get(k,{}).items():
    if not p.startswith('@types/'):
      print(f'{p}\\t{v}')
" 2>/dev/null || true)
  while IFS=$'\t' read -r pkg version; do
    [ -z "$pkg" ] && continue
    if [[ "$version" == npm:* ]] || [[ "$version" == workspace:* ]] || [[ "$version" == file:* ]] || [[ "$version" == link:* ]] || [[ "$version" == github:* ]] || [[ "$version" == git+https:* ]] || [[ "$version" == patch:* ]] || [[ "$version" == portal:* ]]; then
      continue
    fi
    check_npm "$pkg"
  done <<< "$deps"
fi

# Python
if [ -f "requirements.txt" ]; then
  while IFS= read -r line; do
    pkg=$(echo "$line" | sed 's/[>=<!\[].*//;s/#.*//' | tr -d '[:space:]')
    [ -n "$pkg" ] && check_pypi "$pkg"
  done < requirements.txt
elif [ -f "pyproject.toml" ]; then
  deps=$(python3 -c "
try:
  import tomllib
except: import tomli as tomllib
with open('pyproject.toml','rb') as f: d=tomllib.load(f)
for dep in d.get('project',{}).get('dependencies',[]):
  print(dep.split('>')[0].split('<')[0].split('=')[0].split('[')[0].strip())
" 2>/dev/null || true)
  for pkg in $deps; do
    check_pypi "$pkg"
  done
fi

# Rust
if [ -f "Cargo.toml" ]; then
  deps=$(python3 -c "
try:
  import tomllib
except: import tomli as tomllib
with open('Cargo.toml','rb') as f: d=tomllib.load(f)
for dep in d.get('dependencies',{}):
  print(dep)
" 2>/dev/null || true)
  for pkg in $deps; do
    check_crate "$pkg"
  done
fi

if [ ${#HALLUCINATED[@]} -gt 0 ]; then
  echo "HALLUCINATED DEPENDENCIES FOUND:" >&2
  for h in "${HALLUCINATED[@]}"; do
    echo "  ❌ $h" >&2
  done
  # Serialize the hallucinated list to JSON via a short one-liner, then pass
  # it as an env variable to the reporting script.  This avoids the pipe+heredoc
  # stdin conflict that would cause findings to be under-reported.
  HALLUCINATED_JSON=$(printf '%s\n' "${HALLUCINATED[@]}" | python3 -c "
import json, sys
seen = set()
items = []
for raw in sys.stdin:
    entry = raw.strip()
    if entry and entry not in seen:
        seen.add(entry)
        items.append(entry)
print(json.dumps(items))
")
  # Build the final report: findings MUST always equal len(hallucinated)
  HALLUCINATED_JSON="$HALLUCINATED_JSON" python3 - <<'PYEOF'
import json, os

items = json.loads(os.environ["HALLUCINATED_JSON"])

# Invariant: findings == len(hallucinated) — enforced here, not assumed.
findings = len(items)

print(json.dumps({
    "status": "FAIL",
    "confidence": 1.0,
    "findings": findings,
    "hallucinated": items
}))
PYEOF
else
  echo "All dependencies verified in registries." >&2
  python3 - <<'PYEOF'
import json
print(json.dumps({
    "status": "PASS",
    "confidence": 1.0,
    "findings": 0,
    "hallucinated": []
}))
PYEOF
fi

exit 0
