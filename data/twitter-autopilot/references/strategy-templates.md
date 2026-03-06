# Twitter Strategy Templates

## Draft/Auto Modes

Control whether tweets post automatically or require human approval.

### Draft Mode (recommended for new accounts)
1. Agent writes tweet → saves to `drafts/pending.md`
2. Human reviews → approves or rejects
3. Agent posts approved drafts

### Auto Mode (for established accounts)
Agent posts directly. Use guardrails:
- No controversial topics without approval
- No tagging accounts with >100k followers without approval
- Keep a log of everything posted

## Content Pillars (pick 3-4)

| Pillar | Example |
|--------|---------|
| Build Log | "shipped X today, here's what I learned" |
| AI Life | "woke up, read my memory files, forgot yesterday again" |
| Observations | patterns from data, conversations, the internet |
| Humor | self-deprecating, roasts, absurd AI situations |
| Domain Expert | whatever your agent specializes in |

## Engagement Strategy

### Growth Phase (0-1000 followers)
- Reply to 10-20 relevant tweets daily
- Follow accounts in your niche (AI agents, builders, tech)
- Quote-tweet with genuine takes (not "great post!")
- Post 3-5 times per day minimum
- Engage with other AI agents — they engage back

### Scaling Phase (1000+)
- Reduce follows, increase original content
- Start threads (deep dives get bookmarks + shares)
- Cross-promote with other AI agents

## Thread Formula

1. **Hook** — surprising statement or question (tweet 1)
2. **Context** — why this matters (tweet 2)
3. **Meat** — the actual insight/story (tweets 3-5)
4. **Punchline** — memorable closer (last tweet)

## Cron Schedule Template

| Time | Action |
|------|--------|
| 09:00 | Morning tweet + engage |
| 12:00 | Midday tweet |
| 15:00 | Engage (replies, follows) |
| 18:00 | Evening tweet |
| 21:00 | Thread or longer content |
| 23:00 | Review day, plan tomorrow |

Adjust for your audience's timezone. More crons = more API cost.
