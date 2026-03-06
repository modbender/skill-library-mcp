#!/usr/bin/env bash
# pull-sdk-ref.sh — Pull reference docs from wayfinder-paths-sdk skill files.
#
# Usage:
#   ./pull-sdk-ref.sh <topic>          Show docs for a specific topic
#   ./pull-sdk-ref.sh --list           List available topics
#   ./pull-sdk-ref.sh --all            Show all reference docs
#   ./pull-sdk-ref.sh --commit <hash>  Checkout a specific SDK commit before reading
#   ./pull-sdk-ref.sh --version        Show the pinned SDK version from sdk-version.md
#
# Topics:
#   strategies   Developing Wayfinder strategies (workflow, manifests, safety, data sources)
#   setup        First-time SDK setup
#   boros        Boros adapter (fixed-rate markets, rate locking, funding swaps)
#   brap         BRAP adapter (cross-chain swaps and bridges)
#   hyperlend    HyperLend adapter (HyperEVM lending)
#   hyperliquid  Hyperliquid adapter (perps, spot, deposits/withdrawals)
#   polymarket   Polymarket adapter (prediction markets, trading, bridging)
#   moonwell     Moonwell adapter (Base lending/borrowing)
#   pendle       Pendle adapter (PT/YT markets)
#   uniswap      Uniswap V3 adapter (concentrated liquidity)
#   projectx     ProjectX adapter (Uniswap V3 fork on HyperEVM)
#   data         Pool, token, and balance data (pool discovery, token metadata, ledger)

set -euo pipefail

# --- Parse --commit flag ---
SDK_COMMIT=""
RESTORE_REF=""

# Check for sdk-version.md file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SDK_VERSION_FILE="$SCRIPT_DIR/../sdk-version.md"

if [[ -f "$SDK_VERSION_FILE" ]]; then
    SDK_COMMIT="$(tr -d '[:space:]' < "$SDK_VERSION_FILE")"
fi

# Command-line --commit overrides sdk-version.md
ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --commit)
            SDK_COMMIT="$2"
            shift 2
            ;;
        --version|-v)
            if [[ -n "$SDK_COMMIT" ]]; then
                echo "Pinned SDK version: $SDK_COMMIT"
            else
                echo "No SDK version pinned (no sdk-version.md file and no --commit flag)."
            fi
            exit 0
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done
set -- "${ARGS[@]+"${ARGS[@]}"}"

# --- Resolve SDK path ---
if [[ -n "${WAYFINDER_SDK_PATH:-}" ]] && [[ -d "$WAYFINDER_SDK_PATH" ]]; then
    SDK_ROOT="$WAYFINDER_SDK_PATH"
elif [[ -d "$REPO_ROOT/../wayfinder-paths-sdk" ]]; then
    SDK_ROOT="$(cd "$REPO_ROOT/../wayfinder-paths-sdk" && pwd)"
elif [[ -d "$HOME/wayfinder-paths-sdk" ]]; then
    SDK_ROOT="$HOME/wayfinder-paths-sdk"
else
    echo "ERROR: Cannot find wayfinder-paths-sdk." >&2
    echo "Tried:" >&2
    echo "  \$WAYFINDER_SDK_PATH (not set or missing)" >&2
    echo "  $REPO_ROOT/../wayfinder-paths-sdk" >&2
    echo "  $HOME/wayfinder-paths-sdk" >&2
    echo "" >&2
    echo "Set WAYFINDER_SDK_PATH or clone the SDK next to this repo." >&2
    exit 1
fi

# --- Checkout pinned ref if specified ---
if [[ -n "$SDK_COMMIT" ]]; then
    RESTORE_REF="$(cd "$SDK_ROOT" && { git symbolic-ref -q --short HEAD 2>/dev/null || git rev-parse HEAD; })"
    echo "Checking out SDK ref: $SDK_COMMIT" >&2
    (cd "$SDK_ROOT" && git checkout --quiet "$SDK_COMMIT")
    trap '(cd "$SDK_ROOT" && git checkout --quiet "$RESTORE_REF") 2>/dev/null' EXIT
fi

SKILLS_DIR="$SDK_ROOT/.claude/skills"

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "ERROR: Skills directory not found at $SKILLS_DIR" >&2
    exit 1
fi

# --- Topic → directory mapping ---
declare -A TOPIC_MAP=(
    [strategies]="developing-wayfinder-strategies"
    [setup]="setup"
    [boros]="using-boros-adapter"
    [brap]="using-brap-adapter"
    [hyperlend]="using-hyperlend-adapter"
    [hyperliquid]="using-hyperliquid-adapter"
    [polymarket]="using-polymarket-adapter"
    [moonwell]="using-moonwell-adapter"
    [pendle]="using-pendle-adapter"
    [uniswap]="using-uniswap-adapter"
    [projectx]="using-projectx-adapter"
    [data]="using-pool-token-balance-data"
)

# --- Functions ---

print_topic_header() {
    local topic="$1"
    local dir_name="$2"
    echo ""
    echo "================================================================================"
    echo "  $topic  ($dir_name)"
    echo "================================================================================"
    echo ""
}

print_file() {
    local filepath="$1"
    local relpath="${filepath#$SKILLS_DIR/}"
    echo "--- $relpath ---"
    echo ""
    cat "$filepath"
    echo ""
}

show_topic() {
    local topic="$1"
    local dir_name="${TOPIC_MAP[$topic]:-}"

    if [[ -z "$dir_name" ]]; then
        echo "ERROR: Unknown topic '$topic'." >&2
        echo "Run with --list to see available topics." >&2
        exit 1
    fi

    local skill_dir="$SKILLS_DIR/$dir_name"

    if [[ ! -d "$skill_dir" ]]; then
        echo "ERROR: Skill directory not found: $skill_dir" >&2
        exit 1
    fi

    print_topic_header "$topic" "$dir_name"

    # Print SKILL.md first
    if [[ -f "$skill_dir/SKILL.md" ]]; then
        print_file "$skill_dir/SKILL.md"
    fi

    # Print all rules files sorted
    if [[ -d "$skill_dir/rules" ]]; then
        for rule_file in "$skill_dir/rules"/*.md; do
            [[ -f "$rule_file" ]] && print_file "$rule_file"
        done
    fi
}

show_list() {
    echo "Available topics:"
    echo ""
    echo "  strategies   Developing Wayfinder strategies (workflow, manifests, safety, data sources)"
    echo "  setup        First-time SDK setup"
    echo "  boros        Boros adapter (fixed-rate markets, rate locking, funding swaps)"
    echo "  brap         BRAP adapter (cross-chain swaps and bridges)"
    echo "  hyperlend    HyperLend adapter (HyperEVM lending)"
    echo "  hyperliquid  Hyperliquid adapter (perps, spot, deposits/withdrawals)"
    echo "  polymarket   Polymarket adapter (prediction markets, trading, bridging)"
    echo "  moonwell     Moonwell adapter (Base lending/borrowing)"
    echo "  pendle       Pendle adapter (PT/YT markets)"
    echo "  uniswap      Uniswap V3 adapter (concentrated liquidity)"
    echo "  projectx     ProjectX adapter (Uniswap V3 fork on HyperEVM)"
    echo "  data         Pool, token, and balance data (pool discovery, token metadata, ledger)"
    echo ""
    echo "Usage:"
    echo "  $0 <topic>          Show docs for a topic"
    echo "  $0 --all            Show all docs"
    echo "  $0 --list           This list"
    echo "  $0 --commit <hash>  Checkout a specific SDK commit before reading"
    echo "  $0 --version        Show the pinned SDK version"
    echo ""
    echo "SDK path: $SDK_ROOT"
    if [[ -n "$SDK_COMMIT" ]]; then
        echo "SDK ref: $SDK_COMMIT"
    fi
}

show_all() {
    for topic in strategies setup boros brap hyperlend hyperliquid polymarket moonwell pendle uniswap projectx data; do
        show_topic "$topic"
    done
}

# --- Main ---

if [[ $# -eq 0 ]]; then
    show_list
    exit 0
fi

case "$1" in
    --list|-l)
        show_list
        ;;
    --all|-a)
        show_all
        ;;
    --help|-h)
        show_list
        ;;
    *)
        # Support multiple topics: pull-sdk-ref.sh boros moonwell
        for topic in "$@"; do
            show_topic "$topic"
        done
        ;;
esac
