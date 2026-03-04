#!/bin/bash
# detect-proxy.sh - Detect local proxy ports on macOS

set -e

COMMON_PORTS=(7890 7891 7897 6152 6153 1080 10808 10809)
FOUND=()

echo "🔍 Scanning for proxy ports..."

# Test common ports
for port in "${COMMON_PORTS[@]}"; do
  if nc -z 127.0.0.1 "$port" 2>/dev/null; then
    echo "✓ Port $port is OPEN"
    FOUND+=("$port")
  fi
done

# Check for Clash specific config
if pgrep -f "clash" > /dev/null; then
  echo ""
  echo "📱 Clash process detected"
  
  CLASH_CONFIG="${HOME}/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml"
  if [[ -f "$CLASH_CONFIG" ]]; then
    MIXED_PORT=$(grep -E "^mixed-port:" "$CLASH_CONFIG" | awk '{print $2}' || true)
    if [[ -n "$MIXED_PORT" ]]; then
      echo "   Clash mixed-port: $MIXED_PORT"
      if [[ ! " ${FOUND[@]} " =~ " ${MIXED_PORT} " ]]; then
        FOUND+=("$MIXED_PORT")
      fi
    fi
  fi
fi

echo ""
if [[ ${#FOUND[@]} -eq 0 ]]; then
  echo "❌ No proxy ports found"
  echo "   Make sure Clash/V2Ray/Surge is running"
  exit 1
else
  echo "✅ Found ${#FOUND[@]} open port(s): ${FOUND[*]}"
  echo ""
  echo "💡 To set proxy for OpenClaw:"
  echo "   launchctl setenv HTTPS_PROXY http://127.0.0.1:${FOUND[0]}"
  echo "   openclaw gateway restart"
fi
