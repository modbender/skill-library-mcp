#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  publish_skill.sh --path <skill_dir> [options]

Options:
  --path <dir>           Skill directory path (required)
  --slug <slug>          Skill slug (default: infer)
  --name <name>          Display name (default: infer)
  --version <semver>     Version (default: infer)
  --changelog <text>     Changelog text
  --tags <tags>          Comma-separated tags (default: latest)
  --registry <url>       Registry URL override
  --env-file <file>      Env file path (default: $HOME/.openclaw/.env)
  --allow-cjk            Allow CJK text in skill files (default: blocked)
  --skip-preflight       Skip content and secret checks
  --dry-run              Print command without publishing
  -h, --help             Show help
EOF
}

json_get() {
  local file="$1"
  local field="$2"
  python3 - "$file" "$field" <<'PY'
import json
import sys

path = sys.argv[1]
field = sys.argv[2]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cur = data
    for part in field.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            cur = None
            break
    if isinstance(cur, (str, int, float)):
        print(cur)
except Exception:
    pass
PY
}

load_token_from_env_file() {
  local env_file="$1"
  if [[ ! -f "$env_file" ]]; then
    return 1
  fi
  local value
  value="$(sed -n 's/^CLAWHUB_TOKEN=//p' "$env_file" | sed -n '1p')"
  value="${value%\"}"
  value="${value#\"}"
  value="${value%\'}"
  value="${value#\'}"
  if [[ -n "$value" ]]; then
    export CLAWHUB_TOKEN="$value"
    return 0
  fi
  return 1
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: missing command '$cmd'" >&2
    exit 1
  fi
}

validate_slug() {
  local slug="$1"
  if [[ ! "$slug" =~ ^[a-z0-9][a-z0-9-]{1,63}$ ]]; then
    echo "Error: invalid slug '$slug'. Use lowercase letters, digits, and hyphens only." >&2
    exit 1
  fi
}

validate_semver() {
  local version="$1"
  if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then
    echo "Error: invalid version '$version'. Expected semver like 1.2.3" >&2
    exit 1
  fi
}

ensure_authenticated() {
  if clawhub whoami >/dev/null 2>&1; then
    echo "Using existing ClawHub login session."
    return 0
  fi

  if [[ -z "${CLAWHUB_TOKEN:-}" ]]; then
    load_token_from_env_file "$ENV_FILE" || {
      echo "Error: CLAWHUB_TOKEN not found in env or $ENV_FILE" >&2
      exit 1
    }
  fi

  echo "Logging into ClawHub with token (hidden)..."
  clawhub login --token "$CLAWHUB_TOKEN" --no-browser >/dev/null
  clawhub whoami >/dev/null
}

run_preflight_checks() {
  local skill_path="$1"
  local allow_cjk="$2"

  python3 - "$skill_path" "$allow_cjk" <<'PY'
import os
import re
import sys

root = os.path.abspath(sys.argv[1])
allow_cjk = (sys.argv[2].lower() == "true")

skip_dirs = {".git", "node_modules", ".cursor"}
forced_block_files = {".env", ".env.local", ".env.production", ".env.development"}

secret_patterns = [
    re.compile(r"CLAWHUB_TOKEN\s*=\s*['\"]?clh_[A-Za-z0-9_-]{12,}", re.IGNORECASE),
    re.compile(r"HF_TOKEN\s*=\s*['\"]?hf_[A-Za-z0-9]{16,}", re.IGNORECASE),
    re.compile(r"(GEMINI_API_KEY|VECTOR_ENGINE_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*=\s*['\"]?[A-Za-z0-9._-]{20,}", re.IGNORECASE),
    re.compile(r"\bclh_[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bhf_[A-Za-z0-9]{16,}\b"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

cjk_pattern = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

def is_likely_text(path):
    text_ext = {
        ".md", ".txt", ".json", ".yaml", ".yml", ".sh", ".js", ".ts", ".mjs", ".cjs",
        ".py", ".toml", ".ini", ".cfg", ".conf", ".xml", ".html", ".css", ".csv"
    }
    _, ext = os.path.splitext(path.lower())
    return ext in text_ext or os.path.basename(path) in {"SKILL.md", "skill.md", "package.json", "_meta.json"}

violations = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in skip_dirs]
    for filename in filenames:
        rel = os.path.relpath(os.path.join(dirpath, filename), root)
        base = os.path.basename(rel)
        if base in forced_block_files:
            violations.append(f"blocked file included: {rel}")
            continue

        full = os.path.join(root, rel)
        if not is_likely_text(full):
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        for pat in secret_patterns:
            if pat.search(content):
                violations.append(f"potential secret pattern in: {rel}")
                break

        if not allow_cjk and cjk_pattern.search(content):
            violations.append(f"CJK text detected in: {rel}")

if violations:
    print("Preflight failed:")
    for item in violations[:20]:
        print(f"- {item}")
    if len(violations) > 20:
        print(f"- ... and {len(violations)-20} more")
    sys.exit(2)

print("Preflight checks passed.")
PY
}

SKILL_PATH=""
SLUG=""
NAME=""
VERSION=""
CHANGELOG=""
TAGS="latest"
REGISTRY=""
ENV_FILE="${HOME}/.openclaw/.env"
ALLOW_CJK="false"
SKIP_PREFLIGHT="false"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      SKILL_PATH="${2:-}"; shift 2 ;;
    --slug)
      SLUG="${2:-}"; shift 2 ;;
    --name)
      NAME="${2:-}"; shift 2 ;;
    --version)
      VERSION="${2:-}"; shift 2 ;;
    --changelog)
      CHANGELOG="${2:-}"; shift 2 ;;
    --tags)
      TAGS="${2:-}"; shift 2 ;;
    --registry)
      REGISTRY="${2:-}"; shift 2 ;;
    --env-file)
      ENV_FILE="${2:-}"; shift 2 ;;
    --allow-cjk)
      ALLOW_CJK="true"; shift ;;
    --skip-preflight)
      SKIP_PREFLIGHT="true"; shift ;;
    --dry-run)
      DRY_RUN="true"; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Error: unknown option '$1'" >&2
      usage
      exit 1 ;;
  esac
done

if [[ -z "$SKILL_PATH" ]]; then
  echo "Error: --path is required" >&2
  usage
  exit 1
fi

require_cmd clawhub
require_cmd python3

if [[ ! -d "$SKILL_PATH" ]]; then
  echo "Error: skill path not found: $SKILL_PATH" >&2
  exit 1
fi

if [[ ! -f "$SKILL_PATH/SKILL.md" && ! -f "$SKILL_PATH/skill.md" ]]; then
  echo "Error: $SKILL_PATH does not contain SKILL.md or skill.md" >&2
  exit 1
fi

if [[ -n "$REGISTRY" ]]; then
  export CLAWHUB_REGISTRY="$REGISTRY"
fi

if [[ -z "$SLUG" ]]; then
  SLUG="$(basename "$SKILL_PATH")"
fi

if [[ -z "$VERSION" && -f "$SKILL_PATH/package.json" ]]; then
  VERSION="$(json_get "$SKILL_PATH/package.json" "version")"
fi
if [[ -z "$VERSION" && -f "$SKILL_PATH/_meta.json" ]]; then
  VERSION="$(json_get "$SKILL_PATH/_meta.json" "latest.version")"
fi

if [[ -z "$NAME" && -f "$SKILL_PATH/_meta.json" ]]; then
  NAME="$(json_get "$SKILL_PATH/_meta.json" "displayName")"
fi
if [[ -z "$NAME" ]]; then
  NAME="$SLUG"
fi

if [[ -z "$VERSION" ]]; then
  echo "Error: --version is required when version cannot be inferred" >&2
  exit 1
fi

validate_slug "$SLUG"
validate_semver "$VERSION"

if [[ "$SKIP_PREFLIGHT" != "true" ]]; then
  run_preflight_checks "$SKILL_PATH" "$ALLOW_CJK"
fi

ensure_authenticated

cmd=(clawhub publish "$SKILL_PATH" --slug "$SLUG" --name "$NAME" --version "$VERSION" --tags "$TAGS")
if [[ -n "$CHANGELOG" ]]; then
  cmd+=(--changelog "$CHANGELOG")
fi

if [[ "$DRY_RUN" == "true" ]]; then
  printf '[dry-run] '
  printf '%q ' "${cmd[@]}"
  printf '\n'
  exit 0
fi

"${cmd[@]}"
echo "Publish finished: ${SLUG}@${VERSION}"
