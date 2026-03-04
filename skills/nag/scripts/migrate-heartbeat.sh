#!/bin/bash
# migrate-heartbeat.sh
# Prints a HEARTBEAT.md nag check block to stdout.
# Append this to your existing HEARTBEAT.md.

cat << 'EOF'
## Nag Check
Read nag-config.json and memory/nag-state.json.
For each reminder in nag-config.json:
- If date in state differs from today, reset all reminders (set confirmed: false, nagCount: 0).
- Skip if today's weekday isn't in the reminder's `days` array (if specified).
- If current time is after `nagAfter` and confirmed is false: send a nag message to the user.
  - Generate the message from the reminder's label and tone (or use messages.nag if provided).
  - If nagCount >= 3, escalate urgency (use messages.escalate if provided, otherwise generate with more intensity).
  - Increment nagCount in state.
- Do NOT nag before the nagAfter time.
EOF
