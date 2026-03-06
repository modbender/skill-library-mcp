# Yuboto Omni API Skill — User Guide

## What this skill helps with

- Send SMS messages
- Check delivery status (DLR)
- Send bulk SMS from CSV
- Track pending/delivered/failed messages locally
- Estimate sending cost by country/channel

## Prerequisites

- Active Yuboto/Octapush API key (base64 format)
- Approved sender ID (e.g., `Dinos`)
- Python 3 installed

## Environment variables

Set these in your shell or `.env`:

- `OCTAPUSH_API_KEY`
- `TEST_PHONENUMBER` (optional test recipient)
- `SMS_SENDER` (optional default sender)

## Quick start

Run from skill root:

```bash
python3 scripts/yuboto_cli.py balance
python3 scripts/yuboto_cli.py cost --channel sms --iso2 gr --phonenumber +3069XXXXXXX
python3 scripts/yuboto_cli.py send-sms --sender "Dinos" --text "hello" --to +3069XXXXXXX
python3 scripts/yuboto_cli.py dlr --id <MESSAGE_GUID>
```

## Bulk send (CSV)

CSV example:

```csv
phonenumber,text,sender
+3069AAAAAAA,Campaign message one,Dinos
+3069BBBBBBB,Campaign message two,Dinos
```

Send:

```bash
python3 scripts/yuboto_cli.py send-csv \
  --file contacts.csv \
  --phone-col phonenumber \
  --text-col text \
  --sender-col sender
```

## Tracking and pending queue

```bash
python3 scripts/yuboto_cli.py status
python3 scripts/yuboto_cli.py poll-pending
python3 scripts/yuboto_cli.py history --last 20
```

## Common issues

- `Sms Sender is not valid`:
  - Use an approved sender ID from your account.
- `Invalid omni_channel` on cost:
  - Use `channel=sms` and include `iso2` (e.g., `gr`).
- `Invalid Id` on DLR:
  - Use a real `messageGuid` returned from a successful send.

## Security notes

- Do not hardcode API keys in scripts.
- Prefer env vars over CLI `--api-key` to avoid shell history leaks.
- Treat local logs/state as sensitive (phone numbers + message previews).
