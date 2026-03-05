#!/bin/bash
# Morning training brief: Garmin recovery + optional Strava activity
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GARMIN_STATS=$("$SCRIPT_DIR/get-stats.sh" 2>/dev/null)
GARMIN_OK=false
if [ -n "$GARMIN_STATS" ] && ! echo "$GARMIN_STATS" | grep -q '"error"'; then
  GARMIN_OK=true
fi

STRAVA=$(/root/clawd/skills/strava/scripts/training-summary.sh 2>/dev/null || true)

echo "🏋️🚴 **Morning Training Brief**"
echo ""

if [ "$GARMIN_OK" = "true" ]; then
  val() { echo "$GARMIN_STATS" | jq -r "$1 // empty"; }

  SLEEP=$(val '.sleep.duration_hours')
  SCORE=$(val '.sleep.sleep_score')
  BB=$(val '.body_battery.current')
  RHR=$(val '.heart_rate.resting')
  STRESS=$(val '.stress.average')
  STATUS=$(val '.training_status.status')

  # Sleep
  [ -n "$SLEEP" ] && {
    line="💤 **Sleep:** ${SLEEP}h"
    [ -n "$SCORE" ] && line="$line (score: $SCORE)"
    echo "$line"
  }

  # Body Battery
  [ -n "$BB" ] && {
    label="moderate"
    (( $(echo "$BB > 70" | bc -l) )) && label="good energy!"
    (( $(echo "$BB <= 40" | bc -l) )) && label="low — prioritize recovery"
    echo "⚡ **Body Battery:** ${BB}% ($label)"
  }

  # Resting HR
  [ -n "$RHR" ] && echo "❤️ **Resting HR:** ${RHR} bpm"

  # Stress
  [ -n "$STRESS" ] && {
    tag="Low"
    (( $(echo "$STRESS >= 30" | bc -l) )) && tag="Moderate"
    (( $(echo "$STRESS >= 60" | bc -l) )) && tag="High — consider recovery day"
    echo "😌 **Stress:** $tag ($STRESS)"
  }

  # Training Status
  [ -n "$STATUS" ] && {
    pretty=$(echo "$STATUS" | sed 's/_/ /g; s/.*/\L&/; s/\b./\U&/g')
    echo "🏋️ **Training:** $pretty"
  }

  echo ""
fi

[ -n "$STRAVA" ] && echo "$STRAVA"
