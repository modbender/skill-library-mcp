# Expanso GTM Strategy: Riding the Data-to-AI Transformation Wave

## Final Version — Self-Critiqued & Revised

---

## The Opportunity

Brad Gerstner (Altimeter Capital) is calling this the **AI infrastructure supercycle** — $500B+ in CapEx deployed in 2026 alone. His thesis: value is shifting to the **data and infrastructure layer**. Real-time data processing is the "critical backbone" for AI. Confluent sits in a "$100B+ market opportunity" for foundational data flow.

**The gap Expanso fills:** As enterprises pour money into AI infrastructure, they're hitting a wall — 83% of leaders expect infrastructure failure within 24 months (source: Cockroach Labs "State of AI Infrastructure 2026"). Central cloud costs are exploding. Edge processing that filters at source is becoming a necessity.

---

## Honest Self-Assessment

Before the strategy: what we need to acknowledge.

**What we know:**
- The narrative timing is excellent (AI spend, infrastructure stress, cost pressure)
- Edge-first processing is a real technical differentiator
- Gerstner's thesis gives us a hook

**What we don't know:**
- Whether our target buyers (Snowflake/Databricks users) actually care about edge processing
- What their real buying process looks like
- Whether "50% cost reduction" holds across workload types
- Who actually signs the check for infrastructure changes

**The critique:** A content-first strategy without customer validation is guessing. We need to balance content creation with direct customer conversations.

---

## Revised Positioning

### The Narrative
**"AI is eating your cloud budget. Expanso processes data where it lives — cutting costs while making AI pipelines faster and more resilient."**

### Key claim: "Cut costs 50%"
⚠️ **This needs receipts.** Before publishing anything, we need:
- At least 1 documented workload with real before/after numbers
- Clear assumptions (what % of data is filterable, what workload types)
- Honest ranges ("30-60% depending on workload") beats a magic number

### Actual competitive landscape (honest version)
| Competitor | What they do | Why we're different |
|-----------|-------------|-------------------|
| **Cribl** | Data routing for observability | Narrow focus; we handle arbitrary compute |
| **Kubernetes + DIY** | Roll-your-own orchestration | Our real competition — we reduce complexity |
| **Cloud-native tools** | Snowflake OpenFlow, etc. | Vendor lock-in; we're cloud-agnostic |
| **Alluxio/Starburst** | Data virtualization | Different layer; complementary |
| **Inertia** | "It's fine, we'll just pay more" | The biggest competitor of all |

---

## Week 1 Game Plan (Feb 9–15, 2026)

### REVISED: Two Tracks Running in Parallel

**Track 1: SELL (60% of time) — Find out if anyone cares**
**Track 2: CONTENT (40% of time) — Plant the flag**

---

### Track 1: Customer Discovery & Sales (Priority)

**Monday-Tuesday: Build the list**
- Identify 50 companies likely running Snowflake/Databricks with high data volumes
  - Sources: LinkedIn Sales Navigator, Snowflake partner directory, job postings mentioning "data cost optimization"
  - Filter for: 500-5000 employees, data-intensive industries (fintech, adtech, IoT, healthcare)
- Draft cold email template:
  > "Hi [name], I noticed [company] is running [Snowflake/Databricks] at scale. We help companies reduce data infrastructure costs 30-60% by processing and filtering data at the edge before it hits the cloud. Would a 15-minute demo be worth your time?"

**Wednesday-Thursday: Outreach**
- Send 50 cold emails (personalized, not mass blast)
- Post in 3-5 relevant Slack/Discord communities asking about edge processing pain points
- Reach out to 5 existing contacts in data engineering roles for informal calls
- Goal: **book 5 demo calls for Week 2**

**Friday: Learn**
- Compile what we've heard
- Update positioning based on actual feedback
- Identify the 1-2 pain points that resonate most

---

### Track 2: Content (Support Sales, Not Replace It)

**Monday: Anchor Blog Post**
- Title: *"The $500B Problem: Why AI Infrastructure Needs Edge-First Data Processing"*
- Hook: Gerstner's supercycle thesis → infrastructure crisis → Expanso's approach
- Structure:
  1. The spending tsunami ($500B CapEx, 44% AI growth)
  2. The infrastructure crisis (failure expectations, downtime costs)
  3. Why centralized processing hits limits
  4. Edge-first processing as an answer (with honest technical explanation)
  5. A concrete example with real numbers (even if from internal testing)
- Length: 1,500-2,000 words. Quality > length.
- **Publish Tuesday morning**

**Tuesday: Social amplification**
- X thread (8 tweets summarizing the thesis)
- LinkedIn post (shorter, business-focused)
- Submit to Hacker News
- Engage relevant accounts: data infra influencers, Gerstner, All-In ecosystem

**Wednesday-Thursday: Technical Demo**
- Record ONE 10-minute technical demo video
- Show a real pipeline: raw data → edge filter → reduced cloud ingestion
- Include actual numbers (even if from a synthetic workload)
- This is the single highest-leverage content asset — a tool people can evaluate

**Friday: ROI Calculator (if time permits)**
- Simple web page on expanso.io
- Inputs: current cloud spend, data volume, estimated filterable %
- Output: projected savings
- Lead capture form
- **This is the stretch goal, not the requirement**

---

### Partnership Outreach (Lightweight — Don't Over-Invest)

These take months. This week is about planting seeds, not closing deals.

| Partner | Action This Week | Why |
|---------|-----------------|-----|
| **Confluent** | One warm intro email via network | Kafka + edge preprocessing is natural |
| **Datadog** | Email partnership team | Edge observability gap |
| **Snowflake** | Apply to Partner Program | Table stakes |
| **KubeCon** | Submit talk proposal (deadline check) | "Edge-First Data Processing for AI Workloads" |
| **Gartner** | Email requesting analyst briefing | Edge computing platform coverage |

---

## Content Assets (Realistic for 1-2 people)

| Asset | Priority | Day | Time Est |
|-------|----------|-----|----------|
| Anchor blog post | **Must do** | Mon-Tue | 6 hours |
| X thread + LinkedIn | **Must do** | Tue | 1 hour |
| Technical demo video | **Must do** | Wed-Thu | 4 hours |
| Cold email campaign | **Must do** | Mon-Thu | 3 hours |
| ROI calculator | Stretch | Fri | 4 hours |
| HN submission | Easy win | Tue | 15 min |

**Total: ~18 hours of content work + ~15 hours of sales work = realistic for 1-2 people over 5 days**

---

## Metrics That Actually Matter

### Vanity (track but don't obsess)
- Blog views: 500+ would be good, 1000+ is great
- Video views: 100+ is realistic
- Social engagement: any meaningful discussion

### Revenue (this is what matters)
- **Demo calls booked: 5+**
- **Cold email response rate: >5%**
- **Qualified conversations: 3+**
- **Customer pain points documented: 5+ distinct patterns**
- **Partnership conversations started: 2+**

---

## Week 2+ Roadmap (Depends on Week 1 Learnings)

**If cold outreach works (>5% response rate):**
- Double down on outbound
- Build sales playbook from what resonated
- Create targeted content addressing specific pain points discovered

**If content takes off (1000+ views, inbound interest):**
- Produce weekly content (blog + video cadence)
- Build email drip sequence
- Create gated guide

**If neither works:**
- Revisit positioning entirely
- Do 10 more customer interviews
- Consider whether the ICP is wrong (maybe it's not Snowflake users)

---

## The Hard Questions We Need to Answer This Week

1. **Can we prove the cost reduction claim?** If not, don't lead with it.
2. **Who is our actual buyer?** Data engineer? Platform engineer? VP of Infrastructure? CFO?
3. **What's the real competitive alternative?** Is it Cribl, or is it "just pay the cloud bill"?
4. **What's our wedge?** The first use case that gets us in the door.
5. **Do we have a 10-minute demo that makes someone say "holy shit"?** If not, build one before anything else.

---

## Bottom Line

The Gerstner thesis gives us a perfect narrative hook. The market data supports the timing. But **narrative without customer validation is fiction.**

**This week's real goal isn't content. It's learning.**

The blog post and demo video are tools for starting conversations, not ends in themselves. If we publish a great blog post and book zero demo calls, we've failed. If we publish nothing but book 5 qualified demos, we've succeeded.

**Priority order:**
1. 🎯 Build a killer 10-minute demo with real numbers
2. 📧 Send 50 cold emails to qualified prospects  
3. ✍️ Publish the anchor blog post
4. 🎥 Record the demo as a video
5. 🤝 Plant partnership seeds
6. Everything else

**Ship the demo. Start selling. Write about it after.**
