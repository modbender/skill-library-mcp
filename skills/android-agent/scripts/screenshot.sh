#!/bin/bash
# screenshot.sh — Take a screenshot via ADB screencap (bypasses DroidRun screenshot tooling)
#
# Usage:
#   ./screenshot.sh [serial] [output_path]
#
# Defaults:
#   serial: $ANDROID_SERIAL or auto-detected
#   output: /tmp/android-screenshot.png
set -euo pipefail

SERIAL="${1:-${ANDROID_SERIAL:-}}"
OUT_PATH="${2:-/tmp/android-screenshot.png}"

if ! command -v adb &>/dev/null; then
  echo "❌ adb not found in PATH"
  exit 1
fi

# Auto-detect serial if not provided
if [ -z "$SERIAL" ]; then
  SERIAL=$(adb devices | grep -E 'device$' | head -1 | awk '{print $1}')
fi

if [ -z "$SERIAL" ]; then
  echo "❌ No device found. Connect a phone or set ANDROID_SERIAL."
  exit 1
fi

mkdir -p "$(dirname "$OUT_PATH")"

echo "📸 Taking screenshot from $SERIAL -> $OUT_PATH"
# exec-out streams raw bytes; screencap -p outputs PNG
adb -s "$SERIAL" exec-out screencap -p > "$OUT_PATH"

SIZE=$(wc -c < "$OUT_PATH" | tr -d ' ')
if [ "$SIZE" -lt 1024 ]; then
  echo "❌ Screenshot file too small ($SIZE bytes): $OUT_PATH"
  exit 1
fi

echo "✅ Saved: $OUT_PATH ($SIZE bytes)"
