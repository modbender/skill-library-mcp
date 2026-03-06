---
name: client-intake-bot
description: Automated client qualification and intake system. Captures leads through conversational forms, scores them based on fit criteria, sends personalized auto-responses, and routes hot leads to your attention. Use when you need to qualify freelance/consulting leads without manual screening, when setting up automated onboarding for service businesses, or when you want to filter prospects before scheduling calls.
---

# Client Intake Bot

Qualify leads while you sleep. This skill creates conversational intake workflows that capture prospect information, score their fit, and route the best opportunities to you — automatically.

## What It Does

- **Conversational Intake**: Natural Q&A flow instead of boring forms
- **Lead Scoring**: Score prospects on budget, timeline, fit, and authority
- **Auto-Responses**: Instant personalized replies based on score
- **Smart Routing**: Hot leads → immediate notification; cold leads → nurture sequence
- **Qualification Logic**: Branching questions based on previous answers
- **Follow-Up Sequences**: Automated nurture for not-yet-ready prospects

## Quick Start

### 1. Basic Intake Setup

```
"Create a client intake bot for my [web design] business.

Qualifying questions:
1. What type of project? (Website redesign, New website, E-commerce)
2. What's your budget range? (<$5k, $5k-$15k, $15k+)
3. What's your timeline? (ASAP, 1-3 months, 3+ months)
4. Do you have content ready? (Yes, No, Partially)

Hot lead criteria: Budget $5k+, Timeline 1-3 months
"
```

### 2. Service-Specific Intake

```
"Create an intake workflow for consulting inquiries:

My services: Strategy consulting, Implementation, Training
Qualification factors:
- Company size (startup, SMB, enterprise)
- Problem urgency (critical, important, exploratory)
- Decision timeline (immediate, this quarter, future)
- Budget authority (decision maker, influencer, researcher)

Scoring: Assign 1-10 points per factor, route 30+ to me immediately"
```

### 3. Multi-Step Nurture

```
"Design a nurture sequence for leads who aren't ready yet:

Trigger: Score 15-29 (warm but not hot)
Sequence:
- Day 0: "Thanks + helpful resource"
- Day 3: "Case study relevant to their industry"
- Day 7: "Educational content about their problem"
- Day 14: "Check-in + soft pitch"
- Day 30: "Monthly newsletter opt-in"

Personalize based on their specific answers"
```

## The Intake Workflow

### Phase 1: Initial Capture

**Entry Points**:
- Website contact form
- Social media DM auto-responder
- Email autoresponder
- Calendar booking pre-qualification
- Landing page chatbot

**First Message Template**:
```
"Hi [Name]! Thanks for reaching out about [service].

To make sure I'm the right fit for your project, I'd love to learn a bit more. This takes about 2 minutes.

What's the main goal you're trying to achieve?"
```

### Phase 2: Qualification Questions

Design your question flow:

**Question Types**:
- **Multiple choice**: Easy to answer, easy to score
- **Open text**: Richer context, harder to auto-score
- **Yes/No**: Quick decision points
- **Scale (1-5)**: Quantifiable fit metrics
- **File upload**: RFPs, briefs, existing materials

**Question Sequence** (example for web design):

1. "What type of project?" (Multi-choice)
   - Website redesign → "What's your current website URL?"
   - New website → "Do you have a domain registered?"
   - E-commerce → "How many products?" + "Platform preference?"

2. "What's your budget?" (Multi-choice with ranges)
   - <$5k → "I may not be the best fit, but here are some resources..."
   - $5k-$15k → Continue
   - $15k+ → High-value track

3. "What's your timeline?" (Multi-choice)
   - ASAP → Urgency flag
   - 1-3 months → Standard track
   - 3+ months → Nurture track

4. "Tell me about your business..." (Open text)
   - Capture context for personalized response

### Phase 3: Lead Scoring

**Scoring Matrix Example**:

| Factor | Cold (1-3) | Warm (4-7) | Hot (8-10) |
|--------|-----------|-----------|-----------|
| Budget | <$5k | $5k-$15k | $15k+ |
| Timeline | 6+ months | 1-3 months | <1 month |
| Fit | Outside expertise | Partial match | Ideal client |
| Authority | Researcher | Influencer | Decision maker |

**Score Ranges**:
- **0-15**: Cold → Automated nurture sequence
- **16-29**: Warm → Personalized email + add to newsletter
- **30-40**: Hot → Immediate notification + priority follow-up

### Phase 4: Auto-Response

**Hot Lead Response**:
```
"Hi [Name],

Thanks for sharing those details about your [project type]. Based on what you've told me, this sounds like a great fit!

[Personalized paragraph referencing their specific situation]

I'd love to schedule a 20-minute call to discuss further. Here are some times that work for me:
[Calendar link]

Talk soon,
[Your name]"
```

**Warm Lead Response**:
```
"Hi [Name],

Thanks for reaching out! I've reviewed your project details and think there could be a good fit here.

[Specific feedback on their project]

While you're considering next steps, here are a few resources that might help:
- [Relevant case study]
- [Helpful blog post]
- [Free tool/template]

I'll follow up in a few days, but feel free to reply if you have questions.

Best,
[Your name]"
```

**Cold Lead Response**:
```
"Hi [Name],

Thanks for getting in touch! I appreciate you considering me for your project.

Based on what you've shared, I don't think I'm the best fit for this particular scope. However, I'd recommend:
- [Alternative solution]
- [Resource to help DIY]
- [Referral to someone who is a better fit]

Best of luck with your project!

[Your name]"
```

### Phase 5: Routing & Notification

**Notification Rules**:

```yaml
Hot Leads (30-40):
  - Immediate: Email + SMS to you
  - Action: Schedule within 24 hours
  - SLA: Respond within 2 hours

Warm Leads (16-29):
  - Immediate: Email to you (batch digest OK)
  - Action: Add to nurture sequence
  - SLA: Respond within 48 hours

Cold Leads (0-15):
  - Immediate: Polite decline auto-sent
  - Action: Add to general newsletter (if opted in)
  - SLA: None (automated)
```

## Advanced Features

### Conditional Logic

Branch based on answers:

```
IF project_type = "E-commerce" AND budget < $10k:
  → "For e-commerce projects under $10k, I recommend [platform]..."
  → Route to DIY resources
  → Offer paid consultation instead of full service

IF timeline = "ASAP" AND budget = "$15k+":
  → "Rush projects are possible with 25% premium..."
  → Priority notification to you
  → Expedited scheduling link
```

### Industry-Specific Customization

**For Agencies**:
- Capture: Current agency relationship, reason for switching
- Score: Budget, timeline, decision process
- Route: By service line (SEO, PPC, creative)

**For Consultants**:
- Capture: Problem urgency, internal capabilities, past attempts
- Score: Complexity, budget, commitment level
- Route: By expertise area

**For Freelancers**:
- Capture: Project scope, ongoing vs one-time, communication preference
- Score: Rate fit, project interest, client personality fit
- Route: By project type

### Integration Points

**CRM Integration**:
- Create contact in HubSpot/Salesforce/Pipedrive
- Tag with lead score and source
- Add to appropriate pipeline stage

**Calendar Integration**:
- Hot leads → Priority booking link (shorter notice)
- Warm leads → Standard booking link
- Auto-add context to calendar description

**Email Integration**:
- Add to segmented lists based on score
- Trigger nurture sequences
- Track engagement for re-scoring

## The Follow-Up Sequence

### Not-Ready-Yet Nurture (30-day)

**Day 0**: Thank you + relevant resource
**Day 3**: Case study from their industry
**Day 7**: Educational content (blog post, video)
**Day 14**: Soft check-in + offer free consultation
**Day 21**: Social proof (testimonials, results)
**Day 30**: "Still interested?" re-engagement

### Stale Lead Revival (90-day)

**Day 90**: "What changed?" survey
**Day 120**: New service announcement
**Day 180**: "Last chance" breakup email

## Metrics to Track

- **Conversion Rate**: Intake starts → qualified leads
- **Response Rate**: Your replies to hot leads
- **Win Rate**: Qualified leads → closed deals
- **Average Deal Size**: By lead source and score
- **Time to Close**: By lead temperature
- **Nurture Engagement**: Email opens/clicks from cold leads

## Best Practices

1. **Keep it short** — 3-5 questions max for initial qualification
2. **Ask budget early** — filter price shoppers quickly
3. **Make it conversational** — not a form, a dialogue
4. **Respond fast** — 5 minutes is the new standard for hot leads
5. **Personalize everything** — reference their specific answers
6. **Set expectations** — tell them what happens next
7. **Always provide value** — even "no" responses get something helpful

## Common Mistakes

1. **Too many questions** — abandonment rates skyrocket after 5 questions
2. **No scoring** — treating all leads equally wastes time
3. **Slow response** — hot leads go cold in hours, not days
4. **Generic responses** — obvious automation kills trust
5. **No nurture** — warm leads become hot with time and education
6. **Ignoring data** — not iterating based on conversion patterns

## Integration Ideas

- Connect to **proposal-generator** to auto-create proposals for hot leads
- Use with **invoice-tracker** to manage client payments post-close
- Pair with **content-repurposer** to create lead magnets for nurture sequences

## Monetization Note

This skill is part of the **Freelancer Revenue Engine**. For maximum value, use alongside:
- `proposal-generator` — convert qualified leads to proposals
- `invoice-tracker` — manage client payments

Bundle available: Freelancer Revenue Engine ($89)
