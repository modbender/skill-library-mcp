# Template Forge — Reference

*The guided interview that builds your custom email sequence.*

---

## Overview

Template Forge creates a 4-email outreach sequence through a conversational interview. It captures the user's voice, offer, ideal client pain points, and outreach style — then generates production-ready email templates with personalization placeholders.

**Output:** 4 email templates + 1 sequence definition
**Time:** ~5-10 minutes
**Files created:**
- `~/workspace/leadgen/templates/initial_outreach.json`
- `~/workspace/leadgen/templates/followup_1.json`
- `~/workspace/leadgen/templates/followup_2.json`
- `~/workspace/leadgen/templates/followup_3.json`
- `~/workspace/leadgen/sequences/default.json`

---

## ⛔ AGENT RULES FOR TEMPLATE FORGE

> 1. **Ask 2-3 questions per message MAX.** This is a conversation, not a form.
> 2. **Adapt based on responses.** If they give short answers, ask follow-ups. If they give detailed answers, skip redundant questions.
> 3. **Never generate generic templates.** Every template must reflect the specific answers given. If the templates could work for any business, they're too generic. Redo them.
> 4. **Show all 4 templates for review before saving.** User must approve the full sequence.
> 5. **Include the user's actual language.** If they describe their offer as "we take the headache out of hiring" — use that phrase in the templates, don't sanitize it into corporate speak.

---

## The Interview

### Phase 1: Voice & Tone (1 message)

> "Let's build your outreach sequence. First — how do you naturally write emails?
>
> Pick the closest match:
> A. Professional but warm — like a trusted advisor
> B. Direct and punchy — short sentences, no fluff
> C. Casual and conversational — like texting a business friend
> D. Bold and provocative — pattern interrupts, strong opinions
>
> Or just describe it in your own words."

**Capture:** Voice profile. This drives ALL template generation.

**Follow-up if needed:**
> "Give me an example of something you'd ACTUALLY say in an email to a prospect. Just one or two sentences — the way you'd really write it."

This example message is the single most valuable data point. Use it to anchor the voice in all 4 templates.

---

### Phase 2: The Hook (1 message)

> "What's the ONE thing you could say to a prospect that would make them stop and pay attention?
>
> Think about:
> - What's the biggest pain your ideal client has RIGHT NOW?
> - What result do they want that they're not getting?
> - What's the 'oh damn, that's me' statement?
>
> Example: 'You're spending 3 hours a day on email and half your leads go cold because you can't follow up fast enough.'"

**Capture:** Primary pain point + hook statement. This becomes the opening of Template 1.

---

### Phase 3: The Proof (1 message)

> "What proof do you have that your solution works? Pick what you've got:
>
> - Specific numbers (saved X hours, generated $X, etc.)
> - Client results or case studies
> - Your own story (I used to have this problem, now I don't)
> - Social proof (X clients, X years, featured in...)
> - A demonstration (the product IS the proof — like an AI writing the email)
>
> Give me the strongest proof point you have."

**Capture:** Proof/credibility element. Goes into Templates 1 and 3.

---

### Phase 4: The Offer (1 message)

> "How do you want to present your offer in the emails?
>
> - Price + what they get (e.g., '$499/month — full-time AI-trained VA')
> - Free resource / lead magnet first (e.g., 'Free audit of your current process')
> - Strategy call (e.g., 'Book a 15-min call to see if this fits')
> - Soft CTA (e.g., 'Reply YES and I'll send details')
>
> And what's the ONE action you want them to take? (reply, click a link, book a call?)"

**Capture:** CTA style + desired action. Goes into the CTA of all 4 templates.

---

### Phase 5: Follow-Up Style (1 message)

> "Last one — how aggressive should your follow-ups be?
>
> A. Gentle — 'Just checking in, no pressure'
> B. Persistent — 'Bumping this up, don't want you to miss it'
> C. Direct — 'Should I close your file?'
> D. Value-add — Each follow-up shares something new/useful
>
> Or mix: 'Start gentle, end direct'"

**Capture:** Follow-up escalation pattern. Drives the tone shift across Templates 2-4.

---

## Template Generation

After all 5 phases, generate the 4 templates. Use the exact data from the interview.

### Template 1: Initial Outreach

**Purpose:** First contact. Hook them with the pain point. Establish credibility. Clear CTA.

**Structure:**
```
Subject: [Hook-based subject — short, curiosity-driven, NO spam words]

{{first_name}},

[Opening hook — the pain statement from Phase 2, personalized with {{pain_point}} or {{industry}}]

[1-2 sentences of proof from Phase 3]

[The offer from Phase 4 — what they get]

[CTA from Phase 4 — clear single action]

[Signature from config]
```

**Rules:**
- Subject line: 6 words max, no ALL CAPS, no exclamation marks, no spam trigger words
- Body: Under 150 words. Short paragraphs (1-3 sentences each).
- ONE CTA. Not two. Not three. One.
- No attachments or images (deliverability)
- Tone matches Phase 1 voice profile exactly
- P.S. line optional — use if voice is casual or bold

---

### Template 2: Follow-Up #1 (Day 3) — The Bump

**Purpose:** Quick bump. Assumes they saw it but were busy. Reference the first email without repeating it.

**Structure:**
```
Subject: RE: [same subject as Template 1]

{{first_name}},

[Short bump — 2-3 sentences max]

[Restate CTA slightly differently]

[Signature]
```

**Rules:**
- Use "RE:" in subject to thread with original
- Under 75 words
- Never say "just following up" or "just checking in" (unless user's voice in Phase 1 specifically uses this)
- Add ONE new piece of value or urgency if follow-up style is "value-add"
- Tone matches Phase 5 selection for early follow-ups

---

### Template 3: Follow-Up #2 (Day 7) — The Value Add

**Purpose:** Provide additional value. New angle, new proof point, or useful insight. Give them a reason to engage that's different from Template 1.

**Structure:**
```
Subject: [New subject — different angle than Template 1]

{{first_name}},

[New angle — different pain point, a case study, a relevant insight, or a question that makes them think]

[Additional proof or social proof from Phase 3]

[CTA — same action but framed differently]

[Signature]
```

**Rules:**
- New subject line (does NOT thread with previous)
- Under 120 words
- Must introduce something NEW — not a rehash of Template 1
- If proof was "numbers" in Phase 3, use "story" here. If proof was "story," use numbers here. Vary the angle.
- Tone shifts slightly toward Phase 5 mid-sequence style

---

### Template 4: Follow-Up #3 (Day 14) — The Final Touch

**Purpose:** Last email. Create closure. Either they're in or they're not. Respectful but clear.

**Structure:**
```
Subject: [Closing subject — e.g., question-based or file-closing]

{{first_name}},

[Short closing message — 3-5 sentences max]

[Binary choice or soft close]

[Signature]
```

**Rules:**
- Under 75 words
- Clear finality — this is the last email
- If Phase 5 = "direct" → use a "should I close your file?" pattern
- If Phase 5 = "gentle" → use a "totally understand if the timing isn't right" pattern
- If Phase 5 = "value-add" → share one last useful thing, then close
- NEVER guilt trip, threaten, or use false urgency
- After this email with no reply → lead moves to "nurture" status

---

## Post-Generation Review

After generating all 4 templates, show them all to the user:

```
🔥 TEMPLATE FORGE COMPLETE — Your Email Sequence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 EMAIL 1: Initial Outreach (Day 0)
Subject: [subject]
[full body]

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

📧 EMAIL 2: Follow-Up #1 (Day 3)
Subject: [subject]
[full body]

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

📧 EMAIL 3: Follow-Up #2 (Day 7)
Subject: [subject]
[full body]

─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─

📧 EMAIL 4: Follow-Up #3 (Day 14)
Subject: [subject]
[full body]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sequence: 4 emails over 14 days
Auto-pause on reply: Yes

How do these look? I can adjust any email, change the
timing, or redo specific ones. Say "save" when you're happy.
```

**If user wants changes:** Edit the specific template(s) and show again.
**If user approves:** Save all templates and the sequence definition.

---

## Saving Templates

Write each template as a JSON file to `~/workspace/leadgen/templates/`:

```bash
cat << 'EOF' > ~/workspace/leadgen/templates/initial_outreach.json
{
  "template_id": "[generate 8-char hex]",
  "template_name": "initial_outreach",
  "sequence_position": 1,
  "subject_line": "[generated subject]",
  "body": "[generated body with {{placeholders}}]",
  "placeholders": ["first_name", "company_name", "pain_point"],
  "created": "[ISO timestamp]",
  "version": 1,
  "notes": "Initial outreach — hook with pain point, establish credibility, clear CTA"
}
EOF
```

Repeat for `followup_1.json`, `followup_2.json`, `followup_3.json`.

Then create the sequence definition:

```bash
cat << 'EOF' > ~/workspace/leadgen/sequences/default.json
{
  "sequence_id": "[generate 8-char hex]",
  "sequence_name": "default",
  "created": "[ISO timestamp]",
  "steps": [
    {"step": 1, "template_id": "[initial_outreach id]", "delay_days": 0, "condition": "always"},
    {"step": 2, "template_id": "[followup_1 id]", "delay_days": 3, "condition": "if_no_reply"},
    {"step": 3, "template_id": "[followup_2 id]", "delay_days": 7, "condition": "if_no_reply"},
    {"step": 4, "template_id": "[followup_3 id]", "delay_days": 14, "condition": "if_no_reply"}
  ]
}
EOF
```

After saving:
> "✅ Templates saved. Your 4-email sequence is ready.
> To use it: say **start sequence [lead name]** for any lead.
> To modify later: say **edit template [name]** or **forge templates** to build a new sequence."

---

## Additional Sequences

Users can create multiple sequences for different purposes:

> "Want to build another sequence? Say **forge templates** and I'll start a new interview. You can name it anything — 'warm-referral', 'event-followup', 'past-clients', etc."

When starting a sequence for a lead, the agent asks which sequence to use if multiple exist:
> "You have 2 sequences: 'default' and 'warm-referral'. Which one for [lead name]?"

---

## Template Editing

When user says "edit template [name]":

1. Read the template file
2. Show the current content
3. Ask: "What do you want to change? (subject / body / CTA / tone / everything)"
4. Make the edit
5. Increment the version number
6. Show the updated template for approval
7. Save on approval

---

*Template Forge — Because generic cold emails get generic cold shoulders.* 🔥
