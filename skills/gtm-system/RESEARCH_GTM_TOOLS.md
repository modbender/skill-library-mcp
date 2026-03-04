# Developer-Focused GTM Tools Research

**Date:** 2026-02-06
**For:** Expanso/Prometheus GTM Strategy

## Executive Summary

I researched the landscape of developer-focused GTM, sales intelligence, and intent signal platforms. This document catalogs the tools, their pricing where available, and recommendations for Expanso's stage and needs.

---

## Tool Categories

### 1. Developer-Specific GTM Intelligence

These are purpose-built for developer tool companies:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Reo.Dev** | Tracks 625M+ developer signals: npm installs, GitHub activity, docs visits, API usage, cloud sign-ups. Deanonymizes sign-ups, predicts buyers. | Enterprise ($$$) | ⭐ **TOP PICK** for dev tools. Purpose-built for companies like Expanso. |
| **Common Room** | Aggregates signals from 50+ sources, AI-powered identity resolution, community listening. "Person360" profiles. | Enterprise | Good but broader than just devs. More for community-led growth. |

### 2. Product-Led Growth (PLG) Intelligence

Track in-product behavior to identify sales-ready users:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Koala** | Website visitor identification, product usage tracking, real-time alerts. "360-view" for sales. | Freemium + Paid | ✅ Good for tracking free tier users |
| **Pocus** | AI recommendations for reps, intent signals, automated guidance. Enterprise-focused. | Enterprise | For larger sales teams |
| **UserMotion** | Predictive lead scoring, PQL scoring, playbooks. Cross-channel intent signals. | Free trial + Paid | ✅ Good for PQL identification |
| **Heap** (now Contentsquare) | Product analytics, session replay, behavioral insights. | Enterprise | More analytics than GTM |
| **June.so** | ❌ Acquired by Amplitude | - | Use Amplitude instead |

### 3. Data Enrichment & Prospecting Platforms

General B2B data and outreach:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Clay** | 150+ data providers, AI agents (Claygent), workflow automation. Industry darling. | $149-$800/mo | ⭐ **TOP PICK** for enrichment. Extremely powerful. |
| **Apollo.io** | B2B database, email sequences, engagement tracking. | Free tier + $49/mo+ | ✅ Good value, strong free tier |
| **Clearbit** | ❌ Acquired by HubSpot | - | Use HubSpot or alternatives |
| **BuiltWith** | Technographic data (what tech companies use). | Paid | Useful for finding prospects using specific tech |

### 4. ICP & Account Scoring

Model your ideal customer and score accounts:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Keyplay** | ICP modeling, account scoring, "whitebox" intent (transparent). | $18K-$29K/yr | For funded companies with sales teams |
| **Bombora** | B2B intent data from publisher Co-op, topic-level signals. | Enterprise | Industry standard but expensive |

### 5. Community & Social Listening

Monitor where developers talk:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Syften** | Real-time keyword monitoring across Reddit, HN, Twitter, Indie Hackers, forums. Webhook support. | $29-$79/mo | ⭐ **TOP PICK** for community monitoring. Very dev-focused. |
| **F5Bot** | Free alerts for Reddit, HN, Lobsters mentions. | **FREE** | ✅ Start here - zero cost |
| **Mention** | Social listening, analytics, social management. Broader than dev. | $41-$149/mo | More for brands than dev tools |

### 6. Website Visitor Identification

See which companies visit your site:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Leadfeeder** (Dealfront) | IP-based company identification, 50+ filters, CRM sync. | $99-$1199/mo | Good but generic |
| **Reo.Dev** | Combines this with developer-specific signals | Enterprise | Better for dev tools |
| **Koala** | Lighter weight, focuses on high-intent | Freemium | ✅ Good starting point |

### 7. Network-Based GTM

Leverage your existing connections:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Commsor** | Maps network connections, referral programs, warm intros. | Contact sales | Interesting for relationship-driven sales |

### 8. Workflow Automation

Connect everything together:

| Tool | What It Does | Pricing | Recommendation |
|------|--------------|---------|----------------|
| **Clay** | Best-in-class for GTM workflows | $149/mo+ | ⭐ Already mentioned |
| **n8n** | Open-source workflow automation | Self-host free | ✅ Good for custom integrations |
| **Zapier** | General automation | $19/mo+ | Less GTM-specific |

---

## Recommended Stack for Expanso

### Tier 1: Start Here (Low/No Cost)

These can be set up immediately:

| Tool | Cost | Purpose |
|------|------|---------|
| **Custom GTM System** (built today) | $0 | Pipeline tracking, daily tasks, follow-ups |
| **F5Bot** | FREE | Reddit/HN/Lobsters alerts for "bacalhau", competitors |
| **Apollo.io Free** | $0 | Contact lookup, basic sequences |
| **BuiltWith Free** | $0 | Check what tech prospects use |

### Tier 2: Add When Growing (~$100-300/mo)

| Tool | Cost | Purpose |
|------|------|---------|
| **Syften** | $29-79/mo | Better community monitoring with webhooks |
| **Koala** | $99/mo+ | Website visitor identification |
| **Clay Starter** | $149/mo | Data enrichment, AI research |

### Tier 3: Scale Up (~$500-2000/mo)

| Tool | Cost | Purpose |
|------|------|---------|
| **Reo.Dev** | Contact sales | Full developer intent platform |
| **Apollo.io Basic** | $49/mo | More sequences, better data |
| **Common Room** | Contact sales | Community intelligence at scale |

### Tier 4: Enterprise

| Tool | Purpose |
|------|---------|
| **Reo.Dev + Keyplay + Clay** | Full stack for serious GTM motion |
| **Bombora** | Intent data layer |
| **Pocus** | AI sales guidance |

---

## Specific Recommendations for Expanso

### Why Reo.Dev Makes Sense (Eventually)

Reo.Dev is specifically built for developer tool companies. Their signals include:
- **npm/package installs** - See who's installing Bacalhau
- **GitHub activity** - Stars, forks, issues on your repo
- **Docs visits** - Who's reading your documentation
- **API/SDK usage** - First-party telemetry
- **Cloud sign-ups** - Free tier activity
- **Job postings** - Companies hiring for skills you solve

This is 10x more relevant than generic B2B intent data for a company like Expanso.

**BUT:** It's enterprise-priced. Save for when you have:
- Dedicated sales/BD person
- Budget for tooling
- Clear ICP definition

### What to Do Today

1. **Use the GTM system I built** - It's working now, $0/mo
2. **Sign up for F5Bot** - Free, takes 2 minutes
3. **Create Apollo.io account** - Free tier is generous
4. **Add Syften later** - When you want Slack/webhook alerts

### Content/Community Signals to Monitor

For Bacalhau/Expanso, watch for discussions about:
- "distributed computing" on HN/Reddit
- "compute over data" mentions
- "edge computing" + "data processing"
- Competitor mentions: Ray, Dask, Spark (for specific use cases)
- "IPFS" + "compute" combinations
- "wasm" / "webassembly" + "cloud" or "distributed"
- Job postings for "data engineer" + "distributed"

---

## Tools That Shut Down / Got Acquired

For awareness - these were popular but no longer independent:

| Tool | Status |
|------|--------|
| Orbit.love | Appears to be down (DNS error) |
| Calixa | Acquired/shut down |
| June.so | Acquired by Amplitude |
| Clearbit | Acquired by HubSpot |
| Correlated | Appears inactive |
| Toplyne | Appears inactive |

The PLG/GTM space has significant churn. Bet on established players or build custom.

---

## Open-Source Alternatives

If you want to self-host more:

| Tool | What It Does |
|------|--------------|
| **PostHog** | Product analytics (open-source) |
| **Matomo** | Web analytics (self-hosted) |
| **Plausible** | Simple analytics |
| **n8n** | Workflow automation |
| **Custom scripts** | What we built today |

---

## Integration with Our GTM System

The custom system I built can be extended to:

1. **Pull from Syften webhooks** - Ingest signals automatically
2. **Sync with Apollo.io** - Export contacts, import enrichment
3. **Connect to Clay** - Use their data, push to our DB
4. **Alert via Telegram** - Already working

### Adding Syften Integration (Example)

When you're ready, add to the GTM system:
```python
# In gtm.py, add endpoint to receive Syften webhooks
@app.route('/webhook/syften', methods=['POST'])
def syften_webhook():
    signal = request.json
    # Save to signals table
    save_signal(source='syften', data=signal)
    return 'OK'
```

---

## Summary

**Immediate actions:**
1. ✅ GTM system is running (done)
2. ⏳ Sign up for F5Bot (free)
3. ⏳ Create Apollo.io account (free)

**Next month:**
1. Evaluate Syften ($29-79/mo) for better monitoring
2. Consider Koala for website visitor ID

**When you raise / have budget:**
1. Demo Reo.Dev - they're the clear winner for dev tools
2. Consider Clay for enrichment

**Long-term:**
1. Build vs. buy decision based on what works
2. The custom system we built is a foundation you own

---

## Links

- Reo.Dev: https://www.reo.dev/
- Common Room: https://www.commonroom.io/
- Koala: https://getkoala.com/
- Clay: https://clay.com/
- Syften: https://syften.com/
- F5Bot: https://f5bot.com/ (FREE)
- Apollo.io: https://www.apollo.io/
- Keyplay: https://keyplay.io/
- UserMotion: https://usermotion.com/
- Leadfeeder: https://www.leadfeeder.com/
- Bombora: https://bombora.com/
- Commsor: https://www.commsor.com/
- n8n: https://n8n.io/
