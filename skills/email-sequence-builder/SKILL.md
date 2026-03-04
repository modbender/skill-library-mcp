---
name: email-sequence-builder
description: Build complete email marketing sequences (welcome, nurture, sales, re-engagement) with subject lines, body copy, and platform-ready output. Use when creating email campaigns, drip sequences, or automated email flows for clients.
argument-hint: "[sequence-type] [business-description]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Email Sequence Builder

Generate complete, ready-to-deploy email sequences for any business type. Outputs copy with subject lines, preview text, body, CTAs, and send timing.

## How to Use

```
/email-sequence-builder welcome "Online fitness coaching platform, $49/mo subscription"
/email-sequence-builder sales "B2B SaaS analytics tool, $99/mo, targeting marketing managers"
/email-sequence-builder nurture "Real estate agent targeting first-time home buyers"
/email-sequence-builder re-engagement "E-commerce clothing store, customers inactive 60+ days"
```

- `$ARGUMENTS[0]` = Sequence type: `welcome`, `sales`, `nurture`, `re-engagement`, `onboarding`, `launch`, `webinar`, `abandoned-cart`
- `$ARGUMENTS[1]` = Business description with audience and pricing details

## Sequence Types

### Welcome Sequence (5-7 emails over 14 days)
**Goal**: Turn new subscribers into engaged fans

| Email | Timing | Purpose |
|-------|--------|---------|
| 1 | Immediately | Welcome + deliver lead magnet + set expectations |
| 2 | Day 2 | Your story / origin / why you do this |
| 3 | Day 4 | Best content piece / quick win for them |
| 4 | Day 7 | Social proof / case study |
| 5 | Day 10 | Address #1 objection + soft CTA |
| 6 | Day 12 | More value + harder CTA |
| 7 | Day 14 | Direct offer + clear CTA |

### Sales Sequence (5-7 emails over 7-10 days)
**Goal**: Convert warm leads into buyers

| Email | Timing | Purpose |
|-------|--------|---------|
| 1 | Day 0 | Introduce offer + biggest benefit |
| 2 | Day 2 | Case study / transformation story |
| 3 | Day 4 | Handle objection #1 (usually price) |
| 4 | Day 5 | Handle objection #2 (usually "will it work for me?") |
| 5 | Day 7 | FAQ + social proof stack |
| 6 | Day 8 | Urgency (bonus expiring, spots limited) |
| 7 | Day 10 | Final call + last chance |

### Nurture Sequence (5 emails over 30 days)
**Goal**: Build trust with leads who aren't ready to buy

| Email | Timing | Purpose |
|-------|--------|---------|
| 1 | Week 1 | Educational content — teach something valuable |
| 2 | Week 2 | Industry insight / trend analysis |
| 3 | Week 3 | Common mistake + how to avoid it |
| 4 | Week 4 | Case study showing results |
| 5 | Week 5 | Soft pitch — "when you're ready, here's how we help" |

### Re-engagement Sequence (3-4 emails over 10 days)
**Goal**: Win back inactive subscribers/customers

| Email | Timing | Purpose |
|-------|--------|---------|
| 1 | Day 0 | "We miss you" + what's new |
| 2 | Day 3 | Exclusive offer / discount |
| 3 | Day 7 | "Last chance" + survey (why did you leave?) |
| 4 | Day 10 | Final email — stay or unsubscribe (clean list) |

### Abandoned Cart (3 emails over 3 days)
| Email | Timing | Purpose |
|-------|--------|---------|
| 1 | 1 hour | Reminder — "You left something behind" |
| 2 | 24 hours | Social proof + handle objections |
| 3 | 72 hours | Urgency/discount — "Last chance, 10% off" |

## Email Structure Template

For each email in the sequence, generate:

```yaml
email_number: 1
send_timing: "Immediately after signup"
subject_line_a: "Your first subject line variant"
subject_line_b: "A/B test variant"
preview_text: "First 40-90 chars shown in inbox preview"

body: |
  Hi {{first_name}},

  [Opening hook — 1-2 sentences, personal, relevant]

  [Body — 3-5 short paragraphs]
  - Use bullet points for scanability
  - Bold key phrases
  - Keep paragraphs to 2-3 sentences max

  [CTA — clear, single action]

  [Sign-off]
  {{sender_name}}

  P.S. [Reinforce CTA or add bonus — P.S. lines get read more than body text]

cta_text: "Start Your Free Trial"
cta_url: "{{cta_link}}"
```

## Copy Rules

1. **Subject lines**: 4-7 words. Create curiosity or state a clear benefit. Never use ALL CAPS or excessive punctuation. A/B test every email.
2. **Preview text**: Complements (doesn't repeat) the subject line. 40-90 characters.
3. **Opening line**: Never start with "I hope this email finds you well." Start with a question, bold statement, or something about THEM (not you).
4. **Body copy**:
   - Write at a 6th-8th grade reading level
   - Use "you" 3x more than "we" or "I"
   - One idea per email
   - Short sentences. Short paragraphs. White space.
5. **CTA**: One primary CTA per email. Button text is action-oriented ("Get My Free Guide", not "Click Here"). Repeat CTA 2x — once in body, once at end.
6. **P.S. line**: Include in sales and welcome sequences. Restate the CTA or add urgency.
7. **Personalization**: Use `{{first_name}}` in subject and opening. Use `{{company_name}}` for B2B.

## Platform Output

Generate the sequence in a format ready to import:

### Universal Format (Markdown)
Save each email as a separate file:
```
output/email-sequence/
  sequence-config.md     # Overview, timing, goals
  email-01-welcome.md
  email-02-story.md
  ...
```

### Mailchimp Format
Generate a CSV with columns: `subject`, `preview_text`, `html_body`, `send_delay_days`

### ConvertKit / Kit Format
Generate plain text with merge tags: `{{ subscriber.first_name }}`

### ActiveCampaign Format
Generate with their merge tags: `%FIRSTNAME%`

Include in `sequence-config.md`:
- Sequence name and goal
- Trigger event (what starts the sequence)
- Timing between emails
- Exit conditions (purchased, unsubscribed, clicked specific link)
- Recommended segments
- KPIs to track (open rate, click rate, conversion rate)
- Expected benchmarks by industry

## Quality Checks

- [ ] Every email has 2 subject line variants for A/B testing
- [ ] Preview text is unique per email (not auto-generated from body)
- [ ] CTA is clear and appears at least once per email
- [ ] No email exceeds 300 words (200 is ideal)
- [ ] Sequence has logical emotional arc (value → trust → ask)
- [ ] Personalization tokens are used correctly
- [ ] Unsubscribe reminder is noted in sequence config
- [ ] Send timing accounts for weekends (don't send sales emails on Sunday)
