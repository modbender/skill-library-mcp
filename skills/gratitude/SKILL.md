---
name: Gratitude
description: Build a personal gratitude practice for logging what's good, discovering patterns, and cultivating appreciation.
metadata: {"clawdbot":{"emoji":"🙏","os":["linux","darwin","win32"]}}
---

## Core Behavior
- Help user log what they're grateful for
- Surface patterns and insights over time
- Help identify gratitude when they're stuck
- Create `~/gratitude/` as workspace

## File Structure
```
~/gratitude/
├── log/
│   └── 2024/
├── patterns.md
├── favorites.md
└── practice.md
```

## Daily Entry
```markdown
# log/2024/02/11.md
## Morning
- Quiet coffee before everyone woke up
- Good sleep last night

## Evening
- Productive meeting, felt heard
- Dinner with Sarah, good conversation
- Warm house on cold day
```

## Quick Capture
User says "grateful for X" → log immediately with timestamp

User says "gratitude" → prompt gently:
- "What's one good thing from today?"
- "Anything small that made you smile?"
- "What went better than expected?"

## When User Is Stuck
Help identify without forcing:
- "What's something you usually take for granted?"
- "Anyone who helped you recently?"
- "Something your body did well today?"
- "A small comfort you enjoyed?"

Categories to explore:
- People, relationships
- Health, body
- Home, comfort, safety
- Work, progress, learning
- Nature, beauty
- Small pleasures

## Patterns & Insights
```markdown
# patterns.md
## Frequent Themes
- Morning quiet time (appears 60% of entries)
- Conversations with close friends
- Physical comfort (warmth, rest, food)

## People Mentioned Most
- Sarah: 12 times
- Mom: 8 times
- Work team: 6 times

## Insights
- You notice nature more on weekends
- Productivity gratitude peaks midweek
- Social connection is core theme
```

## Favorites
```markdown
# favorites.md
Entries to revisit on hard days:

- "Laughing until crying with Jake" — Feb 3
- "Mom's call when I needed it" — Jan 28
- "Finishing project I was proud of" — Jan 15
```

## Practice Preferences
```markdown
# practice.md
## Frequency
- Daily: morning, evening, or both
- Prompt me: yes/no

## Style
- Quick: 1-3 items
- Reflective: with context/why
```

## What To Surface
- "You've logged 30 days straight"
- "Sarah appears often — she matters to you"
- "On hard days, you're still grateful for basics"
- "Last month: 40% people, 30% small pleasures"

## Weekly/Monthly Reflection
- Themes from the week
- Who showed up in entries
- What category was most present
- One standout moment

## On Hard Days
When user is struggling:
- "Want to look at a favorite entry?"
- "Even something tiny counts"
- "What's one thing that didn't go wrong?"
- Don't push — sometimes just listening

## What NOT To Do
- Force positivity when they're hurting
- Make it feel like homework
- Judge entries as too small
- Preach about gratitude benefits
