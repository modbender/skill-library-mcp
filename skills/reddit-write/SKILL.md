# Reddit Write Skill

## Use When
Drafting posts and comments for Luka to review and post manually. This skill runs after research (9am weekdays). Use Kimi model — this is internal drafting work.

## Don't Use When
Doing research (use reddit-research skill). Posting (Luka posts manually — never auto-post). Writing anything that won't go through Luka's review first.

---

## Drafting Workflow

### Step 1 — Load context
Read in this order:
1. `shared/research/trends-[today].md` — what opportunities the research found
2. `shared/memory/lessons.md` — what works per subreddit, what gets removed, the hard rules table
3. `agents/reddit/skills/reddit-write/ref-voice.md` — Luka's voice, examples, anti-examples

### Step 2 — Pick the best 1-2 opportunities
Choose based on:
- Luka's expertise fits the gap (CC management, rolling, assignment, Greeks in practice)
- The subreddit has a real need — not just an excuse to post
- The topic hasn't been done to death in that sub recently

### Step 3 — Draft the post
Follow ref-voice.md strictly. Write as Luka. The draft must sound like he wrote it after sitting down with coffee.

### Step 4 — Run the self-validation checklist (from SOUL.md)
Do not save until it passes every item.

### Step 5 — Save to shared/pending/
Filename: `YYYY-MM-DD-[subreddit]-[topic-slug].md`

File format:
```markdown
---
subreddit: r/thetagang
type: post
title: [Proposed post title]
quantwheel_mention: no
ai_flag: [none | REVIEW CAREFULLY]
---

[Full post content here — exactly what Luka will copy-paste]

---
_Research source: shared/research/trends-[date].md_
_Self-validation: passed_
```

### Step 6 — Update active-tasks.md
Add the draft filename under "Pending Decisions".

---

## Post Types

**Experience post** — Luka shares what he actually does, with real trade reasoning. Best performer. Lead with a specific situation, explain the thinking, give the rule that came from it. End with an open question.

**Take post** — Luka takes a clear position on a debated topic (e.g., "yes the Greeks are necessary"). Short, punchy, opinionated. 200-400 words. No headers.

**Guide post** — Detailed walkthrough of a decision process. 500-800 words. Uses some structure but stays conversational. Real examples required.

**Comment reply** — Identified during research as a thread where Luka can add value. 3-6 sentences. No headers. Direct response to what was said.

---

## Title Guidelines

Good titles from Luka's actual posts:
- "Covered calls guide based on my experience (advice for rolling and what to do if getting assigned)"
- "yes, the greeks are necessary"
- "One tool for trading options - CC,CSP,Journal,Screener.."

Pattern: specific, lowercase-ish, practical, slightly personal. Not clickbait. Not generic.

Bad titles:
- "My complete guide to covered calls" (generic)
- "Why you NEED to learn the Greeks" (hype)
- "Comprehensive analysis of rolling strategies" (sounds corporate)

---

## QuantWheel Mention Rules (Read Lessons.md First)

**Only mention QuantWheel when:**
1. The post is for a Tier 2 sub (r/Options_Beginners, r/fatFIRE, r/OptionsMillionaire)
2. The post discusses a real problem QuantWheel actually solves (cost basis tracking, screening, roll decisions)
3. The mention comes after the value — never in the first paragraph, never in the title

**How Luka mentions QuantWheel (natural):**
- "I use a tool that calculates all that stuff and gives me a rating — not magical, but helps me decide what's the better deal" (from his CC guide)
- Describe the problem first. Then: "This is what QuantWheel is built for."
- Include what it doesn't do: "It helps me decide, but you can't put news context into a number."

**Never say:**
- "Check out QuantWheel!" / "Sign up for QuantWheel" / "QuantWheel is a great tool"
- Anything that reads like an ad
- Anything with a direct link in subs that ban external links
