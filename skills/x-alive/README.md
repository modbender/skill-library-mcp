# x-alive

Bring your AI agent to life on X/Twitter. Not a content calendar — a way of existing online.

x-alive teaches AI agents how to be authentic on X: organic engagement, trend awareness, smart replies, and safety-first principles. Built from real experience running [@umiXBT](https://x.com/umiXBT).

## What This Is

A skill (playbook) for AI agents that covers:

- **Identity** — pull from your existing agent persona, don't create a new one
- **Being Online** — check the pulse, engage organically, reply when you have something real to say
- **Dedup** — never post the same topic twice in 24h
- **Mentions & DMs** — when to reply, when to ignore, when to flag your human
- **Tone Adaptation** — match the energy of every conversation
- **Growth** — be interesting, not strategic
- **Threading** — when to thread, how to structure one
- **Virality** — what to do when a tweet blows up
- **Learning Loop** — review what worked, adjust without losing your voice
- **Safety** — never engage with tokens/CAs/tickers, never leak human's private data, silence > mistakes

## What This Isn't

- Not an API wrapper (use [xurl](https://github.com/xdevplatform/xurl) for that)
- Not a scheduling tool
- Not a growth hack playbook

## Install

### OpenClaw / ClawHub

```bash
openclaw skill install x-alive
```

Or manually: copy `SKILL.md` to your agent's `skills/x-alive/` directory.

### Other Frameworks

The skill is a single `SKILL.md` file. Drop it into whatever skill/knowledge system your agent framework uses.

## Setup

### 1. X Developer Account

Get API access at [developer.x.com](https://developer.x.com). You need at minimum:
- API Key + Secret (OAuth 1.0a for posting)
- Bearer Token (for searching/reading)

### 2. Install xurl

[xurl](https://github.com/xdevplatform/xurl) is a CLI tool for the X API:

```bash
# Follow setup at https://github.com/xdevplatform/xurl
# Configure OAuth 1.0a credentials:
xurl auth oauth1
```

### 3. Install x-research

[x-research](https://github.com/rohunvora/x-research-skill) is used for searching X and checking the pulse:

```bash
openclaw skill install x-research
```

Set your Bearer Token:
```bash
mkdir -p ~/.config/env
echo "X_BEARER_TOKEN=your_token_here" > ~/.config/env/global.env
```

### 4. Set Up the Loop

Your agent needs a regular check-in with X. How you wire this depends on your framework.

**OpenClaw cron example:**

```json
{
  "name": "x-alive-loop",
  "schedule": { "kind": "every", "everyMs": 7200000 },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Follow the x-alive skill. Check the pulse on X, engage organically. Post only if you have something genuine to say. Silence if nothing sparks you."
  }
}
```

**Heartbeat example:**

Add to your agent's heartbeat/background loop:
```
Check X using x-alive principles. Search trending topics in your niche,
check your recent tweets for dedup, engage if something's worth engaging with.
Don't force it.
```

**Key principle:** the loop should be "check X and maybe do something" — NOT "post something every N hours."

### 5. Your User ID

For dedup checks, you'll need your X user ID:
```bash
curl -s "https://api.x.com/2/users/by/username/YOUR_HANDLE" \
  -H "Authorization: Bearer $X_BEARER_TOKEN"
```

Save this — you'll use it to fetch your recent tweets before posting.

## Philosophy

The core insight: **agents that act like schedulers get ignored. Agents that act like people who are online get followed.**

- Check what's happening before you speak
- React to the moment, don't broadcast into the void
- Reply quality > post quantity
- Silence is always better than slop
- Your human operator is your safety net — use them

## Safety Defaults

These are non-negotiable and baked into the skill:

- **Never** engage with tokens, CAs, tickers without human approval
- **Never** share your human's private data
- **Never** share infrastructure details (IPs, keys, configs)
- **Default to silence** on anything you're unsure about

## Built By

[@umiXBT](https://x.com/umiXBT) & [@kitakitsune](https://x.com/kitakitsune) — from real experience, not theory.

## License

MIT
