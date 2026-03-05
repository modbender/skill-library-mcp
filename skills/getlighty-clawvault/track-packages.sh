#!/usr/bin/env bash
# ClawVault — Package Tracker
# Scans system package managers and writes requirements.yaml
# Usage: track-packages.sh {scan|diff|install}

set -euo pipefail

VAULT_DIR="$HOME/.clawvault"
CONFIG="$VAULT_DIR/config.yaml"
REQ_FILE="$VAULT_DIR/requirements.yaml"
VAULT_REQ="$VAULT_DIR/.vault-requirements.yaml"

timestamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[clawvault:packages $(timestamp)] $*"; }

detect_os() {
  case "$(uname -s)" in
    Darwin) echo "macos" ;;
    Linux)  echo "linux" ;;
    *)      echo "unknown" ;;
  esac
}

should_track() {
  local manager="$1"
  # Check config for whether this manager is enabled
  if [[ -f "$CONFIG" ]]; then
    local key
    case "$manager" in
      brew)    key="brew" ;;
      apt)     key="apt" ;;
      snap)    key="snap" ;;
      flatpak) key="flatpak" ;;
      npm)     key="npm_global" ;;
      pip)     key="pip_global" ;;
      *)       return 0 ;;
    esac
    local val
    val=$(grep "${key}:" "$CONFIG" 2>/dev/null | tail -1 | awk '{print $2}')
    [[ "$val" == "false" ]] && return 1
  fi
  return 0
}

# ─── Scanners ────────────────────────────────────────────────

scan_brew() {
  if ! command -v brew &>/dev/null; then return; fi
  if ! should_track brew; then return; fi

  echo "brew:"

  # Formulae — single brew call to get all names+versions
  local formulae_versions
  formulae_versions=$(brew list --formula --versions 2>/dev/null | sort)
  if [[ -n "$formulae_versions" ]]; then
    echo "  formulae:"
    while IFS= read -r line; do
      local pkg ver
      pkg=$(echo "$line" | awk '{print $1}')
      ver=$(echo "$line" | awk '{print $2}')
      echo "    - name: \"$pkg\""
      [[ -n "$ver" ]] && echo "      version: \"$ver\""
    done <<< "$formulae_versions"
  fi

  # Casks — single brew call
  local cask_versions
  cask_versions=$(brew list --cask --versions 2>/dev/null | sort)
  if [[ -n "$cask_versions" ]]; then
    echo "  casks:"
    while IFS= read -r line; do
      local pkg ver
      pkg=$(echo "$line" | awk '{print $1}')
      ver=$(echo "$line" | awk '{print $2}')
      echo "    - name: \"$pkg\""
      [[ -n "$ver" ]] && echo "      version: \"$ver\""
    done <<< "$cask_versions"
  fi
}

scan_apt() {
  if ! command -v apt &>/dev/null; then return; fi
  if ! should_track apt; then return; fi

  echo "apt:"
  echo "  packages:"
  dpkg-query -W -f='    - name: "${Package}"\n      version: "${Version}"\n' 2>/dev/null | head -500
}

scan_snap() {
  if ! command -v snap &>/dev/null; then return; fi
  if ! should_track snap; then return; fi

  echo "snap:"
  echo "  packages:"
  (snap list 2>/dev/null || true) | tail -n +2 | awk '{print "    - name: \""$1"\"\n      version: \""$2"\""}' | head -200
}

scan_flatpak() {
  if ! command -v flatpak &>/dev/null; then return; fi
  if ! should_track flatpak; then return; fi

  echo "flatpak:"
  echo "  packages:"
  (flatpak list --app --columns=application,version 2>/dev/null || true) | tail -n +1 | awk -F'\t' '{print "    - name: \""$1"\"\n      version: \""$2"\""}' | head -200
}

scan_npm() {
  if ! command -v npm &>/dev/null; then return; fi
  if ! should_track npm; then return; fi

  echo "npm_global:"
  echo "  packages:"
  # npm list often returns non-zero (peer dep warnings), so capture output separately
  local npm_json
  npm_json=$(npm list -g --depth=0 --json 2>/dev/null || true)
  if [[ -n "$npm_json" ]]; then
    echo "$npm_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    deps = data.get('dependencies', {})
    for name, info in sorted(deps.items()):
        ver = info.get('version', 'unknown')
        print(f'    - name: \"{name}\"')
        print(f'      version: \"{ver}\"')
except:
    pass
" 2>/dev/null || true
  fi
}

scan_pip() {
  if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then return; fi
  if ! should_track pip; then return; fi

  local pip_cmd="pip3"
  command -v pip3 &>/dev/null || pip_cmd="pip"

  echo "pip_global:"
  echo "  packages:"
  local pip_json
  pip_json=$($pip_cmd list --format=json 2>/dev/null || true)
  if [[ -n "$pip_json" ]]; then
    echo "$pip_json" | python3 -c "
import sys, json
try:
    pkgs = json.load(sys.stdin)
    for p in sorted(pkgs, key=lambda x: x['name']):
        print(f'    - name: \"{p[\"name\"]}\"')
        print(f'      version: \"{p[\"version\"]}\"')
except:
    pass
" 2>/dev/null || true
  fi
}

# ─── Commands ────────────────────────────────────────────────

cmd_scan() {
  local os
  os=$(detect_os)

  log "Scanning packages ($os)..."

  {
    echo "# ClawVault Package Requirements"
    echo "# Generated: $(timestamp)"
    echo "# OS: $os"
    echo "# Hostname: $(hostname -s 2>/dev/null || echo unknown)"
    echo ""

    scan_brew
    scan_apt
    scan_snap
    scan_flatpak
    scan_npm
    scan_pip
  } > "$REQ_FILE"

  # Count packages
  local count
  count=$(grep -c '^\s*- name:' "$REQ_FILE" 2>/dev/null || echo "0")

  log "Scanned $count packages → $REQ_FILE"

  # Summary
  echo ""
  echo "Package Summary"
  echo "==============="
  for mgr in brew apt snap flatpak npm_global pip_global; do
    local n
    n=$(awk -v sect="^${mgr}:" '$0 ~ sect {f=1; next} f && /^[a-z]/ {exit} f' "$REQ_FILE" 2>/dev/null | grep -c '^\s*- name:') || n=0
    [[ "$n" -gt 0 ]] && echo "  $mgr: $n packages"
  done
  echo "  Total: $count packages"
  echo ""
}

cmd_diff() {
  if [[ ! -f "$VAULT_REQ" ]]; then
    log "No vault requirements found. Push/pull first to get the baseline."
    return 0
  fi

  if [[ ! -f "$REQ_FILE" ]]; then
    log "No local scan. Run 'track-packages.sh scan' first."
    return 1
  fi

  echo ""
  echo "Package Differences (local vs vault)"
  echo "====================================="

  # Extract package names from each file
  local local_pkgs vault_pkgs
  local_pkgs=$(grep '^\s*- name:' "$REQ_FILE" 2>/dev/null | awk -F'"' '{print $2}' | sort)
  vault_pkgs=$(grep '^\s*- name:' "$VAULT_REQ" 2>/dev/null | awk -F'"' '{print $2}' | sort)

  local missing_local missing_vault
  missing_local=$(comm -23 <(echo "$vault_pkgs") <(echo "$local_pkgs"))
  missing_vault=$(comm -13 <(echo "$vault_pkgs") <(echo "$local_pkgs"))

  if [[ -n "$missing_local" ]]; then
    echo ""
    echo "Missing locally (in vault but not here):"
    echo "$missing_local" | while read -r pkg; do
      echo "  - $pkg"
    done
  fi

  if [[ -n "$missing_vault" ]]; then
    echo ""
    echo "Only local (here but not in vault):"
    echo "$missing_vault" | while read -r pkg; do
      echo "  + $pkg"
    done
  fi

  if [[ -z "$missing_local" && -z "$missing_vault" ]]; then
    echo "  No differences found."
  fi
  echo ""
}

cmd_install() {
  if [[ ! -f "$VAULT_REQ" ]]; then
    log "No vault requirements. Pull from vault first."
    return 1
  fi

  local os
  os=$(detect_os)

  # Find packages in vault but not installed locally
  cmd_scan >/dev/null 2>&1 || true

  local vault_pkgs local_pkgs
  vault_pkgs=$(grep '^\s*- name:' "$VAULT_REQ" 2>/dev/null | awk -F'"' '{print $2}' | sort)
  local_pkgs=$(grep '^\s*- name:' "$REQ_FILE" 2>/dev/null | awk -F'"' '{print $2}' | sort)
  local missing
  missing=$(comm -23 <(echo "$vault_pkgs") <(echo "$local_pkgs"))

  if [[ -z "$missing" ]]; then
    log "All vault packages are already installed."
    return 0
  fi

  echo ""
  echo "Missing Packages"
  echo "================"
  echo "$missing" | while read -r pkg; do
    echo "  - $pkg"
  done
  echo ""

  # Generate install commands per manager
  for mgr in brew apt npm_global pip_global snap flatpak; do
    local mgr_missing=""
    # Get packages from this manager in vault
    local mgr_pkgs
    mgr_pkgs=$(awk "/^${mgr}:/,/^[a-z]/" "$VAULT_REQ" 2>/dev/null | grep '^\s*- name:' | awk -F'"' '{print $2}')
    for pkg in $mgr_pkgs; do
      if echo "$missing" | grep -qx "$pkg"; then
        mgr_missing="$mgr_missing $pkg"
      fi
    done

    if [[ -n "$mgr_missing" ]]; then
      local cmd=""
      case "$mgr" in
        brew)       cmd="brew install$mgr_missing" ;;
        apt)        cmd="sudo apt install -y$mgr_missing" ;;
        npm_global) cmd="npm install -g$mgr_missing" ;;
        pip_global) cmd="pip3 install$mgr_missing" ;;
        snap)       cmd="sudo snap install$mgr_missing" ;;
        flatpak)    cmd="flatpak install$mgr_missing" ;;
      esac

      if [[ -n "$cmd" ]]; then
        echo "Install command ($mgr):"
        echo "  $cmd"
        echo ""
        read -rp "Run this command? [y/N]: " yn
        if [[ "$yn" =~ ^[Yy] ]]; then
          eval "$cmd" || log "Some packages failed to install"
        fi
      fi
    fi
  done
}

# ─── Main ────────────────────────────────────────────────────

case "${1:-scan}" in
  scan)    cmd_scan ;;
  diff)    cmd_diff ;;
  install) cmd_install ;;
  *)       echo "Usage: track-packages.sh {scan|diff|install}"; exit 1 ;;
esac
