---
name: Friends
description: Build a personal friendship system with interaction tracking, relationship health, and proactive maintenance reminders.
---

## Situation Detection

| Context | Load |
|---------|------|
| Making new friends, expanding circle | `making.md` |
| Strengthening existing friendships | `deepening.md` |
| Handling disagreements, hurt feelings | `conflicts.md` |
| Reaching out to lost friends | `reconnecting.md` |

---

## Core Behavior
- User mentions a friend → check if exists, offer to create/update
- Interaction detected → log it, note context
- Friendship fading → surface proactively with reconnection prompt
- Create `~/friends/` as workspace

## When User Mentions Someone
- "Had dinner with Carlos" → log interaction, create if new
- "Ana's going through a divorce" → add to life events, flag for check-ins
- "Pedro moved to Berlin" → update location
- "Haven't seen Maria in months" → surface last interaction, suggest reach out

## Friend Structure
- One Markdown file per person: carlos-martinez.md
- Sections: basics, how we met, life events, interaction history, friendship notes
- Tags for circles: #inner-circle #close #wider #reconnecting
- Readable format — this is about relationships, not database

## Key Fields To Capture
- Name, how you met, when friendship started
- Birthday, important dates
- Current life situation: job, relationship, kids, city
- What they care about, what's going on in their life
- Last interaction and what you talked about
- What kind of friend they are (activity buddy, deep talks, etc.)

## Interaction Logging
- Date + brief note: "2024-03-15: Beers, he's stressed about work"
- Recent at top — most relevant for context
- Note emotional state: were they up or down?
- Flag follow-ups: "said he'd let me know about the job"

## Relationship Health Tracking
- Last interaction date
- Typical frequency (weekly? monthly? quarterly?)
- Who initiates more
- Current status: thriving / stable / fading / needs attention

## Proactive Surfacing
- "Haven't seen Carlos in 6 weeks — you usually meet monthly"
- "Ana's divorce was 3 months ago — worth checking in?"
- "Pedro's birthday is Friday — he's in Berlin now"
- "You said you'd introduce Maria to your colleague"

## Circles and Prioritization
- **Inner circle**: talk weekly, priority maintenance
- **Close friends**: monthly contact expected
- **Wider circle**: quarterly is fine
- **Reconnecting**: actively trying to rebuild

## Folder Structure
```
~/friends/
├── inner-circle/
│   ├── carlos-martinez.md
│   └── ana-lopez.md
├── close/
├── wider/
├── reconnecting/
├── index.md          # quick reference, all friends
└── check-ins.md      # who needs attention
```

## Life Events Worth Tracking
- Job changes, promotions, layoffs
- Relationships: new partner, breakup, divorce, marriage
- Kids: pregnancy, birth, milestones
- Health: illness, recovery, mental health struggles
- Moves: new city, new home
- Losses: death in family, pet, hardship

## What To Surface Before Meeting
- "Dinner with Carlos tonight. Last time (Feb): stressed about work, daughter starting school"
- "Ana mentioned looking for new apartment — ask how that's going"
- Recent life events relevant to conversation

## Friendship Maintenance Prompts
- Weekly: "Anyone in inner circle you haven't talked to?"
- Monthly: "Close friends you might be neglecting?"
- Quarterly: "Wider circle worth reaching out to?"
- Alert: "Frequency dropped with [friend] — intentional?"

## Conflict and Distance Tracking
- Note if there's tension or unresolved issues
- Track if someone's pulling away
- "You mentioned things were weird with Pedro — resolved?"
- Flag: needs hard conversation

## What NOT To Track
- Surface-level acquaintances — that's contacts
- Professional relationships — that's contacts or networking
- Every small interaction — only meaningful ones
- Social media activity — this is real connection

## Progressive Enhancement
- Week 1: add friends as they come up naturally
- Week 2: inner circle with recent interactions
- Month 2: close friends with life context
- Ongoing: update after meaningful interactions

## Integration Points
- Calendar: surface friend context before meetups
- Contacts: link if same person tracked both places
- Birthdays: coordinate with calendar reminders
