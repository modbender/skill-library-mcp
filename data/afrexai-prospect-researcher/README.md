# Prospect Researcher

Turns a company name into a structured B2B prospect profile — complete with company intel, key contacts, pain points, and an engagement recommendation.

## What It Does

- Researches companies using web search (public sources only)
- Identifies key decision-makers and their recent activity
- Analyzes pain points and timing signals
- Scores prospects as Hot/Warm/Cold with reasoning
- Suggests personalized openers and best channels

## Install

```bash
cp -r prospect-researcher ~/.openclaw/workspace/skills/
```

Or from ClawHub:

```bash
clawhub install prospect-researcher
```

## Usage

- "Research Acme Corp as a prospect"
- "Build a prospect profile for Stripe"
- "Qualify these 3 companies as leads: X, Y, Z"

## Output

Produces a structured research report using a consistent template. Every section is filled with sourced data — unknowns are marked explicitly, not guessed.

## Requirements

- Web search capability (Brave Search or similar configured in OpenClaw)

## License

MIT
