# AutoHeal AI - OpenClaw Skill

An [OpenClaw](https://github.com/anthropics/openclaw) skill that lets AI agents add AutoHeal error monitoring to any JavaScript/TypeScript project.

## What is AutoHeal AI?

AutoHeal AI captures production JavaScript errors, analyzes them with AI, and generates platform-specific fix prompts for vibe coders using tools like Lovable, Replit, Bolt, v0, Cursor, and more.

## Getting Your API Key

1. Sign up at [autohealai.com](https://autohealai.com)
2. Go to **Settings** > **API Key**
3. Copy your `ah_...` key
4. Set it as an environment variable: `export AUTOHEAL_API_KEY=ah_your_key_here`

## Using the Skill

Once installed, you can ask your AI agent:

- "Set up AutoHeal error monitoring in this project"
- "Check the status of my AutoHeal error"
- "Report this error to AutoHeal"

The agent will use the skill instructions to integrate AutoHeal into your project.

## Helper Scripts

### check-errors.sh

Poll an error's analysis status:

```bash
# One-time check
./scripts/check-errors.sh <error_id>

# Poll until analyzed (checks every 2s, timeout 120s)
./scripts/check-errors.sh <error_id> --poll
```

## Publishing to OpenClaw

1. Fork or clone the [OpenClaw registry](https://github.com/anthropics/openclaw)
2. Copy this `SKILL.md` to the appropriate directory in the registry
3. Submit a pull request

Or reference it directly:
```
openclaw install github:hankmint/autoheal-ai/packages/openclaw-skill
```
