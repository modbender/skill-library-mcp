---
name: publora-twitter
description: >
  Post or schedule content to X (Twitter) using the Publora API. Use this skill
  when the user wants to tweet, schedule a tweet, or post a thread to X/Twitter via Publora.
---

# Publora — X / Twitter

Post and schedule X/Twitter content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Twitter Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "twitter-123456789"
```

## Tweet Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Just shipped something exciting. More soon. 👀',
    platforms: ['twitter-123456789']
  })
});
```

## Schedule a Tweet

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Hot take: most productivity advice is just procrastination in disguise.',
    platforms: ['twitter-123456789'],
    scheduledTime: '2026-03-16T14:00:00.000Z'
  })
});
```

## Posting a Thread

Publora supports two ways to create a Twitter thread:

### 1. Auto-split (long content)

Send content longer than 280 characters — Publora automatically splits it into a thread at sentence boundaries and adds `[1/N]` markers to each tweet (e.g., `[1/3]`, `[2/3]`, `[3/3]`).

> ⚠️ Each `[X/N]` marker takes ~6–8 characters. Publora accounts for this automatically per tweet.

```python
import requests

content = """AI is changing how we work, but most people are using it wrong.

They treat it like a search engine — ask a question, get an answer, done. That's leaving 90% of the value on the table.

Here's how the top 1% of AI users actually think about it: they use it as a thought partner, not a lookup tool. The difference in output quality is night and day.

Let me break down the 5 mental models that separate AI power users from everyone else."""

response = requests.post(
    'https://api.publora.com/api/v1/create-post',
    headers={'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY'},
    json={'content': content, 'platforms': ['twitter-123456789']}
)
# Publora splits this into multiple tweets: [1/4], [2/4], [3/4], [4/4]
```

### 2. Manual split with `---`

Use `---` on its own line to explicitly define where each tweet ends. This gives you full control over the thread structure regardless of character count.

```python
content = """48% of developers distrust AI code. Only 3% highly trust it.

The problem? "Almost right" errors. AI gets you 90% there. That last 10% is where bugs live.

---

New study: AI helps you code faster. But hurts your learning.

Developers using AI scored lower on concept mastery tests.

Speed today. Skill gaps tomorrow. Junior devs, take note.

---

The fix? Use AI for boilerplate and scaffolding.
Write the logic yourself.
Review every line it touches.

That's how you stay sharp AND ship fast."""

response = requests.post(
    'https://api.publora.com/api/v1/create-post',
    headers={'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY'},
    json={
        'content': content,
        'platforms': ['twitter-123456789'],
        'scheduledTime': '2026-03-16T14:00:00.000Z'
    }
)
# Posts as 3 separate tweets in a thread, each part exactly as written
```

> **Tip:** Manual `---` split is the recommended approach when you want precise control over each tweet's wording and length.

## Tweet with Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'New dashboard dropped 🎉',
    'platforms': ['twitter-123456789'],
    'scheduledTime': '2026-03-16T14:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'dashboard.png', 'contentType': 'image/png',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('dashboard.png', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/png'}, data=f)
```

## Cross-post to X + LinkedIn

```javascript
body: JSON.stringify({
  content: 'Your content here',
  platforms: ['twitter-123456789', 'linkedin-ABC123'],
  scheduledTime: '2026-03-16T10:00:00.000Z'
})
```

## Tips for X/Twitter

- **Character limit:** 280 characters standard; 25,000 with X Premium (Publora detects this automatically — no threading needed for Premium)
- **Thread markers:** Publora appends `[1/N]` to each tweet in an auto-split thread; use `---` to avoid this and control splits manually
- **Character counting:** Emojis = 2 chars; URLs are normalized to 23 chars — Publora handles this automatically
- **Images:** PNG preferred; up to 4 per tweet; video and images are mutually exclusive in a single tweet
- **Hashtags:** 1–2 max; more looks spammy
- **Best times:** Weekdays 8 AM–4 PM, peak at 12 PM
- **Hooks:** First sentence must grab — most users don't click "show more"
