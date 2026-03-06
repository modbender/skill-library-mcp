#!/usr/bin/env bash
set -euo pipefail

# Install companion CacheForge skills next to this primary skill.
# Expected layout after install:
#   <workspace>/skills/cacheforge
#   <workspace>/skills/cacheforge-setup
#   <workspace>/skills/cacheforge-ops
#   <workspace>/skills/cacheforge-stats

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$(dirname "$SELF_DIR")"
WORKDIR="$(dirname "$SKILLS_DIR")"
DIR_NAME="$(basename "$SKILLS_DIR")"

companions=(
  "cacheforge-setup"
  "cacheforge-ops"
  "cacheforge-stats"
)

missing=()
for skill in "${companions[@]}"; do
  if [[ ! -f "$SKILLS_DIR/$skill/SKILL.md" ]]; then
    missing+=("$skill")
  fi
done

if [[ ${#missing[@]} -eq 0 ]]; then
  echo "status=ok message='all companion skills already installed'"
  exit 0
fi

if ! command -v clawhub >/dev/null 2>&1; then
  echo "status=error message='clawhub not found; cannot auto-install companion skills'"
  echo "missing=${missing[*]}"
  exit 2
fi

install_one() {
  local slug="$1"
  clawhub --workdir "$WORKDIR" --dir "$DIR_NAME" install "$slug" >/dev/null 2>&1
}

installed=()
for skill in "${missing[@]}"; do
  if install_one "$skill"; then
    installed+=("$skill")
    continue
  fi
  # Fallback for namespaced slugs if your registry uses cacheforge/<skill>.
  if install_one "cacheforge/$skill"; then
    installed+=("cacheforge/$skill")
    continue
  fi
  echo "status=error message='failed to install companion skill' skill='$skill'"
  exit 3
done

echo "status=ok installed='${installed[*]}'"
