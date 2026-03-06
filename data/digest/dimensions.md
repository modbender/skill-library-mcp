# Digest Dimensions

Reference for categorizing user preferences. Load when updating `preferences.md`.

## Content

What topics/domains they want:
- `industries` — Tech, finance, health, etc.
- `competitors` — Specific companies to track
- `topics` — AI, climate, markets, sports, etc.
- `people` — Thought leaders, executives, creators
- `regions` — Geographic focus

What to exclude:
- `noise` — Topics that waste their time
- `saturated` — Covered elsewhere, don't duplicate

## Sources

Where information comes from:
- `trusted` — Sources they explicitly trust
- `blocked` — Sources to never use
- `weight` — Preference for certain source types (research > news > social)
- `recency` — How fresh must info be

## Format

How to present:
- `channel` — Telegram group, DM, email, Slack
- `medium` — Text, PDF, audio, video summary
- `structure` — Bullets, prose, headers, cards
- `length` — Headlines only, summaries, full analysis
- `visuals` — Include images/charts or text-only
- `tone` — Formal, casual, direct, conversational

## Timing

When to deliver:
- `schedule` — Morning, evening, both, custom times
- `frequency` — Daily, weekday-only, weekly
- `timezone` — User's timezone for delivery
- `context-aware` — Different digests for work vs personal time

## Prioritization (Ponderación)

How to order and emphasize:
- `hierarchy` — What goes first (breaking news? most relevant?)
- `highlight` — What deserves emphasis
- `bury` — What can be at the bottom
- `urgent-signal` — When to break schedule for urgent news

## Depth

How deep to go:
- `default-depth` — Headlines, summaries, or analysis
- `per-topic` — Some topics need more depth than others
- `expandable` — Offer "read more" or include everything

## Personalization Levels

```
[none]      → Generic digest, default settings
[pattern]   → 2+ signals observed, not confirmed
[confirmed] → User explicitly approved
[locked]    → Reinforced multiple times, stable
```
