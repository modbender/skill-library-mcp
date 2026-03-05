#!/bin/bash
# Morning Report with Photo
# Captures office photo and sends report with image

MOTION_DIR="$HOME/.clawdbot/overwatch"
REPORT_IMAGE="$MOTION_DIR/morning-report-$(date +%Y%m%d).jpg"
DATE=$(date +%Y-%m-%d)

# Capture morning photo
imagesnap -q "$REPORT_IMAGE" 2>/dev/null

# Count overnight activity
OVERNIGHT_COUNT=$(find $MOTION_DIR -name "motion_*.jpg" -mtime -1 | wc -l)

# Create report text
REPORT="📊 Morning Camera Report - $DATE

"

if [ "$OVERNIGHT_COUNT" -eq 0 ]; then
    REPORT+="✅ Quiet night! No motion detected.
"
else
    REPORT+="🚨 $OVERNIGHT_COUNT motion event(s) overnight

Latest captures:"
    ls -lt $MOTION_DIR/motion_*.jpg 2>/dev/null | head -3 | while read line; do
        FILE=$(echo $line | awk '{print $9}')
        SIZE=$(echo $line | awk '{print $5}')
        REPORT+="
  • $(basename $FILE) ($SIZE)"
    done
fi

REPORT+="

🎥 Live Stream: http://localhost:8080
📁 Captures: $MOTION_DIR

Commands:
  'analyze' - Check images for people
  'stream'  - Get live stream link  
  'capture' - Take fresh photo"

echo "$REPORT"
echo ""
echo "IMAGE:$REPORT_IMAGE"
