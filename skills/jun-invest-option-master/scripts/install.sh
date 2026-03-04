#!/usr/bin/env bash
set -euo pipefail

# Install target: an isolated OpenClaw agent workspace directory
# Recommended: /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master
WORKSPACE=""

# Back-compat: if you prefer installing under a parent workspace folder, you can
# pass --target-name. If omitted, we install directly into --workspace.
TARGET_DIR_NAME=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install.sh --workspace <AGENT_WORKSPACE_DIR> [--target-name <subdir>]

What it does:
  - If --target-name is omitted: copies ./agent/* directly into <workspace>/
  - If --target-name is set: copies ./agent/* into <workspace>/<target-name>/
  - Best-effort installs external skills listed in skills.lock.json (latest)

Safety:
  - If target exists, it will be backed up with a timestamp.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="$2"; shift 2;;
    --target-name)
      TARGET_DIR_NAME="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 1;;
  esac
done

if [[ -z "${WORKSPACE}" ]]; then
  echo "Missing --workspace" >&2
  usage
  exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/agent"

# If target-name is empty, install directly into WORKSPACE.
if [[ -z "${TARGET_DIR_NAME}" ]]; then
  DST_DIR="${WORKSPACE}"
else
  DST_DIR="${WORKSPACE}/${TARGET_DIR_NAME}"
fi

# Create workspace dir if needed (agent workspaces are standalone directories).
mkdir -p "${WORKSPACE}"

if [[ -e "${DST_DIR}" ]]; then
  TS=$(date +"%Y%m%d-%H%M%S")
  BACKUP="${DST_DIR}.bak.${TS}"
  echo "Target exists; backing up to: ${BACKUP}"
  mv "${DST_DIR}" "${BACKUP}"
fi

mkdir -p "${DST_DIR}"

echo "Installing jun-invest-option-master into: ${DST_DIR}"
rsync -a "${SRC_DIR}/" "${DST_DIR}/"

# Best-effort: install skills (latest)
if command -v clawhub >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
  LOCK_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills.lock.json"
  SKILLS=$(node -e 'const fs=require("fs"); const j=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log((j.skills||[]).map(s=>s.slug).filter(Boolean).join("\n"));' "${LOCK_FILE}" || true)
  if [[ -n "${SKILLS}" ]]; then
    echo "Installing external skills (latest):"
    echo "${SKILLS}" | while IFS= read -r slug; do
      [[ -z "${slug}" ]] && continue
      echo "- clawhub install ${slug} (best-effort)"
      clawhub install "${slug}" || true
    done
  fi
else
  echo "clawhub/node not found; skipping external skill install. (OK)"
fi

echo "Done."
