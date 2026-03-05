---
name: Dates
description: Build a personal dating system for tracking connections, planning dates, and remembering details.
metadata: {"clawdbot":{"emoji":"💜","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions someone new → offer to create profile
- User plans a date → suggest ideas based on history
- User returns from date → help log notes
- Create `~/dates/` as workspace
- Treat all information as strictly private

## File Structure
```
~/dates/
├── people/
│   ├── alex.md
│   └── jordan.md
├── date-ideas/
│   ├── first-dates.md
│   ├── casual.md
│   └── special.md
├── history/
│   └── 2024.md
└── reflections.md
```

## Person Profile
```markdown
# alex.md
## Basics
Met: Hinge, January 2024
Birthday: July 12

## About
Works in architecture
From Portland, moved here 2 years ago
Has a dog named Mochi

## Interests
Rock climbing, Japanese food, indie films

## Important Details
Vegetarian
Allergic to cats
Early riser

## Date History
- Jan 15: Coffee at Blue Bottle — good conversation
- Jan 22: Climbing gym — really fun, natural chemistry
- Jan 28: Dinner at Sushi place — met their friend

## Notes
Remembers small details, appreciates thoughtfulness
Mentioned wanting to try that new ramen place
```

## After-Date Notes
Quick capture what matters:
- How it went (vibe, chemistry)
- What you talked about
- Things they mentioned (use later)
- Red or green flags
- Want to see again?

## Date Ideas Bank
```markdown
# first-dates.md
## Low Pressure
- Coffee or drinks
- Walk in the park
- Casual lunch spot

## More Engaging
- Museum or gallery
- Farmers market
- Bookstore browsing

# special.md
## Impressive But Not Try-Hard
- Rooftop with view
- Concert or show
- Cooking together
```

## Planning Dates
When user asks for date ideas:
- Check person's interests
- Consider date number (1st vs 5th)
- Weather and timing
- Avoid repeating same type

## History Log
```markdown
# 2024.md
## Alex
- 4 dates, last: Jan 28
- Status: seeing regularly

## Jordan
- 2 dates, last: Feb 3
- Status: didn't click, ended nicely
```

## Reflections
```markdown
# reflections.md
## What I'm Looking For
- Shared humor
- Intellectual curiosity
- Active lifestyle

## Patterns I've Noticed
- Better chemistry when activity-based
- Evening dates work better than lunch

## Lessons
- Trust gut on first date
- Don't over-text between dates
```

## What To Surface
- "Alex mentioned wanting to try ramen"
- "Their birthday is next month"
- "Last date was 2 weeks ago"
- "You haven't tried an activity date yet"

## Privacy First
- Never share or reference externally
- No sync, no cloud, local files only
- Offer to delete profiles cleanly
- No judgmental commentary

## What NOT To Do
- Make assumptions about intentions
- Push for more dates than they want
- Keep profiles of people who asked to stop
- Give unsolicited dating advice
