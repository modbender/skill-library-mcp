#!/usr/bin/env bash
set -euo pipefail

# Install target: an isolated OpenClaw agent workspace directory
# Recommended: /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent
WORKSPACE=""
TARGET_DIR_NAME=""
FORCE_RESET="false"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/install.sh --workspace <AGENT_WORKSPACE_DIR> [--target-name <subdir>] [--force-reset]

What it does:
  - First install: copies ./agent/* into <workspace>/ (or <workspace>/<target-name>/)
  - Subsequent runs: non-destructive by default (does NOT overwrite runtime source-of-truth)
  - Use --force-reset to backup+replace the runtime workspace from this package
  - Best-effort installs external skills listed in skills.lock.json (latest)

Safety:
  - Default is safe/non-destructive.
  - --force-reset will backup existing target with a timestamp, then replace it.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="$2"; shift 2;;
    --target-name)
      TARGET_DIR_NAME="$2"; shift 2;;
    --force-reset)
      FORCE_RESET="true"; shift 1;;
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

if [[ -z "${TARGET_DIR_NAME}" ]]; then
  DST_DIR="${WORKSPACE}"
else
  DST_DIR="${WORKSPACE}/${TARGET_DIR_NAME}"
fi

mkdir -p "${WORKSPACE}"

if [[ -e "${DST_DIR}" ]]; then
  if [[ "${FORCE_RESET}" == "true" ]]; then
    TS=$(date +"%Y%m%d-%H%M%S")
    BACKUP="${DST_DIR}.bak.${TS}"
    echo "--force-reset: backing up existing runtime to: ${BACKUP}"
    mv "${DST_DIR}" "${BACKUP}"
    mkdir -p "${DST_DIR}"
    echo "Installing (reset) jun-invest-option-master-agent into: ${DST_DIR}"
    rsync -a "${SRC_DIR}/" "${DST_DIR}/"
  else
    echo "Runtime workspace already exists at ${DST_DIR}; leaving it untouched (source-of-truth)."
  fi
else
  mkdir -p "${DST_DIR}"
  echo "First install: creating runtime workspace at ${DST_DIR}"
  rsync -a "${SRC_DIR}/" "${DST_DIR}/"
fi

# Best-effort: install skills (latest)
if command -v clawhub >/dev/null 2>&1 && command -v node >/dev/null 2>&1; then
  LOCK_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills.lock.json"
  SKILLS=$(node -e 'const fs=require("fs"); const j=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); console.log((j.skills||[]).map(s=>s.slug).filter(Boolean).join("\n"));' "${LOCK_FILE}" || true)
  if [[ -n "${SKILLS}" ]]; then
    echo "Installing external skills (latest):"
    echo "${SKILLS}" | while IFS= read -r slug; do
      [[ -z "${slug}" ]] && continue
      echo "- clawhub update ${slug} --force (latest, best-effort)"
      clawhub update "${slug}" --force >/dev/null 2>&1 || clawhub install "${slug}" || true
    done
  fi
else
  echo "clawhub/node not found; skipping external skill install. (OK)"
fi

echo "Done."
