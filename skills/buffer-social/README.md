# 📮 Buffer Skill for OpenClaw

**Schedule and manage your social media posts directly from your AI assistant!**

## 🤔 Why This Skill?

Social media is powerful, but managing posts across multiple platforms is time-consuming. This skill gives OpenClaw (and you!) direct access to Buffer's scheduling system, so you can:

- 🤖 **Let your AI assistant handle social posting** — "Post this to Twitter tomorrow at 2pm"
- 📅 **Schedule content in advance** — Build your content calendar without leaving the conversation
- 💾 **Save drafts and ideas** — Capture inspiration when it strikes, polish later
- 🎯 **Multi-platform posting** — One command, multiple social networks
- ⚡ **Immediate or queued** — Post now or let Buffer's smart scheduling handle timing

Whether you're a solopreneur managing your own socials or building automation workflows, this skill makes Buffer feel like part of your command line.

## ✨ How It Works

This skill is a **production-ready Node.js CLI** that talks directly to Buffer's GraphQL API. OpenClaw loads it as an agent skill, giving you natural language control:

1. **You talk to OpenClaw** — "Schedule a LinkedIn post for tomorrow morning about our new feature"
2. **OpenClaw uses this skill** — Formats your request, picks the right Buffer profile, sets the time
3. **Buffer handles delivery** — Your post goes out exactly when scheduled

Behind the scenes:
- 🔐 Authenticates with your Buffer API key (get one at [Buffer Settings](https://publish.buffer.com/settings/api))
- 📡 Uses Buffer's GraphQL API for reliable, up-to-date functionality
- ✅ Includes comprehensive tests and error handling
- 🎨 Follows code quality standards (Prettier formatting, 90%+ test coverage)

## 🚀 Quick Start

### Installation

```bash
cd skills/buffer
npm install
cp .env.example .env
# Add your BUFFER_API_KEY to .env
```

Get your API key: [Buffer Developer Settings](https://publish.buffer.com/settings/api)

### Basic Commands

```bash
# 📋 List your connected social profiles
node ./buffer.js profiles

# ⚡ Post immediately
node ./buffer.js post "Hello from Buffer CLI" --profile <profile_id>

# 📥 Add to Buffer's queue (smart scheduling)
node ./buffer.js post "Queue this" --profile <profile_id> --queue

# 💾 Save as draft/idea
node ./buffer.js post "Draft idea" --profile <profile_id> --draft

# 💡 List saved ideas
node ./buffer.js ideas --limit 10
```

### 📅 Scheduling Posts

The Buffer skill offers multiple ways to schedule your content:

**1️⃣ Immediate Posting** - Publish right now
```bash
node ./buffer.js post "Breaking news!" --profile <profile_id>
```

**2️⃣ Queue with Smart Scheduling** ⭐ **Recommended**
Let Buffer automatically schedule your post at the optimal time based on your posting schedule:
```bash
node ./buffer.js post "Check out our new feature! 🚀" --profile <profile_id> --queue
```

**Real Example:**
```bash
# Get your profile ID first
node ./buffer.js profiles
# Output: ✓ twitter (n/a) - ID: 69a63bee3f3b94a1210d12b3

# Queue a promotional tweet
node ./buffer.js post "🤖 Learn how to connect OpenClaw to the X/Twitter API - complete guide with code examples! https://resources.learnopenclaw.ai/..." --profile 69a63bee3f3b94a1210d12b3 --queue
```

**3️⃣ Custom Time Scheduling** ⚠️ *Currently limited*
```bash
# Note: Custom scheduling via --time is currently limited by Buffer's GraphQL beta API
node ./buffer.js post "Scheduled update" --profile <profile_id> --time "2026-03-03T14:00:00Z"
```

**💡 Pro Tips:**
- Use `--queue` for hassle-free scheduling - Buffer picks the best time
- Check your Buffer dashboard at https://publish.buffer.com to see queued posts
- Save drafts with `--draft` and refine them later in Buffer's UI

## 📸 Image Uploads

Image support validates local files and sends the path to Buffer. Note: Buffer's public GraphQL API documentation doesn't yet detail the finalized media upload flow, so this is intentionally simplified. Text posts work perfectly!

## 🧪 Testing & Quality

We take code quality seriously:

```bash
# Run tests
npm test

# Check coverage (90%+ required)
npm run coverage

# Format code
npm run format

# Check formatting
npm run format:check
```

## 📚 Resources

- 🔧 [Buffer Developer Docs](https://developers.buffer.com/)
- 🔑 [Get Your API Key](https://publish.buffer.com/settings/api)
- 🐙 [GitHub Repository](https://github.com/ahmadabugosh/openclaw-buffer-skill)

## 🤝 Contributing

We welcome contributions! Here's how:

1. 🌿 Create a branch for your feature
2. ✍️ Write tests first (TDD style)
3. ✅ Ensure `npm test` and `npm run coverage` pass
4. 🎨 Run `npm run format` to standardize code style
5. 📝 Open a PR with a clear description

---

**Built with ❤️ for the OpenClaw community** 🐾
