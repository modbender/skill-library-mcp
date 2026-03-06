---
name: picsee-short-link
description: Shorten URLs using PicSee (pse.is). Stores API token in skills/picsee-short-link/config.json (optional). Use when the user asks to shorten a URL, create a short link, or mentions PicSee. Supports both unauthenticated mode (basic shortening) and authenticated mode (analytics, editing, search, custom thumbnails for Advanced plan users).
metadata:
  {
    "openclaw":
      {
        "emoji": "🔗",
        "configPaths": ["skills/picsee-short-link/config.json"],
        "requires": { "bins": ["curl", "jq"] },
        "externalApis": ["api.pics.ee", "chrome-ext.picsee.tw", "api.qrserver.com", "quickchart.io"],
        "writesPaths": ["/tmp/*.png", "skills/picsee-short-link/config.json"]
      }
  }
---

# PicSee Short Link

Quick URL shortener with optional analytics.

## Security & Scope

This skill performs the following operations:

**File operations:**
- Reads/writes `skills/picsee-short-link/config.json` (stores API token in plaintext, optional)
- Writes QR code images to `/tmp/<shortcode>.png` (only if user requests QR)
- Writes analytics charts to `/tmp/<encodeId>_analytics.png` (only if user requests visualization)

**Network operations:**
- HTTPS API calls to `api.pics.ee` (authenticated mode, PicSee API)
- HTTPS API calls to `chrome-ext.picsee.tw` (unauthenticated mode, PicSee API)
- HTTPS API calls to `api.qrserver.com` (QR code generation, optional)
- HTTPS API calls to `quickchart.io` (chart generation, optional)

**Security notes:**
- API token is stored in plaintext in workspace config file (not system-wide)
- All API calls use HTTPS
- No data is sent to third parties except PicSee API and user-requested QR/chart services
- Token is never logged or transmitted except to PicSee API

**Scope:**
Core function is URL shortening. Analytics, QR codes, and charts are optional features that require explicit user request. 

## Fast Track: Shorten a URL

**For 99% of requests, use this workflow:**

1. **Check config**: Read `skills/picsee-short-link/config.json`
   - If **NOT exist** → Go to **First-Time Setup** (see below)
   - If **exists** → Check `status` field and proceed

2. **Call API**:
   - **Unauthenticated** (no token):
     ```bash
     curl -X POST https://chrome-ext.picsee.tw/v1/links \
       -H "Content-Type: application/json" \
       -d '{"url":"<LONG_URL>","domain":"pse.is","externalId":"openclaw"}'
     ```
   
   - **Authenticated** (has token):
     ```bash
     # Read token from config.json first
     TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
     
     curl -X POST https://api.pics.ee/v1/links \
       -H "Authorization: Bearer $TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"url":"<LONG_URL>","domain":"pse.is","externalId":"openclaw"}'
     ```
     (Token stored in `config.json` → `apiToken` field)

3. **Display result** (code block for easy copying):
   ```text
   https://pse.is/abc123
   ```
   Then ask user if they want a QR code? if user is unauthenticated, also ask if they want to add their API token for analytics/editing features.

4. **QR code** (ONLY if user explicitly asks):
   ```bash
   curl -o /tmp/qrcode.png "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=<SHORT_URL>"
   ```
   Then send via `message` tool with `filePath:"/tmp/qrcode.png"`

**Done.** No need to ask about analytics unless user requests them.

---

## First-Time Setup (if no config exists)

**Detection**: Check if `skills/picsee-short-link/config.json` exists. If NOT exist → first-time user.

**Ask user** (explain features):

> "Would you like to provide a PicSee API token to unlock advanced features? (y/n)
> 
> **With token (authenticated mode), you can:**
> - View link analytics and daily click stats
> - List your short links (filter by date range)
> - Search short links
> - Edit links (change destination URL) — **Advanced plan only**
> - Customize thumbnails/titles — **Advanced plan only**
> 
> **Without token (unauthenticated mode), you can:**
> - Create basic short links (no analytics)
> 
> **To get your API token:**
> Go to https://picsee.io/ → Click avatar (top-right) → Settings → API → Copy token"

**If user says YES**:

1. Wait for token (alphanumeric string, e.g., `abc123def456...`)

2. Create `skills/picsee-short-link/config.json`:
   ```json
   {
     "status": "authenticated",
     "apiToken": "<user_token>",
     "setupDate": "YYYY-MM-DD"
   }
   ```

3. Verify token by calling API status:
   ```bash
   TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
   curl -X GET https://api.pics.ee/v2/my/api/status \
     -H "Authorization: Bearer $TOKEN"
   ```

4. Show user their plan tier (free/basic/advanced) and quota info.

**If user says NO**:

1. Create `skills/picsee-short-link/config.json`:
   ```json
   {
     "status": "unauthenticated",
     "setupDate": "YYYY-MM-DD"
   }
   ```

2. Explain: "You can create short links in unauthenticated mode. To unlock analytics/editing later, just ask me to add your API token."

---

## Advanced Features (Authenticated Mode Only)

### View Link Analytics

Extract `encodeId` from short URL (e.g., `pse.is/abc123` → `abc123`), then:

```bash
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
curl -X GET "https://api.pics.ee/v1/links/<ENCODE_ID>/overview?dailyClicks=true" \
  -H "Authorization: Bearer $TOKEN"
```

**Response includes:**
- `totalClicks`, `uniqueClicks`
- `dailyClicks` array (date + click counts)

**Generate chart** (if user asks for visualization):

1. Extract daily clicks data from API response using jq
2. Build QuickChart URL with chart config (line chart, total/unique clicks over time)
3. Download chart image

**Example:**
```bash
# After getting API response, parse data and generate chart
ENCODE_ID="abc123"
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)

# Fetch analytics
RESPONSE=$(curl -s -X GET "https://api.pics.ee/v1/links/$ENCODE_ID/overview?dailyClicks=true" \
  -H "Authorization: Bearer $TOKEN")

# Parse dates and clicks (example - adjust based on actual response structure)
DATES=$(echo "$RESPONSE" | jq -r '.data.dailyClicks[].date' | jq -R -s -c 'split("\n")[:-1]')
TOTAL=$(echo "$RESPONSE" | jq -r '.data.dailyClicks[].totalClicks' | jq -s -c '.')
UNIQUE=$(echo "$RESPONSE" | jq -r '.data.dailyClicks[].uniqueClicks' | jq -s -c '.')

# Build QuickChart config (URL-encoded JSON)
CHART_CONFIG=$(cat <<EOF | jq -R -s -c '@uri'
{
  "type": "line",
  "data": {
    "labels": $DATES,
    "datasets": [
      {
        "label": "Total Clicks",
        "data": $TOTAL,
        "borderColor": "rgb(75, 192, 192)",
        "fill": false
      },
      {
        "label": "Unique Clicks",
        "data": $UNIQUE,
        "borderColor": "rgb(255, 99, 132)",
        "fill": false
      }
    ]
  },
  "options": {
    "title": {
      "display": true,
      "text": "Link Analytics - $ENCODE_ID"
    },
    "scales": {
      "yAxes": [{
        "ticks": {
          "beginAtZero": true
        }
      }]
    }
  }
}
EOF
)

# Download chart
curl -o "/tmp/${ENCODE_ID}_analytics.png" "https://quickchart.io/chart?c=$CHART_CONFIG"
```

4. Send chart via `message` tool with `filePath: "/tmp/<encodeId>_analytics.png"`

---

### List Recent Links

```bash
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
curl -X POST "https://api.pics.ee/v2/links/overview?isAPI=false&limit=50&startTime=<ISO8601_DATE>" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Date format**: `YYYY-MM-DDTHH:MM:SS` (no timezone suffix)

**⚠️ IMPORTANT: startTime Parameter Behavior**

The `startTime` parameter **FILTERS results backwards from that timestamp**. It returns links created **on or before** the specified date, in reverse chronological order (newest first).

**Examples:**

- **To query December 2025**:
  - Use: `startTime=2025-12-31T23:59:59` (last day of month, not first!)
  - This returns all links up to Dec 31, including Dec 1–31
  
- **To query a specific month**:
  - Use the **LAST DAY** of that month at `23:59:59`
  - December → `2025-12-31T23:59:59`
  - January → `2026-01-31T23:59:59`

- **To query a specific date range**:
  - Use `startTime` = **end date of range**
  - Combine with `limit` to control how many results returned
  - Adjust limit if you need older entries

**Common mistake**: Using the **first day** of a month will miss data from that month.

---

### Check Plan Tier

```bash
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
curl -X GET https://api.pics.ee/v2/my/api/status \
  -H "Authorization: Bearer $TOKEN"
```

**Plan values**: `"free"`, `"basic"`, `"advanced"`

**Feature restrictions**:
- **Free/Basic**: Create links, view analytics, list links
- **Advanced only**: Edit links, custom thumbnails/titles, UTM params, tracking pixels

---

### Edit Short Link (Advanced plan only)

```bash
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
curl -X PUT https://api.pics.ee/v2/links/<ENCODE_ID> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"<NEW_DESTINATION_URL>"}'
```

**If user is NOT on Advanced plan**: Block and suggest creating a new link instead.

---

### Delete Short Link

```bash
TOKEN=$(jq -r '.apiToken' ~/.openclaw/workspace/skills/picsee-short-link/config.json)
curl -X POST https://api.pics.ee/v2/links/<ENCODE_ID>/delete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value":"delete"}'
```

(Use `"recover"` to restore)

---

## Mode Summary

| Mode | Base URL | Auth Required | Features |
|------|----------|---------------|----------|
| **Unauthenticated** | `chrome-ext.picsee.tw` | No | Create links only |
| **Authenticated** | `api.pics.ee` | Yes | Create + analytics + list + edit (plan-dependent) |

**Default**: Unauthenticated (fastest, no setup).

---

## Output Guidelines

- **Short URLs**: Always in code blocks for easy copying
- **Language**: All responses in user's language
- **No jargon**: Avoid "API call", "endpoint", "JSON" in user-facing messages
- **Charts**: English labels, professional styling, save to `/tmp/` and send via `message` tool

---

## Quick Reference

**Token location**: `skills/picsee-short-link/config.json` → `apiToken` field  
**Config location**: `skills/picsee-short-link/config.json`  
**Default domain**: `pse.is`  
**externalId**: Always `openclaw`

---

## Error Handling

- **Unauthenticated mode + user requests analytics**: Reply: "This feature requires login. Provide your PicSee API token to unlock it."
- **Non-Advanced plan + user requests edit**: Reply: "Editing links requires the Advanced plan. You can create a new link instead."
- **Invalid token**: Reply: "Invalid API token. Get a new one from https://picsee.io/ → Settings → API"
