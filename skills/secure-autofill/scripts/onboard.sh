#!/usr/bin/env bash
set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CFG_EXAMPLE="${SKILL_DIR}/config.env.example"
CFG_REAL="${SKILL_DIR}/config.env"
GATEWAY_ENV="${HOME}/.config/openclaw/env"

fail() { echo "secure-autofill onboarding: $*" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

has_systemd_gateway() {
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl --user status openclaw-gateway --no-pager >/dev/null 2>&1
}

get_kv() {
  # get_kv <file> <KEY>
  local file="$1" key="$2"
  [[ -f "$file" ]] || return 1
  # Support: KEY=value or KEY="value"; first match wins
  local line
  line="$(grep -E "^${key}=" "$file" | head -n 1 || true)"
  [[ -n "$line" ]] || return 1
  echo "${line#*=}" | sed -E 's/^"(.*)"$/\1/; s/^\x27(.*)\x27$/\1/'
}

set_kv() {
  # set_kv <file> <KEY> <VALUE>
  local file="$1" key="$2" val="$3"
  mkdir -p "$(dirname "$file")"
  touch "$file"

  if grep -qE "^${key}=" "$file"; then
    # replace first occurrence
    # shellcheck disable=SC2016
    sed -i -E "0,/^${key}=.*/s//${key}=\"${val//\"/\\\"}\"/" "$file"
  else
    printf '%s="%s"\n' "$key" "$val" >> "$file"
  fi
}

prompt_apply_key() {
  # prompt_apply_key <KEY> <NEWVAL> <MASK>
  local key="$1" newval="$2" mask="$3"
  local cur=""

  if [[ -f "$GATEWAY_ENV" ]]; then
    cur="$(get_kv "$GATEWAY_ENV" "$key" || true)"
  fi

  if [[ -n "$cur" ]]; then
    echo
    if [[ "$mask" == "1" ]]; then
      echo "$key already exists in $GATEWAY_ENV"
      echo "  current: <set>"
      echo "  new:     <set>"
    else
      echo "$key already exists in $GATEWAY_ENV"
      echo "  current: $cur"
      echo "  new:     $newval"
    fi
    read -r -p "Override? [y/N]: " ok
    [[ "$ok" =~ ^[Yy]$ ]] || return 0
  else
    echo
    if [[ "$mask" == "1" ]]; then
      echo "$key is not set in $GATEWAY_ENV; add it? (value: <set>)"
    else
      echo "$key is not set in $GATEWAY_ENV; add it? (value: $newval)"
    fi
    read -r -p "Add? [y/N]: " ok
    [[ "$ok" =~ ^[Yy]$ ]] || return 0
  fi

  set_kv "$GATEWAY_ENV" "$key" "$newval"
}

write_skill_local_env() {
  local disp="$1" wdisp="$2" token="$3"

  {
    echo "# secure-autofill env (machine-specific)"
    echo "# Example file: ${CFG_EXAMPLE}"
    echo ""
    echo "DISPLAY=\"${disp}\""
    echo "WAYLAND_DISPLAY=\"${wdisp}\""
    if [[ -n "$token" ]]; then
      echo "OP_SERVICE_ACCOUNT_TOKEN=\"${token}\""
    fi
  } > "$CFG_REAL"
}

main() {
  [[ -f "$CFG_EXAMPLE" ]] || fail "missing example: $CFG_EXAMPLE"

  echo "This will:"
  echo "  1) Write skill-local env values to: $CFG_REAL"
  echo "  2) Optionally update gateway env file: $GATEWAY_ENV"
  echo "Example (untouched): $CFG_EXAMPLE"
  echo

  read -r -p "DISPLAY [:0]: " disp
  disp="${disp:-:0}"
  read -r -p "WAYLAND_DISPLAY [wayland-0]: " wdisp
  wdisp="${wdisp:-wayland-0}"

  echo
  echo "OP_SERVICE_ACCOUNT_TOKEN is optional if you use 1Password desktop integration."
  read -r -p "OP_SERVICE_ACCOUNT_TOKEN (leave blank to skip): " token

  echo
  echo "About to write skill-local env:" 
  echo "  DISPLAY=\"$disp\""
  echo "  WAYLAND_DISPLAY=\"$wdisp\""
  if [[ -n "$token" ]]; then
    echo "  OP_SERVICE_ACCOUNT_TOKEN=<set>"
  else
    echo "  OP_SERVICE_ACCOUNT_TOKEN=<empty>"
  fi
  read -r -p "Confirm? [y/N]: " ok
  [[ "$ok" =~ ^[Yy]$ ]] || fail "aborted"

  write_skill_local_env "$disp" "$wdisp" "$token"
  echo "Wrote: $CFG_REAL"

  echo
  read -r -p "Update gateway env file ($GATEWAY_ENV)? [y/N]: " doenv
  if [[ "$doenv" =~ ^[Yy]$ ]]; then
    echo "Ensuring: $GATEWAY_ENV"
    mkdir -p "$(dirname "$GATEWAY_ENV")"
    touch "$GATEWAY_ENV"

    prompt_apply_key "DISPLAY" "$disp" 0
    prompt_apply_key "WAYLAND_DISPLAY" "$wdisp" 0
    if [[ -n "$token" ]]; then
      prompt_apply_key "OP_SERVICE_ACCOUNT_TOKEN" "$token" 1
    fi

    echo
    echo "Updated: $GATEWAY_ENV"
  else
    echo "Skipped gateway env update."
  fi

  echo
  if has_systemd_gateway; then
    read -r -p "Restart openclaw-gateway now (systemd --user)? [y/N]: " r
    if [[ "$r" =~ ^[Yy]$ ]]; then
      systemctl --user restart openclaw-gateway
      echo "Restarted openclaw-gateway."
    else
      echo "Skipped restart."
    fi
  else
    echo "systemd user service openclaw-gateway not detected."
    echo "If needed, restart the gateway using whatever method you use on this machine."
  fi
}

main "$@"
