---
name: founder-coach
description: AI founder coaching system — daily decision journal, accountability tracking, weekly strategy reviews, and AI-era specific questions on moat, commoditization risk, and outcome-based pricing. Not generic startup advice. Use for founder productivity, decision tracking, and strategic reflection.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: OpenClaw agent with cron jobs
metadata: {"openclaw": {"emoji": "\ud83c\udfaf", "homepage": "https://www.agxntsix.ai"}}
---

# Founder Coach 🎯

**Your AI-powered founder accountability system.**

A structured coaching framework for AI-era founders. Daily check-ins, decision journaling, weekly strategy reviews, and accountability tracking — all stored in your agent's memory.

## Quick Start

```bash
# Morning check-in
python3 {baseDir}/scripts/founder_checkin.py morning

# Evening reflection
python3 {baseDir}/scripts/founder_checkin.py evening

# Weekly review
python3 {baseDir}/scripts/founder_checkin.py weekly

# View stats
python3 {baseDir}/scripts/founder_checkin.py stats

# View recent entries
python3 {baseDir}/scripts/founder_checkin.py history --days 7
```

---

## 🌅 Morning Brief Template

Use this every morning to set your day:

### 1. Yesterday Recap
- What did I commit to yesterday?
- What actually got done? (completion rate)
- What carried over and why?

### 2. Today's Top 3 Priorities
| # | Priority | Why it matters | Time block |
|---|----------|---------------|------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Rule:** If you can only do ONE thing today, which is it? That's #1.

### 3. AI Founder Question of the Day
Pick one to reflect on:
- "What manual process am I doing that AI could handle?"
- "Where is my moat — data, workflow, distribution, or brand?"
- "What's my cost-per-serve and how do I halve it?"
- "Am I building a product or a feature that GPT will add next quarter?"
- "What would a 10-person AI-native company do differently?"

---

## 🌙 Evening Reflection Template

### Wins
- What went well today?
- What am I proud of?

### Losses
- What didn't happen? Why?
- What would I do differently?

### Tomorrow
- Top 3 priorities for tomorrow
- One thing to stop doing
- One thing to start doing

### Energy Check
Rate 1-5: Energy [ ] Focus [ ] Motivation [ ]

---

## 📊 Weekly Strategy Review

Run every Sunday or Monday. Takes 30-60 minutes.

### Performance
- Commitments made this week: ___
- Commitments kept: ___ (___%)
- Trend vs last week: ↑ / → / ↓

### Key Metrics
| Metric | Last Week | This Week | Target |
|--------|-----------|-----------|--------|
| Revenue | | | |
| Users/Customers | | | |
| Key Feature Progress | | | |
| Cost-per-serve | | | |

### Strategic Questions

#### Moat Analysis
- **Data moat:** Are we accumulating proprietary data? What data do we have that others don't?
- **Workflow moat:** Are we embedded in customer workflows? Switching cost?
- **Distribution moat:** Do we own a channel? Community? Brand?
- **Speed moat:** Are we shipping faster than anyone else?

#### Commoditization Risk
- Which parts of our stack are becoming commoditized?
- What happens when GPT-5 / Claude 4 / Gemini 3 drops?
- Are we building on top of APIs that could become competitors?

#### AI-Era Economics
- **Cost-per-serve:** What does it cost to serve one customer?
- **Outcome-based pricing:** Can we charge for outcomes, not seats?
- **Marginal cost:** Does our 1000th customer cost the same as the 1st?
- **AI leverage:** Where does AI give us 10x leverage vs humans?

### Decisions Made This Week
| Decision | Context | Options Considered | Chosen | Reversible? |
|----------|---------|-------------------|--------|-------------|
| | | | | |

### Next Week
- #1 priority (must happen):
- #2 priority (should happen):
- #3 priority (nice to have):
- One bet/experiment to run:

---

## 📓 Decision Journal Format

For important decisions, use this format:

```
## Decision: [Title]
Date: YYYY-MM-DD
Stakes: Low / Medium / High / Critical

### Context
What's the situation? Why does this decision need to be made now?

### Options
1. **Option A:** [description]
   - Pro: ...
   - Con: ...
   - Cost: ...

2. **Option B:** [description]
   - Pro: ...
   - Con: ...
   - Cost: ...

### Decision
Chose: [Option X]
Reasoning: [Why]
Reversible: Yes/No
Review date: [When to check if this was right]

### Outcome (fill in later)
Date reviewed:
Result:
Lesson:
```

---

## 📈 Accountability System

### How It Works
1. **Morning:** Set 3 commitments
2. **Evening:** Mark complete/incomplete with notes
3. **Weekly:** Review completion rate and patterns
4. **Monthly:** Identify systemic issues

### Scoring
- **90-100%** completion: You're either crushing it or setting easy goals
- **70-89%**: Healthy stretch zone
- **50-69%**: Overcommitting or execution issues
- **Below 50%**: Stop. Fewer commitments. Execute on 1-2 things.

### Patterns to Watch
- **Always incomplete #3:** You're overcommitting — do 2 things well
- **Same item carrying over:** It's either not important (cut it) or you're avoiding it (why?)
- **High completion but no progress:** You're busy, not productive — wrong priorities
- **Energy always low:** Burnout risk — take a break before it takes you

---

## 🤖 AI-Era Founder Questions Bank

Rotate through these in morning briefs:

### Product & Moat
1. What would this business look like if AI could do 80% of the work?
2. Are we a thin wrapper around an API? How do we add defensible value?
3. What proprietary data or feedback loops do we create?
4. If OpenAI built our feature tomorrow, what would still be ours?

### Economics
5. What's our cost-per-serve and trajectory?
6. Can we charge for outcomes instead of access?
7. Where do margins come from when AI costs drop 10x yearly?
8. What's our unit economics at 10x scale?

### Competition
9. What can a 3-person AI-native startup build in 3 months that competes with us?
10. Where do we have distribution that new entrants don't?
11. What switching costs have we built?

### Personal
12. Am I building a company or a project?
13. What am I uniquely positioned to build that AI can't easily replicate?
14. Am I spending time on $10/hr tasks or $1000/hr tasks?
15. What would I do if I had 10x the resources? What about 1/10th?

---

## Storage

All entries are stored in `memory/founder-journal/`:
```
memory/founder-journal/
├── 2026-02-15.md       # Daily entries
├── 2026-02-16.md
├── weekly/
│   └── 2026-W07.md     # Weekly reviews
└── decisions/
    └── 2026-02-15-decision-name.md
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
