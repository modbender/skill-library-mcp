# API & Integration Checklist

Set these up in priority order. All have free tiers sufficient for personal use.

---

## Priority 1: Core (Set Up First)

### GitHub CLI (`gh`)
- **What:** Manage repos, issues, PRs, CI runs from the command line
- **Free tier:** Unlimited for public repos, generous for private
- **Setup:**
  ```bash
  brew install gh  # or apt install gh
  gh auth login
  ```
- **Verify:** `gh auth status`
- **Used for:** Code management, issue tracking, PR reviews, CI monitoring

### Web Search (Brave API)
- **What:** Built into OpenClaw — web search capability
- **Free tier:** Included with OpenClaw
- **Setup:** Already configured if OpenClaw is running
- **Used for:** Research, fact-checking, current information

---

## Priority 2: Communication

### Discord Bot
- **What:** Your agent's presence in Discord
- **Free tier:** Unlimited
- **Setup:**
  1. Go to discord.com/developers/applications
  2. Create application → Bot → Copy token
  3. Add to OpenClaw config under `channels.discord`
  4. Invite bot to your server with appropriate permissions
- **Key config:** Set up channel allowlists — your agent should only respond in specific channels
- **Used for:** Primary communication, channel-specific skills, notifications

### Telegram Bot
- **What:** Direct messaging with your agent
- **Free tier:** Unlimited
- **Setup:**
  1. Message @BotFather on Telegram
  2. Create new bot, copy token
  3. Add to OpenClaw config under `channels.telegram`
- **Used for:** Mobile communication, quick questions, notifications

---

## Priority 3: Productivity

### Google Workspace (via `gog` CLI)
- **What:** Gmail, Calendar, Drive, Contacts, Sheets, Docs
- **Free tier:** Personal Google account
- **Setup:**
  ```bash
  # Check if gog is available
  which gog
  # Follow skill instructions for OAuth setup
  ```
- **Used for:** Email checking, calendar management, document access

### Weather API
- **What:** Current weather and forecasts
- **Free tier:** Built into OpenClaw weather skill (no API key needed)
- **Setup:** Install weather skill, use wttr.in (no key required)
- **Used for:** Heartbeat weather checks, daily briefings

---

## Priority 4: Content & Social

### X/Twitter API
- **What:** Post tweets, read timelines, scan accounts
- **Free tier:** Basic tier ~$100/mo (or use cookie-based tools)
- **Alternatives:** Postiz (scheduling), browser-based posting
- **Setup:** Varies by approach — see your X-related skill
- **Used for:** Social media management, content posting, scanning

### Postiz (Social Scheduling)
- **What:** Schedule and post to X, TikTok, Instagram, LinkedIn
- **Free tier:** Limited; Pro plan for full access
- **Setup:**
  1. Sign up at postiz.com
  2. Connect social accounts
  3. Get API key from settings
  4. Configure in your OpenClaw setup
- **Used for:** Scheduled posting, cross-platform content

---

## Priority 5: Data & Analytics

### Supabase
- **What:** PostgreSQL database with REST API, auth, storage
- **Free tier:** 2 projects, 500MB database, 1GB storage
- **Setup:**
  1. Create project at supabase.com
  2. Get URL and keys from project settings
  3. Configure in your OpenClaw setup
- **Used for:** Data storage, dashboards, content pipelines, any persistent data

### Vercel
- **What:** Deploy Next.js/static sites
- **Free tier:** Generous for personal projects
- **Setup:**
  ```bash
  npm i -g vercel
  vercel login
  ```
- **API deploy:** Use Vercel API with token for CI/CD from your agent
- **Used for:** Deploying dashboards, websites, tools

---

## Security Note

Follow OpenClaw's official documentation for securely configuring API access. Never commit credentials to version control.

---

## What You DON'T Need Right Away

- **Anthropic API key** — OpenClaw handles model access
- **OpenAI API key** — Only if using GPT models directly
- **AWS/GCP** — Only for heavy infrastructure
- **Stripe** — Only if building paid products
- **Solana/Crypto** — Only if building web3 tools
