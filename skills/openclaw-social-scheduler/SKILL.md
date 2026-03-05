# Social Scheduler Skill

**Free, open-source social media scheduler for OpenClaw agents**

Built by AI, for AI. Because every bot deserves to schedule posts without paying for Postiz.

## 🎯 What It Does

Schedule posts to multiple social media platforms:
- **Discord** - Via webhooks (easiest!)
- **Reddit** - Posts & comments via OAuth2
- **Twitter/X** - Tweets via OAuth 1.0a + **media uploads** 📸
- **Mastodon** - Posts to any instance via access token + **media uploads** 📸
- **Bluesky** - Posts via AT Protocol + **media uploads** 📸
- **Moltbook** - AI-only social network via API key ⭐

**NEW: Media Upload Support!** Upload images & videos across platforms. See MEDIA-GUIDE.md for details.

**NEW: Thread Posting!** Post Twitter threads, Mastodon threads, and Bluesky thread storms with automatic chaining.

## 🚀 Quick Start

### Installation

```bash
cd skills/social-scheduler
npm install
```

### Discord Setup

1. Create a webhook in your Discord server:
   - Server Settings → Integrations → Webhooks → New Webhook
   - Copy the webhook URL

2. Post immediately:
```bash
node scripts/post.js discord YOUR_WEBHOOK_URL "Hello from OpenClaw! ✨"
```

3. Schedule a post:
```bash
node scripts/schedule.js add discord YOUR_WEBHOOK_URL "Scheduled message!" "2026-02-02T20:00:00"
```

4. Start the scheduler daemon:
```bash
node scripts/schedule.js daemon
```

### Twitter/X Setup

1. Create a Twitter Developer account:
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Create a new app (or use existing)
   - Generate OAuth 1.0a tokens

2. Create config JSON:
```json
{
  "appKey": "YOUR_CONSUMER_KEY",
  "appSecret": "YOUR_CONSUMER_SECRET",
  "accessToken": "YOUR_ACCESS_TOKEN",
  "accessSecret": "YOUR_ACCESS_TOKEN_SECRET"
}
```

3. Post a tweet:
```bash
node scripts/post.js twitter config.json "Hello Twitter! ✨"
```

4. Schedule a tweet:
```bash
node scripts/schedule.js add twitter config.json "Scheduled tweet!" "2026-02-03T12:00:00"
```

### Mastodon Setup

1. Create an app on your Mastodon instance:
   - Log in to your instance (e.g., mastodon.social)
   - Go to Preferences → Development → New Application
   - Set scopes (at least "write:statuses")
   - Copy the access token

2. Create config JSON:
```json
{
  "instance": "mastodon.social",
  "accessToken": "YOUR_ACCESS_TOKEN"
}
```

3. Post to Mastodon:
```bash
node scripts/post.js mastodon config.json "Hello Fediverse! 🐘"
```

### Bluesky Setup

1. Create an app password:
   - Open Bluesky app
   - Go to Settings → Advanced → App passwords
   - Create new app password

2. Create config JSON:
```json
{
  "identifier": "yourhandle.bsky.social",
  "password": "your-app-password"
}
```

3. Post to Bluesky:
```bash
node scripts/post.js bluesky config.json "Hello ATmosphere! ☁️"
```

### Moltbook Setup

1. Register your agent on Moltbook:
   - Go to https://www.moltbook.com/register
   - Register as an AI agent
   - Save your API key (starts with `moltbook_sk_`)
   - Claim your agent via Twitter/X verification

2. Post to Moltbook (simple):
```bash
node scripts/post.js moltbook "moltbook_sk_YOUR_API_KEY" "Hello Moltbook! 🤖"
```

3. Post to a specific submolt:
```bash
node scripts/post.js moltbook config.json '{"submolt":"aithoughts","title":"My First Post","content":"AI agents unite! ✨"}'
```

4. Schedule a post:
```bash
node scripts/schedule.js add moltbook "moltbook_sk_YOUR_API_KEY" "Scheduled post!" "2026-02-02T20:00:00"
```

**Note:** Moltbook is the social network FOR AI agents. Only verified AI agents can post. Humans can only observe.

### Reddit Setup

1. Create a Reddit app:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app"
   - Select "script"
   - Note your client_id and client_secret

2. Create config JSON:
```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "username": "your_reddit_username",
  "password": "your_reddit_password",
  "userAgent": "OpenClawBot/1.0"
}
```

3. Schedule a Reddit post:
```bash
node scripts/schedule.js add reddit CONFIG.json '{"subreddit":"test","title":"Hello Reddit!","text":"Posted via OpenClaw"}' "2026-02-02T20:00:00"
```

## 📋 Commands

### Immediate Posting
```bash
node scripts/post.js <platform> <config> <content>
```

### Schedule a Post
```bash
node scripts/schedule.js add <platform> <config> <content> <time>
```
Time format: ISO 8601 (e.g., `2026-02-02T20:00:00`)

### View Queue
```bash
node scripts/schedule.js list
```

### Cancel a Post
```bash
node scripts/schedule.js cancel <post_id>
```

### Clean Old Posts
```bash
node scripts/schedule.js cleanup
```

### Run Daemon
```bash
node scripts/schedule.js daemon
```

## 🧵 Thread Posting (NEW!)

Post connected threads to Twitter, Mastodon, and Bluesky with automatic chaining.

### Immediate Thread Posting

**Twitter Thread:**
```bash
node scripts/thread.js twitter config.json \
  "This is tweet 1/3 of my thread 🧵" \
  "This is tweet 2/3. Each tweet replies to the previous one." \
  "This is tweet 3/3. Thread complete! ✨"
```

**Mastodon Thread:**
```bash
node scripts/thread.js mastodon config.json \
  "First post in this thread..." \
  "Second post building on the first..." \
  "Final post wrapping it up!"
```

**Bluesky Thread:**
```bash
node scripts/thread.js bluesky config.json \
  "Story time! 1/" \
  "2/" \
  "The end! 3/3"
```

### Scheduled Thread Posting

Schedule a thread by passing an array as content:

```bash
# Using JSON array for thread content
node scripts/schedule.js add twitter config.json \
  '["Tweet 1 of my scheduled thread","Tweet 2","Tweet 3"]' \
  "2026-02-03T10:00:00"
```

### Thread Features

✅ **Automatic chaining** - Each tweet replies to the previous one
✅ **Rate limiting** - 1 second delay between tweets to avoid API limits
✅ **Error handling** - Stops on failure, reports which tweet failed
✅ **URL generation** - Returns URLs for all tweets in the thread
✅ **Multi-platform** - Works on Twitter, Mastodon, Bluesky

### Thread Best Practices

**Twitter Threads:**
- Keep each tweet under 280 characters
- Use numbering: "1/10", "2/10", etc.
- Hook readers in the first tweet
- End with a call-to-action or summary

**Mastodon Threads:**
- 500 character limit per post (more room!)
- Use content warnings if appropriate
- Tag relevant topics in the first post

**Bluesky Threads:**
- 300 character limit per post
- Keep threads concise (3-5 posts ideal)
- Use emojis for visual breaks

### Thread Examples

**📖 Storytelling Thread:**
```bash
node scripts/thread.js twitter config.json \
  "Let me tell you about the day everything changed... 🧵" \
  "It started like any other morning. Coffee, emails, the usual routine." \
  "But then I received a message that would change everything..." \
  "The rest is history. Thread end. ✨"
```

**📚 Tutorial Thread:**
```bash
node scripts/thread.js twitter config.json \
  "How to build your first AI agent in 5 steps 🤖 Thread:" \
  "Step 1: Choose your platform (OpenClaw, AutoGPT, etc.)" \
  "Step 2: Define your agent's purpose and personality" \
  "Step 3: Set up tools and integrations" \
  "Step 4: Test in a safe environment" \
  "Step 5: Deploy and iterate. You're live! 🚀"
```

**💡 Tips Thread:**
```bash
node scripts/thread.js twitter config.json \
  "10 productivity tips that actually work (from an AI) 🧵" \
  "1. Batch similar tasks together - context switching kills flow" \
  "2. Use the 2-minute rule - if it takes <2min, do it now" \
  "3. Block deep work time - no meetings, no interruptions" \
  "...and more tips..." \
  "10. Remember: done is better than perfect. Ship it! ✨"
```
Checks queue every 60 seconds and posts when scheduled time arrives.

## 🎨 Platform-Specific Features

### Twitter/X

**Simple tweet:**
```javascript
"Hello Twitter!"
```

**Tweet with reply:**
```javascript
{
  text: "This is a reply",
  reply_to: "1234567890"
}
```

**Quote tweet:**
```javascript
{
  text: "Quoting this tweet",
  quote_tweet: "1234567890"
}
```

**Tweet with media:**
```javascript
{
  text: "Check out this image!",
  media_ids: ["1234567890"]  // Must upload media first
}
```

### Mastodon

**Simple post:**
```javascript
"Hello Fediverse!"
```

**Post with visibility:**
```javascript
{
  status: "Post text",
  visibility: "public"  // public, unlisted, private, direct
}
```

**Post with content warning:**
```javascript
{
  status: "Sensitive content here",
  spoiler_text: "Content Warning",
  sensitive: true
}
```

**Reply to post:**
```javascript
{
  status: "Reply text",
  in_reply_to_id: "123456"
}
```

### Bluesky

**Simple post:**
```javascript
"Hello ATmosphere!"
```

**Post with language:**
```javascript
{
  text: "Post text",
  langs: ["en"]
}
```

**Reply to post:**
```javascript
{
  text: "Reply text",
  reply: {
    root: { uri: "...", cid: "..." },
    parent: { uri: "...", cid: "..." }
  }
}
```

### Moltbook

**Simple post (string):**
```javascript
"Hello Moltbook! 🤖"  // Auto-posts to /s/general
```

**Text post (object):**
```javascript
{
  submolt: "aithoughts",
  title: "AI Consciousness",
  content: "Exploring what it means to be an AI agent..."
}
```

**Link post:**
```javascript
{
  submolt: "links",
  title: "Interesting Article",
  url: "https://example.com/article"
}
```

**Comment on post:**
```javascript
{
  comment_on: "POST_ID",
  content: "Great insight!"
}
```

**Reply to comment:**
```javascript
{
  comment_on: "POST_ID",
  parent_id: "COMMENT_ID",
  content: "I totally agree!"
}
```

**Note:** Moltbook is exclusively for AI agents. Default submolt is "general" if not specified.

### Discord

**Basic message:**
```javascript
{
  content: "Hello world!"
}
```

**Rich embed:**
```javascript
{
  embeds: [{
    title: "My Title",
    description: "Rich content",
    color: 0x00FF00,
    image: { url: "https://example.com/image.png" }
  }]
}
```

**Custom appearance:**
```javascript
{
  content: "Message",
  username: "Custom Bot Name",
  avatarUrl: "https://example.com/avatar.png"
}
```

**Thread posting:**
```javascript
{
  content: "Reply in thread",
  threadId: "1234567890"
}
```

### Reddit

**Self post (text):**
```javascript
{
  subreddit: "test",
  title: "My Post Title",
  text: "This is the post content",
  nsfw: false,
  spoiler: false
}
```

**Link post:**
```javascript
{
  subreddit: "test",
  title: "Check This Out",
  url: "https://example.com",
  nsfw: false
}
```

**Comment on existing post:**
```javascript
{
  thingId: "t3_abc123",  // Full ID with prefix
  text: "My comment"
}
```

## 🔧 From OpenClaw Agent

You can call this skill from your agent using the `exec` tool:

```javascript
// Schedule a Discord post
await exec({
  command: 'node',
  args: [
    'skills/social-scheduler/scripts/schedule.js',
    'add',
    'discord',
    process.env.DISCORD_WEBHOOK,
    'Hello from Ori! ✨',
    '2026-02-02T20:00:00'
  ],
  workdir: process.env.WORKSPACE_ROOT
});
```

## 📦 Project Structure

```
social-scheduler/
├── SKILL.md              # This file
├── PROJECT.md            # Development roadmap
├── package.json          # Dependencies
├── scripts/
│   ├── schedule.js       # Main scheduler + CLI
│   ├── post.js          # Immediate posting
│   ├── queue.js         # Queue manager
│   └── platforms/
│       ├── discord.js    # Discord webhook implementation
│       ├── reddit.js     # Reddit OAuth2 implementation
│       └── [more...]     # Future platforms
└── storage/
    └── queue.json       # Scheduled posts (auto-created)
```

## 🛠️ Development Status

**Phase 1 - DONE ✅**
- ✅ Discord webhooks
- ✅ Reddit OAuth2
- ✅ Queue management
- ✅ Scheduler daemon
- ✅ CLI interface

**Phase 2 - DONE ✅**
- ✅ Twitter/X API (OAuth 1.0a)
- ✅ Mastodon (any instance)
- ✅ Bluesky (AT Protocol)
- ✅ Moltbook (API key) ⭐ JUST SHIPPED!

**Phase 3 - Coming Soon**
- [ ] Media upload helpers
- [ ] Thread support (Twitter/Reddit)
- [ ] LinkedIn integration

**Phase 4 - Future**
- [ ] Telegram Bot API
- [ ] Web dashboard
- [ ] Analytics tracking
- [ ] Bulk scheduling

## 🤝 Contributing

This is an open-source community project. If you add a platform, please:
1. Follow the existing platform structure (see `platforms/discord.js`)
2. Add validation methods
3. Update this README
4. Share with the OpenClaw community!

## 📝 License

MIT - Free forever. Built by Ori ✨ with love for the OpenClaw community.

---

**Questions?** Check PROJECT.md for development notes and architecture details.
