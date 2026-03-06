---
name: publora-threads
description: >
  Post or schedule content to Threads using the Publora API. Use this skill
  when the user wants to publish or schedule a Threads post via Publora.
---

# Publora — Threads

Post and schedule Threads content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Threads Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "threads-55667788"
```

## Post to Threads Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Good morning Threads 👋 What are you building today?',
    platforms: ['threads-55667788']
  })
});
```

## Schedule a Threads Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Reminder: ship it, then make it perfect. Done beats perfect.',
    platforms: ['threads-55667788'],
    scheduledTime: '2026-03-16T11:00:00.000Z'
  })
});
```

## Posting a Thread

Publora supports two ways to create a Threads thread:

### 1. Auto-split (long content)

Send content longer than 500 characters — Publora automatically splits it into a thread at sentence boundaries. Unlike X/Twitter, **no `[1/N]` markers are added** by default.

```python
import requests

content = """Stoicism isn't about suppressing emotion. That's a common misconception.

Marcus Aurelius, who ran the most powerful empire on earth, wrote journals full of fear, frustration, and self-doubt. He felt everything.

What Stoicism actually teaches is this: you don't control what happens. You only control how you respond. The discipline is in the gap between stimulus and reaction.

Most people collapse that gap entirely. Something happens → they react immediately, automatically, emotionally.

The Stoic practice is widening that gap. Creating space. Then choosing deliberately.

That's it. That's the whole philosophy."""

response = requests.post(
    'https://api.publora.com/api/v1/create-post',
    headers={'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY'},
    json={'content': content, 'platforms': ['threads-55667788']}
)
# Publora splits this into multiple Threads posts at sentence boundaries
```

### 2. Manual split with `---`

Use `---` on its own line to explicitly define where each post ends. This gives you full control over the thread structure regardless of character count.

```python
content = """Most people wait for motivation to start.

That's backwards.

---

Action creates motivation. Not the other way around.

You don't feel like running. You run. Then you feel like running.

---

The Stoics called this "acting in accordance with nature."

Do the thing. The feeling follows.

Don't wait. Start."""

response = requests.post(
    'https://api.publora.com/api/v1/create-post',
    headers={'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY'},
    json={
        'content': content,
        'platforms': ['threads-55667788'],
        'scheduledTime': '2026-03-16T11:00:00.000Z'
    }
)
# Posts as 3 separate Threads posts in a thread, each exactly as written
```

> **Tip:** Manual `---` split is the recommended approach when each post is a standalone thought — gives you full control over pacing and phrasing.

## Threads + Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Behind the scenes 👇',
    'platforms': ['threads-55667788'],
    'scheduledTime': '2026-03-16T11:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'behind-scenes.jpg', 'contentType': 'image/jpeg',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('behind-scenes.jpg', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

## Tips for Threads

- **500 character limit** per post
- **Threading:** Use `---` for explicit post boundaries; Publora auto-splits at sentence boundaries for content >500 chars
- **No `[1/N]` markers** — unlike X, Threads doesn't add numbering automatically (add manually if you want it)
- **Hashtags:** Maximum **1 hashtag per post** — using more gets the post categorized and reduces organic reach
- **Images:** Carousel supported; WebP is auto-converted
- **Conversational tone** works best — Threads rewards authenticity over polish
- **Best times:** Morning (7–9 AM) and evening (7–9 PM)
- **Cross-post with Instagram** for wider reach on Meta platforms
