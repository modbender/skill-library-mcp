---
name: sensorpro
description: "Manage your Sensorpro email marketing account in OpenClaw."
metadata:
  openclaw:
    emoji: "📨"
    homepage: "https://github.com/forcequit/openclaw-sensorpro"
    requires:
      env: ["SENSORPRO_API_KEY","SENSORPRO_ORG","SENSORPRO_USER","SENSORPRO_PASS"]
      bins: ["curl","python3"]
    primaryEnv: "SENSORPRO_API_KEY"
---

Use this skill to **manage your Sensorpro email marketing account in OpenClaw**.

Official docs:
- Home: https://sensorpro.net/api/
- Contacts: https://sensorpro.net/api/contacts.html
- Campaigns + metrics: https://sensorpro.net/api/campaigns.html
- Relay Email: https://sensorpro.net/api/sendemail.html
- Imports: https://www.sensorpro.net/api/imports.html
- Account: https://sensorpro.net/api/account.html

## Setup (required)
Set these environment variables in your OpenClaw `.env` (or in the shell before running curl):

- `SENSORPRO_API_KEY` — API key for the `x-apikey` header
- `SENSORPRO_ORG` — organization code/name
- `SENSORPRO_USER` — API username (**must be an API user**)
- `SENSORPRO_PASS` — API user password

### How to get the API key
From the Sensorpro UI:
1) Go to **API → API keys**
2) Select **“Sensorpro rest API default key”**
3) Copy the key value into `SENSORPRO_API_KEY`
4) If your API key is IP-restricted, whitelist the **calling IP** (the machine running OpenClaw)

The key is passed as an HTTP header:
- `x-apikey: $SENSORPRO_API_KEY`

### How to create an API user
Sensorpro distinguishes between UI users and API users:
- **API users** have *no UI access* but **can** use the REST API.
- **Normal users** have UI access but typically **cannot** use the REST API.

Create a dedicated **API user** in Sensorpro and set:
- `SENSORPRO_USER` to that username
- `SENSORPRO_PASS` to that password

### Safe secret handling (important)
- Put secrets in `~/.openclaw/.env` (or your process manager), **not** in `SKILL.md`.
- Don’t commit `.env` to git.
- Rotate the API key if it’s ever pasted into a public place.

## Global gotchas
- **IP allowlisting**: Sensorpro REST API can be locked to whitelisted IPs.
- Every response includes `Result.TotalErrors`; treat `0` as success.
- **Signin token** (`Token`) must be used in the URL path for most endpoints.
- **Logoff**: server may require a body (HTTP 411 otherwise). Use `-d '{}'`.

## Quick workflow pattern (recommended)
1) Signin once → store `TOKEN`
2) Make one or more API calls
3) Logoff

Example (bash):
```bash
TOKEN=$(curl -sS -X POST "https://apinie.sensorpro.net/auth/sys/signin" \
  -H "Content-Type: application/json" \
  -H "x-apikey: ${SENSORPRO_API_KEY}" \
  -d "{\"Organization\":\"${SENSORPRO_ORG}\",\"User\":\"${SENSORPRO_USER}\",\"Password\":\"${SENSORPRO_PASS}\"}" \
| python3 -c 'import sys,json; print(json.load(sys.stdin).get("Token",""))')

# Call an endpoint (example)
curl -sS -X POST "https://apinie.sensorpro.net/api/Contact/UpdateAdd/${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"AddToList":[],"Contact":[{"PersonalEMail":"someone@example.com"}],"Options":{"Parameters":{},"Action":""},"ReturnFailedRequests":false,"UpdateByKey":"email","SendWelcomeEmail":false,"SignupFormId":"00000000-0000-0000-0000-000000000000"}'

# Log off (some servers require a body)
curl -sS -X POST "https://apinie.sensorpro.net/auth/sys/logoff/${TOKEN}" \
  -H "Content-Type: application/json" -d '{}'
```

---

# Core endpoints (cheat sheet)

## Authentication
- `POST https://apinie.sensorpro.net/auth/sys/signin`  (header `x-apikey` required)
- `POST https://apinie.sensorpro.net/auth/sys/logoff/[Token]`

## Contacts (token required)
Base: `https://apinie.sensorpro.net/api/Contact/<Endpoint>/[Token]`
- `UpdateAdd` (recommended)
- `Add`, `Update`
- `GetContacts`, `GetContactsPaged`
- `UpdateAddAsync`, `GetUpdateAddAsyncStatus`
- `ChangeStatus`, `ChangeOptOutStatus`
- `DeleteContacts`, `ForgetMe`

## Campaigns + sending
Base: `https://apinie.sensorpro.net/api/campaign/<Endpoint>/[Token]` (note casing differs for some Get endpoints)
- `AddCampaign`, `AddDesign`, `AddSegment`, `AddBroadcast`

## Campaign results / metrics
- `POST https://apinie.sensorpro.net/api/Campaign/GetBroadcastStatus/[Token]`
- `POST https://apinie.sensorpro.net/api/campaign/GetCampaignResults/[Token]`
- `POST https://apinie.sensorpro.net/api/campaign/GetCampaignResultsLinks/[Token]`

## Relay Email
- `POST https://apinie.sensorpro.net/api/Email/SendEmail/[Token]`

## Imports
- `POST https://apinie.sensorpro.net/api/import/ExecuteFTPImport/[Token]`
- `POST https://apinie.sensorpro.net/api/import/GetImportStatus/[Token]`
- `POST https://apinie.sensorpro.net/api/import/ClearTagList/[Token]`

## Account
- `POST https://apinie.sensorpro.net/api/Account/AddSubOrganization/[Token]`
- `POST https://apinie.sensorpro.net/api/Account/AddUpdateUser/[Token]`

---

# Examples

## Signin (manual curl)
```bash
curl -sS -X POST "https://apinie.sensorpro.net/auth/sys/signin" \
  -H "Content-Type: application/json" \
  -H "x-apikey: ${SENSORPRO_API_KEY}" \
  -d '{"Organization":"'"${SENSORPRO_ORG}"'","User":"'"${SENSORPRO_USER}"'","Password":"'"${SENSORPRO_PASS}"'"}'
```

## Contacts: UpdateAdd (add/update by email)
```bash
curl -sS -X POST "https://apinie.sensorpro.net/api/Contact/UpdateAdd/${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "AddToList": [],
    "Contact": [{"PersonalEMail":"someone@example.com","FirstName":"","LastName":""}],
    "Options":{"Parameters":{},"Action":""},
    "ReturnFailedRequests": true,
    "UpdateByKey": "email",
    "SendWelcomeEmail": false,
    "SignupFormId": "00000000-0000-0000-0000-000000000000"
  }'
```

## Campaign metrics: GetCampaignResults
```bash
curl -sS -X POST "https://apinie.sensorpro.net/api/campaign/GetCampaignResults/${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"CampaignId": 53}'
```

## Relay: SendEmail (one-off)
```bash
curl -sS -X POST "https://apinie.sensorpro.net/api/Email/SendEmail/${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "From": {"DisplayName":"Marketing","Email":"marketing@myco.net"},
    "To": [{"DisplayName":"","Email":"recipient@example.com"}],
    "Cc": [],
    "Bcc": [],
    "Headers": {},
    "ReplyTo": null,
    "ReturnPath": null,
    "Subject": "Hello",
    "HTMLMessageStyle": "",
    "HTMLMessageEncoded": "<html><body><p>Hello</p></body></html>",
    "PlainTextMessage": "Hello",
    "MsgType": 0,
    "MailEncoding": "UTF8",
    "Schedule": {"DelayByMinutes": 0, "DelayUntilUTC": ""}
  }'
```