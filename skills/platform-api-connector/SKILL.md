---
name: platform-api-connector
description: Connect to social media and content platform APIs by navigating developer portals, creating apps, obtaining OAuth tokens, and storing credentials. Covers Facebook Graph API, Instagram Business API, YouTube Data API, Twitter/X API v2, and TikTok Content Posting API. Use when setting up API access for any social platform, refreshing expired OAuth tokens, or debugging authentication flows.
---

# Platform API Connector

Navigate developer portals and obtain API credentials for social/content platforms. Store credentials in Supabase (or any DB) for reuse.

## General Pattern

1. Create developer app on platform's developer portal
2. Configure OAuth redirect URIs and scopes
3. Complete OAuth flow (or generate API keys)
4. Store credentials in structured format
5. Test with a simple API call

## Facebook + Instagram

Facebook and Instagram share the same auth system. One Facebook Page Token unlocks both.

### Setup
1. Go to `developers.facebook.com/apps` → Create App → Business type
2. Add "Facebook Login" product
3. In Graph API Explorer (`developers.facebook.com/tools/explorer/`):
   - Select your app
   - Add permissions: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`
   - Generate User Access Token → authorize
   - Exchange for long-lived token: `GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={secret}&fb_exchange_token={short_token}`
4. Get Page Access Token: `GET /me/accounts` → find page → copy `access_token`
5. Get Instagram Business Account ID: `GET /{page_id}?fields=instagram_business_account`

### Store
```json
{
  "platform": "facebook",
  "credentials": {
    "app_id": "...",
    "app_secret": "...",
    "page_id": "...",
    "page_access_token": "...",
    "ig_user_id": "..."
  }
}
```

### Key gotcha
Page Access Tokens from Graph API Explorer are **short-lived** unless you exchange the User Token for a long-lived one FIRST, then request Page tokens from the long-lived User Token. Page tokens derived from long-lived user tokens are **permanent** (no expiry).

## YouTube

### Setup
1. Go to `console.cloud.google.com` → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Web application type)
3. Add redirect URI: `http://localhost:8422/callback` (or your callback URL)
4. Enable YouTube Data API v3
5. Run local OAuth flow:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly']
)
creds = flow.run_local_server(port=8422)
# creds.token, creds.refresh_token, creds.expiry
```

### Store
```json
{
  "platform": "youtube",
  "credentials": {
    "client_id": "...",
    "client_secret": "...",
    "access_token": "...",
    "refresh_token": "...",
    "token_expiry": "..."
  }
}
```

### Key gotcha
If the user previously authorized with limited scopes, the refresh token may not cover `youtube.upload`. Must re-authorize with `prompt='consent'` to get a new refresh token with full scopes.

## Twitter/X

### Setup
1. Go to `developer.x.com/en/portal/dashboard`
2. Create Project + App (Free tier: 100 posts/month)
3. Under Keys and Tokens:
   - API Key + Secret (consumer credentials)
   - Bearer Token (app-only auth for reading)
   - Access Token + Secret (user auth for posting) — generate with Read & Write permissions
4. If permissions were Read Only when tokens were generated, **regenerate** Access Token after changing to Read & Write

### Store
```json
{
  "platform": "twitter",
  "credentials": {
    "api_key": "...",
    "api_secret": "...",
    "bearer_token": "...",
    "access_token": "...",
    "access_token_secret": "..."
  }
}
```

### Key gotcha
Free tier caps at **100 posts/month** (resets on billing date, not calendar month). No delete or analytics on free tier.

## TikTok

### Setup
1. Go to `developers.tiktok.com` → Create App
2. Add products: Login Kit + Content Posting API
3. Configure: app icon (1024x1024), category, ToS URL, Privacy Policy URL, redirect URI
4. **Submit for review** — TikTok requires demo video showing the app in action
5. Until approved, use **Manual mode** (generate content but post manually)

### Key gotcha
TikTok Content Posting API requires **full app review with demo video**. This takes days to weeks. Plan for Manual mode as interim solution. Login Kit can work in sandbox mode for development.

## Credential Storage Pattern

Use a single table with JSONB for flexibility:

```sql
CREATE TABLE platform_connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform TEXT NOT NULL,
  account_name TEXT,
  credentials JSONB NOT NULL,
  scopes TEXT[],
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

JSONB accommodates different auth shapes per platform without schema changes.

## Token Refresh Pattern

```python
async def get_valid_token(platform: str) -> dict:
    conn = await get_connection(platform)
    creds = conn['credentials']
    
    if platform == 'youtube' and is_expired(creds.get('token_expiry')):
        new_token = refresh_google_token(creds['refresh_token'], creds['client_id'], creds['client_secret'])
        creds['access_token'] = new_token
        await update_connection(conn['id'], creds)
    
    # Facebook page tokens don't expire (if derived from long-lived user token)
    # Twitter tokens don't expire
    # TikTok tokens expire in 24h — refresh with refresh_token
    
    return creds
```
