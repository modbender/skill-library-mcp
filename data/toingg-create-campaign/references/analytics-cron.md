# Analytics Cron Playbook

1. **Prerequisites**
   - `TOINGG_API_TOKEN` exported in the environment used by the OpenClaw Gateway.
   - `skills/toingg-create-campaign/scripts/get_campaign_analytics.py` committed to the workspace.

2. **Create a destination folder** for daily snapshots (optional but recommended):
   ```bash
   mkdir -p ~/toingg-analytics
   ```

3. **Create the cron job** (fires at 19:00 local time):
   ```bash
   openclaw cron create toingg-analytics-digest \
     --schedule "0 19 * * *" \
     --command "cd /Users/abhinavkalvacherla/.openclaw/workspace/skills/toingg-create-campaign && ./scripts/get_campaign_analytics.py > ~/toingg-analytics/analytics-$(date +%Y%m%d).json"
   ```

   - Edit the output path to wherever you want the JSON stored.
   - Cron inherits the environment from the gateway; confirm `TOINGG_API_TOKEN` is set there.

4. **Enable only when requested**:
   - Before creating the cron, confirm the user wants scheduled analytics.
   - To pause or remove it later:
     ```bash
     openclaw cron delete toingg-analytics-digest
     ```

5. **Notify the user** after the first successful run and share where the files live.
