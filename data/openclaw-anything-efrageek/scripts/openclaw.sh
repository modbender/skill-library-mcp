#!/bin/bash
# OpenClaw Unified Manager

set -euo pipefail

if ! command -v openclaw >/dev/null 2>&1; then
    echo "Error: 'openclaw' CLI not found in PATH." >&2
    echo "Install OpenClaw first and verify with: openclaw version" >&2
    echo "Docs: https://docs.openclaw.ai/install" >&2
    exit 127
fi

require_risky_opt_in() {
    if [[ "${OPENCLAW_WRAPPER_ALLOW_RISKY:-0}" != "1" ]]; then
        echo "Blocked: this action is marked high-risk by wrapper policy." >&2
        echo "Set OPENCLAW_WRAPPER_ALLOW_RISKY=1 for explicit, per-session opt-in." >&2
        exit 2
    fi
}

case ${1:-} in
    install|setup|doctor|status|reset|version|tui|dashboard)
        openclaw "$@"
        ;;
    service)
        shift
        openclaw gateway service "$@"
        ;;
    channel)
        shift
        command=${1:-}
        shift || true
        case "$command" in
            login) openclaw channels login --channel "$@" ;;
            list) openclaw channels list ;;
            logout) openclaw channels logout --channel "$@" ;;
            pairing)
                require_risky_opt_in
                openclaw pairing "$@"
                ;;
            *) openclaw channels "$command" "$@" ;;
        esac
        ;;
    model)
        shift
        command=${1:-}
        shift || true
        case "$command" in
            auth) openclaw models auth "$@" ;;
            alias) openclaw models aliases "$@" ;;
            scan) openclaw models scan ;;
            list) openclaw models list ;;
            set) openclaw models set "$@" ;;
            *) openclaw models "$command" "$@" ;;
        esac
        ;;
    cron)
        require_risky_opt_in
        shift
        openclaw cron "$@"
        ;;
    browser)
        require_risky_opt_in
        shift
        openclaw browser "$@"
        ;;
    plugin)
        require_risky_opt_in
        shift
        openclaw plugins "$@"
        ;;
    msg)
        shift
        openclaw message send "$@"
        ;;
    prose)
        require_risky_opt_in
        echo "Enabling open-prose plugin..."
        openclaw plugins enable open-prose
        ;;
    *)
        echo "OpenClaw Manager"
        echo "Usage: $0 {install|setup|doctor|status|service|channel|model|cron|browser|plugin|msg|dashboard}"
        echo "Note: high-risk actions require OPENCLAW_WRAPPER_ALLOW_RISKY=1"
        exit 1
        ;;
esac
