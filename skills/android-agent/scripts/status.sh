#!/bin/bash
# status.sh — Show Android device status
#
# Usage: ./status.sh [serial]
set -euo pipefail

SERIAL="${1:-${ANDROID_SERIAL:-}}"

if ! command -v adb &>/dev/null; then
    echo "❌ ADB not found."
    exit 1
fi

# Auto-detect if no serial
if [ -z "$SERIAL" ]; then
    SERIAL=$(adb devices | grep -E 'device$' | head -1 | awk '{print $1}')
fi

if [ -z "$SERIAL" ]; then
    echo "❌ No device found. Connect a phone or set ANDROID_SERIAL."
    exit 1
fi

# Check device is reachable
if ! adb -s "$SERIAL" shell echo ok &>/dev/null; then
    echo "❌ Device ${SERIAL} not reachable."
    exit 1
fi

MODEL=$(adb -s "$SERIAL" shell getprop ro.product.model 2>/dev/null || echo "unknown")
BRAND=$(adb -s "$SERIAL" shell getprop ro.product.brand 2>/dev/null || echo "unknown")
ANDROID=$(adb -s "$SERIAL" shell getprop ro.build.version.release 2>/dev/null || echo "?")
API=$(adb -s "$SERIAL" shell getprop ro.build.version.sdk 2>/dev/null || echo "?")
BATTERY=$(adb -s "$SERIAL" shell dumpsys battery 2>/dev/null | grep level | awk '{print $2}' || echo "?")
CHARGING=$(adb -s "$SERIAL" shell dumpsys battery 2>/dev/null | grep "AC powered" | awk '{print $3}' || echo "?")

# Screen state
SCREEN_STATE="unknown"
POWER_STATE=$(adb -s "$SERIAL" shell dumpsys power 2>/dev/null)
if echo "$POWER_STATE" | grep -qE "mWakefulness=Awake|getWakefulnessLocked..=Awake"; then
    SCREEN_STATE="ON"
elif echo "$POWER_STATE" | grep -qE "mWakefulness=Asleep|mWakefulness=Dozing|getWakefulnessLocked..=Asleep|getWakefulnessLocked..=Dozing"; then
    SCREEN_STATE="OFF"
fi

# Lock state
LOCK_STATE="unknown"
WINDOW_STATE=$(adb -s "$SERIAL" shell dumpsys window 2>/dev/null)
if echo "$WINDOW_STATE" | grep -q "mDreamingLockscreen=true"; then
    LOCK_STATE="locked"
elif echo "$WINDOW_STATE" | grep -q "isStatusBarKeyguard=true"; then
    LOCK_STATE="locked"
else
    LOCK_STATE="unlocked"
fi

# Connection type
CONN_TYPE="USB"
if echo "$SERIAL" | grep -q ":"; then
    CONN_TYPE="TCP/WiFi"
fi

# DroidRun Portal
PORTAL="not installed"
if adb -s "$SERIAL" shell pm list packages 2>/dev/null | grep -q "droidrun"; then
    PORTAL_VER=$(adb -s "$SERIAL" shell dumpsys package com.droidrun.portal 2>/dev/null | grep versionName | head -1 | awk -F= '{print $2}' || echo "?")
    PORTAL="v${PORTAL_VER}"
fi

echo "📱 Device:     ${BRAND} ${MODEL}"
echo "🤖 Android:    ${ANDROID} (API ${API})"
echo "🔋 Battery:    ${BATTERY}% (AC: ${CHARGING})"
echo "📺 Screen:     ${SCREEN_STATE} (${LOCK_STATE})"
echo "🔌 Connection: ${CONN_TYPE} (${SERIAL})"
echo "📦 Portal:     ${PORTAL}"
