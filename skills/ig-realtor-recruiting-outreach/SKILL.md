---
name: ig-realtor-recruiting-outreach
description: Build compliant Instagram DM outreach campaigns to recruit realtors into brokerage downlines (e.g., eXp Realty, Real Broker). Use when a user wants lead qualification, personalized first-touch DMs, and follow-up sequences from IG profile data, then export ready-to-send outreach files.
---

# IG Realtor Recruiting Outreach

Use this skill to turn IG lead lists into practical recruiting outreach without mass-blast spam language.

## Workflow

### 1. Gather Leads

Use the best source available:

- ClawHub/IG scraping skill output (preferred if available)
- Manually curated CSV from IG research

Minimum CSV fields:

- `instagram_handle`
- `first_name` (or `name`)
- `city` (optional)
- `brokerage` (optional)
- `target_brokerage` (optional; falls back to CLI default)

Recommended enrichments:

- `followers`
- `last_post_theme`
- `pain_point`
- `production_tier` (`new`, `building`, `team_lead`, `top_producer`)
- `notes`

### 2. Generate Outreach Sequence

Run:

```bash
python3 scripts/build_ig_recruiting_outreach.py \
  --input /path/to/realtor_leads.csv \
  --campaign-name "exp-phoenix-week1" \
  --default-target-brokerage "eXp Realty" \
  --output-dir output/ig-recruiting
```

The script creates:

- `messages_<campaign>.csv` with staged DM sequence
- `audit_<campaign>.json` with lead-level rationale + quality notes
- `playbook_<campaign>.md` with send cadence and talking points

### 3. QA Before Sending

Check each message for:

- Correct name/handle and brokerage
- Specific but truthful personalization
- No guaranteed income claims
- No manipulative urgency or fake scarcity

### 4. Send and Track

Send manually in Instagram. Use CRM tags for sequence stage:

- `ig_sent_d1`
- `ig_sent_f1`
- `ig_sent_f2`
- `ig_sent_breakup`

## Input Schema

The script supports these columns (case-insensitive):

- `instagram_handle` (required)
- `first_name`
- `name`
- `brokerage`
- `target_brokerage`
- `city`
- `followers`
- `last_post_theme`
- `pain_point`
- `production_tier`
- `notes`

## Safety Rules

- Do not claim guaranteed income, splits, or stock upside.
- Do not impersonate existing recruits or fabricate social proof.
- Keep tone consultative and one clear CTA per message.
- Respect platform rules and local solicitation regulations.

## References

- `references/message-framework.md`
- `references/compliance-guardrails.md`
