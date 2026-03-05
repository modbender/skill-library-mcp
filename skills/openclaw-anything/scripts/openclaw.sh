#!/bin/bash
# OpenClaw Unified Manager — v2.1 (optimized)
# Minimized case branches + hash-based risk check

set -euo pipefail

command -v openclaw >/dev/null 2>&1 || {
    echo "Error: 'openclaw' not in PATH. See: https://docs.openclaw.ai/install" >&2
    exit 127
}

# --- Risk gate ---
_risky() {
    [[ "${OPENCLAW_WRAPPER_ALLOW_RISKY:-0}" == "1" ]] && return 0
    echo "Blocked: high-risk. Set OPENCLAW_WRAPPER_ALLOW_RISKY=1" >&2; exit 2
}

# --- Risky command set (full-gate) ---
declare -A RISKY_FULL=([cron]=1 [browser]=1 [nodes]=1 [node]=1 [devices]=1 [pairing]=1 [webhooks]=1 [dns]=1)

# --- Main dispatch ---
cmd=${1:-help}
shift 2>/dev/null || true

case "$cmd" in
    # Pass-through (low-risk)
    install|setup|doctor|status|reset|version|tui|dashboard|update|uninstall|health|configure|completion|logs|config|docs|qr|system|sessions|directory|acp|approvals|security|memory|skills|agents|agent|message|msg)
        case "$cmd" in
            msg) openclaw message send "$@" ;;
            *)   openclaw "$cmd" "$@" ;;
        esac
        ;;

    # Gateway
    service) openclaw gateway service "$@" ;;
    gateway) openclaw gateway "$@" ;;

    # Channel routing
    channel)
        sub=${1:-}; shift 2>/dev/null || true
        case "$sub" in
            login)   openclaw channels login --channel "$@" ;;
            logout)  openclaw channels logout --channel "$@" ;;
            pairing) _risky; openclaw pairing "$@" ;;
            *)       openclaw channels "$sub" "$@" ;;
        esac
        ;;

    # Model routing
    model)
        sub=${1:-}; shift 2>/dev/null || true
        case "$sub" in
            auth)      openclaw models auth "$@" ;;
            alias)     openclaw models aliases "$@" ;;
            fallback)  openclaw models fallbacks "$@" ;;
            *)         openclaw models "$sub" "$@" ;;
        esac
        ;;

    # Granular-gated commands
    plugin)
        sub=${1:-}
        [[ "$sub" == "install" || "$sub" == "enable" ]] && _risky
        openclaw plugins "$@"
        ;;
    hooks)
        sub=${1:-}
        [[ "$sub" == "install" || "$sub" == "enable" ]] && _risky
        openclaw hooks "$@"
        ;;
    secrets)
        sub=${1:-}
        [[ "$sub" == "apply" ]] && _risky
        openclaw secrets "$@"
        ;;
    sandbox)
        sub=${1:-}
        [[ "$sub" == "recreate" ]] && _risky
        openclaw sandbox "$@"
        ;;

    # Prose special
    prose)
        _risky
        openclaw plugins enable open-prose
        ;;

    # Full-gated risky commands
    *)
        if [[ -n "${RISKY_FULL[$cmd]+x}" ]]; then
            _risky
            openclaw "$cmd" "$@"
        else
            cat <<'EOF'
OpenClaw Manager v2.1

Usage: openclaw.sh <command> [args]

Low-risk: install setup doctor status version health logs tui dashboard
          update uninstall reset configure completion config docs qr
          channel model agent agents message sessions memory skills
          security approvals system directory acp gateway service

High-risk (OPENCLAW_WRAPPER_ALLOW_RISKY=1):
  cron browser nodes node devices pairing webhooks dns prose
  plugin (install|enable)  hooks (install|enable)
  secrets (apply)          sandbox (recreate)
EOF
            exit 1
        fi
        ;;
esac
