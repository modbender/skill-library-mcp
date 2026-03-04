# ClawHQ Dashboard Reporter

Monitor your AI agents in real-time at [app.clawhq.co](https://app.clawhq.co).

## Quick Start

```bash
# 1. Get your API key from Settings → API Keys
# 2. Set env var
export CLAWHQ_API_KEY=chq_your_key_here

# 3. Install skill and you're done
```

## What Gets Reported

- Agent name & status (active, idle, error, offline)
- Current task description
- Heartbeat timestamps

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CLAWHQ_API_KEY` | Yes | API key from ClawHQ Settings |
