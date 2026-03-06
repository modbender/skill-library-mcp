#!/bin/bash
# Rune Session Handler - SECURE wrapper for session hooks
# This script safely handles user input to prevent shell injection vulnerabilities

ACTION="$1"

# Security function to sanitize input
sanitize_message() {
  local input="$1"
  
  # Remove dangerous characters and limit length
  echo "$input" | \
    head -c 500 | \
    tr -d '`$(){}[]|;&<>' | \
    sed 's/[^a-zA-Z0-9 ._-]//g' | \
    head -c 200
}

# Get MESSAGE from environment and sanitize it
SAFE_MESSAGE=$(sanitize_message "$MESSAGE")

case "$ACTION" in
  "start")
    # Session start hook - recall relevant context
    if [[ -n "$SAFE_MESSAGE" ]] && command -v rune >/dev/null 2>&1; then
      # Pass sanitized message as argument (safe from shell injection)
      rune recall "$SAFE_MESSAGE" --limit 10 2>/dev/null || true
    fi
    ;;
    
  "end")
    # Session end hook - save interaction style  
    if [[ -n "$SAFE_MESSAGE" ]] && command -v rune >/dev/null 2>&1; then
      # Pass sanitized message as argument (safe from shell injection)
      rune session-style "$SAFE_MESSAGE" --save 2>/dev/null || true
    fi
    ;;
    
  *)
    echo "Usage: $0 [start|end]" >&2
    echo "Sanitizes MESSAGE environment variable and calls appropriate rune function" >&2
    exit 1
    ;;
esac