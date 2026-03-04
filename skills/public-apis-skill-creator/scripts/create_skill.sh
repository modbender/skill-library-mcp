#!/usr/bin/env bash
# 根据选定 API 生成可直接使用的 skill 包骨架
# Usage:
#   create_skill.sh --skill-name weather-api --api-name "Open-Meteo" --api-url "https://..." --auth "No" [--desc "..."]

set -euo pipefail

SKILL_NAME=""
API_NAME=""
API_URL=""
AUTH="No"
DESC=""
OUT_DIR="/root/.openclaw/workspace/skills"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-name) SKILL_NAME="$2"; shift 2 ;;
    --api-name) API_NAME="$2"; shift 2 ;;
    --api-url) API_URL="$2"; shift 2 ;;
    --auth) AUTH="$2"; shift 2 ;;
    --desc) DESC="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

if [[ -z "$SKILL_NAME" || -z "$API_NAME" || -z "$API_URL" ]]; then
  echo "Usage: create_skill.sh --skill-name <name> --api-name <api> --api-url <url> [--auth No|apiKey|OAuth] [--desc text] [--out-dir dir]"
  exit 2
fi

# 规范化 skill 名称
SKILL_NAME=$(echo "$SKILL_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g; s/-\+/-/g; s/^-//; s/-$//')
TARGET="$OUT_DIR/$SKILL_NAME"
mkdir -p "$TARGET/scripts"

if [[ -z "$DESC" ]]; then
  DESC="Use ${API_NAME} API for data fetching and automation tasks."
fi

cat > "$TARGET/SKILL.md" <<EOF
---
name: $SKILL_NAME
description: $DESC
---

# $SKILL_NAME

## API
- Name: $API_NAME
- URL: $API_URL
- Auth: $AUTH

## Quick start

\
\
\

a) Curl:
\
\
\

bash {baseDir}/scripts/call.sh
\
\
\

b) Python example:
\
\
\

bash {baseDir}/scripts/python_example.sh
\
\
\

## Notes
- Replace auth token/key as needed.
- Update endpoint params for your task.
EOF

# call.sh
if [[ "$AUTH" == "No" ]]; then
  cat > "$TARGET/scripts/call.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
curl -s "$API_URL"
EOF

  cat > "$TARGET/scripts/python_example.sh" <<EOF
#!/usr/bin/env bash
python3 - <<'PY'
import requests
r = requests.get("$API_URL", timeout=20)
print(r.status_code)
print(r.text[:1000])
PY
EOF
else
  cat > "$TARGET/scripts/call.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
: "\\${API_TOKEN:?Please set API_TOKEN}"
curl -s "$API_URL" \\
  -H "Authorization: Bearer \\$API_TOKEN"
EOF

  cat > "$TARGET/scripts/python_example.sh" <<EOF
#!/usr/bin/env bash
python3 - <<'PY'
import os, requests
token = os.environ.get("API_TOKEN")
if not token:
    raise SystemExit("Please set API_TOKEN")
r = requests.get("$API_URL", headers={"Authorization": f"Bearer {token}"}, timeout=20)
print(r.status_code)
print(r.text[:1000])
PY
EOF
fi

chmod +x "$TARGET/scripts/call.sh" "$TARGET/scripts/python_example.sh"

echo "✅ Skill created: $TARGET"
echo "Next: customize SKILL.md description and publish if needed."
