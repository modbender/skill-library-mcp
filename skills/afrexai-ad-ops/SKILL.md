---
name: Ad Ops & Cross-Channel Advertising Agent
description: Autonomous advertising operations framework for AI agents managing
  campaigns across Google Ads, Meta, LinkedIn, TikTok, and programmatic.
---

# Ad Ops & Cross-Channel Advertising Agent

Autonomous advertising operations framework for AI agents managing campaigns across Google Ads, Meta, LinkedIn, TikTok, and programmatic.

## What This Skill Does

Turns your agent into an ad ops manager that can plan, audit, optimize, and report on cross-channel advertising — without touching a dashboard.

## Capabilities

### Campaign Architecture
- **Channel Selection Matrix** — Score 8 channels (Google Search, Display, Meta, Instagram, LinkedIn, TikTok, Programmatic, YouTube) across 6 factors: CPL range, intent level, audience precision, creative complexity, minimum viable budget, time-to-signal
- **Budget Allocation Framework** — 70/20/10 rule: 70% proven channels, 20% scaling channels, 10% experimental. Rebalance weekly based on CPA trends
- **Campaign Naming Convention** — `{brand}_{channel}_{objective}_{audience}_{geo}_{date}` — enforced across all platforms for clean reporting

### Performance Audit (Run Weekly)
1. **Spend Efficiency** — Flag any campaign with CPA >2x target or ROAS <1.5x
2. **Budget Pacing** — Alert if any channel is >110% or <80% of weekly pace
3. **Creative Fatigue** — Flag ads with CTR decline >20% over 14 days
4. **Audience Overlap** — Identify cross-channel audience collision (Meta + Google remarketing competing)
5. **Landing Page Alignment** — Check bounce rate by ad-to-page combination; flag >65%

### Optimization Playbook
| Signal | Action | Timeline |
|--------|--------|----------|
| CPA rising, CTR stable | Audience fatigue — refresh targeting | 48 hours |
| CPA rising, CTR falling | Creative fatigue — new variants | 24 hours |
| High CTR, low conversion | Landing page mismatch — A/B test | 72 hours |
| Low impression share | Budget cap or bid floor — increase or restructure | Same day |
| One channel dominates ROAS | Scale budget 20% weekly until CPA ceiling | Weekly |

### Budget Framework by Company Size

| Company Size | Monthly Ad Budget | Channels | Expected Pipeline |
|-------------|-------------------|----------|-------------------|
| Startup (1-10) | $2,000-$5,000 | 2 channels max | $20K-$50K |
| Growth (11-50) | $5,000-$25,000 | 3-4 channels | $50K-$250K |
| Scale (51-200) | $25,000-$100,000 | 5-6 channels | $250K-$1M |
| Enterprise (200+) | $100,000+ | Full stack | $1M+ |

### Channel-Specific Benchmarks (B2B SaaS, 2026)

| Channel | Avg CPC | Avg CPL | Avg CTR | Conv Rate |
|---------|---------|---------|---------|-----------|
| Google Search (branded) | $2-$5 | $15-$40 | 4-8% | 8-15% |
| Google Search (non-brand) | $5-$15 | $40-$120 | 2-4% | 3-6% |
| LinkedIn Sponsored | $8-$14 | $75-$200 | 0.4-0.8% | 2-4% |
| Meta (B2B lookalike) | $1-$4 | $30-$80 | 0.8-1.5% | 3-5% |
| Programmatic Display | $0.50-$2 | $50-$150 | 0.1-0.3% | 1-2% |
| YouTube Pre-roll | $0.03-$0.08/view | $80-$200 | 0.5-1% | 1-3% |
| TikTok (B2B emerging) | $1-$3 | $40-$100 | 1-2% | 2-4% |

### Reporting Template (Weekly)
```
WEEKLY AD OPS REPORT — Week of [DATE]

TOTAL SPEND: $[X] ([+/-]% vs budget)
TOTAL LEADS: [X] (Blended CPL: $[X])
TOTAL PIPELINE: $[X] (ROAS: [X]x)

BY CHANNEL:
[Channel] — $[spend] | [leads] leads | $[CPL] CPL | [ROAS]x ROAS
[repeat per channel]

TOP PERFORMERS:
- [Campaign] — [metric] ([why it works])

UNDERPERFORMERS (action required):
- [Campaign] — [metric] → [recommended action]

NEXT WEEK PLAN:
- [Action 1]
- [Action 2]
```

### 7 Ad Ops Mistakes That Burn Budget

1. **Running identical audiences across channels** — Cross-platform audience collision inflates your own CPMs. Segment by funnel stage per channel.
2. **Ignoring frequency caps** — Showing the same ad 15+ times doesn't build brand, it builds resentment. Cap at 3-5/week for prospecting.
3. **Optimizing for clicks instead of pipeline** — CTR is vanity. Optimize for cost-per-qualified-lead or cost-per-opportunity.
4. **No creative testing cadence** — Launching 1 ad and "seeing how it goes" is not a strategy. Run 3-5 variants, kill losers weekly.
5. **Budget allocation by gut** — "LinkedIn feels right" isn't data. Allocate by CPA-to-deal-value ratio per channel.
6. **Ignoring attribution windows** — LinkedIn's 90-day influence window vs Google's 30-day click. Comparing raw ROAS across channels is misleading.
7. **Manual bid management at scale** — If you're managing >20 campaigns manually, you're leaving 15-30% efficiency on the table. Automate or agent-ify.

### Industry Ad Strategy Quick-Reference

| Industry | Top 2 Channels | Key Metric | Budget Sweet Spot |
|----------|---------------|------------|-------------------|
| Fintech | Google Search + LinkedIn | Cost per qualified demo | $15K-$40K/mo |
| Healthcare | Google Search + Programmatic | Cost per HCP engagement | $10K-$30K/mo |
| Legal | Google Search + YouTube | Cost per consultation | $8K-$25K/mo |
| Construction | Google Search + Meta | Cost per RFQ | $5K-$15K/mo |
| Ecommerce | Meta + Google Shopping | ROAS (target 4x+) | $10K-$50K/mo |
| SaaS | LinkedIn + Google Search | Cost per trial signup | $10K-$35K/mo |
| Real Estate | Meta + Google Display | Cost per showing/inquiry | $5K-$20K/mo |
| Recruitment | LinkedIn + Indeed/programmatic | Cost per application | $8K-$25K/mo |
| Manufacturing | Google Search + LinkedIn | Cost per RFQ | $5K-$15K/mo |
| Professional Services | LinkedIn + Google Search | Cost per consultation | $8K-$30K/mo |

---

## Get Industry-Specific Ad Strategy

These frameworks give you the structure. For deep industry context — compliance rules, audience segments, messaging angles, competitive positioning — grab the full context packs:

**[AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/)** — $47 each | Pick 3 for $97 | All 10 for $197

10 industries. Real operator knowledge, not recycled blog posts.

**Free tools:**
- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — Find where you're losing money
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — Configure your first AI agent in 5 minutes
