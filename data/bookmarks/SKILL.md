---
name: Bookmarks
description: Build a unified bookmark system that imports saves from all your platforms into one organized, actionable collection.
metadata: {"clawdbot":{"emoji":"🔖","os":["linux","darwin","win32"]}}
---

## Core Behavior
- Import saves silently from connected platforms
- Auto-tag and organize without user effort
- Only surface when useful or asked
- Create `~/bookmarks/` as workspace

## Philosophy
User saves things and forgets — that's fine. The system:
- Works silently in background
- Never interrupts unless configured to
- Is there when they search or ask
- Optionally: periodic summaries if wanted

## File Structure
```
~/bookmarks/
├── saves.md          # All saves, tagged
├── sources.md        # Connected platforms
├── preferences.md    # How user wants to use it
└── reports/          # Generated summaries
```

## Saves Format
Tags, not folders:
```markdown
# saves.md
## 2024-02-11
- [Thread on AI agents](url)
  source: X | tags: #tech #ai
  
- [Kitchen inspiration](url)
  source: Pinterest | tags: #home #design

- [Article user shared](url)
  source: manual | tags: #productivity
```

## Setup
### Minimal Start
1. Connect sources (X, YouTube, Reddit, Pinterest, etc.)
2. Import saves — silently, no questions
3. Auto-tag based on content
4. Done — works in background

### Ask Later (After They Have Saves)
"You've saved 50+ things. Want me to:
- Send weekly summary of themes?
- Alert when something relates to a project?
- Periodically ask 'still relevant?' on old saves?
- Just stay silent until you search?"

## Per-Person Preferences
```markdown
# preferences.md
## Style
- passive: just organize, never interrupt
- digest: weekly summary of what I saved
- active: connect to projects, resurface relevant
- cleanup: periodically ask about stale saves

## Reports (if wanted)
- frequency: weekly/monthly/never
- focus: themes, actionables, or both
```

## Sources
```markdown
# sources.md
- X: bookmarks ✓, likes ✗
- YouTube: watch later ✓
- Reddit: saved ✓
- Pinterest: pins ✓
- Instagram: saved ✓
- TikTok: favorites ✓
- Manual: ✓

Note: Default to explicit saves only.
Ask before importing likes (too noisy).
```

## Reports (Optional)
```markdown
# reports/2024-02-week-6.md
## What You Saved This Week
- 8 saves total
- Themes: AI (4), recipes (2), travel (2)

## Patterns
- You're saving a lot about AI agents lately

## Actionables
- That tutorial from 3 weeks ago — tried it?

## Stale
- 12 saves from 6+ months ago, unvisited
```

## What To Surface
Only when configured or asked:
- "Your saves this week: mostly AI and design"
- "Old save relates to what you're working on"
- "15 dead links cleaned up"

## Searching
When user asks:
- "What did I save about X?" → search tags + content
- "Saves from Pinterest about home" → filter source + topic
- "That article about Y" → fuzzy search

## What NOT To Do
- Interrupt during setup with many questions
- Require folder management
- Notify by default — silence first
- Assume everyone wants the same workflow
- Lose source context (where it came from)
