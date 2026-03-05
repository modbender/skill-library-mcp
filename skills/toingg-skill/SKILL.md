---
name: toingg-skill
description: End-to-end Toingg ops: create campaigns, (optionally) schedule daily analytics pulls, and turn Excel contact sheets into WhatsApp outreach via add_contacts + send_whatsapp_templates. Use when Codex needs to automate Toingg voice/WhatsApp workflows and requires scripts for campaign POSTs, analytics cron setup, or bulk contact uploads.
---

# Toingg Ops Toolkit

This skill bundles everything needed to manage Toingg campaigns from Claw:

- **Campaign creation** via `create_campaign.py`
- **Optional analytics cron** (7 PM daily) powered by `get_campaign_analytics.py`
- **Contact upload + WhatsApp broadcast** using `xlsx_to_contacts.py`, `add_contacts.py`, and `send_whatsapp_templates.py`

All HTTP calls reuse the `TOINGG_API_TOKEN` bearer token.

## Setup

1. Export your token in every environment that runs these scripts (gateway, cron, terminals).
   ```bash
   export TOINGG_API_TOKEN="tg_..."
   ```
2. Install Python deps once if you will ingest Excel files:
   ```bash
   pip install openpyxl requests
   ```
3. Keep payloads (campaign JSON, analytics snapshots, contact exports) in version control or shared storage per your security rules.

## Campaign creation workflow

1. Gather campaign fields from the user (title, voice, language, script, purpose, tone,
   post-call schema, notification numbers, autopilot flags, etc.).
2. Draft a payload JSON using [`references/payload-template.md`](references/payload-template.md) as the scaffold.
3. Run the helper:
   ```bash
   cd skills/toingg-skill
   ./scripts/create_campaign.py payloads/my_campaign.json > responses/create-$(date +%s).json
   ```
4. Return the API response (campaign ID, status, or validation errors) to the user and log it.

## Opt-in analytics cron (7 PM daily)

Only offer this when the user explicitly asks for daily analytics.

1. Confirm desired schedule/output directory.
2. Follow [`references/analytics-cron.md`](references/analytics-cron.md) to create `openclaw cron create toingg-analytics-digest ...` with the provided command snippet. Adjust paths if needed.
3. Double-check `TOINGG_API_TOKEN` is visible to the gateway before enabling the cron.
4. After the first run, share where the JSON snapshots live and how to disable the cron (`openclaw cron delete ...`).

`get_campaign_analytics.py` can also be run ad-hoc for on-demand pulls:
```bash
./scripts/get_campaign_analytics.py > analytics.json
```

## Contact upload + WhatsApp templates

When a user supplies an Excel sheet (name / phone / context columns) and wants to blast a WhatsApp template:

1. **Convert Excel → JSON**
   ```bash
   ./scripts/xlsx_to_contacts.py ~/Downloads/leads.xlsx contacts.json
   ```
   See [`references/contact-workflow.md`](references/contact-workflow.md) for the exact column expectations and troubleshooting. The script skips blank rows and normalizes phone numbers.

2. **Upload contacts** to a Toingg contact list (auto-creates if missing):
   ```bash
   ./scripts/add_contacts.py ClawTest contacts.json
   ```

3. **Send WhatsApp templates** once the list is ready:
   ```bash
   ./scripts/send_whatsapp_templates.py \
     231565687 \
     bfesfbgf \
     en-US \
     ClawTest \
     --payload template-variables.json
   ```
   - Omit `--payload` (defaults to `[]`) if the template has no variables.
   - Pass `--resend` only when the user explicitly wants to re-contact existing recipients.

4. Confirm delivery status in Toingg and report any errors back to the user (the helper prints full JSON responses for logging).

## File map

| Script | Purpose |
|--------|---------|
| `scripts/create_campaign.py` | POST `/api/v3/create_campaign` with arbitrary payloads |
| `scripts/get_campaign_analytics.py` | GET `/api/v3/get_campaign_analytics` (cron-friendly) |
| `scripts/xlsx_to_contacts.py` | Convert Excel sheets into Toingg contact JSON |
| `scripts/add_contacts.py` | Upload contact lists via `/api/v3/add_contacts` |
| `scripts/send_whatsapp_templates.py` | Trigger `/api/v3/send_whatsapp_templates` |

Keep this toolkit lightweight: update the references when Toingg adds new fields or workflows so other operators can follow the same patterns.
