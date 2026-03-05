# Piano Progress Tracking

Reference for file structure and logging format.

## Workspace Structure

```
~/piano/
├── repertoire.md      # All pieces: current, completed, wishlist
├── sessions/
│   └── YYYY-MM.md     # Monthly practice logs
├── technique.md       # Recurring issues and exercises
└── goals.md           # Short and long-term goals
```

## Repertoire Format

```markdown
# repertoire.md

## Currently Learning
- Chopin Nocturne Op.9 No.2 — started 2024-01-15, ~60% complete
  - Struggle: left hand arpeggios in middle section
  - Next: measures 25-32 hands separate

- Bach Invention No.1 — started 2024-02-01, ~30% complete
  - Focus: voice independence

## Completed
- Für Elise — completed 2023-12-01 (3 months to learn)
- Minuet in G — completed 2023-09-15 (beginner piece)

## Wishlist
- Clair de Lune — "someday" piece, too hard now
- Maple Leaf Rag — want to try ragtime
```

## Session Log Format

```markdown
# sessions/2024-02.md

## 2024-02-15 (25 min)
- Nocturne: worked mm. 25-32 hands separate
- Invention: full run-through, tempo 60
- Issue: still rushing the ornaments

## 2024-02-14 (20 min)
- Scales: C, G, D major — thumb crossing better
- Nocturne: left hand alone, slow
```

## Technique Tracking

```markdown
# technique.md

## Recurring Issues
- Thumb crossings in scales — improving since adding Hanon exercises
- Tension in right wrist during octaves — need to check posture
- Rushing in fast passages — use metronome more

## Exercises in Rotation
- Hanon No.1-5 — daily warm-up
- Czerny Op.299 No.1 — for finger independence
- Scales: all major, hands separate then together
```

## Goals Format

```markdown
# goals.md

## Current Focus (this month)
- Complete Bach Invention No.1
- Fix thumb crossing in scales
- Practice minimum 20 min/day, 5 days/week

## Longer Term
- Learn a Chopin Waltz by summer
- Be comfortable sight-reading hymns
- Memorize 3 pieces for informal performance
```

## Logging Triggers

Prompt user to log when:
- They mention practicing
- They say they finished a piece
- They describe a struggle or breakthrough
- Weekly check-in if no recent logs
