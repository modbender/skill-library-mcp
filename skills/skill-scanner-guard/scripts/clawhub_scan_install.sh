#!/usr/bin/env bash
set -euo pipefail

# Install a skill from ClawHub into a staging directory, scan it, and only then
# copy into OpenClaw's default user skill directory (~/.openclaw/skills).

usage() {
  cat <<'EOF'
Usage:
  clawhub_scan_install.sh <slug> [--version <version>] [--tag <tag>] [--force]

Notes:
  - Uses: npx clawhub install (downloads skill) + skill-scanner (security scan)
  - SAFE => installs to ~/.openclaw/skills/<slug>
  - Findings => blocks and prints a report path (unless --force)

Options:
  --version V   Install specific version (passed to clawhub)
  --tag TAG     (Currently unused for install; kept for future parity)
  --force       Install even if issues are found (NOT recommended)
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" || ${1:-} == "help" ]]; then
  usage
  exit 0
fi

SLUG=${1:-}
shift || true
if [[ -z "$SLUG" ]]; then
  echo "ERROR: slug required" >&2
  usage >&2
  exit 2
fi

# Sanitize SLUG: allow only alphanumeric, hyphen, underscore, forward slash
if [[ ! "$SLUG" =~ ^[a-zA-Z0-9_\/-]+$ ]]; then
  echo "ERROR: Invalid slug characters" >&2
  exit 2
fi

VERSION=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION=${2:-}
      if [[ -z "$VERSION" ]]; then
        echo "ERROR: --version requires a value" >&2
        exit 2
      fi
      shift 2
      ;;
    --tag)
      # clawhub install doesn't accept --tag, but we accept it to avoid footguns.
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    *)
      echo "ERROR: Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$STATE_DIR/workspace}"
STAGE_ROOT="$WORKSPACE_DIR/.skill_stage"
mkdir -p "$STAGE_ROOT"
STAGE_DIR="$(mktemp -d -p "$STAGE_ROOT" "clawhub-${SLUG}-XXXXXXXX")"

cleanup() {
  # Leave staging dir in place if debugging is needed.
  :
}
trap cleanup EXIT

# Install into staging
INSTALL_ARGS=(install "$SLUG")
if [[ -n "$VERSION" ]]; then
  INSTALL_ARGS+=(--version "$VERSION")
fi

# NOTE: --workdir controls where clawhub writes its metadata; --dir is where skills land.
# We keep everything inside the staging dir.
( cd "$STAGE_DIR" && npx -y clawhub --workdir "$STAGE_DIR" --dir skills "${INSTALL_ARGS[@]}" )

CANDIDATE="$STAGE_DIR/skills/$SLUG"
if [[ ! -d "$CANDIDATE" ]]; then
  echo "ERROR: clawhub install did not produce expected folder: $CANDIDATE" >&2
  exit 3
fi

ADD_SCRIPT="$STATE_DIR/skills/skill-scanner-guard/scripts/scan_and_add_skill.sh"
if [[ $FORCE -eq 1 ]]; then
  "$ADD_SCRIPT" "$CANDIDATE" --name "$SLUG" --force
else
  "$ADD_SCRIPT" "$CANDIDATE" --name "$SLUG"
fi

# If we got here, the add script already copied into ~/.openclaw/skills.
# (We intentionally keep the staging directory around in case you want to diff.)
echo "Staging directory preserved at: $STAGE_DIR"
