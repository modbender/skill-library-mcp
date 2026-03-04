---
name: browsex
description: "X/Twitter CLI using OpenClaw browser tool. Use when the user wants to interact with X/Twitter: reading timeline, posting tweets, liking, retweeting, replying, or searching. Read-only browsing (profiles, tweets, search) works without login. Alternative to bird CLI for environments without Homebrew."
metadata: {"clawdhub":{"emoji":"𝕏"}}
---

# browsex

Manipulate X(formerly Twitter) using the OpenClaw browser tool. Browser-based alternative to bird CLI.

## Prerequisites

### Environment requirements
- OpenClaw with browser tool enabled
- `openclaw` browser profile
- X/Twitter account logged in *(only required for posting, liking, retweeting, replying, following)*

Read-only browsing (viewing profiles, individual tweets, search) works without login.
X may show login popups on unauthenticated sessions -- dismiss them or ignore.

### For headless servers

Xvfb virtual display required (see spool skill's Prerequisites)

### Login (only needed for write actions)

```
browser action=start profile=openclaw
browser action=open profile=openclaw targetUrl="https://x.com/login"
# Ask user to log in manually
```

---

## Usage

### Read-only (no login required)

These actions work without an X/Twitter account. X may show login modals after
a few pages -- look for close/dismiss buttons in the snapshot and click them.

### 1. View a specific tweet

```
browser action=open profile=openclaw targetUrl="https://x.com/username/status/1234567890"
browser action=snapshot profile=openclaw compact=true
```

### 2. View profile

```
browser action=open profile=openclaw targetUrl="https://x.com/username"
browser action=snapshot profile=openclaw compact=true
```

### 3. Search

```
browser action=open profile=openclaw targetUrl="https://x.com/search?q=search_term&src=typed_query"
browser action=snapshot profile=openclaw compact=true
```

### Login required

These actions require an authenticated session. Complete the login step in Prerequisites first.

### 4. Read timeline

```
browser action=open profile=openclaw targetUrl="https://x.com/home"
browser action=snapshot profile=openclaw compact=true
```

For each article, you can see author, content, and like/retweet/reply counts.

### 5. Post a tweet

**Step 1: Find the textbox on home**
```
browser action=open profile=openclaw targetUrl="https://x.com/home"
browser action=snapshot profile=openclaw compact=true
```
→ Find `textbox "Post text"` ref

**Step 2: Enter content**
```
browser action=act profile=openclaw request={"kind":"click","ref":"<textbox-ref>"}
browser action=act profile=openclaw request={"kind":"type","ref":"<textbox-ref>","text":"tweet content"}
```

**Step 3: Click Post button**
```
browser action=snapshot profile=openclaw compact=true
```
→ Find `button "Post"` ref (one that is not disabled)
```
browser action=act profile=openclaw request={"kind":"click","ref":"<post-ref>"}
```

### 6. Like a tweet

From timeline, find `button "Like"` or `button "X Likes. Like"` ref within article:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<like-ref>"}
```

### 7. Retweet

Find `button "Repost"` or `button "X reposts. Repost"` ref:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<repost-ref>"}
browser action=snapshot profile=openclaw compact=true
# Select "Repost" option
browser action=act profile=openclaw request={"kind":"click","ref":"<repost-option-ref>"}
```

### 8. Reply to a tweet

**Method 1: From timeline**
```
browser action=act profile=openclaw request={"kind":"click","ref":"<reply-button-ref>"}
browser action=snapshot profile=openclaw compact=true
# Enter text in reply input box, then click Reply button
```

**Method 2: From tweet page**
```
browser action=open profile=openclaw targetUrl="https://x.com/username/status/1234567890"
browser action=snapshot profile=openclaw compact=true
# Find reply input box and enter text
```

### 9. Follow

On profile page, find `button "Follow"` ref:
```
browser action=act profile=openclaw request={"kind":"click","ref":"<follow-ref>"}
```

---

## Key points

1. **Snapshot first** - Check current state before any action
2. **ref changes every time** - Always find fresh ref from snapshot
3. **compact=true** - Save tokens
4. **article structure** - Each tweet is an article element with author/content/buttons inside
5. **Confirm before posting** - Get user confirmation of content

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser not working | Check Xvfb, DISPLAY=:99, restart Gateway |
| Login failed | Navigate to /login and log in manually |
| Post button disabled | Verify text was entered |
| Rate limit | Wait a moment and retry |
| Login popup blocking page | Snapshot, find close/dismiss button ref, click it. If persistent, log in or try a direct URL instead |

---

## vs bird CLI

| Feature | bird CLI | browsex (browser) |
|---------|----------|-----------------|
| Installation | Requires brew | Only Xvfb needed |
| Auth | Cookie extraction | Browser session |
| Stability | API-based | UI-dependent (may change) |
| Speed | Fast | Slightly slower |
