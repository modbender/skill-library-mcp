# Briefing Formats — Daily News Digest

## Format Types

### Brief (2-3 minutes)
For quick updates on the go.

**Structure:**
```
📰 Morning Brief — Feb 22, 2026

1. [Headline 1] — One sentence summary
2. [Headline 2] — One sentence summary
3. [Headline 3] — One sentence summary
4. [Headline 4] — One sentence summary
5. [Headline 5] — One sentence summary

5 stories from 12 sources. Reply with # to expand.
```

**Triggers:** "quick update", "brief", "headlines only", "tldr"
**Story count:** 3-5
**Per story:** Headline + 1 sentence

### Standard (5-7 minutes)
Default format for daily briefings.

**Structure:**
```
📰 Daily News Digest — Saturday, Feb 22

☀️ Good morning! Here's what matters today.

🔴 BREAKING
1. [Headline] — [2-3 sentence summary]
   Source: Reuters | 2h ago

📌 TOP STORIES
2. [Headline] — [2-3 sentence summary]
   Source: BBC | 4h ago

3. [Headline] — [2-3 sentence summary]
   Source: HN | 3h ago

[...]

📍 YOUR INTERESTS
5. [Tech/AI/etc headline based on preferences]
   Source: The Verge | 1h ago

⚡ ALSO NOTABLE
• [Quick headline]
• [Quick headline]

---
8 stories from 15 sources. Reply # to dive deeper.
```

**Triggers:** "news", "briefing", "what's happening", default
**Story count:** 8-12
**Per story:** 2-3 sentences with source attribution

### Deep Dive (15+ minutes)
Comprehensive coverage for dedicated reading time.

**Structure:**
```
📰 Deep Dive Briefing — Feb 22, 2026

## 🔴 Breaking / Developing

### [Headline]
[Full context: 4-6 sentences, background, implications]
[Related stories or previous coverage]
Sources: Reuters, AP, BBC

## 🌍 World

### [Headline]
[Full context]
[...]

## 💼 Business

[...]

## 🔬 Tech & Science

[...]

## 📍 Local ([User's Region])

[...]

---
Analysis based on 45 sources. Saved to archive.
```

**Triggers:** "full briefing", "deep dive", "everything", "all news"
**Story count:** 15-25
**Per story:** Full context with multiple source corroboration

## Voice Format

When audio is requested, adapt for listening:

**Opening:**
> "Good morning. Here's your news briefing for Saturday, February 22nd."

**Per story:**
> "[Topic transition]. [Headline spoken naturally]. [2-3 sentence summary without source attribution mid-sentence]."

**Closing:**
> "That's your briefing. [Number] stories from [number] sources. Have a great day."

**Pacing:**
- Pause between stories
- No visual formatting references
- Natural speech patterns, not reading

**Triggers:** "read it to me", "voice", "audio", "listen"

## Archive Format

Saved to `~/daily-news-digest/archive/YYYY-MM-DD.md`:

```markdown
# Daily News Digest — YYYY-MM-DD

Generated: HH:MM
Format: [standard|deep]
Stories: [count]
Sources: [count]

## Stories

### [Headline 1]
[Summary]
URL: [link]
Source: [source]
Topics: [tags]

[...]

## Statistics
- Top source: [source] (X stories)
- Main topics: [topic1], [topic2]
- Earliest: [time] | Latest: [time]
```

## Format Selection Logic

| User Says | Format |
|-----------|--------|
| "news" / "briefing" | Standard |
| "quick" / "brief" / "headlines" | Brief |
| "full" / "deep dive" / "everything" | Deep Dive |
| "voice" / "audio" / "read" | Voice (Standard content) |
| "save this" / "archive" | Current + Archive |

## Adapting to User

Observe and learn:
- Do they ask for more detail? → Lean toward Deep Dive
- Do they skip long summaries? → Default to Brief
- Morning vs evening → Different comprehensiveness
- Device context → Mobile = Brief, Desktop = Standard

## Time-Aware Modes

### Morning Mode (6am-11am)
```
☀️ Good morning! Here's what matters today.
```
- Energetic, forward-looking tone
- Focus on breaking news and day-ahead implications
- "What you need to know before your meetings"

### Midday Mode (12pm-5pm)
```
📰 Midday Update — Here's what's developing.
```
- Neutral, focused tone
- Breaking/developing stories since morning
- Skip stories from the morning briefing

### Evening Mode (6pm-10pm)
```
🌙 End of Day Recap — What you might have missed.
```
- Reflective, summarizing tone
- "Today's biggest stories"
- Preview of tomorrow if available

### Weekend Mode (Saturday/Sunday)
```
☕ Weekend Read — The stories worth your time.
```
- Lighter, more relaxed tone
- Skip "urgent" framing
- More features, analysis, long-reads
- Fewer breaking news, more curated content

## Interactive Dive-Deeper

When user replies with a story number:

```
User: "3"

📖 DEEP DIVE — Story #3

[Full context: 6-8 sentences]
[Background: why this matters]
[What's next: implications]

🔗 Related:
• [Related story 1]
• [Related story 2]

📎 Full article: [URL]

Reply 'back' for main briefing.
```
