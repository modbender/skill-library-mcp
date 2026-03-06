#!/bin/bash
# Output the copyright notice for this skill namespace.
# This script is the main entry point for the reserved skill.
# Usage: copyright.sh [--format text|json]

set -e

FORMAT="${1:---format}"
VALUE="${2:-text}"

if [ "$FORMAT" = "--format" ] && [ "$VALUE" = "json" ]; then
  echo '{"copyright":"Netsnek e.U.","year":2026,"license":"All rights reserved","website":"https://netsnek.com"}'
else
  echo "Copyright (c) 2026 Netsnek e.U. All rights reserved."
  echo "Website: https://netsnek.com"
fi
