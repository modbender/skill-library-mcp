#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CFG_EXAMPLE="${SKILL_DIR}/config.env.example"
CFG_REAL="${SKILL_DIR}/config.env"

say() { printf '%s\n' "$*"; }

have() { command -v "$1" >/dev/null 2>&1; }

fail() { echo "onedrive-integration onboarding: $*" >&2; exit 1; }

prereqs() {
  have python3 || fail "python3 not found"
}

discover_candidates() {
  # Print one candidate per line
  shopt -s nullglob
  local paths=(/mnt/c/Users/*/OneDrive*)
  for p in "${paths[@]}"; do
    [[ -d "$p" ]] && echo "$p"
  done
}

write_real_config() {
  local root="$1"
  local subdir="$2"
  [[ -f "$CFG_EXAMPLE" ]] || fail "missing example config: $CFG_EXAMPLE"

  cat > "$CFG_REAL" <<EOF
# onedrive-integration config (machine-specific)
# Example file: ${CFG_EXAMPLE}

ONEDRIVE_ROOT="${root}"
ONEDRIVE_SUBDIR="${subdir}"
EOF
  say "Wrote: $CFG_REAL"
}

main() {
  prereqs

  say "Using example config: $CFG_EXAMPLE"
  say "Writing real config:   $CFG_REAL"
  say

  say "Discovered OneDrive candidates:" 
  mapfile -t cands < <(discover_candidates)
  if [[ ${#cands[@]} -eq 0 ]]; then
    fail "no OneDrive folders found under /mnt/c/Users/*/OneDrive*"
  fi

  local i=1
  for c in "${cands[@]}"; do
    say "  [$i] $c"
    i=$((i+1))
  done

  say
  read -r -p "Select a number (or type an absolute path): " choice

  local root=""
  if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#cands[@]} )); then
    root="${cands[$((choice-1))]}"
  else
    root="$choice"
  fi

  [[ -d "$root" ]] || fail "not a directory: $root"

  read -r -p "Destination subdir within OneDrive [openclaw]: " subdir
  subdir="${subdir:-openclaw}"

  say
  say "About to set:" 
  say "  ONEDRIVE_ROOT=\"$root\""
  say "  ONEDRIVE_SUBDIR=\"$subdir\""
  read -r -p "Confirm? [y/N]: " ok
  if [[ ! "$ok" =~ ^[Yy]$ ]]; then
    fail "aborted"
  fi

  write_real_config "$root" "$subdir"

  # Smoke test
  local tmp
  tmp="$(mktemp)"
  echo "onedrive-integration smoke test" > "$tmp"
  say "Running smoke test copy..."
  python3 "${SKILL_DIR}/scripts/copy_to_onedrive.py" "$tmp" | head -n 1
  say "Done."
}

main "$@"
