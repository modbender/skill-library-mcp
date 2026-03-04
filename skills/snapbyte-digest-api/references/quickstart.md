# Snapbyte Digest API Quickstart

## 1) Install ClawHub CLI

```bash
npm i -g clawhub
```

## 2) Install skill

```bash
clawhub install snapbyte-digest-api
```

## 3) Configure API key

Set your Snapbyte API key via OpenClaw config using `SNAPBYTE_API_KEY`.

```json
{
  skills: {
    entries: {
      "snapbyte-digest-api": {
        enabled: true,
        apiKey: "snap-your-api-key"
      }
    }
  }
}
```

## 4) Try common commands

```bash
python3 scripts/snapbyte_digest.py configurations
python3 scripts/snapbyte_digest.py latest
python3 scripts/snapbyte_digest.py history --configuration-id 12 --page 1 --limit 10
python3 scripts/snapbyte_digest.py items --digest-id dst_abc123 --page 1 --limit 10
```

## 5) Schedule daily digest with OpenClaw cron

```bash
openclaw cron add \
  --name "Snapbyte Daily Digest" \
  --cron "0 7 * * 1-5" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Use snapbyte-digest-api and send my daily developer digest with top links and one-line why it matters." \
  --announce \
  --channel last
```

## 6) Verify cron runs

```bash
openclaw cron list
openclaw cron runs --id <job-id> --limit 50
openclaw cron run <job-id> --due
```

## Prompt examples

- "Use snapbyte-digest-api and show my latest digest."
- "Use snapbyte-digest-api and fetch my digest history for configuration 12."
- "Use snapbyte-digest-api and list top items for digest dst_abc123."

## Raw mode

Append `--raw` to print JSON payloads instead of formatted markdown.
