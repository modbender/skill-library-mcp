# Postiz Setup Guide (Self-Hosted)

Postiz is 100% free and self-hosted. You own your data. Great for technical users who want full control — no per-channel limits, no monthly fees, and your posts never touch a third-party server.

**GitHub:** [https://github.com/gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app)  
**Docs:** [https://docs.postiz.com](https://docs.postiz.com)

---

## What Postiz Supports

- **Platforms:** X/Twitter, LinkedIn, Instagram, Facebook, TikTok, Pinterest, YouTube, Reddit, Mastodon, Threads, Bluesky, Discord, Dribbble
- **Features:** Post scheduling, media uploads, calendar view, team collaboration, analytics, AI writing assistant
- **API:** Full public REST API at `/api/public/v1/`
- **License:** Open-source (Apache 2.0)

---

## Step 1: Prerequisites

You need:
- A Linux server or VPS (1 vCPU, 1GB RAM minimum — 2GB recommended)
- Docker and Docker Compose installed
- A domain name pointed at your server (for SSL and OAuth callbacks)

```bash
# Check Docker is installed
docker --version
docker compose version
```

If not installed:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
```

---

## Step 2: Clone and Configure

```bash
# Clone the repo
git clone https://github.com/gitroomhq/postiz-app.git
cd postiz-app

# Copy the example env file
cp .env.example .env
```

Edit `.env` with your values:

```bash
nano .env
```

Key environment variables to set:

```env
# App
MAIN_URL=https://postiz.yourdomain.com
FRONTEND_URL=https://postiz.yourdomain.com
NEXT_PUBLIC_BACKEND_URL=https://postiz.yourdomain.com/api

# Database (leave defaults if using Docker Compose)
DATABASE_URL=postgresql://postiz:postiz@postiz-postgres:5432/postiz

# Redis (leave defaults if using Docker Compose)
REDIS_URL=redis://postiz-redis:6379

# JWT Secret — generate a random string
JWT_SECRET=your_random_secret_here_min_32_chars

# Storage (local or S3)
STORAGE_PROVIDER=local
# For S3: STORAGE_PROVIDER=s3 (then fill AWS_* vars)

# Email (optional but recommended for auth)
EMAIL_PROVIDER=nodemailer
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USER=noreply@yourdomain.com
EMAIL_PASS=your_smtp_password
EMAIL_FROM=noreply@yourdomain.com
```

---

## Step 3: Start Postiz

```bash
# Start all services (Postiz + Postgres + Redis)
docker compose up -d

# Check logs
docker compose logs -f postiz
```

Postiz will be available at `http://localhost:5000` (or your configured port).

To expose via HTTPS with Nginx:

```nginx
server {
    listen 443 ssl;
    server_name postiz.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/postiz.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/postiz.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Get an SSL certificate:
```bash
certbot --nginx -d postiz.yourdomain.com
```

---

## Step 4: Create Your Account

1. Navigate to `https://postiz.yourdomain.com`
2. Register with your email
3. Verify email (if SMTP configured) or check the database for the verification link

---

## Step 5: Connect Social Accounts

Each platform requires OAuth app credentials. You'll set these up once in Postiz settings.

### X/Twitter

1. Go to [developer.twitter.com](https://developer.twitter.com) → Create project → Create app
2. Set OAuth 2.0 callback: `https://postiz.yourdomain.com/integrations/social/twitter`
3. Copy **Client ID** and **Client Secret** into `.env`:
   ```env
   TWITTER_CLIENT_ID=your_client_id
   TWITTER_CLIENT_SECRET=your_client_secret
   ```

### LinkedIn

1. Go to [linkedin.com/developers](https://www.linkedin.com/developers/) → Create app
2. Add OAuth redirect: `https://postiz.yourdomain.com/integrations/social/linkedin`
3. Request `w_member_social` permission
4. Add to `.env`:
   ```env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   ```

### Instagram / Facebook

1. Go to [developers.facebook.com](https://developers.facebook.com) → Create app (Business type)
2. Add "Instagram Graph API" and "Facebook Login" products
3. Set callback: `https://postiz.yourdomain.com/integrations/social/facebook`
4. Add to `.env`:
   ```env
   FACEBOOK_APP_ID=your_app_id
   FACEBOOK_APP_SECRET=your_app_secret
   ```

### TikTok

1. Go to [developers.tiktok.com](https://developers.tiktok.com) → Create app
2. Enable "Content Posting API"
3. Set redirect: `https://postiz.yourdomain.com/integrations/social/tiktok`
4. Add to `.env`:
   ```env
   TIKTOK_CLIENT_ID=your_client_key
   TIKTOK_CLIENT_SECRET=your_client_secret
   ```

After updating `.env`, restart:
```bash
docker compose restart postiz
```

Then in the Postiz UI: **Settings → Integrations → Connect** each platform.

---

## Step 6: Get Your API Key

1. In Postiz: **Settings → API Keys**
2. Click "Generate API Key"
3. Copy the key

Set in your environment:

```bash
export POSTIZ_API_KEY="your_api_key_here"
export POSTIZ_BASE_URL="https://postiz.yourdomain.com"
```

Or in `.env` (your project's env, not Postiz's):
```
POSTIZ_API_KEY=your_api_key_here
POSTIZ_BASE_URL=https://postiz.yourdomain.com
```

---

## Postiz API Reference

Base URL: `https://postiz.yourdomain.com/api/public/v1`

All requests require:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### List Connected Integrations (Channels)

```
GET /integrations
```

```bash
curl -H "Authorization: Bearer $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/api/public/v1/integrations"
```

Response:
```json
[
  {
    "id": "clx1234567890",
    "name": "@yourbrand",
    "type": "X",
    "picture": "https://..."
  },
  {
    "id": "clx0987654321",
    "name": "Your Brand",
    "type": "LINKEDIN",
    "picture": "https://..."
  }
]
```

### Create a Post

```
POST /posts
```

Body:
```json
{
  "type": "now",
  "date": "2026-02-25T14:00:00.000Z",
  "posts": [
    {
      "integration": { "id": "INTEGRATION_ID" },
      "value": [
        {
          "content": "Your post text here",
          "media": []
        }
      ],
      "settings": {}
    }
  ],
  "tags": [],
  "shortLink": false
}
```

`type` options: `"now"` (post immediately), `"schedule"` (use `date`), `"draft"`

```bash
curl -X POST "$POSTIZ_BASE_URL/api/public/v1/posts" \
  -H "Authorization: Bearer $POSTIZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "schedule",
    "date": "2026-02-25T14:00:00.000Z",
    "posts": [{
      "integration": { "id": "INTEGRATION_ID" },
      "value": [{ "content": "Your post text here", "media": [] }],
      "settings": {}
    }],
    "tags": [],
    "shortLink": false
  }'
```

### Get All Posts

```
GET /posts?page=1&limit=20
```

Optional filters: `?status=QUEUE` | `SENT` | `ERROR` | `DRAFT`

```bash
curl -H "Authorization: Bearer $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/api/public/v1/posts?status=QUEUE&limit=50"
```

### Delete a Post

```
DELETE /posts/:id
```

```bash
curl -X DELETE \
  -H "Authorization: Bearer $POSTIZ_API_KEY" \
  "$POSTIZ_BASE_URL/api/public/v1/posts/POST_ID"
```

### Upload Media

```
POST /media/upload
```

```bash
curl -X POST "$POSTIZ_BASE_URL/api/public/v1/media/upload" \
  -H "Authorization: Bearer $POSTIZ_API_KEY" \
  -F "file=@/path/to/image.jpg"
```

Response includes `path` field — use this as the media reference in post creation.

---

## API Wrapper Example (Quick Reference)

Here's a minimal wrapper to call from shell scripts:

```bash
#!/bin/bash
# postiz.sh — minimal Postiz API wrapper

BASE="$POSTIZ_BASE_URL/api/public/v1"
AUTH="Authorization: Bearer $POSTIZ_API_KEY"

postiz_list_channels() {
  curl -s -H "$AUTH" "$BASE/integrations" | jq '.[] | {id: .id, name: .name, type: .type}'
}

postiz_schedule_post() {
  local integration_id="$1"
  local content="$2"
  local date="$3"  # ISO8601, e.g. "2026-02-25T14:00:00.000Z"
  
  curl -s -X POST "$BASE/posts" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"schedule\",
      \"date\": \"$date\",
      \"posts\": [{
        \"integration\": {\"id\": \"$integration_id\"},
        \"value\": [{\"content\": \"$content\", \"media\": []}],
        \"settings\": {}
      }],
      \"tags\": [],
      \"shortLink\": false
    }"
}

postiz_draft() {
  local integration_id="$1"
  local content="$2"
  
  curl -s -X POST "$BASE/posts" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d "{
      \"type\": \"draft\",
      \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
      \"posts\": [{
        \"integration\": {\"id\": \"$integration_id\"},
        \"value\": [{\"content\": \"$content\", \"media\": []}],
        \"settings\": {}
      }],
      \"tags\": [],
      \"shortLink\": false
    }"
}

# Usage:
# postiz_list_channels
# postiz_schedule_post "clx1234567890" "Your post text" "2026-02-25T14:00:00.000Z"
# postiz_draft "clx1234567890" "Draft post content"
```

---

## Updating Postiz

```bash
cd postiz-app
git pull origin main
docker compose pull
docker compose up -d
```

---

## Troubleshooting

**Posts stuck in queue, not sending**
→ Check the worker container is running: `docker compose ps`. Restart if needed: `docker compose restart postiz-workers`

**OAuth callback failing**
→ Verify `MAIN_URL` in `.env` exactly matches the URL you set in the platform's developer dashboard (including `https://` and no trailing slash)

**API returns 401**
→ API key is wrong or the Authorization header format is off. Must be `Bearer YOUR_KEY` (with space)

**Can't upload media**
→ Check storage configuration. For local storage, ensure the `uploads` volume is writable. For S3, verify bucket permissions and `AWS_*` env vars.

**Instagram posts failing**
→ Instagram Graph API requires a Business or Creator account connected to a Facebook Page. Personal accounts cannot post via API.

---

## Postiz vs Buffer — When to Choose Which

| | Postiz (self-hosted) | Buffer |
|--|--|--|
| Cost | Free forever | Free for 3 channels |
| Setup time | 30-60 min | 5 min |
| Maintenance | You manage it | None |
| Data control | 100% yours | Buffer's servers |
| Analytics | Basic | Better on paid plans |
| Best for | Developers, privacy-conscious, no channel limits | Quick start, non-technical users |

If you're technical and posting to more than 3 platforms, Postiz is the better long-term setup. If you want to start posting in 5 minutes, use Buffer.
