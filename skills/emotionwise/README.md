# EmotionWise OpenClaw Skill

Official OpenClaw skill for EmotionWise API.

## Features
- Emotion detection for text (28 labels)
- Sarcasm detection
- Developer-friendly summaries

## Requirements
- OpenClaw installed
- EmotionWise API key from https://emotionwise.ai

## Setup

### 1) Configure API key
In your OpenClaw config (usually `~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "emotionwise": {
        "enabled": true,
        "env": {
          "EMOTIONWISE_API_KEY": "YOUR_EMOTIONWISE_API_KEY"
        }
      }
    }
  }
}
```

### 2) Install skill locally
```bash
openclaw skills install /absolute/path/to/emotionwise-openclaw-skill
```

If you cloned this repository:

```bash
git clone https://github.com/timexicali/emotionwise-openclaw-skill.git
cd emotionwise-openclaw-skill
openclaw skills install "$(pwd)"
```

## Usage examples
- "Analyze emotions in: I’m excited but a little nervous about launch day."
- "Check if this is sarcastic: Great, another bug right before deploy."
- "Summarize emotional tone from these 10 support comments."

## API endpoint used
`POST https://api.emotionwise.ai/api/v1/tools/emotion-detector`

## Notes
- Keep your API key private.
- For public distribution, publish this repo as a skill package in ClawHub.

## Publish to ClawHub

### 1) Install and login
```bash
npm i -g clawhub
clawhub login
```

### 2) Publish first public version
Run from this project directory:

```bash
cd "/path/to/emotionwise-openclaw-skill"
clawhub publish . \
  --slug emotionwise \
  --name "EmotionWise API" \
  --version 0.1.1 \
  --changelog "Initial public release" \
  --tags latest,api,nlp,sentiment
```

### 3) Publish updates
```bash
cd "/path/to/emotionwise-openclaw-skill"
clawhub publish . \
  --slug emotionwise \
  --version 0.1.2 \
  --changelog "Compatibility fixes and packaging cleanup"
```
