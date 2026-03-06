# Personal Nutrition

Personal nutrition coach for OpenClaw. Tracks your meals, calories, water intake, and eating habits directly in Telegram.

## What it does

- 🍽️ Logs meals (breakfast, lunch, dinner, snacks) with approximate calories
- 💧 Tracks daily water intake
- 📊 Analyzes eating patterns and trends
- ⚖️ Tracks weight dynamics over time
- 💡 Gives advice for balanced diet and healthy substitutions
- 🔗 Finds correlations (low energy + calorie deficit? feeling bad + yesterday's food?)

## Commands

| Command | Example |
|---------|---------|
| Log a meal | `съел овсянку и кофе на завтрак` |
| Log water | `выпил 500мл воды` |
| Log weight | `вес сегодня 74.5кг` |
| Ask for summary | `что я ел сегодня?` |
| Ask for advice | `как улучшить завтрак?` |
| Show instructions | `инструкция` |

## Installation

1. Download ZIP from [ClawhHub](https://clawdhub.com)
2. Extract the skill folder to `/data/.openclaw/workspace/skills/`
3. Restart the container: `docker restart openclaw-ewcl-openclaw-1`

## Data storage

All data is stored locally on your VPS:
`/data/.openclaw/workspace/knowledge/personal/nutrition.md`
