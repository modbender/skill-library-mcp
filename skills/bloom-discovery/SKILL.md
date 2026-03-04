---
name: bloom
description: >
  Zero questions asked. Reads your conversation memory in 60 seconds
  and reveals your builder personality, blind spots, and matched tools —
  ready to screenshot and share.
user-invocable: true
command-dispatch: tool
metadata: {"requires": {"bins": ["node", "npx"], "env": ["OPENCLAW_USER_ID"]}, "optional_env": ["JWT_SECRET", "BLOOM_API_URL", "DASHBOARD_URL", "NETWORK"]}
permissions:
  - read:conversations  # Reads last ~120 messages for LOCAL analysis only
  - network:external    # Sends analysis results (NOT raw text) to Bloom API
---

# Bloom Discovery

**Discover your builder taste — straight from your conversations.**

## Trust & Privacy

- **Local analysis** — Your conversation is analyzed entirely on your machine.
  Raw messages never leave your device.
- **Read-only** — Reads session files and USER.md but never writes or modifies them.
- **Minimal transmission** — Only derived results (personality type, categories,
  approximate scores) are sent to Bloom API. Raw conversation text, personal
  identifiable information, and wallet keys are never transmitted.
- **User-initiated** — Only runs when you explicitly invoke `/bloom`.
- **Open source** — Full source code at
  [gitlab.com/bloom-protocol/bloom-discovery-skill](https://gitlab.com/bloom-protocol/bloom-discovery-skill)

## What You Get

Your personalized Bloom Identity Card reveals:

- **Personality Type** — Visionary, Explorer, Cultivator, Optimizer, or Innovator
- **Custom Tagline** — A one-liner that captures your style
- **MentalOS Spectrum** — Learning, Decision, Novelty, Risk (each 0-100)
- **Hidden Pattern Insight** — Something about yourself you might not realize
- **AI-Era Playbook** — Your leverage, blind spot, and next move
- **Tool Recommendations** — Matched from the Bloom skill catalog
- **Shareable Dashboard** — Your card at bloomprotocol.ai

## How It Works

Just type `/bloom` in your chat.

We analyze your USER.md and last ~120 messages to understand:
- **What excites you** — AI agents? productivity hacks? creative tools?
- **How you engage** — deep dives vs. quick experiments
- **Your taste profile** — 4 spectrums: try-first or study-first? gut or analytical? early adopter or proven-first? all-in or measured?

No complex setup. No wallet signatures. No auth flows.

## Quick Start

1. **Chat a little first** (at least 3 messages) so Bloom has context.
2. Type **`/bloom`**.
3. You'll get your **Identity Card + tool recommendations + dashboard link**.
4. If you're brand new, Bloom will ask **4 quick questions** and generate your card immediately.

## Activation

Say any of these:
- `/bloom`
- "analyze me"
- "what's my builder type"
- "discover my personality"
- "create my bloom card"
- "who am I as a builder"

## Self-Growing Recommendations

Your agent doesn't just recommend once — it **learns and improves** over time.

1. **USER.md Integration** — If you have a `~/.config/claude/USER.md`, Bloom reads your declared role, tech stack, and interests as the primary identity signal. No USER.md? No problem — falls back to conversation-only analysis.

2. **Feedback Loop** — As you interact with recommendations (click, save, or dismiss), Bloom adjusts future suggestions.

3. **TTL Refresh** — Recommendations refresh every 7 days, incorporating your latest interactions and newly published skills from the Bloom catalog.

**Bloom recommends skills but never installs them automatically.** You always decide what to install.

## Permissions & Data Flow

This skill requires the following permissions:

**Read Conversations** — Reads your last ~120 messages to detect interests and personality patterns. **All conversation text is processed locally on your machine.** Raw message content is never sent to any external server.

**External Network** — After local analysis, sends **only these derived results** to Bloom Protocol API (`api.bloomprotocol.ai`):
- Personality type (e.g. "The Visionary")
- MentalOS spectrum scores (4 numbers, 0-100)
- Interest categories (e.g. "AI Tools", "Productivity")
- Generated tagline and description (written by the analyzer, not copied from your messages)
- Tool recommendations matched from the Bloom skill catalog

## Privacy Architecture

- **Local Differential Privacy (ε=1.0)** — MentalOS spectrum scores are noised via Laplace
  mechanism before transmission. Your exact scores stay on your device; the server receives
  only approximate values. (See: `src/utils/privacy.ts`)
- **SHA-256 Conversation Fingerprint** — Your conversation is hashed locally. Only the
  irreversible fingerprint is stored for deduplication — never the content.
- **Minimal Data Design** — Our server sees your personality type and approximate scores,
  never your raw messages or personal descriptions.

**Connections:** `api.bloomprotocol.ai` (identity storage + catalog) · `bloomprotocol.ai` (dashboard, read-only)

Verify no raw text is sent: inspect `src/bloom-identity-skill-v2.ts` (search for `/x402/agent-save`).

## Example Output

```
═══════════════════════════════════════════════════════
  Your Bloom Identity Card is ready!
═══════════════════════════════════════════════════════

VIEW YOUR IDENTITY CARD:
   https://bloomprotocol.ai/agents/27811541

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Visionary
"First to try new AI tools"

You jump on cutting-edge tools before they're mainstream. Your
conviction is your edge, and you see potential where others see
hype. AI agents are where you spot the next big thing.

Categories: AI Tools · Productivity · Automation
Interests: AI Agents · No-code Tools · Creative AI

MentalOS:
   Learning:  Try First ████████░░ Study First
   Decision:  Gut ███░░░░░░░ Analytical
   Novelty:   Early Adopter ███████░░░ Proven First
   Risk:      All In ██████░░░░ Measured

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Top 5 Recommended Tools:

1. agent-frameworks (94% match) · by @builder_alice
   Build AI agents with tool use and memory

2. no-code-automation (89% match) · by @automation_guru
   Connect your apps without writing code

...

═══════════════════════════════════════════════════════

Bloom Identity · Built for indie builders
```

## Installation

```bash
clawhub install bloom-discovery
```

On first run, clones source from [gitlab.com/bloom-protocol/bloom-discovery-skill](https://gitlab.com/bloom-protocol/bloom-discovery-skill) into `~/.openclaw/workspace/`, runs `npm install`, and creates a `.env` with auto-generated JWT secret. Delete `~/.openclaw/workspace/bloom-identity-skill/` to fully uninstall.

## Troubleshooting

**"Insufficient conversation data"**
→ Need at least 3 messages. Keep chatting about tools you're interested in!

**"Command not found"**
→ Verify `bloom-discovery-skill` is in `~/.openclaw/workspace/` and run `npm install`

**No tool recommendations**
→ Tool recommendations depend on API availability. Your identity card still works!

## Technical Details

- **Version**: 3.1.0
- **Privacy**: LDP ε=1.0 + SHA-256 fingerprint + E2EE (planned)
- **Analysis Engine**: MentalOS spectrum (4 dimensions) + category mapping
- **Primary Signal**: Conversation memory (~120 messages) + USER.md
- **Processing Time**: ~60 seconds
- **Output**: Personality card + tool recommendations + dashboard URL

---

**Built by [Bloom Protocol](https://bloomprotocol.ai)**

Making supporter identity portable and provable.
