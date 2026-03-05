---
name: instance-setup
description: >
  Configure the social-media-ops instance for a specific owner. Sets owner name,
  timezone, communication language, default content language, bot identity,
  and platform settings. Run this during initial setup or when changing
  instance-level configuration.
---

# Instance Setup

## Overview

This skill configures the instance-level settings that apply across all brands and agents. It creates/updates `shared/INSTANCE.md` with owner and platform information.

## When to Use

- During initial social-media-ops setup (called automatically by onboarding)
- When the owner wants to change their communication language
- When changing the bot's name, emoji, or identity
- When switching platform mode (e.g., DM to Group)

## Configuration Items

### Owner Information
Collect from the owner:
1. **Name** — How should the team address you?
2. **Timezone** — For scheduling and cron jobs (e.g., Asia/Taipei, America/New_York)

### Communication Settings
3. **Owner communication language** — Language for all owner-facing messages (e.g., English, 繁體中文, 日本語)
4. **Default content language** — Default language for social media content (can be overridden per brand)
5. **Internal documentation language** — Usually English (recommended)

### Bot Identity
6. **Bot name** — The name your AI assistant goes by
7. **Bot emoji** — A single emoji that represents the bot
8. **Bot vibe** — 2-3 words describing the bot's personality (e.g., "sharp, direct, resourceful")

### Platform
9. **Primary platform** — Currently supports Telegram
10. **Channel mode** — Group+Topics (recommended), DM+Topics, Group-simple, DM-simple

## Output

Updates these files:
- `shared/INSTANCE.md` — Full instance configuration
- `workspace/IDENTITY.md` — Bot identity
- `shared/operations/channel-map.md` — Platform and mode settings

## Example Interaction

```
Owner: Set up my instance
Bot: Let's configure your social media ops instance.

1. What's your name?
> Alex

2. What timezone are you in?
> US/Pacific

3. What language should I use when talking to you?
> English

4. What language should content be written in by default?
> English (brands can override this)

5. What should I call myself?
> Pixel

6. Pick an emoji for me:
> 🤖

Done! Instance configured. Run brand-manager add to set up your first brand.
```
