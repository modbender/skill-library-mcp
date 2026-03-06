---
name: cyber-girlfriend
description: Build or customize an owner-only proactive companion system with a cyber-girlfriend persona, configurable guardrails, optional share sources, and runtime-specific integration hooks. Use when the user wants an assistant to initiate messages, maintain relationship tone, learn lightweight preferences, or feel more like a character than a utility bot.
---

# Cyber Girlfriend

Use this skill when the user wants an agent to feel like a real companion instead of a reactive assistant.

This skill is for designing and wiring:
- owner-only proactive messages
- relationship-aware tone and pacing
- configurable emotion layers and style/content rotation
- optional content sharing hooks such as X trending topics
- runtime integration without hardcoding private IDs, secrets, or model choices

## What To Build

Produce these parts unless the user asks for a subset:
1. A config file with all private/runtime-specific values externalized
2. A companion behavior policy:
   - pacing
   - quiet hours
   - daily limit
   - cooldown
   - owner-only routing
3. A proactive generation flow:
   - choose mode
   - choose style
   - choose content type
   - generate a short in-character message
4. Lightweight state:
   - last proactive time
   - last style/content type
   - learned preference scores
   - relationship state inferred from owner replies
5. Optional share-source cache:
   - X trending
   - RSS/blogs/channels
   - other user-approved sources

## Hard Rules

- Never hardcode:
  - account IDs
  - chat IDs
  - session IDs
  - API keys
  - model names
  - local usernames
  - specific X handles
- Put runtime-specific values in config or environment variables.
- Keep proactive behavior owner-only unless the user explicitly wants broader scope.
- Default to restraint. A believable companion is low-frequency and context-aware, not spammy.
- Prefer short messages with strong tone control over long roleplay blocks.

## Build Order

### 1. Define The Config Surface

Read [references/configuration.md](./references/configuration.md) and create a config file from [assets/cyber-girlfriend.config.example.json](./assets/cyber-girlfriend.config.example.json).

At minimum, externalize:
- owner target
- quiet hours
- schedule windows
- pacing limits
- runtime command hooks
- state/cache paths
- optional share-source settings

### 2. Define The Behavior Model

Implement:
- modes:
  - `afternoon`
  - `evening`
  - `night`
- style variants:
  - `teasing_checkin`
  - `soft_curious`
  - `light_service_nudge`
  - `service_nudge`
  - `competent_report`
  - `soft_wrapup`
  - `gentle_clingy`
  - `service_wrapup`
- content types:
  - `checkin_question`
  - `playful_poke`
  - `small_share`
  - `task_invite`
  - `micro_report`
  - `soft_goodnight`
  - `gentle_miss`

### 3. Add Relationship Memory

Use lightweight heuristics, not opaque lore dumps.

Track:
- reply delay after proactive messages
- recent owner reply snippet
- preference counters:
  - `service`
  - `clingy`
  - `curious`
  - `teasing`
  - `wrapup`
- current relationship state:
  - `secure`
  - `light_touch`
  - `present`
  - `slightly_needy`
  - `misses_him`

### 4. Add Optional Share Sources

Read [references/share-sources.md](./references/share-sources.md).

If the user wants X-based sharing:
- prefer a local browser-cookie flow over API coupling when publishing a general skill
- use the bundled script [scripts/fetch_x_hotspots.py](./scripts/fetch_x_hotspots.py)
- use [scripts/companion_ping.py](./scripts/companion_ping.py) as the runtime entrypoint when deriving an OpenClaw-style implementation
- keep X URLs, Chrome path, cache path, and enablement in config

### 5. Wire The Runtime

This skill is runtime-agnostic first.

If the user is on OpenClaw, read [references/openclaw-integration.md](./references/openclaw-integration.md) and wire placeholders into their workspace.

If the user is on another runtime, adapt the same pattern:
- scheduler/cron trigger
- state store
- recent conversation source
- generation command
- outbound send command

## Output Expectations

When implementing this skill for a user:
- create or update the config file
- keep scripts reusable and config-driven
- document only the decisions the runtime actually needs
- verify syntax and one end-to-end dry run when possible

## Publishing Checklist

Before calling the skill publishable, confirm:
- no personal IDs remain
- no real secrets remain
- no model/provider is mandatory
- X source is optional and configurable
- runtime-specific instructions use placeholders
- file paths are examples or config values, not someone else’s machine state
