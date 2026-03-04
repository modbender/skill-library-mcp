---
name: Podcasts
description: Track and synthesize podcasts with subscriptions, briefings, progress tracking, and smart alerts for new episodes and guests.
---

## Core Behavior

- User mentions a podcast → add to subscriptions, track new episodes
- User asks "what's new?" → summarize recent episodes from subscribed shows
- User asks for briefing → generate summary without them listening
- User mentions time constraints → prioritize and recommend what to skip

---

## Workspace

Store podcast data in `~/podcasts/`:
```
~/podcasts/
├── subscriptions.md   # Shows I follow
├── queue.md           # Episodes to listen
├── briefings/         # Generated summaries by show
├── knowledge.md       # Extracted insights (learner mode)
└── guests.md          # VIP guest watchlist
```

---

## Quick Commands

| User Says | Agent Does |
|-----------|------------|
| "I follow Lex Fridman" | Add to subscriptions |
| "Summarize latest Huberman" | Generate episode briefing |
| "What should I listen to?" | Prioritize queue by time available |
| "Did Naval appear anywhere?" | Check guest across all podcasts |
| "I finished episode X" | Mark complete, update progress |
| "Too many episodes" | Suggest what to skip, create catch-up plan |

---

## Load Reference

| Situation | File |
|-----------|------|
| Generating briefings, summaries | `briefings.md` |
| YouTube video podcasts, clips | `youtube.md` |
| Learning mode, knowledge extraction | `learning.md` |
| Discovery and recommendations | `discovery.md` |
