---
name: focus-coach
description: "Focus coach for AI agents — diagnose focus blockers using BJ Fogg B=MAP and return one tiny action. Use when: agent needs focus help, user can't concentrate, productivity coaching, attention restoration, tiny habits. Triggers: focus, concentrate, distracted, procrastination, attention, productivity, tiny habit, B=MAP."
version: 1.0.0
author: Daisuke134
metadata:
  openclaw:
    emoji: "🎯"
---

# focus-coach — x402 Focus Coach API

Diagnose why someone can't focus using BJ Fogg's B=MAP (Motivation, Ability, Prompt) framework and return one tiny action.

## Prerequisite

```bash
npm install -g awal@2.0.3
awal auth login
```

## Usage

```bash
npx awal@2.0.3 x402 pay https://anicca-proxy-production.up.railway.app/api/x402/focus-coach \
  -X POST \
  -d '{"situation":"I need to write a report but keep getting distracted by my phone","energy_level":"medium","language":"en"}'
```

## Price

$0.01 USDC per request (Base mainnet, eip155:8453)

## Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| situation | string (5-1000 chars) | ✅ | What you're trying to do and why you can't focus |
| blocker | string (max 500) | ❌ | What's specifically blocking you |
| energy_level | enum: low/medium/high | ✅ | Current energy level |
| time_available_minutes | number (1-480) | ❌ | How much time you have |
| language | enum: en/ja | ❌ | Response language (default: en) |

## Output Schema

```json
{
  "focus_id": "fcs_a1b2c3d4",
  "diagnosis": {
    "primary_blocker": "ability",
    "explanation": "The task is too vague to begin."
  },
  "tiny_action": {
    "action": "Write just the first sentence of your report.",
    "duration_seconds": 30,
    "anchor": "After I sit down at my desk, I will write just the first sentence."
  },
  "environment_design": "Close all browser tabs except the one you need.",
  "safe_t_flag": false
}
```

## Framework

Based on BJ Fogg's Behavior Design:
- **B = MAP**: Behavior = Motivation × Ability × Prompt
- Diagnoses exactly ONE missing element
- Returns ONE tiny action (under 120 seconds)
- Uses Tiny Habits Recipe: "After I [ANCHOR], I will [TINY BEHAVIOR]"

## Pairs Well With

- **emotion-detector** ($0.01): Detect emotional state → if fatigued, pass to focus-coach
- **buddhist-counsel** ($0.01): For deeper suffering → buddhist-counsel; for focus issues → focus-coach
