#!/bin/bash
# COBRACLAW CLI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_help() {
    echo "COBRACLAW CLI"
    echo "Usage: cobraclaw.sh <command>"
    echo "Commands: lookup, activate, kata, quote, patrol, test, help"
}

cmd_lookup() {
    term="$1"
    case "$term" in
        strike-first) echo "Strike First - Open with power";;
        strike-hard) echo "Strike Hard - Precision in every word";;
        no-mercy) echo "No Mercy - Commit fully";;
        pillars) echo "Five pillars: Hard Shell, Eagle Fang, Cobra Strike, Sideways, No Mercy";;
        *) echo "Usage: cobraclaw.sh lookup <term>";;
    esac
}

cmd_activate() {
    echo "COBRA MODE ACTIVATED"
    echo "Strike First. Strike Hard. No Mercy."
}

cmd_kata() {
    kata="$1"
    if [ -x "$SCRIPT_DIR/katas/${kata}.sh" ]; then
        "$SCRIPT_DIR/katas/${kata}.sh"
    else
        echo "Kata not found: $kata"
    fi
}

cmd_quote() {
    echo "Strike first. Strike hard. No mercy."
}

cmd_patrol() {
    echo "Patrol complete. The dojo is secure."
}

cmd_test() {
    bash "$SCRIPT_DIR/test-skill.sh"
}

cmd="${1:-help}"
shift
case "$cmd" in
    lookup) cmd_lookup "$@" ;;
    activate) cmd_activate ;;
    kata) cmd_kata "$@" ;;
    quote) cmd_quote ;;
    patrol) cmd_patrol ;;
    test) cmd_test ;;
    help|--help) print_help ;;
esac
