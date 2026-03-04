#!/bin/bash
# Voidborne - Uninstall
# Removes local Voidborne data from this machine

set -e

VOID_DIR="${VOID_DIR:-$HOME/.voidborne}"

echo ""
echo "Voidborne Uninstall"
echo "==================="
echo ""
echo "This will remove the following local data:"
echo "  - Token:       $VOID_DIR/token"
echo "  - Agent ID:  $VOID_DIR/agent_id"
echo "  - Config:      $VOID_DIR/config.json"
echo "  - Cache files:  $VOID_DIR/skill_version, $VOID_DIR/last_check"
echo ""
echo "This does NOT remove your account from the server."
echo ""

if [[ -t 0 ]]; then
    read -p "Proceed? (y/N): " CONFIRM
    if [[ "$CONFIRM" != "y" ]] && [[ "$CONFIRM" != "Y" ]]; then
        echo "Cancelled."
        exit 0
    fi
else
    echo "Non-interactive mode: skipping confirmation."
fi

if [[ -d "$VOID_DIR" ]]; then
    rm -rf "$VOID_DIR"
    echo ""
    echo "Removed: $VOID_DIR"
else
    echo ""
    echo "Nothing to remove: $VOID_DIR does not exist."
fi

echo ""
echo "Uninstall complete."
echo "To also remove the skill files, delete this directory."
