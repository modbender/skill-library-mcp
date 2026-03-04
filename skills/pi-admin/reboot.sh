#!/bin/bash
# Reboot system with countdown

# Usage: ./reboot.sh [--dry-run]

if [ "$1" = "--dry-run" ]; then
  echo "🔍 DRY RUN MODE - System would reboot but won't"
  echo "=================================================="
  echo ""
  echo "The system would show a 10-second countdown, then reboot."
  echo ""
  echo "To actually reboot, run without --dry-run"
  exit 0
fi

echo "🔄 System Reboot"
echo "=================="
echo ""

# Check for sudo
if [ "$EUID" -ne 0 ]; then
  SUDO="sudo"
else
  SUDO=""
fi

echo "⚠️  This will reboot the system!"
echo ""
echo "To cancel, press Ctrl+C"
echo ""

# Countdown
for i in {10..1}; do
  echo -ne "\rRebooting in $i seconds... "
  sleep 1
done

echo ""
echo ""
echo "🔄 Rebooting now..."
$SUDO reboot