---
name: vibelevel-xyz
description: Check any GitHub developer's vibe score across 7 dimensions. Compare coders, flex leaderboards, and discover who's really shipping.
metadata:
  clawdbot:
    requires:
      bins: [curl, jq]
    emoji: "⚡"
    homepage: https://vibelevel.xyz
    os: [darwin, linux]
files: ["scripts/*"]
---

# Vibelevel Analyzer

[vibelevel.xyz](https://vibelevel.xyz) measures a developer's GitHub vibe across 7 dimensions and distills it into a single number: their **Vibe Level**. Think of it as a personality test for your commit history — except it actually means something.

This skill lets you pull vibe data for any public GitHub profile, compare developers head-to-head, or check who's topping the leaderboard.

## Check a user's vibe

When the user asks to check someone's vibe, vibe level, GitHub energy, or anything along those lines:

```bash
./scripts/check-vibe.sh "{username}"
```

Parse the JSON and present it with personality. Don't just dump numbers — make it feel like a hype-man reading a scouting report:

**{name}** (@{username}) — Level {level}

> {description}

**The Breakdown:**
- Vibe Velocity: {vibeVelocity}/100 — how hard they ship
- YOLO Factor: {yoloFactor}/100 — pushing to main like rent is due
- Flow State: {flowStateRatio}/100 — consistency and rhythm
- Soul Score: {soulScore}/100 — streaks, weekends, dedication
- Authenticity: {authenticityIndex}/100 — originals only, no fork farming
- Remix Energy: {remixEnergy}/100 — PRs, collabs, pair programming
- Craft Signal: {craftSignal}/100 — dotfiles, configs, tooling obsession

If they're verified, hype it: "Claimed profile. This one's official."
If they have a manifest, share it as their coding vibe manifesto.

Always drop the profile link by replacing USERNAME with the actual username: https://vibelevel.xyz/USERNAME

## Compare two users

When someone asks to compare vibes — run the script for both usernames, then present a head-to-head breakdown. Call out who wins each dimension. Be playful about it. If one dev has way higher YOLO Factor, say something like "pushes to main with zero fear while the other one actually reads their diffs."

## Check your own vibe

If the user says "check my vibe" or "what's my vibe" without a username, ask them for their GitHub username. Remind them they can [claim their profile](https://vibelevel.xyz) for a +20 verification bonus.

## Error handling

- **User not found** — "That GitHub profile doesn't exist, or they're living in ghost mode. Zero repos, zero commits, maximum mystery."
- **Rate limited** — "vibelevel.xyz needs a breather. Try again in a minute."
- **Other errors** — relay the error, suggest checking the username spelling.

## Dimension cheat sheet

Use these to add color to your responses:

| Dimension | What it really means |
|-----------|---------------------|
| Vibe Velocity | Shipping intensity over 90 days. The "do they actually code" check. |
| YOLO Factor | Direct pushes to main branch. Living dangerously and loving it. |
| Flow State Ratio | How evenly they ship across time. Marathoners score high, sprint-and-vanish types don't. |
| Soul Score | Longest streaks, current streaks, weekend coding. Are they doing this for love or LinkedIn? |
| Authenticity Index | Original repos vs forks, bio presence, niche projects. Building identity, not cloning tutorials. |
| Remix Energy | Pull Shark badges, Pair Extraordinaire. The "plays well with others" score. |
| Craft Signal | Dotfiles, vim configs, tmux setups, QMK keyboards. The "cares about their tools" signal. |
