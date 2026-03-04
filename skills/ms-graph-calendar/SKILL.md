---
name: ms-graph-calendar
description: Find available meeting times and free/busy slots for company employees using Microsoft Graph API. Use when user asks to schedule a meeting, find a free slot, check when employees are available, or look up someone's calendar availability.
version: 1.0.0
metadata: {"openclaw": {"emoji": "📅", "requires": {"env": ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"], "bins": ["node", "curl"]}, "primaryEnv": "AZURE_CLIENT_SECRET"}}
---

# Microsoft Graph Calendar — Find Free Slots

Use this skill when the user wants to:
- Find a time when multiple employees are all free
- Check if a specific person is available at a given time
- List upcoming meetings / busy blocks for one or more people
- Suggest meeting slots across the company

## Setup (ทำครั้งแรกครั้งเดียว)

ถ้าผู้ใช้ยังไม่เคย setup หรือระบบแจ้งว่าขาด credentials ให้ทำดังนี้:

1. ถามผู้ใช้ 3 ค่านี้ทีละค่า:
   - AZURE_TENANT_ID (Azure Portal → Azure Active Directory → Overview)
   - AZURE_CLIENT_ID (App registrations → your app → Application (client) ID)
   - AZURE_CLIENT_SECRET (App registrations → your app → Certificates & secrets)

2. เมื่อได้ครบแล้ว รันคำสั่ง:
```bash
node skills/ms-graph-calendar/scripts/setup.js \
  --tenant-id <AZURE_TENANT_ID> \
  --client-id <AZURE_CLIENT_ID> \
  --client-secret <AZURE_CLIENT_SECRET>
```

ค่าจะถูกบันทึกไว้ที่ `~/.openclaw/ms-graph-calendar.json` (permission 600) และจะถูกโหลดอัตโนมัติทุกครั้งที่ใช้ skill

3. ทดสอบด้วย:
```bash
node skills/ms-graph-calendar/scripts/get-token.js
```
ถ้าได้ "✅ Token acquired" แปลว่าพร้อมใช้งานแล้ว

**App Registration ต้องมี Application Permissions:**
- `Calendars.Read` — read all users' calendars
- `User.Read.All` — list employees
- Admin ต้อง Grant consent ก่อน

---

## Configuration

Authentication is cached after first login. No environment variables required for device code flow.

For headless/automated operation, set these environment variables:
- AZURE_CLIENT_ID - Azure AD app client ID
- AZURE_CLIENT_SECRET - Azure AD app secret
- AZURE_TENANT_ID - Tenant ID (use "consumers" for personal accounts)


---

## Tools

This skill runs Node.js scripts via bash. Files:
- `scripts/` — Node.js scripts
- `nicknames.md` — ตาราง mapping ชื่อเล่น → email (แก้ไขได้เลย)

---

## Instructions

### Step 1 — Get Access Token
Before any Graph API call, get an app-only token:
```bash
node skills/ms-graph-calendar/scripts/get-token.js
```
Store the token in a temp variable for subsequent calls.

### Step 2 — Parse the User's Request
Extract from the user's message:
- **Who**: names or emails of attendees (e.g. "Alice and Bob", "the marketing team")
- **When**: date range to search (e.g. "this week", "next Monday", "March 5–7")
- **Duration**: how long the meeting should be (default 60 minutes)
- **Timezone**: default to `Asia/Bangkok` if not specified

If any info is missing, ask the user before proceeding.

### Step 3 — Resolve Employee Emails

**3a. ลองแปลงชื่อเล่นก่อน** (เร็วกว่า ไม่ต้องเรียก API):
```bash
node skills/ms-graph-calendar/scripts/resolve-nicknames.js --names "แบงค์,มิ้ว,โบ้"
```
อ่านจาก `nicknames.md` ในโฟลเดอร์ skill — แก้ไขได้ตรงนั้นเลย

**3b. ถ้าหาไม่เจอใน nicknames.md** ให้ fallback ไปค้น Graph API:
```bash
node skills/ms-graph-calendar/scripts/list-users.js --search "ชื่อ"
```
Confirm กับ user ถ้ามีคนชื่อเดียวกันหลายคน

### Step 4 — Find Free Slots (choose one method)

**Method A — findMeetingTimes** (best for small groups, ≤10 people):
```bash
node skills/ms-graph-calendar/scripts/find-meeting-times.js \
  --attendees "alice@company.com,bob@company.com" \
  --start "2025-03-01T08:00:00" \
  --end "2025-03-01T18:00:00" \
  --duration 60 \
  --timezone "Asia/Bangkok" \
  --max 5
```

**Method B — getSchedule** (best for large groups or viewing free/busy blocks):
```bash
node skills/ms-graph-calendar/scripts/get-schedule.js \
  --emails "alice@company.com,bob@company.com,carol@company.com" \
  --start "2025-03-01T00:00:00" \
  --end "2025-03-07T00:00:00" \
  --timezone "Asia/Bangkok" \
  --interval 30
```

### Step 5 — Present Results

Format the available slots clearly:
```
📅 Available slots where everyone is free:

1. Monday 3 Mar · 10:00–11:00
2. Tuesday 4 Mar · 14:00–15:00
3. Wednesday 5 Mar · 09:00–10:00

Which slot works best?
```

If no slots are found, widen the search window and try again, or report that no common availability exists in that period.

---

## Example Conversations

**User:** "Find a 1-hour slot this week where Alice, Bob, and Carol are all free"
**Agent:**
1. Resolves emails for Alice, Bob, Carol
2. Runs `find-meeting-times.js` with date range = this Mon–Fri
3. Returns top 3 available slots

**User:** "Is John free tomorrow afternoon?"
**Agent:**
1. Resolves John's email
2. Runs `get-schedule.js` for tomorrow 12:00–18:00
3. Reports free/busy blocks

**User:** "Show me everyone in the marketing team's availability next week"
**Agent:**
1. Lists users in the Marketing group via `list-users.js --group "Marketing"`
2. Runs `get-schedule.js` for all their emails
3. Presents a visual free/busy summary

---

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Token expired or wrong credentials | Re-run `get-token.js`, check env vars |
| `403 Forbidden` | Missing Admin Consent | Ask IT admin to grant consent in Azure Portal |
| `404 Not Found` | User email doesn't exist | Verify email via `list-users.js` |
| No slots found | Everyone is busy | Widen time range or reduce attendees |

---

## Security Notes

- Credentials are read from env vars only — never log or echo them
- This skill has **read-only** access to calendars (`Calendars.Read`)
- It cannot create, edit, or delete any events
- To restrict which mailboxes the app can read, ask your IT admin to set an **App Access Policy** in Exchange Online:
  ```powershell
  New-ApplicationAccessPolicy -AppId <ClientId> -PolicyScopeGroupId <GroupId> -AccessRight RestrictAccess
  ```
