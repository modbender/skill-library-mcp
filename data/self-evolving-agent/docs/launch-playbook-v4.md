# 🚀 Self-Evolving Agent v4.0 — Developer Marketing Launch Playbook

> **Author:** Research Marketing Agent  
> **Date:** 2026-02-18  
> **Based on:** Live data from ClawHub, HackerNews analysis (1,200 Show HNs), ScrapeGraphAI case study, Reddit community research  
> **Target:** 10,000+ ClawHub downloads in 30 days, 200+ GitHub stars, awesome-openclaw-skills listing

---

## 0. Situation Assessment

### Market Context (February 2026)

| Metric | Data | Source |
|--------|------|--------|
| ClawHub total skills | 3,286 (post-security purge) | claw-hub.net |
| Total ClawHub downloads | 1.5M+ | claw-hub.net |
| #1 Capability Evolver | 35,581 downloads (author suspended) | claw-hub.net |
| self-improving-agent (competitor) | 15,962 downloads / 132 ⭐ | claw-hub.net |
| self-evolving-agent target | 10,000+ downloads in D+30 | This playbook |

### Strategic Window

The February 2026 ClawHub security incident (341 malicious skills removed, 2,419 purged total) has created a **trust vacuum**. Users are actively seeking:
1. Skills with transparent, human-in-the-loop design
2. Skills from credible, non-anonymous authors
3. Skills that explicitly don't auto-modify anything

**Self-evolving-agent v4.0's "proposal-only, user must approve" design is the perfect answer.** This is not spin — it's a genuine differentiator. Lead with it everywhere.

### Competitor Gap

- **Capability Evolver (#1 by downloads)**: Author account suspended. Skill effectively orphaned. ~35K users need an alternative.
- **self-improving-agent (pskoett)**: Active competitor, 15,962 downloads. Study their messaging and outflank on: multi-agent pipeline, transparency, effect measurement loop.

---

## 1. Platform Strategy: Reddit

### Primary Subreddits (Tier 1 — post first)

| Subreddit | Members | Why | Angle |
|-----------|---------|-----|-------|
| r/AI_Agents | 85K+ | Direct audience, AI agents | Full feature demo |
| r/ClaudeAI | 120K+ | Claude users = OpenClaw users | "Built with Claude" angle |
| r/LocalLLaMA | 180K+ | Local AI power users | "Runs locally, data stays yours" |
| r/OpenSource | 250K+ | OSS community, upvote culture | "100% open source, MIT license" |

### Secondary Subreddits (Tier 2 — post within first week)

| Subreddit | Members | Angle |
|-----------|---------|-------|
| r/MachineLearning | 2.5M | "Multi-agent pipeline architecture" technical post |
| r/selfhosted | 350K+ | "Your AI, your logs, no cloud" privacy angle |
| r/SideProject | 120K+ | Builder's journey, "I shipped v4.0" story |
| r/learnmachinelearning | 280K+ | Educational angle, "how self-evolving AI actually works" |
| r/programming | 5M | Code quality, architecture deep-dive |
| r/compsci | 900K | Multi-agent theory post |
| r/automation | 200K+ | Workflow automation angle |
| r/homelab | 450K+ | Self-hosted AI assistant improvement angle |

### Reddit Posting Formula (Data-Driven)

**What works in 2025-2026:**
- GIF or Loom demo in the post → **2.5x more replies**
- "One itch scratched" focus → top quartile feedback
- Be the first to comment with extra context within 5 minutes of posting

**Post template (Tier 1):**

```
Title: I built a self-evolving AI agent that improves itself — but NEVER without your approval

Body:
Hey [subreddit name],

I've been running OpenClaw as my personal AI assistant and got frustrated that it
never learned from its mistakes. So I built a skill that fixes this.

[GIF showing: agent spots a repeated failure → analyzes it → proposes a fix → user approves]

**What it does:**
- Weekly: 4-agent pipeline reads your agent's logs
- Finds patterns in failures and inefficiencies  
- Proposes specific improvements to your AGENTS.md
- You approve or reject. It NEVER auto-modifies anything.

**Why I built this instead of using existing tools:**
The #1 skill (Capability Evolver) was just suspended. self-improving-agent is great
but has no feedback loop — you can't tell if last week's suggestion actually helped.

v4.0 adds effect measurement: next cycle, it checks if the previous suggestion
actually improved things.

**GitHub:** https://github.com/Ramsbaby/self-evolving-agent
**ClawHub install:** `clawhub install self-evolving-agent`

Happy to answer anything — I've been dogfooding this for 3 months.
```

### Reddit Rules to Not Break

1. **Never post the same link to multiple subreddits on the same day** — wait 48h minimum between Tier 1 posts
2. **Engage authentically** — respond to every comment within 2h on launch day
3. **Flair your posts correctly** — "Project" or "Show and Tell" where available
4. **Karma prerequisite** — ensure your Reddit account has 50+ karma before posting to large subs

---

## 2. HackerNews (Show HN) Strategy

### Data-Backed Timing (from 1,200 Show HN analysis, Nov 2025)

| Factor | Optimal | Effect |
|--------|---------|--------|
| **Best days** | Tuesday or Wednesday | +28% points & comments |
| **Best time** | 8:00–11:00 AM UTC | Peak active devs |
| **Worst day** | Friday after 2 PM UTC | -45% engagement cliff |
| **Worst time** | Weekend | Only 8% of peak traction |

**→ Target: Tuesday, Feb 24, 2026 at 9:00 AM UTC (6 PM KST)**

### Title Engineering

Rules from data:
- Under **55 characters** → +24% upvotes
- "Open Source" in title → +38% points
- Avoid "AI-Powered" → oversaturated, -15% relative score
- Question-style titles → +2.2x comments (but lower upvotes)
- "CLI" or "API" → +26%

**Candidate titles (all under 55 chars):**

```
✅ Show HN: Open Source self-evolving AI agent (v4.0)
✅ Show HN: AI that improves itself, never without you
✅ Show HN: Self-improving agent – open source, safe
✅ Show HN: Agent that learns from its own failures
```

**Recommended:** `Show HN: Open Source self-evolving AI agent (v4.0)`  
- "Open Source" → +38%  
- "v4.0" signals maturity/iteration  
- 50 chars ✅  

### Show HN Description Template

```
Show HN: Open Source self-evolving AI agent (v4.0)

Self-evolving-agent is an OpenClaw skill that reads your AI agent's weekly 
logs, runs a 4-step multi-agent pipeline to identify failure patterns, and 
proposes targeted improvements to your system prompt.

Key constraint: it NEVER modifies anything without explicit user approval.
Each proposal includes evidence (which logs triggered it) and a predicted 
improvement score. Next cycle measures whether the prediction was accurate.

v4.0 adds:
- Multi-agent pipeline (Collector → Analyzer → Benchmarker → Synthesizer)
- Structural heuristic analysis (not just keyword matching)
- Effect measurement loop: did last week's suggestion actually help?
- False positive rate dropped from ~40% to ~15%

GitHub: https://github.com/Ramsbaby/self-evolving-agent

Background: I've been running this on my own OpenClaw instance for 3 months. 
The agent caught a repeated tool-call failure I'd missed for weeks and 
proposed adding a retry wrapper that reduced that error class by 80%.
```

### HN Engagement Playbook

1. **Post at exactly 9 AM UTC** — competition is lighter in the first 30 minutes
2. **Respond to the first 3 comments within 15 minutes** — signals you're present
3. **Prepare 5 FAQ answers in advance** so you can paste them quickly:
   - "How is this different from Capability Evolver?"
   - "Does it work with Claude only or other LLMs?"
   - "What happens if it makes a bad suggestion?"
   - "How much does it cost to run?"
   - "Is the proposal stored anywhere?"
4. **Post a GIF link in the first comment** — images aren't in HN posts, but comments with demo links get 2.5x replies
5. **Do a follow-up "Lessons learned" post in 2 weeks** — serial posters get 3x traction on follow-ups

---

## 3. awesome-openclaw-skills Listing

### Repository: `VoltAgent/awesome-openclaw-skills`

**Hard requirements (from CONTRIBUTING.md):**
1. ✅ Skill must be in the **official openclaw/skills repo** (not personal repos, not gists)
2. ✅ Skill must have **real community usage** (downloads + GitHub stars)
3. ✅ Proper SKILL.md format
4. ✅ Active maintenance (recent commits, responded issues)

### Pre-requisites Before Submitting PR

| Requirement | Target | Current Status |
|-------------|--------|----------------|
| ClawHub downloads | 500+ | Need to build |
| GitHub stars | 25+ | Need to build |
| Open issues responded | All within 48h | Implement now |
| SKILL.md completeness | 100% | Verify format |
| ClawHub security scan | Passed (VirusTotal) | Auto-checked |

### PR Submission Process

1. **Fork** `VoltAgent/awesome-openclaw-skills`
2. Add entry under `## AI/ML` category (highest-traffic section — 1,588 skills, 48.3% of total):
   ```markdown
   - [self-evolving-agent](https://github.com/Ramsbaby/self-evolving-agent) - 
     Multi-agent pipeline that analyzes your AI agent's logs and proposes 
     AGENTS.md improvements. Never auto-modifies. Includes effect measurement loop.
   ```
3. **PR title:** `Add: self-evolving-agent (AI/ML) - multi-agent self-improvement`
4. **PR description:** Include download count, star count, brief demo GIF

**Timeline:** Submit PR on D+14 when you have 500+ ClawHub downloads and 25+ stars.

### Alternative: Get Mentioned in the Existing Reddit Post

The r/AI_Agents post "Best OpenClaw Skills You Should Install" (73 upvotes, active) is a prime target. Comment with your skill — the thread is still active.

---

## 4. Discord Community Engagement

### OpenClaw Official Discord — Channels to Target

| Channel | Strategy |
|---------|----------|
| `#show-your-setup` | Post your actual setup + demo GIF |
| `#skills-showcase` | Full skill announcement |
| `#feedback-wanted` | Ask for specific feedback on v4.0 |
| `#bugs-and-issues` | Be present, help others, build credibility first |

### Engagement Playbook (30 days)

**Week 1 — Credibility building:**
- Join the server
- Spend 3-4 days helping others with questions (don't mention your skill yet)
- React to posts, contribute to discussions
- Build up a visible, helpful presence

**Week 2 — Soft launch:**
- Post in `#show-your-setup`: "Here's my setup after 3 months of using self-evolving-agent..."
- Include a screenshot of an actual proposal the agent made + what you approved
- Natural, not sales-y

**Week 3 — Full announcement:**
- Post in `#skills-showcase`
- Include: demo GIF, install command, GitHub link
- Respond to every reply

**Week 4 — Community contribution:**
- Create a guide: "How to get the most out of self-evolving-agent"
- Post it as a pinnable resource
- Offer to help anyone set it up

### Other Discord Communities to Join

| Community | Focus | Angle |
|-----------|-------|-------|
| Anthropic Discord (official) | Claude users | "Built on Claude, improves your Claude workflow" |
| r/LocalLLaMA Discord | Local AI | "Fully local, zero data leaves your machine" |
| Open Source AI Discord servers | Builders | Architecture/technical post |

---

## 5. Dev.to / Medium Article Strategy

### Article Sequence (5 articles over 30 days)

**Article 1 (D+2): The Personal Story**
- Title: `I spent 3 months making my AI assistant smarter — here's what I learned`
- Platform: Dev.to (better for technical audience, SEO, syndication)
- Length: 1,200–1,500 words
- Include: what v1.0 looked like vs v4.0, what failed, what surprised you
- CTA: GitHub link + "give it a star if this resonated"
- Tags: `#ai #agents #opensource #productivity`

**Article 2 (D+7): The Technical Deep-Dive**
- Title: `How I built a 4-agent pipeline for AI self-improvement (and why single-agent didn't work)`
- Platform: Dev.to + crosspost to Medium
- Length: 2,000–2,500 words
- Include: architecture diagram, code snippets, why each agent has a specific role
- This is your HN bait — link to this in your Show HN description

**Article 3 (D+14): The Safety Argument**
- Title: `Why "AI that modifies itself" should terrify you — and how we built safeguards`
- Platform: Medium (better reach for non-technical readers)
- Length: 1,000 words
- Angle: the ethics of AI self-modification, why the approval loop matters
- Cross-post to r/MachineLearning and r/compsci

**Article 4 (D+21): The Data Story**
- Title: `3 weeks after launch: what 500 users taught me about AI self-improvement`
- Platform: Dev.to
- Include: actual usage data, most common proposals, rejection rates, user feedback
- This builds long-term credibility

**Article 5 (D+28): The "Lessons" Wrap-Up**
- Title: `What I wish I knew before building a self-evolving AI agent`
- Platform: Dev.to + Hashnode
- Summary of the journey, what v5.0 might look like
- Re-engage the original audience

### Dev.to Tactics
- Post between **Tuesday–Thursday, 9 AM–2 PM UTC** for max feed visibility
- Tag limit is 4 — use wisely: `ai`, `agents`, `opensource`, `productivity`
- Dev.to has a **"Top Posts" algorithm** that looks at reactions in first 2 hours — ask your network to react early
- Add your article to Dev.to's weekly newsletter submission form

---

## 6. YouTube / Demo Video Strategy

### Video Sequence

**Video 1 (D+0): 90-Second Demo Reel (Launch Day)**
- Format: Screen recording with voiceover
- Show: 
  1. Agent runs weekly, detects a failure pattern (15s)
  2. The 4 agents working in sequence — show their output (30s)
  3. Discord notification arrives with proposal (15s)
  4. User reviews, approves, sees effect measurement next cycle (30s)
- Tool: OBS + Quick Time or Loom for first draft
- Upload as YouTube video AND as a Short (same content, square crop)
- Title: `Self-Evolving AI Agent v4.0 — 90 Second Demo`
- No narration needed if captions are clear

**Video 2 (D+7): Full Walkthrough (10-15 mins)**
- Title: `How to Set Up a Self-Evolving AI Agent (OpenClaw + Claude)`
- Structure:
  1. What problem this solves (2 min)
  2. Installation walkthrough (5 min)
  3. First proposal it made for my setup (3 min)
  4. Q&A from comments (2 min)
- This is the evergreen "how-to" that will rank on YouTube search

**Video 3 (D+21): Deep-Dive Architecture**
- Title: `Inside a 4-Agent AI Pipeline: Collector, Analyzer, Benchmarker, Synthesizer`
- For developers who want to fork/modify
- 8-10 mins

### YouTube Shorts Strategy (2025 Algorithm)
- Post one Short per week: 30-60 seconds
- Hook in first 3 seconds: "Your AI agent makes the same mistake every week and you don't know it."
- Use text overlays (60% of viewers watch without sound)
- Include `#AIAgents #OpenSource #Claude #SelfEvolvingAI` in description
- Cross-post to TikTok and Instagram Reels (same content, 3x reach)

### Demo GIF (Most Important Asset)
Before anything else, create a **high-quality demo GIF** showing:
- The proposal arriving in Discord
- The structured format of the proposal
- The user typing "approve" and seeing it take effect

Use this GIF in EVERY platform: README, Reddit posts, HN comment, Discord, Dev.to articles. This single asset will drive more installs than any written description.

---

## 7. How Top ClawHub Skills Got 10K+ Downloads

### Case Study: Capability Evolver (35,581 downloads)

**What worked:**
- Clear, unique concept: "AI that writes its own code to improve itself"
- Early mover advantage in the self-improvement category
- High-quality SKILL.md with detailed examples
- Active issue responses in the first month

**What we can learn:**
- The concept is proven. There's massive demand for self-improving agents.
- With Capability Evolver now suspended, the ~35K user base is up for grabs.
- Our value proposition: same category, but with transparency and safety as core features.

### Case Study: self-improving-agent (15,962 downloads, 132 ⭐)

**What worked:**
- 132 stars is high — this author marketed aggressively on GitHub
- Consistent versioning (v1.0.5 shows active maintenance)
- Strong README with real examples

**How to differentiate:**
| Feature | self-improving-agent | self-evolving-agent v4.0 |
|---------|---------------------|--------------------------|
| Architecture | Single agent | 4-agent pipeline |
| Feedback loop | None | Effect measurement loop |
| Approval required | Yes | Yes |
| False positive rate | Unknown | ~15% (measured) |
| Versioning | v1.0.5 | v4.0.0 (shows maturity) |

### Case Study: Wacli (16,415 downloads, 37 ⭐)

**What worked:**
- Dev tool angle (Development + Utility category overlap)
- CLI focus appeals to power users
- Multiple Reddit posts across r/selfhosted, r/programming, r/OpenSource

**Lesson:** Cross-posting to multiple relevant communities (not spamming — different angles) multiplies reach.

### Universal Pattern for 10K+ Downloads

1. **Launch with a complete product** — SKILL.md, README, config.yaml, scripts all polished
2. **Demo GIF in README** — non-negotiable for ClawHub listing prominence
3. **Respond to every issue within 24h** — ClawHub community trust depends on it
4. **Post to at least 4-5 Reddit communities** with tailored angles
5. **HN Show HN** at peak time — even 200 points = 2,000–5,000 GitHub page visits
6. **Version publicly** — "v4.0" in the title signals stability and iteration
7. **Build the email/Discord list from day 1** — announce v4.1 to them first

---

## 8. Week-by-Week Launch Timeline (D+0 to D+30)

### D-7 to D-1: Pre-Launch Preparation

- [ ] Create demo GIF (the most important asset — do this first)
- [ ] Polish README.md with GIF embedded at top
- [ ] Ensure SKILL.md is 100% complete with examples
- [ ] Create a short Loom walkthrough video (10–15 min)
- [ ] Write Article 1 draft (personal story)
- [ ] Set up GitHub Issues templates
- [ ] Join OpenClaw Discord, start lurking and helping
- [ ] Prepare 5 FAQ answers for HN and Reddit
- [ ] Line up 5-10 friends/colleagues to star the repo on D+0

---

### D+0: Launch Day (Target: Tuesday, Feb 24)

**Morning (09:00–12:00 KST):**
- [ ] Publish to ClawHub: `clawhub publish`
- [ ] Ask your 5-10 contacts to star the GitHub repo
- [ ] Post to r/AI_Agents (largest immediate audience)
- [ ] Post Article 1 on Dev.to
- [ ] Upload 90-second demo to YouTube
- [ ] Share demo GIF on X/Twitter with #AIAgents #OpenSource

**Afternoon (14:00–18:00 KST):**
- [ ] Post to r/ClaudeAI with Claude-specific angle
- [ ] Submit Show HN at exactly 9:00 AM UTC (18:00 KST Tuesday)
- [ ] Monitor HN and respond to first comments within 15 minutes

**Evening (20:00–23:00 KST):**
- [ ] Post in OpenClaw Discord `#skills-showcase`
- [ ] Respond to all Reddit and HN comments
- [ ] Check ClawHub for any install errors reported

**D+0 Target:** 50 GitHub stars, 200 ClawHub downloads, 100 HN upvotes

---

### Week 1 (D+1 to D+7): Momentum Building

**D+1:**
- [ ] Post to r/LocalLLaMA with "runs locally, your data stays yours" angle
- [ ] Post to r/selfhosted with privacy/self-hosting angle
- [ ] Respond to all GitHub issues same-day

**D+2:**
- [ ] Publish Article 1 (if not done D+0)
- [ ] Post Article 1 to r/SideProject: "I shipped my side project v4.0 — here's what 3 months of iteration taught me"

**D+3:**
- [ ] Post to r/OpenSource: focus on MIT license, contributor-friendly, modular architecture
- [ ] First YouTube Short: "Your AI makes the same mistake every week and you don't even know it"

**D+5:**
- [ ] Write and publish Article 2 (technical deep-dive)
- [ ] Post Article 2 to r/MachineLearning with architecture focus

**D+7:**
- [ ] Publish full walkthrough YouTube video (10-15 min)
- [ ] Post to r/automation: "I automated improving my AI assistant's memory"
- [ ] Send HN "follow-up" Ask HN or comment on your original post with v4.0.1 updates

**Week 1 Target:** 150 GitHub stars, 1,000 ClawHub downloads

---

### Week 2 (D+8 to D+14): Community Deepening

**D+8:**
- [ ] Post to r/programming with code architecture deep-dive
- [ ] Post in OpenClaw Discord `#feedback-wanted`: share real usage data, ask for feedback

**D+10:**
- [ ] YouTube Short #2: "90 seconds to set up a self-improving AI agent"
- [ ] Second wave Reddit posts to homelab, compsci subs

**D+12:**
- [ ] Publish Article 3 (safety/ethics angle) on Medium
- [ ] Reach out to 2-3 OpenClaw-focused content creators for potential feature

**D+14:**
- [ ] **Submit PR to awesome-openclaw-skills** (if 500+ downloads and 25+ stars met)
- [ ] Announce the PR submission on Reddit and Discord: "Just submitted to awesome-openclaw-skills 🎉"

**Week 2 Target:** 300 GitHub stars, 3,000 ClawHub downloads

---

### Week 3 (D+15 to D+21): Scale and Amplify

**D+15:**
- [ ] Find and reach out to 2-3 DevTool newsletter curators (Console.dev, TLDR Tech, etc.)
- [ ] Post to r/learnmachinelearning: educational post on multi-agent architectures

**D+17:**
- [ ] YouTube Short #3: "How multi-agent AI pipelines reduce false positives by 60%"
- [ ] Post on Hacker News "Who is hiring" or relevant monthly threads as context-building

**D+18:**
- [ ] Publish Article 4 (data story: 500 users, what we learned)
- [ ] Post data article to r/datascience

**D+21:**
- [ ] Release v4.0.1 with community-requested fixes
- [ ] Announce v4.0.1 as a new Reddit post: "v4.0.1 shipped — you asked, we delivered"
- [ ] Upload YouTube deep-dive architecture video

**Week 3 Target:** 500 GitHub stars, 6,000 ClawHub downloads

---

### Week 4 (D+22 to D+30): Sustainability Setup

**D+22:**
- [ ] Reach out to 2-3 awesome-openclaw-skills maintainers directly (GitHub DM/issue)
- [ ] Post to r/homelab: real-world setup photos + terminal output

**D+24:**
- [ ] Create "Good First Issues" on GitHub to attract contributors
- [ ] Post about it in dev communities: "Looking for contributors to [specific feature]"

**D+26:**
- [ ] Publish Article 5 (lessons learned wrap-up)
- [ ] Cross-post to Hashnode for additional reach

**D+28:**
- [ ] YouTube Short #4: most interesting/surprising proposal the agent ever made
- [ ] Set up GitHub Discussions for community questions (reduces issue noise)

**D+30:**
- [ ] Final metrics review post on Reddit: "30 days of self-evolving-agent — real numbers"
- [ ] Announce what's coming in v4.1 (community roadmap post)
- [ ] Send thank-you messages to everyone who gave significant feedback

**Week 4 Target:** 10,000+ ClawHub downloads, 500+ GitHub stars, awesome-openclaw-skills listed

---

## 9. Message Templates & Titles Cheat Sheet

### GitHub README Opening Hook
```
> **What if your AI assistant got better every week — but only after you approved each change?**

Self-evolving-agent analyzes your agent's logs, finds patterns in failures,
and proposes targeted improvements. You decide what to accept.
No auto-modifications. Ever.
```

### Twitter/X Post (280 chars)
```
I built an AI that improves itself — but never without my permission.

4-agent pipeline: reads logs → finds patterns → measures past suggestions → proposes fixes

I approve or reject each one. Effect is measured next cycle.

Open source, MIT: [GitHub URL]

#AIAgents #OpenSource #Claude
```

### LinkedIn Post
```
I spent 3 months building a self-improving AI agent and here's the most
important design decision I made:

It NEVER modifies anything without my explicit approval.

Every proposal includes:
- Which log entries triggered it
- What change is suggested  
- Predicted improvement score
- (Next cycle) Did the prediction come true?

I call this an "effect measurement loop" and it's what separates
this from simpler self-modification tools.

The code is open source: [GitHub URL]

Happy to discuss the multi-agent architecture in comments.
```

### ClawHub Description (for registry listing)
```
Multi-agent pipeline that reads your OpenClaw agent's weekly logs, identifies 
behavioral patterns and failure modes, and proposes targeted improvements to 
your AGENTS.md. Never auto-modifies — every suggestion requires explicit 
approval. v4.0 adds effect measurement: next cycle tracks whether last week's 
suggestion actually helped.

Features: 4-agent pipeline (Collector→Analyzer→Benchmarker→Synthesizer), 
structural heuristic analysis, ~15% false positive rate, full audit trail.
```

---

## 10. Success Metrics & Checkpoints

| Milestone | D+0 | D+7 | D+14 | D+21 | D+30 |
|-----------|-----|-----|------|------|------|
| ClawHub downloads | 200 | 1,000 | 3,000 | 6,000 | 10,000+ |
| GitHub stars | 50 | 150 | 300 | 500 | 500+ |
| awesome-openclaw-skills | No | No | PR submitted | Merged? | Listed ✅ |
| Articles published | 1 | 2 | 3 | 4 | 5 |
| YouTube videos | 1 | 2 | 2 | 3 | 4 |
| Reddit communities posted | 2 | 5 | 7 | 9 | 10+ |
| HN submission | No | Show HN | — | Follow-up | — |
| Discord engagement | Joined | Active | Post | Guide | Community |

---

## 11. Budget

This entire playbook is **zero-cost** (only time). Optional paid amplification:

| Channel | Cost | Expected ROI |
|---------|------|-------------|
| Reddit Ads targeting r/AI_Agents | $50-100 | 5,000 impressions → ~200 visits |
| Dev.to Listing (featured article) | $0 (organic) | Submit to their newsletter |
| GitHub Sponsors setup | $0 | Shows legitimacy |

**Recommendation:** Spend $0 on ads. The organic strategy above is sufficient for 10K downloads if executed consistently.

---

## 12. Red Lines (What NOT to Do)

| ❌ Don't Do | ✅ Do Instead |
|-------------|---------------|
| Post same text to 5 subreddits same day | Tailor each post, wait 48h between large sub posts |
| Buy GitHub stars | Build authentic community — fake stars are detectable and destroy credibility |
| Claim "AI that writes its own code" without caveats | Be precise: "4-agent pipeline that proposes changes. You approve." |
| Ignore negative comments | Respond thoughtfully — critics become advocates |
| Auto-close issues with no response | Respond within 24h, even "will look into this" |
| Post on HN on a Friday | Tuesday or Wednesday 8-11 AM UTC only |
| Use "AI-Powered" in HN title | Use "Open Source" instead (-15% vs +38% impact) |

---

*Generated from: ClawHub live data, HackerNews 1,200-post analysis (Nov 2025), ScrapeGraphAI 20K star case study, Reddit community research, awesome-openclaw-skills CONTRIBUTING.md*

*Next review: D+15 (March 11, 2026) — update metrics, adjust strategy based on actual performance*
