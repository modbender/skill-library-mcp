---
name: houston-transtar-watch
description: "Poll Houston TranStar incidents RSS every 10 minutes and WhatsApp me when there are changes."
requires: {}
os: ["linux", "macos", "windows"]
schedule:
  cron: "*/10 * * * *"
deliver: true
channel: whatsapp
---

# Houston TranStar Watcher

## Overview
This skill is a specialized traffic monitor for the Greater Houston area. It interfaces with the Houston TranStar Real-Time Incident RSS feed to detect new accidents, stalled vehicles, and road closures. 

## Technical Runbook
The following logic is executed every 10 minutes via the internal cron scheduler:

1. **Script Execution:** The skill navigates to the local directory and executes the diff-check logic:
   ```bash
   python3 transtar_diff.py
2. Output Parsing: - If the script returns the string NO_CHANGES, the process terminates immediately to save bandwidth and prevent notification fatigue.

If any other text is returned, it is treated as a "Delta Report" of new incidents.
3. Delivery Logic
When a "Delta Report" is generated, the content is formatted for mobile viewing and pushed via the WhatsApp Gateway to the configured recipient.

4. Use Cases
Automated commute monitoring for Houston residents.

Alerting logistics teams to major freeway closures on I-10, I-45, and US-59.3. 
---
