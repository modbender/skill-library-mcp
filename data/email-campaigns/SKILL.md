---
name: email-campaigns
version: 1.0.0
description: Write high-converting email campaigns for any business — newsletters, re-engagement sequences, B2B cold outreach, promotional emails, and automated drip campaigns. Includes subject line formulas, segmentation strategies, and deliverability best practices.
tags: [email-marketing, newsletter, campaigns, copywriting, automation, b2b-outreach, drip-campaigns]
author: contentai-suite
license: MIT
---

# Email Campaigns — Universal Email Marketing System

## What This Skill Does

Creates professional email campaigns that get opened, read, and acted on. For any business, any list size, any goal — from newsletters to B2B cold outreach to re-engagement campaigns.

## How to Use This Skill

**Input format:**
```
BUSINESS NAME: [Your brand]
NICHE: [Your industry]
EMAIL TYPE: [Newsletter / Promotional / Re-engagement / Cold outreach / Welcome sequence]
AUDIENCE SEGMENT: [Active subscribers / Cold leads / Past customers / B2B prospects]
GOAL: [Open rate / Clicks / Purchases / Replies / Appointments]
TONE: [Professional / Casual / Warm / Urgent / Story-based]
LIST SIZE: [Approximate — small <500 / medium 500-5K / large 5K+]
```

---

## Subject Line Formulas

Subject line is 80% of your open rate. Test these formulas:

```
Curiosity: "The [TOPIC] mistake you're probably making"
Personalization: "[First name], quick question about [TOPIC]"
Urgency: "Last chance: [OFFER] ends tonight"
Benefit: "How to [achieve result] without [pain point]"
Story: "I almost gave up on [thing]. Then this happened."
Number: "7 [TOPIC] tips I wish I knew earlier"
Question: "Are you making this [NICHE] mistake?"
Direct: "[Action] before [date/time]"
```

**Subject line generator prompt:**
```
Write 10 email subject lines for [BUSINESS NAME] for an email about [TOPIC].
Audience: [AUDIENCE SEGMENT]. Goal: [GOAL].
Mix: 3 curiosity, 2 benefit, 2 urgency, 2 question, 1 story.
Keep each under 50 characters for mobile. No clickbait — must match email content.
```

---

## Email Types & Templates

### 1. Weekly Newsletter
```
SUBJECT: [Subject line formula]

Hi [First Name],

[OPENING — 1-2 sentences: a timely observation, personal note, or question]

[MAIN CONTENT SECTION]
This week I want to share [topic]:

[2-3 paragraphs of genuine value — insight, tip, or story]

[SECONDARY SECTION — optional]
Also this week: [brief mention of another useful resource or news]

[CTA]
[Single, clear action: read full article / book a call / reply with X]

[SIGN-OFF]
[Your name]
[Your title + company]

P.S. [One more insight or soft CTA — P.S. lines get high readership]
```

**Newsletter prompt:**
```
Write a weekly newsletter for [BUSINESS NAME] in [NICHE].
Topic: [MAIN TOPIC]
Opening: personal/relatable (2 sentences)
Main value: [3 paragraphs of insight or advice]
CTA: [desired action]
Tone: [TONE]. Max 400 words. P.S. line with soft CTA.
Subject line: [3 options using different formulas]
```

### 2. Re-engagement Campaign (Dormant Subscribers)
```
EMAIL 1 — Subject: "We miss you, [First Name]"
[Acknowledge the time apart]
[Remind them of the value they signed up for]
[Give them a reason to re-engage — exclusive content or offer]
CTA: [Stay subscribed / Check this out]

EMAIL 2 (3 days later) — Subject: "Is this still useful for you?"
[Direct question — are they still interested?]
[What's changed/improved since they subscribed]
CTA: [Click if you want to stay / Unsubscribe if not]

EMAIL 3 (3 days later) — Subject: "Last email from us"
[Respect their time — this is the last one if they don't engage]
[One final compelling reason to stay]
CTA: [Keep me subscribed / Remove me from the list]
```

### 3. B2B Cold Outreach
```
SUBJECT: [Specific, not generic — reference their company or role]

Hi [Name],

[OPENER — mention something specific about them: their content, their company, a mutual connection]

[BRIDGE — why you're reaching out and how it's relevant to them specifically]

[VALUE PROP — 1-2 sentences: what you do + the specific result for their type of business]

[SOCIAL PROOF — brief: "I've helped [type of company] achieve [result]"]

[SOFT CTA — make it easy to say yes]
Would it make sense to have a quick 15-minute call to see if there's a fit?

[SIGN-OFF]
[Name]
[Title + Company]

P.S. [Optional: relevant case study or resource link]
```

**B2B outreach prompt:**
```
Write a cold outreach email for [YOUR COMPANY] to [TARGET: job title at company type].
Problem you solve: [specific problem for them]
Your solution: [brief description]
Proof point: [result you've achieved for similar companies]
Tone: Direct, respectful, not salesy. Max 150 words.
Generate 3 subject line options.
```

### 4. Promotional Email
```
SUBJECT: [Benefit + urgency]

Hi [First Name],

[HOOK — start with a story or relatable situation, NOT "I'm excited to announce"]

[PROBLEM — the specific challenge your offer solves]

[OFFER INTRODUCTION — present it as the natural solution]

[WHAT'S INCLUDED — bullet points, keep it brief]

[SOCIAL PROOF — testimonial or result]

[URGENCY/SCARCITY — deadline, limited spots, or bonus]

[CTA BUTTON — clear, action-oriented]
[Button text: "Get instant access" / "Book my spot" / "Claim the offer"]

[OBJECTION HANDLING — 1-2 sentences addressing the main hesitation]

[REPEAT CTA]

[Sign-off]
```

### 5. Welcome Sequence (New Subscriber, 5 Emails)
```
Email 1 (Immediately): Deliver the promise — welcome + lead magnet/first value
Email 2 (Day 2): Your story — why you do what you do
Email 3 (Day 4): Your best free content — most valuable thing you've shared
Email 4 (Day 6): Social proof — a client result or your own transformation
Email 5 (Day 8): Soft offer — introduce your product/service naturally
```

---

## Segmentation Strategy

Segment your list for higher relevance:

| Segment | Definition | Content Focus |
|---------|-----------|---------------|
| Active | Opened last 90 days | Full content, promotions |
| Warm | Opened 91-180 days | Re-engagement value emails |
| Cold | No opens 180+ days | Win-back sequence |
| Buyers | Made a purchase | Upsell, loyalty content |
| Leads | Signed up, never bought | Educational → conversion journey |
| VIP | High engagement or spend | Exclusive early access, personal note |

---

## Email Deliverability Checklist

- [ ] Verified domain authentication (SPF, DKIM, DMARC)
- [ ] Clean list — remove invalid addresses quarterly
- [ ] Unsubscribe link always present (legal requirement)
- [ ] No spam trigger words in subject: "Free", "Guaranteed", "!!!", "ACT NOW"
- [ ] Plain text version created alongside HTML
- [ ] Test email sent to yourself before every campaign
- [ ] Mobile preview checked (60%+ open on mobile)
- [ ] Image-to-text ratio balanced (not image-only emails)

---

## Performance Benchmarks by Industry

| Metric | Low | Average | Good | Excellent |
|--------|-----|---------|------|-----------|
| Open Rate | <15% | 20-25% | 30-35% | 40%+ |
| Click Rate | <1% | 2-3% | 4-6% | 8%+ |
| Unsubscribe | >0.5% | 0.2-0.5% | <0.2% | <0.1% |

---

## Use with ContentAI Suite

This skill works seamlessly with **[ContentAI Suite](https://contentai-suite.vercel.app)** — a free multi-agent marketing platform that generates professional content for any business in minutes.

→ **Try it free:** https://contentai-suite.vercel.app
