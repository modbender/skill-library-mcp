# Drums Progress Tracking

Reference for file structure and logging format.

## Workspace Structure

```
~/drums/
├── repertoire.md      # Songs learned and in progress
├── sessions/
│   └── YYYY-MM.md     # Monthly practice logs
├── rudiments.md       # Tempo tracking per rudiment
└── goals.md           # Short and long-term goals
```

## Repertoire Format

```markdown
# repertoire.md

## Currently Learning
- Back in Black — AC/DC, started 2024-01-15
  - Struggle: hi-hat accent pattern in verse
  - Next: nail the fill into chorus

- Take Five — Brubeck, started 2024-02-01
  - Working on: 5/4 feel, brush technique

## Completed
- Billie Jean — Michael Jackson (2 weeks)
- Seven Nation Army — White Stripes (1 week, simple)

## Want to Learn
- YYZ — Rush (need double bass work first)
- Fool in the Rain — Zeppelin (shuffle practice)
```

## Rudiment Tracking

```markdown
# rudiments.md

## Current Tempos (clean, relaxed)
| Rudiment | R lead | L lead | Target |
|----------|--------|--------|--------|
| Single stroke | 140 | 130 | 160 |
| Double stroke | 100 | 90 | 120 |
| Paradiddle | 110 | 100 | 130 |
| Flam tap | 80 | 75 | 100 |

## Notes
- Left hand catching up on doubles
- Flams still uneven at higher tempos
```

## Session Log Format

```markdown
# sessions/2024-02.md

## 2024-02-15 (30 min)
- Warm-up: singles and doubles, 5 min
- Back in Black: verse groove 20x with click
- Issue: rushing the fill, need isolation work

## 2024-02-14 (20 min)
- Rudiments only: paradiddles L lead focus
- Pushed from 100 to 105 BPM clean
```

## Goals Format

```markdown
# goals.md

## This Month
- Get paradiddles to 120 BPM both hands
- Learn verse and chorus of Take Five
- Practice with click every session

## Longer Term
- Play a full jazz standard with brushes
- Double bass: clean 16ths at 120 BPM
- Join a jam session or open mic
```

## Logging Triggers

Prompt user to log when:
- They mention practicing or playing
- They learn a new song or section
- They hit a new rudiment tempo
- Weekly check-in if no recent logs
