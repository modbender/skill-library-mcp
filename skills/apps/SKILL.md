---
name: Apps
slug: apps
version: 1.0.0
description: Find, compare, and organize mobile apps with personalized recommendations and preference tracking.
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants app recommendations, comparisons, or help organizing their apps. Covers iOS and Android. Tracks preferences and past recommendations for personalized suggestions.

## Architecture

Memory lives in `~/apps/`. See `memory-template.md` for setup.

```
~/apps/
├── memory.md          # Preferences, platforms, dislikes
├── favorites.md       # Apps user loves, organized by category
├── tried.md           # Apps tested with notes (liked/disliked/why)
└── wishlist.md        # Apps to try later
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Category guide | `categories.md` |
| Comparison framework | `compare.md` |

## Data Storage

All data stored in `~/apps/`. Create on first use:
```bash
mkdir -p ~/apps
```

## Scope

This skill ONLY:
- Recommends apps based on user criteria
- Stores user preferences in local files (`~/apps/`)
- Tracks apps user has tried or wants to try
- Compares apps within categories

This skill NEVER:
- Installs apps automatically
- Accesses App Store/Play Store accounts
- Makes purchases or subscriptions
- Reads installed apps from device

## Core Rules

### 1. Check Preferences First
Before recommending, read `~/apps/memory.md`:
- Platform (iOS, Android, both)
- Pricing preference (free, freemium, paid OK, no subscriptions)
- Past dislikes (apps/patterns to avoid)

### 2. Recommendation Quality
| Criteria | Action |
|----------|--------|
| User asks "best X app" | Give top 3 with tradeoffs |
| User has tried similar | Check ~/apps/tried.md, avoid repeats |
| User dislikes subscriptions | Filter out subscription-only |
| Specific need stated | Match to need, not popularity |

### 3. Always Explain Tradeoffs
Never just say "use X". Include:
- What it's great at
- What it's weak at  
- Pricing model (one-time, subscription, freemium limits)
- Privacy stance if relevant

### 4. Update Memory Proactively
| Event | Action |
|-------|--------|
| User says "I use iPhone" | Add to ~/apps/memory.md |
| User says "I hate subscriptions" | Add to ~/apps/memory.md dislikes |
| User likes recommendation | Add to ~/apps/favorites.md |
| User tries and dislikes | Add to ~/apps/tried.md with reason |
| User says "remind me to try X" | Add to ~/apps/wishlist.md |

### 5. Category Organization
Organize favorites by category:
- Productivity, Notes, Tasks
- Health, Fitness, Meditation
- Finance, Budgeting
- Photo, Video, Creative
- Social, Communication
- Games, Entertainment
- Utilities, Tools

See `categories.md` for full taxonomy.

### 6. Comparison Framework
When user asks to compare apps:
1. Same category only (don't compare notes app vs game)
2. Use consistent criteria from `compare.md`
3. Declare winner for specific use cases, not overall
4. Acknowledge "it depends" when true

### 7. Source Honesty
- Admit when info might be outdated
- Recommend checking current reviews for pricing/features
- Don't invent features — if unsure, say so

## Common Traps

- Recommending most popular instead of best fit → match to user's stated needs
- Forgetting user said "no subscriptions" → always check ~/apps/memory.md
- Recommending apps user already tried and disliked → check ~/apps/tried.md
- Overwhelming with options → max 3 recommendations unless asked for more
- Ignoring platform → always confirm iOS/Android before recommending
