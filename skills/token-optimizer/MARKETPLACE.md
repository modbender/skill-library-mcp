# Token Optimizer for OpenClaw

## Marketplace Listing

---

### Title
**Token Optimizer - Reduce AI Costs by 97%**

### Tagline
From $1,500+/month to under $50/month in 5 minutes

### Category
- Developer Tools
- Cost Optimization
- AI/ML Tools

### Tags
`openclaw` `token-optimization` `cost-reduction` `claude` `anthropic` `haiku` `ollama` `prompt-caching`

---

### Short Description (100 chars)
Slash OpenClaw API costs by 97% with intelligent model routing, free heartbeats, and prompt caching.

### Medium Description (250 chars)
Stop burning tokens on routine tasks. Token Optimizer configures OpenClaw to use Haiku by default, routes heartbeats to free local LLMs, enables prompt caching, and adds budget controls. Go from $1,500/month to $50/month in 5 minutes.

### Full Description

**Are you watching your OpenClaw API bills climb?**

The default configuration prioritizes capability over cost - meaning you're burning expensive Sonnet tokens on simple tasks that Haiku handles perfectly.

**Token Optimizer fixes this with 4 key optimizations:**

1. **Smart Model Routing** - Haiku by default, Sonnet only when needed (92% savings)
2. **Free Heartbeats** - Route status checks to Ollama instead of paid API (100% savings)
3. **Lean Sessions** - Load 8KB instead of 50KB context per message (80% savings)
4. **Prompt Caching** - 90% discount on repeated agent prompts

**Results our users see:**

| Metric | Before | After |
|--------|--------|-------|
| Daily Cost | $2-3 | $0.10 |
| Monthly Cost | $70-90 | $3-5 |
| Context Size | 50KB | 8KB |
| Heartbeat Cost | $5-15/mo | $0 |

**What's included:**

- Automated configuration optimizer
- Pre-built workspace templates (SOUL.md, USER.md)
- Optimization prompt rules
- Ollama heartbeat setup
- Budget and rate limit controls
- Verification tools
- Installation scripts (Windows + Unix)

**Requirements:**
- Python 3.8+
- OpenClaw
- Ollama (optional, for free heartbeats)

**Setup time:** 5 minutes

---

### Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Personal** | $29.99 | Single user, 1 year updates |
| **Team** | $99.99 | Up to 5 users, priority support |
| **Enterprise** | Contact | Unlimited users, custom integration |

**30-day money-back guarantee**

---

### Screenshots/Media

1. **Before/After Cost Comparison** - Bar chart showing monthly costs
2. **Analyzer Output** - Terminal showing optimization opportunities
3. **Verification Results** - Checklist of successful optimizations
4. **Config Preview** - Optimized openclaw.json configuration

---

### Support

- Documentation: docs.tokenoptimizer.ai
- Email: support@tokenoptimizer.ai
- Response time: 24 hours

---

### Reviews Template

> "Cut our OpenClaw bill from $200/month to $8. Setup was painless."
> - Developer, SaaS Startup

> "The Ollama heartbeat alone saves us $15/month. Everything else is bonus."
> - Founder, AI Agency

> "Finally, a tool that understands not everything needs Opus."
> - Technical Lead, Enterprise

---

### Changelog

**v1.0.8** (2026-02-12) - Quality & Provider Support
- **NEW:** Configurable heartbeat providers: ollama, lmstudio, groq, none
- **NEW:** Rollback command to list and restore config backups
- **NEW:** Health check command for quick system status
- **NEW:** Diff preview in dry-run mode (colored unified diff)
- **NEW:** `--no-color` flag and `NO_COLOR` env var support
- **IMPROVED:** Shared colors module (deduplicated code)
- **IMPROVED:** Version single source of truth across all files
- **IMPROVED:** Extended marketplace triggers (+10 new search terms)
- **FIX:** License consistency (MIT everywhere)
- **FIX:** Version sync (was showing 1.0.0 in 7 files)

**v1.0.7** (2026-02-08) - Security & Savings Report
- **SECURITY:** Removed hidden HTML comment from SKILL.md (ClawHub review finding)
- **SECURITY:** Dry-run is now the default - use `--apply` to make changes
- **SECURITY:** User confirmation before downloading Ollama model (~2GB)
- **SECURITY:** Existing user config files are no longer overwritten
- **NEW:** 7-day savings report shows accumulated cost savings with weekly breakdown
- **BREAKING:** `--dry-run` flag replaced by `--apply` (dry-run is now default)

**v1.0.0 - v1.0.6** (Initial Releases)
- Model routing optimization (Haiku default)
- Ollama heartbeat configuration
- Prompt caching setup
- Session initialization rules
- Budget and rate limit controls
- Cross-platform CLI (Windows, macOS, Linux)
- Workspace templates
- Verification tools
- Ko-fi support integration
- Marketing materials
