# App Store Connect API — Setup Guide

Complete setup guide for authenticating ReviewReply with the App Store Connect API. You'll need an API key to fetch reviews and post replies.

---

## Overview

App Store Connect uses **JWT-based authentication** with ES256-signed tokens. Each API request requires a `Bearer` token generated from:
- A **private key** (`.p8` file)
- A **Key ID** (shown in App Store Connect)
- An **Issuer ID** (your team's issuer UUID)

Tokens expire after 20 minutes — the scripts generate a fresh one per run.

---

## Step 1: Create an API Key

1. Sign in to [App Store Connect](https://appstoreconnect.apple.com)
2. Navigate to **Users and Access** → **Integrations** → **App Store Connect API**
3. Click **Generate API Key** (or the `+` button)
4. Fill in:
   - **Name:** `ReviewReply` (or any label)
   - **Access:** `Customer Support` (minimum required)
     > For posting replies you need at least **App Manager** or **Customer Support** role
5. Click **Generate**

> ⚠️ **Download the `.p8` file immediately.** Apple only shows it once. If you lose it, you must revoke and generate a new key.

---

## Step 2: Note Your Credentials

After creating the key, record three values:

| Value | Where to Find | Example |
|-------|--------------|---------|
| **Key ID** | Shown in the key list | `ABC123DEF4` |
| **Issuer ID** | Top of the API Keys page | `69a6de70-xxxx-xxxx-xxxx-xxxxxxxxxx` |
| **Private Key** | Downloaded `.p8` file | `AuthKey_ABC123DEF4.p8` |

---

## Step 3: Store the Private Key

Move the `.p8` file to a secure location. Recommended:

```bash
mkdir -p ~/.appstoreconnect/keys
mv ~/Downloads/AuthKey_ABC123DEF4.p8 ~/.appstoreconnect/keys/
chmod 600 ~/.appstoreconnect/keys/AuthKey_ABC123DEF4.p8
```

---

## Step 4: Set Environment Variables

Add these to your shell profile (`~/.zshrc` or `~/.bash_profile`):

```bash
# App Store Connect API
export APP_STORE_KEY_ID="ABC123DEF4"
export APP_STORE_ISSUER_ID="69a6de70-xxxx-xxxx-xxxx-xxxxxxxxxx"
export APP_STORE_PRIVATE_KEY_PATH="$HOME/.appstoreconnect/keys/AuthKey_ABC123DEF4.p8"
```

Or add to `~/.openclaw/.env`:
```
APP_STORE_KEY_ID=ABC123DEF4
APP_STORE_ISSUER_ID=69a6de70-xxxx-xxxx-xxxx-xxxxxxxxxx
APP_STORE_PRIVATE_KEY_PATH=/Users/nick/.appstoreconnect/keys/AuthKey_ABC123DEF4.p8
```

Reload your shell:
```bash
source ~/.zshrc
```

---

## Step 5: Install Python Dependencies

The monitor and queue manager scripts require `PyJWT` and `cryptography`:

```bash
pip3 install PyJWT cryptography
```

Verify:
```bash
python3 -c "import jwt; print('JWT OK')"
```

---

## Step 6: Test Authentication

Run the monitor in dry-run mode to verify auth works:

```bash
cd /Users/nick/.openclaw/workspace
python3 skills/review-reply/scripts/monitor.py --dry-run
```

Expected output:
```
🔑 Authenticating with App Store Connect...
  ✅ JWT token generated
```

---

## API Endpoints Used

ReviewReply uses these App Store Connect API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/apps/{id}/customerReviews` | GET | Fetch reviews for an app |
| `/v1/customerReviews/{id}/response` | GET | Check if response exists |
| `/v1/customerReviewResponses` | POST | Post a reply |
| `/v1/customerReviewResponses/{id}` | DELETE | Delete existing reply |

### Fetch Reviews — Query Parameters

```
GET /v1/apps/{appId}/customerReviews

Parameters:
  limit=200                          Max results per page (Apple max: 200)
  sort=-createdDate                  Newest first
  cursor=<token>                     Pagination cursor
  fields[customerReviews]=...        Fields to return
  filter[rating]=1,2,3               Filter by star rating (optional)
  filter[territory]=USA              Filter by territory (optional)
```

### Post a Reply

```
POST /v1/customerReviewResponses

Body:
{
  "data": {
    "type": "customerReviewResponses",
    "attributes": {
      "responseBody": "Your reply text here"
    },
    "relationships": {
      "review": {
        "data": {
          "type": "customerReviews",
          "id": "<review_id>"
        }
      }
    }
  }
}
```

### Rate Limits

Apple's API has rate limits. As of 2026:
- Default: **~3,500 requests per hour**
- No official published limit — monitor for `429 Too Many Requests`
- ReviewReply includes automatic backoff on 429 responses

---

## Multiple Apps

To monitor multiple apps, each app needs its App ID from App Store Connect or the App Store URL.

| App | How to Find App ID |
|-----|-------------------|
| FeedFare | Already configured: `6758923557` |
| Others | App Store URL: `apps.apple.com/app/id{APP_ID}` |

App IDs are added to the `APPS` list in `scripts/monitor.py`:

```python
APPS = [
    {"name": "FeedFare",         "id": "6758923557"},
    {"name": "Inflection Point", "id": "YOUR_APP_ID"},
    {"name": "PetFace",          "id": "YOUR_APP_ID"},
]
```

---

## Troubleshooting

### "Missing App Store Connect credentials"
→ Verify environment variables are set: `echo $APP_STORE_KEY_ID`

### "Private key not found"
→ Check the path: `ls -la $APP_STORE_PRIVATE_KEY_PATH`

### JWT error "Invalid private key"
→ Ensure the `.p8` file is the original — not copy-pasted (line endings can corrupt it)

### API 401 Unauthorized
→ Check that Key ID and Issuer ID match what's in App Store Connect exactly
→ Verify the key hasn't been revoked: App Store Connect → Users & Access → API Keys

### API 403 Forbidden
→ The key doesn't have Customer Support or App Manager role
→ Revoke and create a new key with the correct permissions

### API 409 Conflict when posting reply
→ A response already exists — the script will attempt to delete it first
→ If it persists, check App Store Connect directly

---

## Security Notes

- Never commit the `.p8` file to git
- Add to `.gitignore`: `*.p8`, `~/.appstoreconnect/`
- The JWT token expires after 20 min — scripts regenerate as needed
- Rotate keys annually or if compromised: App Store Connect → Revoke Key
