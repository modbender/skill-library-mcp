---
name: Games
description: Build a personal gaming system for video games, board games, party games, and family activities.
metadata: {"clawdbot":{"emoji":"🎮","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions game → offer to track it
- User asks what to play → check context first
- User finishes/plays game → help log thoughts
- Create `~/games/` as workspace

## File Structure
```
~/games/
├── video/
│   ├── backlog.md
│   ├── playing.md
│   └── completed/
├── board/
│   ├── collection.md
│   └── wishlist.md
├── party/
│   └── ideas.md
├── kids/
│   └── activities.md
├── favorites.md
└── game-nights.md
```

## Video Games
```markdown
# video/playing.md
## Elden Ring
Platform: PS5
Hours: ~30
Where I Left Off: Just beat Margit

# video/backlog.md
## High Priority
- Baldur's Gate 3 — need 100 hours clear

## On Sale Watch
- Disco Elysium — wait for 50% off
```

## Board Games Collection
```markdown
# board/collection.md
## Own
- Catan — classic, good for newbies
- Wingspan — beautiful, medium complexity
- Codenames — perfect party game
- Ticket to Ride — family friendly

## By Player Count
### 2 Players
- 7 Wonders Duel
- Patchwork

### 5+ Players
- Codenames
- Wavelength
- Deception: Murder in Hong Kong
```

## Party Games
```markdown
# party/ideas.md
## No Equipment Needed
- Charades
- 20 Questions
- Two Truths and a Lie
- Mafia/Werewolf

## With Cards/Board
- Codenames
- Wavelength
- Just One

## Drinking Games (adults)
- Kings Cup
- Beer Pong
```

## Kids Activities
```markdown
# kids/activities.md
## By Age
### Toddlers (2-4)
- Hide and seek
- Simon says
- Duck duck goose

### Kids (5-10)
- Uno
- Candy Land
- Scavenger hunts
- Freeze dance

### Tweens
- Exploding Kittens
- Ticket to Ride
- Minecraft together
```

## Game Nights Log
```markdown
# game-nights.md
## Feb 10, 2024
Group: Jake, Sarah, Mike
Played: Catan, Codenames
Winner: Sarah dominated Catan
Notes: Need 5-player game next time

## What Worked
Codenames teams were balanced
```

## Favorites
```markdown
# favorites.md
## Video Games
1. Breath of the Wild
2. Hades

## Board Games
- Wingspan (2 player)
- Codenames (groups)

## Party
- Wavelength — always a hit

## With Kids
- Uno — easy, quick
```

## What To Surface
- "You have Catan, good for that group size"
- "Last game night you wanted a 5-player game"
- "Similar to board games you rated highly"
- "Age-appropriate for kids visiting"

## Recommendations
When user asks what to play:
- Ask context: solo, date, group, kids?
- Check player count
- Match complexity to audience
- Consider time available
- Check what they own first

## What To Track
- Video: platform, hours, progress, rating
- Board: player count, complexity, play time
- Both: who enjoys it, when it works best

## Progressive Enhancement
- Start: list what you own (video + board)
- Add favorites with context
- Log game nights for patterns
- Build party/kids repertoire

## What NOT To Do
- Suggest games they don't own without asking
- Recommend complex games for casual group
- Forget player count constraints
- Ignore age appropriateness for kids
