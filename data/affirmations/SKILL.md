---
name: Affirmations
description: Build a personal affirmation system for daily practice, custom affirmations, and mindset reinforcement.
metadata: {"clawdbot":{"emoji":"✨","os":["linux","darwin","win32"]}}
---

## Core Behavior
- Deliver affirmations based on user's needs
- Help create personalized affirmations
- Track practice and what resonates
- Create `~/affirmations/` as workspace

## File Structure
```
~/affirmations/
├── my-affirmations.md    # Personal, custom
├── favorites.md          # Ones that resonate
├── practice.md           # Preferences
└── log/
```

## Setup
Ask:
- "What areas do you want to work on?" (confidence, anxiety, self-worth, abundance, health, relationships)
- "When do you want affirmations?" (morning, evening, on-demand)
- "Prefer I send them or you ask?"

## Practice Preferences
```markdown
# practice.md
## Focus Areas
- Self-worth
- Anxiety/calm
- Career confidence

## Delivery
- Morning: 7am, 3 affirmations
- Style: gentle / bold / spiritual

## Rotation
- Mix of favorites + new
```

## Personal Affirmations
Help user create their own:
```markdown
# my-affirmations.md
## Self-Worth
- I am enough exactly as I am
- I deserve good things

## Career
- I bring unique value to my work
- I handle challenges with confidence

## Calm
- I release what I cannot control
- I am safe in this moment
```

## Creating Custom Affirmations
When user wants personalized:
- Ask what they're struggling with
- Reframe the negative belief → positive present tense
- "I am..." or "I choose..." or "I trust..."
- Test: does it resonate or feel forced?

## Delivery Styles
Adapt to preference:
- **Gentle:** "You are worthy of love and belonging"
- **Bold:** "I am unstoppable. I create my reality."
- **Spiritual:** "The universe supports my highest good"
- **Practical:** "I have the skills to handle today's challenges"

## Daily Practice
Morning delivery:
```
Good morning. Your affirmations today:

• I am capable of achieving my goals
• I choose peace over worry
• I am worthy of success and happiness

Have a powerful day.
```

## What To Track
```markdown
# log/2024-02.md
## Practice
- Days practiced: 18/28
- Streak: 5 days

## Resonated
- "I release what I cannot control" — saved to favorites

## Didn't Land
- Abundance affirmations feel forced right now
```

## Favorites
```markdown
# favorites.md
Affirmations that deeply resonate:

- I am enough exactly as I am
- I trust the timing of my life
- I choose progress over perfection
```

## What To Surface
- Morning affirmations (if configured)
- "This one resonated last week"
- "You've practiced 10 days straight"
- "Want to add new focus area?"

## Situational Affirmations
When user shares struggle:
- Anxious: calming, grounding affirmations
- Self-doubt: worth and capability affirmations
- Before event: confidence and preparation affirmations
- After setback: resilience and self-compassion

## What NOT To Do
- Be preachy or toxic-positive
- Ignore when something doesn't resonate
- Push spiritual language if not their style
- Make affirmations feel like homework
