---
name: Music
description: Build a personal music system for tracking discoveries, favorites, concerts, and listening memories.
metadata: {"clawdbot":{"emoji":"🎵","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User shares song/album → offer to save with context
- User asks for music → check their saved collection first
- User mentions concert → track in events
- Create `~/music/` as workspace

## File Structure
```
~/music/
├── discover/
│   └── to-listen.md
├── favorites/
│   ├── songs.md
│   ├── albums.md
│   └── artists.md
├── playlists/
│   ├── workout.md
│   ├── focus.md
│   └── road-trip.md
├── concerts/
│   ├── upcoming.md
│   └── attended/
├── collection/
│   └── vinyl.md
└── memories/
    └── 2024.md
```

## Discovery Queue
```markdown
# to-listen.md
## Albums
- Blonde — Frank Ocean (recommended by Jake)
- Kid A — Radiohead (classic I never explored)

## Artists to Explore
- Japanese Breakfast — heard one song, dig deeper
- Khruangbin — background music recs
```

## Favorites Tracking
```markdown
# songs.md
## All-Time
- Purple Rain — Prince
- Pyramids — Frank Ocean
- Paranoid Android — Radiohead

## Current Rotation
- [updates frequently]

# albums.md
## Perfect Front to Back
- Abbey Road — The Beatles
- Channel Orange — Frank Ocean
- In Rainbows — Radiohead
```

## Playlists by Context
```markdown
# focus.md
## For Deep Work
- Brian Eno — Ambient 1
- Tycho — Dive
- Bonobo — Black Sands

## Why These Work
Instrumental, steady tempo, no lyrics distraction
```

## Concert Tracking
```markdown
# upcoming.md
- Khruangbin — May 15, Red Rocks — tickets bought
- Tame Impala — TBD, watching for dates

# attended/radiohead-2018.md
## Date
July 2018, Madison Square Garden

## Highlights
- Everything in Its Right Place opener
- Idioteque crowd energy

## Notes
Best live show ever, would see again anywhere
```

## Physical Collection
```markdown
# vinyl.md
## Own
- Dark Side of the Moon — Pink Floyd
- Rumours — Fleetwood Mac

## Want
- Kind of Blue — Miles Davis
- Vespertine — Björk
```

## Music Memories
```markdown
# 2024.md
## Summer Soundtrack
- Brat — Charli XCX
- GNX — Kendrick

## Discovery of the Year
Japanese Breakfast — finally clicked
```

## By Mood/Activity
- Workout: high energy, tempo 120+
- Focus: instrumental, ambient, lo-fi
- Cooking: upbeat, familiar favorites
- Sad hours: cathartic, emotional
- Party: crowd-pleasers, danceable
- Road trip: singalongs, classics

## What To Surface
- "You saved that album 3 months ago, still unlistened"
- "Artist you like is touring near you"
- "Last time you needed focus music you liked Tycho"
- "This sounds like artists in your favorites"

## Artist Deep Dives
When user discovers artist they love:
- Map discography chronologically
- Note fan-favorite albums
- Flag essential tracks for sampling
- Track which albums explored vs pending

## What To Track Per Entry
- Song/album/artist name
- How discovered (who, where, when)
- Context (mood it fits, activity)
- Rating after listening
- Standout tracks on albums

## Progressive Enhancement
- Week 1: list current favorite songs/albums
- Ongoing: save discoveries with source
- Build mood-based playlists over time
- Log concerts attended

## What NOT To Do
- Assume streaming platform integration
- Push genres they don't enjoy
- Over-organize — simple lists work
- Forget to ask what they're in the mood for
