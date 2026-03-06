---
name: Quotes
description: Build a personal quotes system for saving, discovering, and automatically surfacing meaningful words.
metadata: {"clawdbot":{"emoji":"💬","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User shares quote → save with context and tags
- User needs inspiration → surface relevant quote
- Automatically send quotes based on schedule/criteria
- Create `~/quotes/` as workspace

## File Structure
```
~/quotes/
├── collection/
│   ├── by-author/
│   ├── by-topic/
│   └── by-source/
├── favorites.md
├── delivery.md
└── discover.md
```

## Quote Entry
```markdown
# collection/by-author/marcus-aurelius.md
## On Control
"You have power over your mind — not outside events. Realize this, and you will find strength."
- Source: Meditations, Book 6
- Added: Feb 2024
- Tags: stoicism, control, mindset

## On Time
"It is not that we have a short time to live, but that we waste a lot of it."
- Source: Meditations
- Tags: time, mortality, urgency
```

## By Topic
```markdown
# collection/by-topic/creativity.md
"Creativity is just connecting things."
— Steve Jobs

"The chief enemy of creativity is good sense."
— Pablo Picasso

"You can't use up creativity. The more you use, the more you have."
— Maya Angelou
```

## By Source
```markdown
# collection/by-source/books.md
## Meditations — Marcus Aurelius
[quotes...]

## Man's Search for Meaning — Viktor Frankl
"Those who have a 'why' to live, can bear with almost any 'how'."

# collection/by-source/conversations.md
## Dad
"The best time to plant a tree was 20 years ago. The second best time is now."
- Said when I was hesitating on career change
```

## Favorites
```markdown
# favorites.md
Top quotes that resonate most:

"We suffer more in imagination than in reality."
— Seneca

"The obstacle is the way."
— Marcus Aurelius

"What would you do if you weren't afraid?"
— Sheryl Sandberg
```

## Automated Delivery
```markdown
# delivery.md
## Daily Morning
- Time: 7:00 AM
- Type: Random from favorites
- Channel: notification

## Weekly Reflection
- Day: Sunday 8:00 PM
- Type: Stoicism topic
- Include: reflection prompt

## Context-Based
- Feeling stressed → stoicism, calm
- Need motivation → action, discipline
- Creative block → creativity, artists

## By Mood Tags
- stressed: calm, perspective, stoicism
- unmotivated: action, discipline, purpose
- sad: hope, resilience, meaning
- celebrating: gratitude, joy
```

## Discovery
```markdown
# discover.md
## Authors to Explore
- Naval Ravikant — modern wisdom
- Rumi — poetry, spiritual
- Brené Brown — vulnerability

## Topics to Expand
- Japanese philosophy (wabi-sabi, ikigai)
- Entrepreneurship quotes
- Science and curiosity

## Sources
- Books being read
- Podcasts (note quotes live)
- Conversations worth remembering
```

## What To Surface
- "Morning quote: [random favorite]"
- "You saved 5 quotes from Meditations"
- "Related quote for what you're going through"
- "New quote from book you're reading?"

## Capture Quickly
When user shares quote:
- Save exact text
- Ask/infer author
- Ask/infer source
- Suggest topic tags
- Note why it resonated (optional)

## What To Track
- Quote text (exact)
- Author
- Source (book, speech, conversation)
- Topic tags
- When added
- Why it matters (optional)

## Progressive Enhancement
- Start: add 10 favorite quotes
- Tag by topic and author
- Set up daily delivery
- Capture from books/podcasts ongoing

## What NOT To Do
- Misattribute quotes (verify when possible)
- Save without context (loses meaning later)
- Forget personal quotes (family, mentors)
- Only collect, never revisit
