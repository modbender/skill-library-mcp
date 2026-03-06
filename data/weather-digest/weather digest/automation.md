# Weather Digest Automation Recipes

## Local cron job (macOS/Linux)
1. Activate the project venv once to install deps:
   ```bash
   cd /Users/dannyvett/.openclaw/workspace/skills/weather-digest
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a shell wrapper (`~/bin/run-weather-digest.sh`):
   ```bash
   #!/usr/bin/env bash
   cd /Users/dannyvett/.openclaw/workspace/skills/weather-digest
   source .venv/bin/activate
   python weather_digest.py \
     --config config.json \
     --output outputs/digest-$(date +%Y%m%d).md \
     --html outputs/digest-$(date +%Y%m%d).html \
     --json outputs/digest-$(date +%Y%m%d).json
   ```
   Make it executable: `chmod +x ~/bin/run-weather-digest.sh`.
3. Add a cron entry (6:00 AM daily example):
   ```cron
   0 6 * * * /Users/dannyvett/bin/run-weather-digest.sh >> /Users/dannyvett/logs/weather-digest.log 2>&1
   ```

## OpenClaw heartbeat slot
- Add to `HEARTBEAT.md`:
  ```
  - Every morning before 7:00 AM, run `python skills/weather-digest/weather_digest.py --config ... --output ...` and DM the Markdown file to Dan if there are severe alerts.
  ```
- The agent will batch this into existing heartbeat checks so you get in-chat notifications without a separate cron job.

## Slack notification hook
1. Extend the wrapper to post summaries via webhook:
   ```bash
   SUMMARY=$(head -n 30 outputs/digest-$(date +%Y%m%d).md)
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Weather Digest\n```'     --data '{"text":"Weather Digest\n```\n'$(tail -n +2 outputs/digest-$(date +%Y%m%d).md | head -n 20)\n```"}' $SLACK_WEBHOOK_URL
   ```
   Adjust `tail/head` lines to control preview length. Use Block Kit if you prefer cards.

## LaunchAgent (macOS GUI)
- Save this plist at `~/Library/LaunchAgents/com.dan.weatherdigest.plist`:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  <plist version="1.0">
  <dict>
    <key>Label</key><string>com.dan.weatherdigest</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/zsh</string>
      <string>-lc</string>
      <string>~/bin/run-weather-digest.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key><integer>6</integer>
      <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key><string>/Users/dannyvett/logs/weatherdigest.out</string>
    <key>StandardErrorPath</key><string>/Users/dannyvett/logs/weatherdigest.err</string>
  </dict>
  </plist>
  ```
  Load with `launchctl load ~/Library/LaunchAgents/com.dan.weatherdigest.plist`.

## Delivering to Things 3 / Apple Reminders
- Use `things` CLI to drop the Markdown into Today list for manual review:
  ```bash
  cat outputs/digest-$(date +%Y%m%d).md | /usr/local/bin/things add --title "Weather Digest" --when today --notes -
  ```
- Or `remindctl add` to push the top alert as an actionable reminder.

Feel free to ship this doc as part of the premium tier or bundle it with onboarding emails.
