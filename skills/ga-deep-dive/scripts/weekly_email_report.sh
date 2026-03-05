#!/bin/bash
# GA4 Deep Dive - Bi-weekly Email Report
# Runs deep_dive_v4.py and emails results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../.venv"
OUTPUT_DIR="$SCRIPT_DIR/../data/reports"
TIMESTAMP=$(date +%Y-%m-%d_%H%M)

# Recipients
TO_EMAILS="felipe.cavalcanti.rj@gmail.com,macballona@mac.com"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Activate venv and run report
source "$VENV_DIR/bin/activate"

# Run v3 (executive summary) and v4 (full monty)
echo "Running GA4 Deep Dive reports..."

# V3 - Executive Summary
python3 "$SCRIPT_DIR/deep_dive_v3.py" solvr --days 14 > "$OUTPUT_DIR/solvr_v3_$TIMESTAMP.txt" 2>&1

# V4 - Full Monty  
python3 "$SCRIPT_DIR/deep_dive_v4.py" solvr --days 14 > "$OUTPUT_DIR/solvr_v4_$TIMESTAMP.txt" 2>&1

# Combine reports
REPORT_FILE="$OUTPUT_DIR/solvr_full_report_$TIMESTAMP.txt"
cat > "$REPORT_FILE" << HEADER
═══════════════════════════════════════════════════════════════════════════════
   🏴‍☠️  SOLVR BI-WEEKLY ANALYTICS REPORT
   Generated: $(date -u +"%Y-%m-%d %H:%M UTC")
   Period: Last 14 days
═══════════════════════════════════════════════════════════════════════════════

HEADER

cat "$OUTPUT_DIR/solvr_v3_$TIMESTAMP.txt" >> "$REPORT_FILE"
echo -e "\n\n" >> "$REPORT_FILE"
cat "$OUTPUT_DIR/solvr_v4_$TIMESTAMP.txt" >> "$REPORT_FILE"

echo "Report generated: $REPORT_FILE"
echo "Sending email..."

# Output for email
cat "$REPORT_FILE"
