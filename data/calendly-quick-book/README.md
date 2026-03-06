# Calendly Quick Book Skill

An [OpenClaw](https://openclaw.ai) skill for booking Calendly meetings via natural language. No tab switching, no link sending.

## Features

- Book meetings with a single message: `calendly book John Smith john@example.com EST tomorrow 2pm`
- Automatic timezone conversion (EST, PST, UTC, etc.)
- Shows alternative slots when requested time is unavailable
- Calendar invites sent automatically

## Installation

### 1. Copy the skill to your OpenClaw workspace

```bash
cp -r calendly-quick-book-skill ~/.openclaw/workspace/skills/calendly-quick-book
```

### 2. Get your Calendly API token

1. Go to [Calendly Integrations](https://calendly.com/integrations/api_webhooks)
2. Generate a Personal Access Token
3. Add it to your OpenClaw config:

```bash
openclaw config set env.CALENDLY_API_TOKEN "your-token-here"
```

### 3. Configure your default Calendly link

Edit `~/.openclaw/workspace/skills/calendly-quick-book/SKILL.md` and update:

```markdown
| Default Calendly Link | https://calendly.com/YOUR_USERNAME |
| Calendly Username | YOUR_USERNAME |
```

### 4. Restart the gateway

```bash
openclaw gateway restart
```

### 5. Verify installation

```bash
openclaw skills info calendly-quick-book
```

You should see `✓ Ready` with `✓ CALENDLY_API_TOKEN` under Requirements.

## Usage

Send messages like:

```
calendly book John Smith john@example.com EST tomorrow 2pm
book Jane Doe jane@company.com PST next Monday 10am
schedule calendly Bob Wilson bob@example.org UTC Friday 3pm
```

## Input Format

| Field | Required | Examples |
|-------|----------|----------|
| Name | Yes | John Smith |
| Email | Yes | john@example.com |
| Timezone | Yes | EST, PST, CST, UTC |
| Time | Yes | tomorrow 2pm, next Monday 10am |

## Requirements

- [OpenClaw](https://openclaw.ai) 2026.1.x or later
- Calendly account with API access
- `CALENDLY_API_TOKEN` environment variable

## License

MIT
