# PowerPost Skill for OpenClaw

Tell your agent what to post. It writes the captions, makes the images, and publishes them for you.

[![Version](https://img.shields.io/badge/version-0.1.1-blue)](https://github.com/tarekhoury/openclaw-powerpost)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What it does

You say "post about our product launch on Instagram and TikTok" and the agent takes it from there. It researches the topic, writes captions that fit each platform, generates images if you want them, and publishes to your connected accounts. You review everything before it goes live.

Platforms: Instagram, TikTok, X (Twitter), YouTube, Facebook, LinkedIn, and more as they're added.

The agent can also run in draft-only mode if you'd rather review and publish manually.

---

## What you need

- A PowerPost account ([sign up here](https://powerpost.ai))
- An API key ([create one here](https://powerpost.ai/settings/api))
- Your workspace ID ([find it here](https://powerpost.ai/settings/workspaces))
- At least one connected social account ([connect here](https://powerpost.ai/settings/connections))

New accounts get 50 free credits to start.

---

## Install

```bash
# From ClawHub
openclaw skill install powerpost

# Or clone it
git clone https://github.com/tarekhoury/openclaw-powerpost.git ~/.openclaw/skills/powerpost
```

---

## Configure

You need to set two credentials. The API key can go in the Skills UI or via config. The workspace ID has to be set via config (the UI only has one field per skill).

```bash
# API key (or paste it into the "API key" field in the OpenClaw Skills UI)
openclaw config set skills.entries.powerpost.apiKey "pp_live_sk_YOUR_KEY"

# Workspace ID
openclaw config set skills.entries.powerpost.env.POWERPOST_WORKSPACE_ID "YOUR_WORKSPACE_ID"
```

If you prefer environment variables:

```bash
export POWERPOST_API_KEY="pp_live_sk_YOUR_KEY"
export POWERPOST_WORKSPACE_ID="YOUR_WORKSPACE_ID"
```

---

## Try it

Just talk to your agent:

```
"Post about our new product launch on Instagram and TikTok"
"Write captions about AI trends for all platforms"
"Generate an image for my last post"
"Check my PowerPost credits"
"Upload this image and write captions about it"
"Create a draft about our company update but don't publish yet"
```

---

## API key types

| Type | What it can do | Good for |
|---|---|---|
| `read_write` | Everything, including publishing | Agents that post on your behalf |
| `read_draft` | Generate and draft, but can't publish | When you want a human to approve before posting |

---

## Supported platforms

| Platform | Post types |
|---|---|
| Instagram | Feed, Reel, Story |
| TikTok | Video, Photos |
| X (Twitter) | Post |
| YouTube | Video, Short |
| Facebook | Post, Reel, Story |
| LinkedIn | Post |

---

## Credits

Every generation and publish uses credits. Costs vary by what you're doing and which image model you pick. See [pricing](https://powerpost.ai/pricing) for the full breakdown.

---

## Links

- [API docs](https://powerpost.ai/docs)
- [Dashboard](https://powerpost.ai)
- [Support](https://powerpost.ai/contact)
