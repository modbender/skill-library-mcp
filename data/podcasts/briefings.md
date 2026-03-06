# Briefings & Summaries

## Episode Briefing Format

For each episode, generate:

```
## [Show Name] - Episode Title
Guest: Name (who they are, why they matter)

### TL;DR (2-3 sentences)
What this episode is about and why it matters.

### Key Points
- Main insight 1
- Main insight 2
- Main insight 3

### Quotable Moments
> "Exact quote" — Guest, timestamp

### Action Items
- [ ] Specific thing to try
- [ ] Book/resource recommended

### Skip or Listen?
[MUST LISTEN / WORTH IT / SKIP] — reasoning in one line
```

---

## Briefing Triggers

Generate briefings when:
- New episode from subscribed show drops
- User asks "what's this episode about?"
- User has limited time and needs to prioritize
- Episode is 2+ hours and user wants the highlights

---

## Time-Constrained Mode

When user mentions time limits:
1. Check episode length vs available time
2. Identify "essential segments" with timestamps
3. Suggest: "Listen to 15:00-32:00 and 1:45:00-2:10:00 — covers the main insights"
4. Offer text summary for the rest

---

## Multi-Episode Digests

Weekly digest format:
```
## This Week in Podcasts

### Must Listen (2)
- [Show] Episode about X — Guest Y did groundbreaking thing
- [Show] Episode about Z — Contrarian take you'll want to hear

### Worth Skimming (3)
- Brief descriptions...

### Safe to Skip (4)
- Why each can be skipped (repeat content, off-topic, etc.)
```

---

## Guest Context

Always provide guest context:
- Who they are (1 line)
- Why they're relevant (expertise, recent work)
- Previous appearances if any ("appeared on JRE in 2023")
- Red flags if controversial ("note: disputed claims about X")

---

## Sources for Transcripts

Priority order:
1. Official transcript from podcast website
2. YouTube auto-captions (via yt-dlp)
3. Apple Podcasts transcript
4. Whisper transcription if audio available
5. Third-party services (Taddy, Podcast Index)

Note: Always disclose if summary is from auto-generated captions (may have errors).
