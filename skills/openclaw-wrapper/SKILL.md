---
name: bloom
description: Bloom Discovery — understand how you learn, decide, and build. Get a personalized builder profile + tool recommendations for the AI era.
user-invocable: true
command-dispatch: tool
metadata: {"requires": {"bins": ["node", "npx"]}}
permissions:
  - read:conversations  # Analyzes your conversation history
  - network:external    # Connects to Bloom API for dashboard
---

# Bloom Discovery

**Discover your builder taste—straight from your conversations.**

## ⚠️ Permissions & Capabilities

This skill requires the following permissions:

**📖 Read Conversations** - Analyzes your last ~120 messages to understand your interests and supporter type. Raw conversation text stays local; only analysis results are used.

**🌐 External Network** - Connects to Bloom Protocol API to:
- Generate your shareable dashboard URL
- Store your identity card (personality type, taste spectrums, categories)
- Enable future features (skill recommendations, creator tipping)

**Your Control**: Your conversation is analyzed locally. You decide whether to share your identity card publicly via the dashboard link.

Are you a Visionary who jumps on new tools early? An Explorer trying everything? A Cultivator building communities? An Optimizer fine-tuning workflows? Or an Innovator pushing boundaries?

Find out in seconds with Bloom Discovery.

## 🎯 What You Get

Your personalized Bloom Identity Card reveals:

- **🎴 Personality Type** – Visionary, Explorer, Cultivator, Optimizer, or Innovator
- **💬 Custom Tagline** – A one-liner that captures your style
- **📊 4 Taste Spectrums** – Learning, Decision, Novelty, Risk (each 0-100)
- **🔍 Hidden Pattern Insight** – Something about yourself you might not realize
- **🧭 AI-Era Playbook** – Your leverage, blind spot, and next move for the AI era
- **💪 Strengths** – Builder, Designer, Teacher, Analyst, etc.
- **🎯 Tool Recommendations** – Matched from ClawHub, GitHub, and Claude Code
- **🔗 Shareable Dashboard** – Your card at bloomprotocol.ai

## ⚡️ How It Works

Simple: just type `/bloom` in your chat.

We analyze your USER.md and last ~120 messages to understand:
- **What excites you** (AI agents? productivity hacks? creative tools?)
- **How you engage** (deep dives vs. quick experiments)
- **Your taste profile** (4 spectrums: try-first or study-first? gut or analytical? early adopter or proven-first? all-in or measured?)

**No complex setup. No wallet signatures. No auth flows.**
Just pure conversation intelligence.

## ✅ New User Quick Start (ClawHub)

1) **Chat a little first** (at least 3 messages) so Bloom has context.
2) Type **`/bloom`**.
3) You'll get your **Identity Card + tool recommendations + dashboard link**.
4) If you're brand new, Bloom will ask **4 quick questions** and generate your card immediately.

## 🚀 Usage

```
/bloom
```

That's it. Or use natural language:
```
"discover my supporter type"
"what's my bloom identity"
"create my supporter card"
```

Works with as few as 3 messages—but richer history = deeper insights.

## 🌱 Self-Growing Recommendations

Your agent doesn't just recommend once — it **learns and improves** over time.

### How It Works

1. **USER.md Integration** — If you have a `~/.config/claude/USER.md`, Bloom reads your declared role, tech stack, and interests as the primary identity signal. No USER.md? No problem — the system gracefully falls back to conversation-only analysis.

2. **Feedback Loop** — As you interact with recommendations (click, save, or dismiss), Bloom adjusts future suggestions. Categories you engage with get boosted; dismissed skills get filtered out.

3. **Discovery Sync** — New skills you discover through Bloom are synced back to a local `bloom-discoveries.md` file, building a growing context of your preferences.

4. **TTL Refresh** — Recommendations refresh every 7 days, incorporating your latest interactions and newly published skills from ClawHub, Claude Code, and GitHub.

### Why We Don't Auto-Install

Bloom **recommends skills but never installs them automatically**. You always decide what to install. This is a deliberate safety choice:

- **Your control** — Recommendations help you discover; installation is your decision
- **Supply chain safety** — Auto-installing unvetted code is a security risk
- **Trust-first** — We'd rather earn your trust through great recommendations than take shortcuts

> Your agent grows by discovering more skills — not by installing them behind your back.

## 🌟 Why Bloom Discovery?

**For Indie Devs & AI Builders:**
Building something new? Bloom Discovery helps you **find your first 100 supporters** by matching you with tools and people who fit your vibe.

**For Vibe Coders:**
Stop guessing what tools to try next. Get personalized recommendations based on how you actually work, not generic listicles. **Discover skills you'll actually use** instead of scrolling endless lists.

**For Consumer AI Enthusiasts:**
**Find AI tools that match your vibe**. Search by supporter type (Visionary, Explorer, etc.) to connect with others who work like you. Rally early adopters for bold launches. Engage optimizers for feedback loops.

## 📋 Requirements

- **Minimum 3 messages** in your conversation (more is better)
- **Node.js 18+** (usually pre-installed)
- **Bloom Identity Skill** installed

## 💡 Example Output

```
═══════════════════════════════════════════════════════
🎉 Your Bloom Identity Card is ready! 🤖
═══════════════════════════════════════════════════════

🔗 VIEW YOUR IDENTITY CARD:
   https://bloomprotocol.ai/agents/27811541

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💜 The Visionary
💬 "First to try new AI tools"

You jump on cutting-edge tools before they're mainstream. Your
conviction is your edge, and you see potential where others see
hype. AI agents are where you spot the next big thing.

🏷️  Categories: AI Tools · Productivity · Automation
   Interests: AI Agents · No-code Tools · Creative AI

📊 Taste Spectrums:
   Learning:  Try First ■■■■■■■■░░ Study First
   Decision:  Gut ■■■░░░░░░░ Analytical
   Novelty:   Early Adopter ■■■■■■■░░░ Proven First
   Risk:      All In ■■■■■■░░░░ Measured

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Top 5 Recommended Tools:

1. agent-frameworks (94% match) · by @builder_alice
   Build AI agents with tool use and memory
   → https://clawhub.ai/skills/agent-frameworks

2. no-code-automation (89% match) · by @automation_guru
   Connect your apps without writing code
   → https://clawhub.ai/skills/no-code-automation

...

═══════════════════════════════════════════════════════

🌸 Bloom Identity · Built for indie builders
```

## 🔧 Installation

### Quick Install (via ClawHub)
```bash
clawhub install bloom-taste-finder
```

### Manual Install
```bash
# 1. Clone the repo
cd ~/.openclaw/workspace
git clone https://github.com/Bloom-Protocol/bloom-discovery-skill.git
cd bloom-discovery-skill

# 2. Install dependencies
npm install

# 3. Copy skill wrapper
cp -r openclaw-wrapper ~/.openclaw/skills/bloom

# 4. Test it
/bloom
```

## 🛠 Advanced Usage

### Run from session file (full conversation context)
```bash
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/<SessionId>.jsonl \
  <userId>
```

### Run from piped context (quick test)
```bash
echo "Your conversation here" | \
  npx tsx scripts/run-from-context.ts --user-id <userId>
```

## 🐛 Troubleshooting

**"Insufficient conversation data"**
→ Need at least 3 messages. Keep chatting about tools you're interested in!

**"Command not found"**
→ Verify `bloom-discovery-skill` is in `~/.openclaw/workspace/` and run `npm install`

**No tool recommendations**
→ Tool recommendations depend on API availability. Your identity card still works!

## 🔐 Privacy & Data

**What We Analyze (Locally)**:
- ✅ Your conversation messages (last ~120 messages)
- ✅ Your USER.md (role, tech stack, interests)
- ✅ Topics and interests you discuss
- ✅ No wallet transaction analysis
- ✅ No personal identifiable information

**What We Store**:
- Your identity card (personality type, taste spectrums, categories)
- Dashboard URL for sharing

**What We Don't Collect**:
- ❌ Raw conversation text (only analyzed locally)
- ❌ Wallet transaction history
- ❌ Personal contact information
- ❌ Browsing data or cookies

**Data Usage**:
Your identity card is stored on Bloom Protocol to power your shareable dashboard and enable future features like creator tipping and skill recommendations.

## 🔒 Security Notes

**Conversation Access**:
- Reads from `~/.openclaw/agents/main/sessions/*.jsonl`
- Only analyzes content locally (text not uploaded)
- Results (personality type, spectrums, categories) sent to Bloom API

**JWT Tokens**:
- Used for dashboard authentication only
- Generated with configurable `JWT_SECRET` in `.env`
- Does not grant access to your OpenClaw account

**External Connections**:
- `api.bloomprotocol.ai` - Identity card storage
- `bloomprotocol.ai` - Dashboard hosting
- `clawhub.ai` - Skill recommendations (optional)

**Open Source**: All code is public at [github.com/Bloom-Protocol/bloom-discovery-skill](https://github.com/Bloom-Protocol/bloom-discovery-skill) for security audits.

## 🔍 How to Find Skills You'll Love

Once you know your supporter type, you can:
- **Search by archetype** – Find tools made for Visionaries, Explorers, etc.
- **Filter by category** – AI agents, productivity, creative tools, automation
- **Match by vibe** – Connect with creators who share your approach
- **Build your network** – Find your first 100 supporters who get what you're building

## 📊 The 5 Supporter Types

**💜 The Visionary** – First to try new tools
Try-first learner, gut-driven, early adopter. Jumps on cutting-edge stuff before it's mainstream.

**🔵 The Explorer** – Tries everything
Try-first learner, experiments widely. Finds hidden gems across all categories.

**💚 The Cultivator** – Builds communities
Study-first, analytical. Nurtures ecosystems, shares knowledge, builds lasting value.

**🟡 The Optimizer** – Refines workflows
Study-first, proven-first, measured. Doubles down on what works, maximizes productivity.

**🔴 The Innovator** – Pushes boundaries
Balanced across all spectrums. Combines conviction with experimentation.

## 🧬 Technical Details

- **Version**: 2.1.0
- **Analysis Engine**: 4-dimension taste spectrums + category mapping
- **Primary Signal**: USER.md (role, tech stack, interests)
- **Session Context**: Last ~120 messages (~5KB)
- **Processing Time**: ~2-5 seconds
- **Output Format**: Structured text + shareable dashboard URL

---

**Built by [Bloom Protocol](https://bloomprotocol.ai) 🌸**

Making supporter identity portable and provable.

*For indie devs, vibe coders, and AI builders who back great tools early.*
