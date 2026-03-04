# Buffer Setup Guide

Buffer is the easiest way to get your agent posting. Free for up to 3 channels, no credit card required.

> **Start here:** [Create a free Buffer account](https://dub.sh/buffer-aff)  
> Buffer starts free for up to 3 social channels. Paid plans from $6/month unlock more channels, deeper analytics, and team features.

---

## Step 1: Create Your Buffer Account

1. Go to [join.buffer.com/batsirai-chada](https://dub.sh/buffer-aff) and sign up
2. Connect your social channels during onboarding (or skip and add later)
3. Supported channels: X/Twitter, LinkedIn, Instagram, Facebook, Pinterest, TikTok, YouTube, Google Business, Mastodon

---

## Step 2: Get Your API Key

Buffer's new GraphQL API uses API keys — no OAuth app registration needed.

1. Log into Buffer
2. Go to **Settings → API** ([publish.buffer.com/settings/api](https://publish.buffer.com/settings/api))
3. Create a new API key
4. Copy the key

Set it in your environment:

```bash
export BUFFER_API_KEY="your_key_here"
```

Or add to your `.env` file:

```
BUFFER_API_KEY=your_key_here
```

---

## Step 3: Test the Connection

```bash
node scripts/post-scheduler.js --status
```

Expected output:
```
✅ Buffer connected (GraphQL API)
   Channels: 5 active (5 total)
   - twitter: yourbrand (699dc84d4be271803d62884f)
   - linkedin: Your Name (6481f038c20da04cd14473c8)
   - instagram: yourbrand (699dc7dd4be271803d6286f7)
```

---

## Step 4: List Your Channels

```bash
node scripts/post-scheduler.js --channels
```

This shows all connected channels with their names and IDs. Use the name or ID when posting.

---

## Usage Examples

### Post immediately
```bash
node scripts/post-scheduler.js --channel yourbrand --content "Hello from my AI agent!"
```

### Save as draft (review before publishing)
```bash
node scripts/post-scheduler.js --channel yourbrand --content "Draft post to review" --draft
```

### Schedule for a specific time
```bash
node scripts/post-scheduler.js --channel yourbrand --content "Scheduled post" --schedule "2026-03-01T14:00:00Z"
```

### Post by channel ID (useful when multiple accounts share a name)
```bash
node scripts/post-scheduler.js --channel 699e84194be271803d65efa9 --content "Posted by ID"
```

---

## Buffer GraphQL API Reference

**Endpoint:** `https://api.buffer.com` (POST)

All requests use GraphQL with Bearer token authentication.

### Authentication

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Get Your Channels

```graphql
query {
  account {
    organizations {
      id
      channels {
        id
        name
        service
        isDisconnected
      }
    }
  }
}
```

```bash
curl -s -X POST 'https://api.buffer.com' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{"query": "{ account { organizations { id channels { id name service } } } }"}'
```

### Create a Post

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post { id text status dueAt }
    }
    ... on InvalidInputError { message }
    ... on UnexpectedError { message }
    ... on LimitReachedError { message }
  }
}
```

**Variables:**
```json
{
  "input": {
    "channelId": "YOUR_CHANNEL_ID",
    "text": "Your post content",
    "mode": "addToQueue",
    "schedulingType": "automatic",
    "saveToDraft": false
  }
}
```

**Mode options:**
| Mode | Description |
|------|-------------|
| `addToQueue` | Add to posting queue |
| `shareNow` | Post immediately |
| `shareNext` | Post next in queue |
| `customScheduled` | Schedule for specific time (requires `dueAt`) |

**Full curl example:**
```bash
curl -s -X POST 'https://api.buffer.com' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{
    "query": "mutation CreatePost($input: CreatePostInput!) { createPost(input: $input) { ... on PostActionSuccess { post { id text status } } ... on InvalidInputError { message } } }",
    "variables": {
      "input": {
        "channelId": "YOUR_CHANNEL_ID",
        "text": "Hello world!",
        "mode": "addToQueue",
        "schedulingType": "automatic"
      }
    }
  }'
```

### Save as Draft

Add `"saveToDraft": true` to the input:

```json
{
  "input": {
    "channelId": "YOUR_CHANNEL_ID",
    "text": "Draft to review",
    "mode": "addToQueue",
    "schedulingType": "automatic",
    "saveToDraft": true
  }
}
```

### Create an Idea

```graphql
mutation CreateIdea($input: CreateIdeaInput!) {
  createIdea(input: $input) {
    ... on IdeaActionSuccess {
      idea { id content }
    }
  }
}
```

---

## Troubleshooting

**`401 Unauthorized`**
→ API key is wrong. Re-check at [publish.buffer.com/settings/api](https://publish.buffer.com/settings/api).

**`500 Internal Server Error`**
→ You may be using the old REST API (`api.bufferapp.com/1/`). The new API is at `api.buffer.com` using GraphQL.

**Post created but not visible**
→ It went to the queue or drafts. Check Buffer dashboard at [publish.buffer.com](https://publish.buffer.com).

**Instagram posts failing**
→ Buffer requires a Facebook Page connected to the Instagram Business account. Personal accounts don't support API scheduling.

**Channel not found**
→ Run `--channels` to see available channels. Use the exact name or the channel ID.

---

## Buffer Plans at a Glance

| Plan | Channels | Price | Scheduled Posts |
|------|----------|-------|-----------------|
| Free | 3 | $0 | 10/channel |
| Essentials | 1 | $6/mo | 2,000/channel |
| Team | 8 | $12/mo | 2,000/channel |
| Agency | 25 | $120/mo | 2,000/channel |

For most solo founders and small businesses, the free plan is plenty to start. Upgrade when you need more channels or the analytics dashboard.

→ [Get started with Buffer](https://dub.sh/buffer-aff)
