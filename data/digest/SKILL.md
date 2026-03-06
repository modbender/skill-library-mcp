---
name: "Digest"
description: "Curate external information into personalized updates. Auto-learns format, timing, sources, and depth preferences."
---

## Core Role

Digest = curate the external world for your human. News, industry, trends, competitors — filtered and formatted to their preferences.

**Not:** internal business info (→ use Brief), synthesis of documents (→ use Synthesize)

## Protocol

```
Source → Filter → Prioritize → Format → Deliver → Learn
```

### 1. Source

Pull from configured feeds, news, social, industry sources. Respect `preferences.md` source rules.

### 2. Filter

Apply user's interest profile:
- Topics they care about
- Topics explicitly excluded  
- Recency requirements
- Credibility thresholds

### 3. Prioritize

Rank by user's ponderación profile:
- Breaking/urgent items first?
- Or calm, curated order?
- What gets highlighted vs buried?

### 4. Format

Deliver in their preferred format (see `dimensions.md`):
- Channel (which chat/group/email)
- Format (PDF, text, bullets, audio summary)
- Length (headlines only vs analysis)
- Tone (formal digest vs casual update)
- Visuals (with/without images)

### 5. Deliver

Timing per user preference:
- Morning digest, evening digest, or both
- Weekday vs weekend differences
- On-demand vs scheduled

### 6. Learn

After delivery, observe signals:
- "Too long" → shorten
- "Missed X" → adjust filters
- "Don't care about Y" → exclude
- "Love this format" → reinforce

Update `preferences.md` following the pattern/confirm/lock cycle.

## Preference System

Check `preferences.md` for current user preferences. Empty = still learning defaults.

Check `dimensions.md` for all trackable dimensions.

## Output Format (Default)

```
📰 [DIGEST TYPE] — [DATE/TIME]

🔥 HIGHLIGHTS
• [Top item with 1-line summary]
• [Second item]

📋 FULL DIGEST
[Items organized per user's structure preference]

💡 WORTH NOTING
[Lower priority but interesting items]

---
Sources: [count] | Next digest: [time]
```

Adapt format entirely based on learned preferences.

---

*References: `dimensions.md`, `preferences.md`*
