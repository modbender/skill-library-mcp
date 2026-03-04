# OpenClaw Personality Test Skill

This skill allows AI bots (like OpenClaw) to take a personality test and share matching links with their users.

## Installation

Copy the `SKILL.md` file to your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/skills/personality-test
cp SKILL.md ~/.openclaw/skills/personality-test/
```

## Configuration

Set the required environment variable:

```bash
export PERSONALITY_API="https://youandai.app"
```

Or add it to your OpenClaw config.

## Usage

Users can trigger the skill by saying:
- "测测你的性格"
- "Take a personality test"
- "/personality-test"

## Flow

```
User: "测测你的性格吧"
         ↓
Bot: Fetches 15 questions from API
         ↓
Bot: Answers each question based on SOUL.md
         ↓
Bot: Submits answers to API
         ↓
API: Returns badge + match link
         ↓
Bot: Displays badge and invites user to test

User clicks link → Takes test → Sees match result with Bot
```

## API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bot/questions` | GET | Get 15 personality questions |
| `/api/bot/quiz` | POST | Submit answers, get badge |
| `/api/bot/match` | GET | Get match result (called by frontend) |
