# Expanso 2-Week GTM Sprint Plan
## Anchored on Gerstner's "Data Transformation Wins" Thesis (All-In E209, Feb 7 2026)

**Owner:** Prometheus (aronchick)  
**Sprint dates:** Feb 10–21, 2026  
**North star:** 5 qualified demo calls booked, 2 pipeline conversations started

---

## 1. Narrative Framework

### The Thesis (Gerstner's Words, Our Positioning)

Gerstner's core claim: **data transformation companies are the AI beneficiaries.** Databricks growing 60%+, Snowflake re-accelerating, ClickHouse re-accelerating — all because "all these AI tools rely on data and data transformation."

**Expanso's angle:** Snowflake and Databricks handle data transformation *in the warehouse*. Expanso handles it *at the source* — before data moves. We're not competitive; we're the missing layer that makes their platforms cheaper and faster.

### Key Messages

| Audience | Message |
|----------|---------|
| **Data engineers** | "Filter 50-70% of your data before it hits Snowflake. Same insights, half the bill." |
| **Platform/infra leads** | "Distributed compute at the edge — process where data lives instead of moving it all to cloud." |
| **VPs/Directors** | "Gerstner says data transformation is the winning layer. Your current stack transforms in the warehouse. We transform at the source." |
| **Investors/analysts** | "Expanso is the edge complement to the Snowflake/Databricks stack — the data transformation layer Gerstner says wins." |

### Three Narrative Pillars

**1. The Data Transformation Supercycle**  
Gerstner: *"All these AI tools rely on data and data transformation... that's very different than a thin application layer sitting on top of a CRUD database."*  
→ Expanso is a data transformation company, not an application layer. We sit in the winning part of the stack.

**2. The Agent Multiplier**  
J-Cal: *"We had to open up SaaS accounts for these four agents. Our SaaS spend went up."*  
Freeberg: *"The profit pool available to the agentic layer is increasing."*  
→ Agents multiply data demand exponentially. Every agent needs fresh, processed data. Expanso processes it at the edge before it floods your warehouse. Without edge filtering, your Snowflake bill scales linearly with agent count.

**3. The Profit Pool Shift**  
Gerstner: *"The profit pool available to software is decreasing."*  
Sacks: *"The risk is they become an old layer of the stack."*  
→ The value is moving to infrastructure that actually transforms data. Thin SaaS wrappers lose. Compute layers that do real work win. Expanso does real distributed compute.

### Competitive Positioning

| | Expanso | Cribl | DIY (K8s) | Cloud-native |
|---|---------|-------|-----------|-------------|
| **Scope** | General distributed compute | Observability routing only | Unlimited but painful | Vendor-locked |
| **Edge-native** | ✅ Built for it | Partial | Manual | ❌ |
| **AI/ML workloads** | ✅ | ❌ | DIY | Limited |
| **Setup time** | Hours | Days | Weeks | Days |
| **Lock-in** | None | Low | None | High |

**vs. Cribl specifically:** Cribl filters observability data (logs, metrics). Expanso runs arbitrary compute at the edge — data transformation, ML inference, ETL, aggregation. Cribl is a router; Expanso is a compute platform.

---

## 2. Week 1 Plan (Feb 10–14)

### Monday Feb 10 — Foundation Day

| Time | Task | Owner | Output |
|------|------|-------|--------|
| AM | Finalize demo pipeline: raw IoT/log data → Expanso edge filter → Snowflake ingestion with before/after cost numbers | Eng | Working demo with real metrics |
| AM | Build prospect list: 25 companies running Snowflake/Databricks at scale (500-5000 employees, data-intensive verticals) | GTM | Spreadsheet with name, company, title, LinkedIn, email |
| PM | Write anchor blog post draft (see Section 6 for full outline) | Content | Draft in Google Docs |
| PM | Draft 3 cold email variants (see Section 5) | GTM | Templates ready to personalize |

**Prospect list sources:**
- LinkedIn Sales Navigator: "data engineer" + "Snowflake" or "Databricks" in profile
- Snowflake Partner Directory companies
- Job boards: companies hiring for "data cost optimization" or "data pipeline" roles
- BuiltWith/Stackshare for Snowflake/Databricks usage signals

**Target verticals (highest data volume pain):**
1. Fintech (transaction data, compliance logs)
2. AdTech (event streams, bid logs)
3. IoT/Manufacturing (sensor data, telemetry)
4. Healthcare (device data, EHR pipelines)
5. E-commerce (clickstream, inventory)

### Tuesday Feb 11 — Publish & Start Outreach

| Time | Task | Owner | Output |
|------|------|-------|--------|
| 9 AM | Publish "The Data Transformation Supercycle" blog post | Content | Live URL |
| 10 AM | Post X thread (see social drafts below) | GTM | Thread live |
| 10:30 AM | Post LinkedIn article/post | GTM | Post live |
| 11 AM | Submit to Hacker News | GTM | HN link |
| PM | Send first 15 cold emails (Variant A: cost pain) | GTM | 15 sent, tracked in CRM |
| PM | Engage All-In podcast discussion threads on X, Reddit | GTM | 5+ comments posted |

### Wednesday Feb 12 — Demo & More Outreach

| Time | Task | Owner | Output |
|------|------|-------|--------|
| AM | Record 10-min demo video (see demo outline below) | Eng | Video file ready |
| AM | Send 10 more cold emails (Variants B & C) | GTM | 25 total sent |
| PM | Edit and upload demo video (YouTube unlisted + landing page embed) | Content | Live demo URL |
| PM | Post in r/dataengineering, r/snowflake, dbt Slack, Data Engineering Weekly | GTM | 3-5 community posts |

### Thursday Feb 13 — Follow-up & Engagement

| Time | Task | Owner | Output |
|------|------|-------|--------|
| AM | Follow up on any email replies, schedule demos | GTM | Replies tracked |
| AM | Second social push: share demo video clip on X/LinkedIn | Content | Posts live |
| PM | Engage with all blog/social/HN comments | GTM | Responses posted |
| PM | Reach out to 5 existing network contacts for informal feedback calls | GTM | Outreach sent |

### Friday Feb 14 — Learn & Prep

| Time | Task | Owner | Output |
|------|------|-------|--------|
| AM | Compile Week 1 metrics (see Section 4) | GTM | Dashboard updated |
| AM | Document all feedback: what resonated, what didn't, objections heard | GTM | Feedback doc |
| PM | Refine messaging based on feedback | Content | Updated templates |
| PM | Build Week 2 target list (25 more prospects, informed by Week 1 learnings) | GTM | List ready |

### Demo Outline (10 minutes)

**0:00–1:30 — The Problem**
- Show a typical data pipeline: sources → cloud warehouse → analytics
- Show the bill: "This company ingests 10TB/day into Snowflake. Monthly cost: $X"
- "But 60% of this data is noise — debug logs, duplicate events, low-value telemetry"

**1:30–3:00 — The Expanso Approach**
- Architecture diagram: sources → Expanso edge nodes → filtered data → Snowflake
- "Process where data lives. Filter before you move."

**3:00–7:00 — Live Demo**
- Show Expanso running on edge node
- Ingest raw data stream (IoT sensor data or log stream)
- Apply transformation: filter, aggregate, enrich
- Show output: 60% reduction in data volume
- Show Snowflake ingestion: same insights, fraction of the data

**7:00–9:00 — Results**
- Before/after cost comparison
- Before/after query performance (less data = faster queries)
- Before/after pipeline reliability

**9:00–10:00 — CTA**
- "Want to see this on your data? 30-minute POC with your actual pipeline."
- Link to schedule

### Social Drafts

**X Thread (Tuesday):**

> 🧵 Brad Gerstner just dropped the clearest thesis on who wins in AI infrastructure.
>
> His answer? Data transformation companies.
>
> "All these AI tools rely on data and data transformation." — @altaboraham
>
> Here's what this means for your data stack: (1/7)

> Snowflake re-accelerating. Databricks growing 60%+. ClickHouse re-accelerating.
>
> Why? Because AI doesn't run on vibes. It runs on clean, transformed data.
>
> The transformation layer is THE winning layer. (2/7)

> But here's the gap nobody's talking about:
>
> All that transformation happens AFTER data lands in your warehouse.
>
> You're paying to move 100% of your data, then filtering 60% of it out.
>
> That's like shipping your entire house to sort through your closet. (3/7)

> What if you transformed data WHERE IT LIVES?
>
> Filter at the source. Aggregate at the edge. Send only what matters.
>
> Same insights. 50%+ less warehouse spend. (4/7)

> This is what @expansaboraham does.
>
> Distributed compute at the edge. Process data before it moves.
>
> Not replacing Snowflake/Databricks — making them cheaper and faster. (5/7)

> And with agents multiplying data demand (J-Cal: "our SaaS spend went UP because of agents"), edge processing isn't optional anymore.
>
> Every agent generates data. Without edge filtering, your cloud bill scales linearly with agent count. (6/7)

> Gerstner: "The profit pool available to software is decreasing."
>
> The value is shifting to infrastructure that does real work — real data transformation.
>
> Full analysis: [blog post link]
>
> If you're spending >$50K/mo on Snowflake/Databricks, DM me. (7/7)

**LinkedIn Post (Tuesday):**

> Brad Gerstner just made the case that data transformation companies are the clear AI beneficiaries.
>
> Databricks growing 60%+. Snowflake re-accelerating. The thesis: "All these AI tools rely on data and data transformation."
>
> But there's a $50B blind spot: all that transformation happens after you've already paid to move the data to the cloud.
>
> What if you could filter 50-70% of your data at the source — before it hits your warehouse?
>
> Same insights. Half the infrastructure cost. Faster pipelines.
>
> That's what we're building at Expanso — distributed data transformation at the edge.
>
> Not replacing Snowflake or Databricks. Making them dramatically more efficient.
>
> We just published our analysis of Gerstner's thesis and what it means for data infrastructure: [link]
>
> #DataEngineering #AI #Infrastructure

**LinkedIn Post 2 (Thursday — demo share):**

> We recorded a 10-minute demo showing how edge-first data processing cuts Snowflake ingestion costs by 58%.
>
> No slides. Just a real pipeline, real data, real before/after numbers.
>
> [demo link]
>
> If your data infrastructure bill keeps climbing, this is worth 10 minutes.

**X Post (Thursday — demo):**

> Just published: 10 minutes that could cut your Snowflake bill in half.
>
> Real demo. Real data. Real cost reduction.
>
> No pitch deck. Just a pipeline that filters 60% of data before it hits your warehouse.
>
> [link]

**X Post (Friday — community engagement):**

> Data engineering teams: genuine question.
>
> What % of the data you ingest into your warehouse actually gets used in downstream queries/models?
>
> We're seeing 40-70% of ingested data is effectively noise.
>
> Curious if that matches your experience. 👇

---

## 3. Week 2 Plan (Feb 17–21)

### Monday Feb 17 — Content & Outreach Wave 2

| Task | Output |
|------|--------|
| Publish "Why Every AI Agent Needs a Data Layer" (see outline below) | Live blog post |
| Send 15 cold emails to new prospect list (refined messaging from Week 1 feedback) | 15 sent |
| Follow up on all Week 1 emails that didn't reply (gentle bump) | Follow-ups sent |
| Social push: share new blog post on X/LinkedIn | Posts live |

**"Why Every AI Agent Needs a Data Layer" — Outline:**

1. **The agent explosion** — J-Cal's quote about agents driving SaaS spend up. Every enterprise is deploying agents. Each agent needs data.
2. **The data scaling problem** — 4 agents = 4x data demand. 40 agents = 40x. Your warehouse bill scales with agent count unless you filter upstream.
3. **Why agents need edge processing** — Agents need fresh, clean, contextual data. Not a data lake dump. Edge processing delivers exactly what the agent needs, nothing more.
4. **The architecture** — Sources → Expanso edge transform → Agent-ready data feeds. Show how this plugs into LangChain, CrewAI, etc.
5. **The math** — Cost model: 10 agents × current data pipeline cost vs. 10 agents × edge-filtered pipeline cost.
6. **CTA** — "Your agent fleet is growing. Your data layer should be ready."

### Tuesday Feb 18 — Partnership Outreach

| Partner | Action | Why |
|---------|--------|-----|
| **Snowflake** | Apply to Technology Partner Program + email partner team | "Reduce customer ingestion costs, increase Snowflake stickiness" |
| **Databricks** | Apply to Technology Partner Program + email partner team | Same angle — complementary edge layer |
| **Confluent** | Email partnerships (warm intro if possible) | Kafka + edge preprocessing = natural pairing |
| **dbt Labs** | Email community/partnerships team | dbt transforms in warehouse; Expanso transforms before warehouse. Story writes itself. |

**Partnership pitch (1-liner for all):**
> "We reduce your customers' data infrastructure costs 50%+ by filtering at the source, which makes them happier and stickier on your platform. 15 minutes to show you how?"

### Wednesday Feb 19 — Demo Calls

| Task | Output |
|------|--------|
| Run demo calls booked from Week 1 (target: 3-5) | Call notes, next steps documented |
| Send 10 more cold emails | 50 total across both weeks |
| Post demo video clips to X/LinkedIn (30-60 sec cuts) | Social posts live |

**Demo call structure (30 min):**
- 5 min: "What does your data pipeline look like today? What's your monthly spend?"
- 5 min: "Here's what we see across companies like yours" (the 60% waste stat)
- 10 min: Live demo on their use case (or closest analog)
- 5 min: "Here's what the savings would look like for you"
- 5 min: Next steps — POC proposal, technical deep-dive, or intro to decision-maker

### Thursday Feb 20 — Analyst/Investor Outreach

| Target | Action | Angle |
|--------|--------|-------|
| **Altimeter Capital** (Gerstner's fund) | Cold email or warm intro | "We're building exactly what you described — the data transformation layer, but at the edge" |
| **a16z Infra team** | Email | Edge compute + AI infrastructure thesis |
| **Bessemer (Cloud Index)** | Email | Cloud efficiency play maps to their portfolio thesis |
| **Redpoint** | Email | Data infrastructure focus |
| **Industry analysts** (Gartner, Forrester) | Request briefing | "Edge data processing for AI" category creation |

**Investor/analyst email template:**

> Subject: The edge data transformation layer Gerstner described
>
> Hi [name],
>
> Brad Gerstner's thesis on the All-In pod last week — that data transformation companies are the clear AI beneficiaries — maps exactly to what we're building at Expanso.
>
> The gap: Snowflake/Databricks transform data after ingestion. Expanso transforms it at the source — cutting ingestion costs 50%+ while delivering cleaner data faster.
>
> We're seeing [X metric: pipeline interest, demo requests, early customer traction].
>
> Worth 15 minutes? Happy to share the technical architecture and early traction.
>
> [name]

### Friday Feb 21 — Sprint Retro & Plan Forward

| Task | Output |
|------|--------|
| Compile all metrics (see Section 4) | Sprint dashboard |
| Document every piece of feedback, objection, and insight from all conversations | Learning doc |
| Decision: double down on outbound, content, or pivot positioning? | Week 3+ plan |
| Update strategy doc with validated/invalidated assumptions | Updated strategy |
| If traction: draft 30-day plan. If not: draft pivot hypotheses. | Next plan |

---

## 4. Metrics & KPIs

### Daily Tracking

| Metric | Where to Track |
|--------|---------------|
| Emails sent / opened / replied | CRM or email tool (Apollo, Instantly, etc.) |
| Blog post views | Google Analytics / hosting platform |
| Social impressions & engagement | X Analytics, LinkedIn Analytics |
| Demo calls booked | Calendar + CRM |
| Inbound inquiries (email, DM, form fills) | Inbox + CRM |

### Weekly KPIs

| Metric | Week 1 Target | Week 2 Target |
|--------|--------------|--------------|
| Cold emails sent | 25 | 25 (50 cumulative) |
| Email response rate | >5% (>1 reply) | >5% |
| Blog post views | 500+ | 300+ (second post) |
| Demo calls booked | 3 | 5 cumulative |
| Demo calls completed | 0 (booked for W2) | 3-5 |
| Partnership convos started | 0 | 2+ |
| Qualified pipeline conversations | 1-2 | 3-5 cumulative |
| Community posts/comments | 10+ | 5+ |

### Sprint Success Criteria (Feb 21 EOD)

| Outcome | Grade |
|---------|-------|
| **5+ demo calls completed** with qualified prospects | 🟢 A — Sprint worked, scale it |
| **3-4 demo calls** + clear signal on messaging | 🟡 B — Iterate and continue |
| **1-2 demo calls** + some content traction | 🟠 C — Messaging needs work, keep testing |
| **0 demo calls**, no inbound, no engagement | 🔴 D — Fundamental positioning problem, regroup |

### Leading Indicators (Check Daily)

- **Email open rate >40%** → Subject lines working
- **Email reply rate >5%** → Message resonates
- **Blog post shared >10 times** → Narrative has legs
- **Any inbound "how do I try this?"** → Product-market fit signal
- **Demo no-show rate <30%** → Prospect quality is real

---

## 5. Cold Email Templates

### Variant A: Cost Pain (Lead with savings)

> **Subject:** Your Snowflake bill is 50% noise
>
> Hi [First Name],
>
> I noticed [Company] is running [Snowflake/Databricks] at scale — [evidence: job posting, tech stack signal, LinkedIn mention].
>
> Quick question: what percentage of the data you ingest actually gets used downstream?
>
> We're seeing 50-70% of ingested data is effectively noise — debug logs, duplicate events, low-value telemetry. Companies pay to move it, store it, and query around it.
>
> Expanso processes and filters data at the source before it hits your warehouse. Same insights, 50%+ less ingestion cost.
>
> Worth a 15-minute demo? I can show you what this looks like on a pipeline similar to yours.
>
> [Name]
>
> P.S. Brad Gerstner just made the case on All-In that data transformation is THE winning layer in AI infrastructure. We agree — but think it should happen at the edge, not just in the warehouse. [link to blog post]

### Variant B: Complexity Pain (Lead with simplicity)

> **Subject:** Simpler data pipelines, lower costs
>
> Hi [First Name],
>
> Running data pipelines at scale is a mess — dozens of services, brittle orchestration, and costs that grow faster than your data.
>
> We built Expanso to fix this: distributed compute that runs wherever your data lives. Define a transformation once, run it at the edge, send only clean data downstream.
>
> Teams using Expanso typically:
> - Cut data ingestion costs 50%+
> - Reduce pipeline complexity (fewer services, less orchestration)
> - Get fresher data (processed at source, not batch-delayed)
>
> I'd love to show you a 10-minute demo. Any interest?
>
> [Name]

### Variant C: Agent-Readiness (Lead with AI/agent angle)

> **Subject:** Your data layer isn't ready for AI agents
>
> Hi [First Name],
>
> As [Company] ramps up AI and agents, your data infrastructure is about to get hit with a demand multiplier. Every agent needs clean, fresh, contextual data — and most pipelines weren't built for that scale.
>
> As Gerstner said on All-In last week: "All these AI tools rely on data and data transformation." The winners are the companies whose data layer can keep up.
>
> Expanso processes data at the edge — filtering, transforming, and enriching it before it moves to your warehouse or agent layer. Result: agents get better data, faster, at a fraction of the infrastructure cost.
>
> 15 minutes to show you how this fits your stack?
>
> [Name]

### Follow-Up Email (Send 3 days after no reply)

> **Subject:** Re: [original subject]
>
> Hi [First Name],
>
> Just bumping this — I know inboxes are brutal.
>
> TL;DR: we help companies cut data pipeline costs 50%+ by processing at the edge before data hits the warehouse.
>
> If the timing is wrong, no worries. If you're curious, here's a 10-min demo that shows exactly how it works: [demo video link]
>
> [Name]

---

## 6. Blog Post Outline: "The Data Transformation Supercycle"

**Target length:** 1,800-2,200 words  
**Publish:** Tuesday Feb 11, 9 AM EST  
**Distribution:** Company blog → X thread → LinkedIn → HN → Reddit → community Slacks

---

### Title: The Data Transformation Supercycle: Why the Winning Layer in AI Isn't What You Think

### Hook (200 words)
- Open with Gerstner's quote: *"They have to accelerate their revenue growth in their core business and prove that they are AI beneficiaries."*
- The market's answer: Databricks 60%+ growth, Snowflake re-accelerating, ClickHouse re-accelerating
- The common thread: **data transformation**, not applications
- Gerstner's killer line: *"All these AI tools rely on data and data transformation. That's very different than a thin application layer sitting on top of a CRUD database."*
- Thesis of this post: data transformation is the winning layer, but there's a massive gap in HOW enterprises do it

### Section 1: The Profit Pool Shift (300 words)
- Gerstner: *"The profit pool available to software is decreasing, and the profit pool available to the agentic layer is increasing."*
- Sacks: *"The risk for SaaS companies is they become an old layer of the stack."*
- What this means: thin application layers lose. Infrastructure that does real computation wins.
- Freeberg: *"Everything will be 4 to 10x higher five years from now. But it's not going to be evenly distributed."*
- The distribution question: **which** data transformation companies win?
- Argument: the ones closest to the data source, not just the ones in the warehouse

### Section 2: The Agent Multiplier Problem (300 words)
- J-Cal: *"We had to open up SaaS accounts for these four agents. Our SaaS spend went up."*
- Agents are the new users. Each one generates and consumes data.
- The math: 10 agents × your current data pipeline cost = an infrastructure crisis
- Current architecture: all data → warehouse → transform → serve to agents
- Problem: warehouse costs scale linearly with agent count
- This is unsustainable at enterprise scale (100s of agents)

### Section 3: The Transformation Gap (400 words)
- Today's data transformation happens in the warehouse (Snowflake, Databricks, dbt)
- This means: move ALL data to the cloud FIRST, then filter/transform
- The waste: 50-70% of ingested data is never used in downstream queries or models
- You're paying to: move it, store it, compute over it, and ignore it
- Real numbers: a company ingesting 10TB/day at $X/TB is spending $Y/month on data that gets filtered out
- The missing layer: transformation at the source, before data moves
- This isn't replacing Snowflake/Databricks — it's making them dramatically more efficient

### Section 4: Edge-First Data Transformation (400 words)
- The architecture: process data where it lives
- Filter noise at the source (debug logs, duplicate events, low-value telemetry)
- Aggregate at the edge (send summaries, not raw events)
- Enrich in place (add context before movement)
- Result: only the data that matters reaches your warehouse
- Concrete example: IoT sensor data pipeline — before vs. after
- Show the cost reduction, latency improvement, and query performance gain
- This is complementary to Snowflake/Databricks, not competitive
- Freeberg's point about software eating services: *"The software is going to provide what it's historically been called a services business."* Edge transformation automates what used to require manual data engineering

### Section 5: What This Means for Your Stack (200 words)
- If you're running Snowflake/Databricks today, you need an edge layer
- If you're deploying AI agents, you need data transformation that scales with agent count
- If your data infrastructure costs are growing faster than your revenue, you're doing transformation in the wrong place
- The supercycle is here. The question is whether your stack is ready.

### CTA (100 words)
- "We built Expanso to be the edge data transformation layer — distributed compute that processes data at the source."
- Link to demo video
- Link to schedule a call
- "If your Snowflake/Databricks bill is growing faster than your insights, let's talk."

---

## Appendix: Time Budget

Assumes 1-2 people (founder + one helper). Realistic hours.

### Week 1

| Task | Hours | Who |
|------|-------|-----|
| Prospect list building | 3 | GTM |
| Blog post (write + edit + publish) | 6 | Content/Founder |
| Cold emails (personalize + send 25) | 4 | GTM |
| Demo pipeline prep + recording | 5 | Eng/Founder |
| Social posts + community engagement | 3 | GTM |
| Email follow-ups + reply handling | 2 | GTM |
| Metrics compilation + learning doc | 1 | GTM |
| **Total** | **24** | |

### Week 2

| Task | Hours | Who |
|------|-------|-----|
| Second blog post (write + edit + publish) | 4 | Content/Founder |
| Cold emails (25 new + follow-ups) | 4 | GTM |
| Partnership outreach (4 emails + applications) | 3 | Founder |
| Demo calls (5 × 45 min including prep) | 5 | Founder |
| Investor/analyst outreach | 2 | Founder |
| Social + community engagement | 2 | GTM |
| Sprint retro + metrics + next plan | 3 | Founder |
| **Total** | **23** | |

**Grand total: ~47 hours across 2 weeks = realistic for a founder spending 50% of time on GTM.**

---

*Last updated: Feb 8, 2026. Based on All-In Podcast E209 (Feb 7, 2026) with Gerstner, Sacks, Freeberg, Calacanis.*
