---
name: repliz
description: Repliz social media management API integration. Use when working with Repliz to manage social media accounts, schedules, and comments. Requires REPLIZ_ACCESS_KEY and REPLIZ_SECRET_KEY environment variables.
homepage: https://repliz.com
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":["curl"],"env":["REPLIZ_ACCESS_KEY","REPLIZ_SECRET_KEY"]},"primaryEnv":"REPLIZ_ACCESS_KEY"}}
---

# Repliz API Skill

## Prerequisites & Setup

Before using this skill, you must complete the following setup steps:

### 1. Register/Login to Repliz
- **Register**: Visit https://repliz.com/register to create a new account
- **Login**: Visit https://repliz.com/login to sign in to your existing account

### 2. Connect Social Media Accounts
After logging in, connect your social media accounts:
- Go to your Repliz dashboard
- Add and connect accounts like **Instagram**, **Threads**, **TikTok**, **Facebook**, **LinkedIn**, or **YouTube**
- Ensure the accounts show as "connected" before proceeding

### 3. Obtain API Credentials
To get your Access Key and Secret Key for Basic Authentication:
1. Navigate to https://repliz.com/user/setting/api
2. Generate or copy your **Access Key** and **Secret Key**
3. Store these credentials securely - they grant access to post, delete, and manage your social media content

### 4. Configure Environment Variables
This skill requires the following environment variables to be set:

```bash
export REPLIZ_ACCESS_KEY="your-access-key-here"
export REPLIZ_SECRET_KEY="your-secret-key-here"

## Authentication

All API requests require **Basic Authentication** in the header:
- **Username**: $REPLIZ_ACCESS_KEY
- **Password**: $REPLIZ_SECRET_KEY
- **Base URL**: `https://api.repliz.com`

## API Endpoints

### Accounts

**GET /public/account**
- Query params: `page` (default 1), `limit` (default 10), `search` (optional)
- Returns list of connected social media accounts
- Fields: `_id`, `generatedId`, `name`, `username`, `picture`, `isConnected`, `type` (instagram/threads/tiktok/etc), `userId`, `createdAt`, `updatedAt`

**GET /public/account/{_id}**
- Get account details by ID (use `_id` field from account list)
- Returns full account info including `token.access` for posting

---

### Schedules

**GET /public/schedule**
- Query params: `page`, `limit`, `accountIds` (can be repeated)
- Returns scheduled posts

**GET /public/schedule/{_id}**
- Get schedule details by ID

**POST /public/schedule**
- Create new scheduled post. Request body varies by type:

Text post (Facebook, Threads):
```json
{
  "title": "",
  "description": "Your post text",
  "type": "text",
  "medias": [],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Image post (Facebook, Instagram, Threads, TikTok, LinkedIn):
```json
{
  "title": "",
  "description": "Caption",
  "type": "image",
  "medias": [{"type": "image", "thumbnail": "url", "url": "url", "alt": "description"}],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Video post (Facebook, Instagram, Threads, TikTok, YouTube, LinkedIn):
```json
{
  "title": "Hello there, this is from Repliz",
  "description": "Hello there, this is from Repliz",
  "type": "video",
  "medias": [
    {
      "type": "video",
      "thumbnail": "thumbnail-url",
      "url": "video-url"
    }
  ],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Album post (Facebook, Instagram, Threads, TikTok, LinkedIn):
```json
{
  "title": "Hello there, this is from Repliz",
  "description": "Hello there, this is from Repliz",
  "type": "album",
  "medias": [
    {
      "type": "image",
      "thumbnail": "thumbnail-url-1",
      "url": "image-url-1",
      "alt": "alt-image-1"
    },
    {
      "type": "image",
      "thumbnail": "thumbnail-url-2",
      "url": "image-url-2",
      "alt": "alt-image-2"
    },
    {
      "type": "image",
      "thumbnail": "thumbnail-url-99",
      "url": "image-url-99",
      "alt": "alt-image-99"
    },
  ],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Story post (Facebook, Instagram):
```json
{
  "title": "",
  "description": "",
  "type": "story",
  "medias": [
    {
      "type": "image or video", // you can choose
      "thumbnail": "thumbnail-url",
      "url": "media-url"
    }
  ],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Instagram post with additional info:
```json
{
  "title": "Hello there, this is from Repliz",
  "description": "Hello there, this is from Repliz",
  "type": "video",
  "medias": [
    {
      "type": "video",
      "thumbnail": "thumbnail-url",
      "url": "video-url"
    }
  ],
  "additionalInfo": {
    "collaborators": [
      "usernameCollab1",
      "usernameCollab2",
      "usernameCollab3"
    ]
  },
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e"
}
```

Nested/Thread post (Threads):
```json
{
  "title": "",
  "description": "First Post",
  "type": "text",
  "medias": [],
  "scheduleAt": "2026-02-14T10:35:09.658Z",
  "accountId": "680affa5ce12f2f72916f67e",
  "replies": [
    {"title": "", "description": "Second Post reply First Post", "type": "text", "medias": []},
    {"title": "", "description": "Third Post reply Second Post", "type": "text", "medias": []}
  ]
}
```

**DELETE /public/schedule/{_id}**
- Delete scheduled post (cannot be recovered)

---

### Comment Queue

**GET /public/queue**
- Query params: `page`, `limit`, `search`, `status` (pending/resolved/ignored), `accountIds` (can be repeated)
- Returns comment queue from social media

**GET /public/queue/{_id}**
- Get queue item details

**POST /public/queue/{_id}**
- Reply to comment (automatically marks as resolved)
```json
{
  "text": "Your reply"
}
```

---

## Error Handling

- `401`: Invalid authorization header
- `404`: Not found
- `500`: Internal server error

## Notes

- `accountId` for posting comes from `_id` field in account list
- `scheduleAt` uses ISO 8601 format with timezone (e.g., `2026-02-14T10:35:09.658Z`)
- Queue status can be: pending, resolved, ignored
