# Luna Calorie Tracker 🍽️

An OpenClaw skill for the Luna agent that tracks daily caloric intake through food photo analysis. Send Luna a picture of your meal and she'll estimate calories, macros, and store everything in her memory for daily and weekly tracking.

## Features

- **Image-based calorie estimation** — Send a photo of your food, get instant calorie and macro breakdown
- **Persistent memory** — All meals stored in OpenClaw's memory system (`memory/YYYY-MM-DD.md`)
- **Daily & weekly summaries** — Track progress with `/calories today` and `/calories week`
- **Calorie goals** — Set a daily target with `/calories goal 2000`
- **Food history search** — Find past entries with `/calories history pizza`
- **Undo support** — Made a mistake? `/calories undo` removes the last entry

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed and running
- A vision-capable LLM provider configured (GPT-4o, Claude 3.5 Sonnet, Gemini Pro, etc.)
- `OPENAI_API_KEY` environment variable set (or equivalent for your provider)

## Installation

### Option 1: ClawHub (Recommended)
```bash
clawhub install luna-calorie-tracker
```

### Option 2: Manual Install (Per-Agent — Luna only)
```bash
# Navigate to Luna's workspace
cd ~/.openclaw/workspace   # or your agent's workspace path

# Create the skills directory if it doesn't exist
mkdir -p skills/luna-calorie-tracker

# Clone the skill
git clone https://github.com/sidneyschwartz/luna-calorie-tracker.git skills/luna-calorie-tracker
```

### Option 3: Manual Install (Shared — All Agents)
```bash
# Install to the shared skills directory
mkdir -p ~/.openclaw/skills/luna-calorie-tracker
git clone https://github.com/sidneyschwartz/luna-calorie-tracker.git ~/.openclaw/skills/luna-calorie-tracker
```

## Configuration

Add to `~/.openclaw/openclaw.json`:
```json
{
  "skills": {
    "entries": {
      "luna-calorie-tracker": {
        "enabled": true,
        "env": {
          "OPENAI_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

Or if your `OPENAI_API_KEY` is already set in your environment, just enable it:
```json
{
  "skills": {
    "entries": {
      "luna-calorie-tracker": {
        "enabled": true
      }
    }
  }
}
```

## Usage

### Log a Meal
Just send Luna a photo of your food via any connected channel (Telegram, Discord, WhatsApp, iMessage, etc.):

> 📸 [sends food photo]
> 
> Luna: 🍽️ Meal Logged!
> Items detected:
> - Grilled chicken breast: 150g — 248 kcal (P: 46g | C: 0g | F: 5g)
> - Brown rice: 200g — 216 kcal (P: 5g | C: 45g | F: 2g)
> - Steamed broccoli: 100g — 35 kcal (P: 3g | C: 7g | F: 0g)
> 
> Meal Total: 499 kcal
> Daily Running Total: 1,247 kcal (3 meals logged today)

### Check Daily Progress
```
/calories today
```

### View Weekly Summary
```
/calories week
```

### Set a Calorie Goal
```
/calories goal 2000
```

### Search Food History
```
/calories history salmon
```

### Undo Last Entry
```
/calories undo
```

## How It Works

1. **Image Analysis**: When you send a food photo, Luna uses the configured vision-language model (GPT-4o, Claude, etc.) to identify food items and estimate portions
2. **Calorie Estimation**: Based on identified foods and portions, Luna calculates calories and macronutrients using nutritional knowledge built into the LLM
3. **Memory Storage**: Results are appended to OpenClaw's daily memory log (`memory/YYYY-MM-DD.md`), maintaining running totals
4. **Recall**: Luna can search past memory files for history, trends, and summaries using OpenClaw's `memory_search` tool

## Memory File Structure

The skill stores data in OpenClaw's standard memory format:

```
<workspace>/memory/
  MEMORY.md          # Long-term: calorie goal, dietary preferences
  2026-03-01.md      # Daily log with meal entries and running totals
  2026-03-02.md
  ...
```

## Accuracy Notes

- Calorie estimates from images are approximations (typically ±20-30%)
- For better accuracy, mention portion sizes: "this is about 200g of rice"
- Restaurant meals are estimated conservatively (higher) due to hidden oils/butter
- Packaged foods with visible labels will be more accurate
- The more you use it, the better Luna understands your typical portions

## License

MIT
