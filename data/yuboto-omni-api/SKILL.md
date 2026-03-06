---
name: yuboto-omni-api
description: Implement, troubleshoot, and generate integrations for Yuboto Omni API (SMS/Viber/messaging endpoints, callbacks, lists/contacts/blacklist, cost/balance/account methods). Use when building code or workflows against Yuboto API docs, especially when endpoint details differ between PDF docs and live Swagger.
---

# Yuboto Omni API

Use this skill to work with Yuboto Omni API safely and consistently.

## Source-of-truth order

1. `references/swagger_v1.json` (live endpoint contract)
2. `references/api_quick_reference.md` (human-readable endpoint map)
3. `references/omni_api_v1_10_raw.md` (legacy PDF extract)
4. `assets/OMNI_API_DOCUMENTATION_V1_10.pdf` (original PDF)

If PDF and Swagger conflict, prefer Swagger for endpoint paths/fields.

## Fast workflow

1. Identify the use case (send message, get DLR, contacts, subscriber lists, blacklist, cost/balance).
2. Find matching endpoint(s):
   - Read `references/api_quick_reference.md`, or
   - Run: `python3 scripts/find_endpoints.py --q "<keyword>"`
3. Validate request schema directly in `references/swagger_v1.json`:
   - parameters (path/query/header)
   - requestBody
   - response schema
4. Build implementation code with:
   - clear auth header handling
   - retries + timeout
   - structured error mapping
5. For advanced Viber features, check Swagger first.

## Available commands (provided by scripts/yuboto_cli.py)

- `balance` — get account balance
- `cost --channel sms --iso2 gr --phonenumber +30...` — estimate sending cost
- `send-sms --sender <approved_sender> --text "..." --to +30...` — send SMS
- `dlr --id <messageGuid>` — check delivery status for one message
- `send-csv --file contacts.csv --phone-col phonenumber --text-col text --sender-col sender` — bulk send from CSV
- `poll-pending` — refresh statuses for all pending messages
- `history --last 20` — show recent send records
- `status` / `status --id <messageGuid>` — inspect tracked message state

## Output requirements

When generating code or integration instructions:

- Include exact method + path.
- Include required auth headers.
- Include minimal working request example.
- Include expected response shape.
- Include 1 failure case and handling.

## Security + Ops Notes

- Store API key in environment variable `OCTAPUSH_API_KEY`, not in source files.
- Prefer env vars over CLI `--api-key` to avoid leaking credentials in shell history.
- Use only approved sender IDs (e.g. account-approved SMS sender names).
- Treat local runtime logs/state as sensitive (phone numbers, message previews, DLR payloads).
- Keep runtime data outside the skill package when publishing.

## Notes

- Swagger URL: `https://api.yuboto.com/scalar/#description/introduction`
- Swagger JSON: `https://api.yuboto.com/swagger/v1/swagger.json`
- Keep generated examples language-neutral unless user requests GR/EN copy.
