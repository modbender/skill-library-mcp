# 🔥 ZeroRules — Stop the API Wallet Assassin

**Intercept deterministic tasks before they burn tokens. Math, time, currency, files, dates → $0.**

Every time your OpenClaw uses Claude Opus to calculate `247 × 18`, you pay ~$0.01 for something a calculator does in 0ms. ZeroRules catches these queries and resolves them locally. Zero tokens. Zero latency.

## The Problem

OpenClaw sends *everything* to your LLM — including tasks that don't need AI:

| Query | Without ZeroRules | With ZeroRules |
|-------|-------------------|----------------|
| "247 × 18" | ~850 tokens, ~$0.01 | **0 tokens, $0** |
| "Time in Tokyo" | ~1,200 tokens, ~$0.01 | **0 tokens, $0** |
| "$100 to EUR" | ~1,500 tokens, ~$0.01 | **0 tokens, $0** |
| "List ~/projects" | ~900 tokens, ~$0.01 | **0 tokens, $0** |
| "Days until Christmas" | ~1,000 tokens, ~$0.01 | **0 tokens, $0** |

These add up. 50 deterministic queries/day × 30 days = **1,500 intercepted calls/month = ~$12-18 saved** just from the built-in rules.

## Install (30 seconds)

### Option 1: ClawHub (recommended)

```bash
clawhub install zero-rules
```

### Option 2: Manual

```bash
cd ~/clawd/skills   # or ~/.openclaw/skills
git clone https://github.com/deeqyaqub1-cmd/zero-rules-openclaw zero-rules
```

### Option 3: Copy-paste

Create `~/clawd/skills/zero-rules/` and copy `SKILL.md` + `rules.js` into it. That's it.

**No dependencies. No API keys. No config. Just Node.js (which OpenClaw already requires).**

## How It Works

1. You ask OpenClaw: *"What's 247 × 18?"*
2. OpenClaw sees ZeroRules is active → runs `rules.js` with your query
3. `rules.js` matches the math pattern → computes `4,446` in 2ms
4. OpenClaw returns the result **without calling the LLM**
5. You see: **4,446** 🔥 ZeroRules | math | ~850 tokens saved

If ZeroRules can't handle it (e.g., *"Write a proposal for Sarah"*), it returns `matched: false` and OpenClaw proceeds with the LLM normally. Zero interference.

## 5 Built-in Rules (Free)

| Rule | Catches | Examples |
|------|---------|----------|
| 🧮 **Math** | Arithmetic, percentages, sqrt, powers | "15% of 200", "sqrt 144", "2^10" |
| 🕐 **Time** | Current time in 60+ cities | "Time in Tokyo", "What time in London" |
| 💱 **Currency** | 20+ currencies, live + offline rates | "$100 to EUR", "500 GBP to JPY" |
| 📁 **Files** | Directory listings (read-only, sandboxed) | "List ~/projects", "What's in src/" |
| 📅 **Dates** | Today, tomorrow, days-until, day-of-week | "Days until Christmas", "What day is March 15" |

## Commands

```
/zero-rules          → Show session stats (matches, tokens saved, cost saved)
/zero-rules test <msg> → Test if a message would be intercepted
```

## Security

- **File operations are read-only** — ZeroRules only lists directories, never reads/writes/deletes files
- **No data leaves your machine** except currency API calls (exchangerate.host, free, no key)
- **No API keys required** — works entirely locally for math, files, and dates
- **3-second timeout** on all network calls — if they fail, falls back to LLM
- **No telemetry** — session stats stored locally in `~/.zerorules-session.json`
- **Open source** — read every line before you install

## Pro ($9/mo)

Free tier covers the 5 built-in rules. [ZeroRules Pro](https://cascadeai.dev/pro) unlocks:

- ♾️ Unlimited custom rules (regex + handler)
- 📊 Persistent savings dashboard (across sessions)
- 📧 Weekly cost reports via email/Telegram
- 🔧 Priority support + rule templates
- 🧩 Community rule library

## Verify It Works

After installing, ask your OpenClaw:

> "What's 1337 × 42?"

If you see `🔥 ZeroRules | math | ~850 tokens saved` — you're live.

## FAQ

**Q: Does this slow down my agent?**
No. Rule matching takes <5ms. LLM calls take 2-6 seconds. ZeroRules makes matched queries *faster*.

**Q: What if it intercepts something it shouldn't?**
It won't. Rules only match explicit patterns (math expressions, "time in X", etc.). Ambiguous queries always fall through to the LLM.

**Q: Does it work with local models (Ollama)?**
Yes, but the savings are smaller since local inference is free. ZeroRules still helps with latency — 2ms vs 2s.

**Q: How is this different from model routing (Lynkr, save-money skill)?**
Model routing sends simple queries to *cheaper* models. ZeroRules skips the model *entirely*. No tokens consumed at all.

---

**Built for the OpenClaw community. Stop feeding calculators to Opus.**

[GitHub](https://github.com/deeqyaqub1-cmd/zero-rules-openclaw) · [ClawHub](https://clawhub.com/deeqyaqub1-cmd/zero-rules) · [Pro](https://cascadeai.dev/pro) · [Discord](https://discord.gg/cascadeai)
