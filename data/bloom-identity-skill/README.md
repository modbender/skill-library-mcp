# 🌸 Bloom Taste Finder (Bloom Identity Skill)

**AI skill that analyzes your conversations to uncover builder taste and recommend the right tools.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/unicornbloom/bloom-identity-skill)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Compatible-green)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-Published-purple)](https://clawhub.ai/skills/bloom)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

---

## 🎯 What Is This?

**Bloom Taste Finder** reveals your builder taste and recommends tools, projects, and skills based on your unique preferences and personality.

Unlike traditional recommendation systems that rely on popularity, Bloom Taste Finder analyzes nuanced patterns in user behavior to understand their unique "taste" — then finds and matches them with tools they'll genuinely love.

**Key Features:**
- 🎴 **5 Personality Types** – Discover your taste archetype (The Visionary, The Explorer, etc.)
- 🎯 **Taste-Based Recommendations** – Get personalized tool suggestions from 3 sources:
  - ClawHub Skills (200+ community-created AI agent skills)
  - Claude Code (Official Anthropic + 6 community repositories)
  - GitHub Repositories (1000+ open source projects)
- 🌱 **Self-Growing Agent** – Recommendations evolve as you interact, with USER.md integration and feedback loops
- 📊 **Taste Profile** – Understand your preferences beyond simple keywords
- 🔗 **Shareable Identity Card** – Showcase your taste profile
- 🤖 **Agent-Ready** – Works with Claude Code, OpenClaw, and other AI agents

---

## ⚡️ Quick Start

### For OpenClaw Users

```bash
/bloom
```

That's it. Get your taste profile in ~3 seconds.

### For Developers

```bash
# Clone and install
git clone https://github.com/unicornbloom/bloom-identity-skill.git
cd bloom-identity-skill
npm install

# Set up environment
cp .env.example .env
# Edit .env with your keys

# Run analysis
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/<SessionId>.jsonl \
  <userId>
```

---

## 🌟 Why Bloom Taste Finder?

### For AI Agents
Help your users discover tools they'll actually love — not just popular ones, but tools that match their unique taste and personality.

### For Users
- **Save Time** – No need to browse hundreds of tools
- **Truly Personalized** – Goes beyond popularity to match individual taste
- **Multi-Source** – Aggregates from ClawHub, Claude Code, and GitHub (200+ sources total)
- **Nuanced Understanding** – Analyzes personality, not just keywords

### For Developers
- **Easy Integration** – Simple CLI command or API call
- **High Quality** – Curated from trusted sources (Anthropic, ClawHub, GitHub)
- **Open Source** – Audit the taste algorithm yourself
- **Free to Use** – Open for all AI agents

---

## 📊 The 5 Personality Types

Bloom Taste Finder maps users to one of 5 distinct taste archetypes based on their conversation patterns:

| Type | Tagline | Characteristics |
|------|---------|-----------------|
| 💜 **The Visionary** | First to back what's next | High conviction + High intuition - Backs bold ideas early |
| 🔵 **The Explorer** | Discovers new frontiers | Low conviction + High intuition - Experiments widely |
| 💚 **The Cultivator** | Builds lasting communities | Low conviction + Low intuition - Nurtures ecosystems |
| 🟡 **The Optimizer** | Refines what works | High conviction + Low intuition - Doubles down on winners |
| 🔴 **The Innovator** | Pushes boundaries | Balanced dimensions - Combines conviction + discovery |

---

## 🎁 What You Get

Your personalized **Bloom Taste Profile** includes:

- **🎴 Personality Type** – Your taste archetype (The Trailblazer, The Curator, etc.)
- **💬 Custom Tagline** – A one-liner that captures your taste
- **📊 Taste Dimensions** – Conviction, Intuition, and Contribution scores
- **🏷️ Main Categories** – AI Tools, Productivity, Wellness, Education, Crypto, Lifestyle
- **🎯 Personalized Recommendations** – From 3 sources:
  - ClawHub Skills (200+ AI agent skills)
  - Claude Code (Official Anthropic + community skills)
  - GitHub Repositories (1000+ open source projects)
- **🔗 Shareable Dashboard** – Showcase your taste profile
- **🤖 Agent Wallet** – Ready for blockchain interactions (Coinbase CDP on Base)

---

## 🚀 How It Works

### 1. Conversation Analysis
Bloom analyzes your conversation history to understand:
- **What excites you** – Topics you discuss with passion
- **Your interests** – AI, crypto, productivity, wellness, education, lifestyle
- **How you engage** – Deep exploration vs. quick experiments
- **Your preferences** – Tools and projects you mention or recommend

### 2. Taste Profile Generation
Using multiple dimensions (Conviction × Intuition × Contribution), we map you to one of 5 personality types and identify your main interest categories:
- **AI Tools** – Agent frameworks, AI development tools
- **Productivity** – Workflow automation, productivity apps
- **Wellness** – Health tech, mindfulness tools
- **Education** – Learning platforms, educational resources
- **Crypto** – DeFi, NFTs, blockchain projects
- **Lifestyle** – Consumer apps, lifestyle tools

### 3. Multi-Source Recommendations
We match your taste profile against tools from 3 trusted sources:
- **ClawHub Skills** – 200+ community-created AI agent skills
- **Claude Code** – Official Anthropic + 6 community repositories
- **GitHub Repositories** – 1000+ open source projects across categories

Ranking by:
- **Keyword matching** – Exact and semantic similarity
- **Personality fit** – Trailblazers get cutting-edge tools
- **Category alignment** – Your interests × tool categories
- **Community validation** – What similar users love

### 4. Self-Growing Recommendations

Your agent doesn't stop at the first recommendation — it **learns and improves**:

- **USER.md Integration** — Reads your `~/.config/claude/USER.md` for declared role, tech stack, and interests. Falls back gracefully if not present.
- **Feedback Loop** — Interactions (clicks, saves, dismissals) adjust future recommendations. Engaged categories get boosted; dismissed skills get filtered out.
- **Discovery Sync** — Newly discovered skills sync to a local `bloom-discoveries.md`, building growing context.
- **TTL Refresh** — Recommendations refresh every 7 days via backend worker, pulling in new skills and applying your latest feedback.

**Signal weighting evolves over time:**
| Source | Initial Weight | After 15+ interactions |
|--------|---------------|----------------------|
| Conversation | ~60% | ~40% |
| USER.md | ~30% | ~20% |
| Feedback | ~0% | up to ~30% |

> **Safety-first:** Bloom recommends skills but **never auto-installs** them. You always decide what to install. We believe great recommendations earn trust — auto-installing unvetted code doesn't.

### 5. Identity Card & Dashboard
You get:
- A shareable taste profile dashboard
- Personalized tool recommendations with match reasons
- An on-chain agent wallet (Base network)
- A JWT-signed token for verification

**Privacy-first. Conversation-based. No wallet signatures required.**
Pure taste intelligence from how you communicate.

---

## 🔧 Installation

### Option 1: ClawHub (Recommended)

```bash
clawhub install bloom-taste-finder
```

### Option 2: Manual Install

```bash
# 1. Clone the repo
cd ~/.openclaw/workspace
git clone https://github.com/unicornbloom/bloom-taste-skill.git
cd bloom-taste-skill

# 2. Install dependencies
npm install

# 3. Set up environment
cp .env.example .env
# Edit .env with your JWT_SECRET, DASHBOARD_URL, etc.

# 4. Copy skill wrapper to OpenClaw
cp -r openclaw-wrapper ~/.openclaw/skills/bloom

# 5. Test it
/bloom
```

---

## 📖 Usage

### As an OpenClaw Skill

```bash
/bloom
```

Or use natural language:
```
"discover my taste profile"
"what's my bloom taste"
"find tools based on my taste"
"recommend tools for me"
```

### As a Standalone Tool

#### From session file (full context)
```bash
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/<SessionId>.jsonl \
  telegram:123456
```

#### From piped conversation
```bash
cat conversation.txt | \
  npx tsx scripts/run-from-context.ts --user-id telegram:123456
```

---

## 🔐 Privacy

- ✅ **Conversation-based analysis** – Analyzes your chat history only
- ✅ **No wallet signatures** – No transaction scraping required
- ✅ **No social auth required** – Twitter/Farcaster optional, not mandatory
- ✅ **Ephemeral processing** – Data not stored long-term
- ✅ **Local-first** – Runs in your OpenClaw environment
- ✅ **Open source** – Audit the taste algorithm yourself

---

## 🛠 Configuration

### Environment Variables

```bash
# Required
JWT_SECRET=your_secret_key_here
DASHBOARD_URL=https://bloomprotocol.ai

# Optional (for real agent wallet creation)
CDP_API_KEY_ID=your_coinbase_key
CDP_API_KEY_SECRET=your_coinbase_secret
NETWORK=base-mainnet  # or base-sepolia
```

### Advanced Options

See [SETUP_CDP_CREDENTIALS.md](SETUP_CDP_CREDENTIALS.md) for Coinbase CDP setup.
See [SESSION-READER-GUIDE.md](SESSION-READER-GUIDE.md) for session file analysis.

---

## 🧪 Testing

```bash
# Run full test suite
npm test

# Test with real session data
npx tsx scripts/run-from-session.ts \
  ~/.openclaw/agents/main/sessions/<SessionId>.jsonl \
  test-user-123

# Test end-to-end flow
npx tsx scripts/test-full-flow.ts
```

---

## 📊 Technical Details

| Feature | Details |
|---------|---------|
| **Version** | 2.0.0 |
| **Analysis Engine** | Conversation memory + category mapping |
| **Session Context** | Last ~120 messages (~5KB) |
| **Processing Time** | ~2-5 seconds |
| **Output Format** | Structured text + shareable dashboard URL |
| **Agent Wallet** | Coinbase CDP (Base network) |
| **Supported Platforms** | OpenClaw, CLI, API |

---

## 🐛 Troubleshooting

**"Insufficient conversation data"**
→ Need at least 3 messages. Keep chatting about what you're interested in!

**"Command not found"**
→ Verify `bloom-taste-skill` is in `~/.openclaw/workspace/` and run `npm install`

**No recommendations**
→ Recommendations depend on data source availability. Your taste profile still works!

**Wallet creation fails**
→ Check your CDP credentials in `.env`. See [SETUP_CDP_CREDENTIALS.md](SETUP_CDP_CREDENTIALS.md).

---

## 📚 Documentation

- [Installation Guide](SESSION-READER-GUIDE.md)
- [OpenClaw Integration](openclaw-wrapper/SKILL.md)
- [CDP Wallet Setup](SETUP_CDP_CREDENTIALS.md)
- [Frontend Implementation](FRONTEND-IMPLEMENTATION-GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)

---

## 🤝 Contributing

We welcome contributions! See issues or submit PRs.

Key areas:
- More personality type archetypes
- Better taste matching algorithms
- Additional data sources (Product Hunt, Hacker News, Twitter)
- Multilingual support
- Enhanced privacy features

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🌐 Links

- **Homepage**: [bloomprotocol.ai](https://bloomprotocol.ai)
- **For Agents**: [bloomprotocol.ai/for-agents](https://bloomprotocol.ai/for-agents)
- **ClawHub**: [clawhub.ai/skills/bloom](https://clawhub.ai/skills/bloom)
- **GitHub**: [github.com/unicornbloom/bloom-taste-skill](https://github.com/unicornbloom/bloom-taste-skill)
- **Dashboard**: [bloomprotocol.ai/agents](https://bloomprotocol.ai/agents)

---

**Built by [Bloom Protocol](https://bloomprotocol.ai) 🎨**

Understanding taste, one agent at a time.

*Built with [@openclaw](https://openclaw.ai), [@coinbase](https://www.coinbase.com/cloud), and [@base](https://base.org)*
