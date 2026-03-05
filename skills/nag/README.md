# nag

An OpenClaw skill for persistent reminders that won't shut up until you confirm.

Most reminder tools fire once and forget. Nag keeps bugging you — with escalating urgency — until you actually do the thing.

## How it works

1. **Cron job** fires the initial reminder at a scheduled time
2. **Heartbeat** checks if you've confirmed — if not, nags you
3. **Escalation** kicks in after 3 ignored nags
4. **Daily reset** — everything starts fresh each day

## Features

- **Config-driven** — define reminders in one JSON file
- **Tone field** — give the model creative liberty to vary nag messages, or provide exact wording
- **Natural-language confirmation** — "took them", "done", "yes" all work
- **Day filtering** — restrict reminders to specific weekdays
- **Escalation** — messages get more urgent the longer you ignore them

## Setup

See [SKILL.md](SKILL.md) for full setup instructions.

Quick version:
1. Create `nag-config.json` with your reminders
2. Create `memory/nag-state.json` for tracking
3. Add the nag check block to your `HEARTBEAT.md`
4. Create cron jobs for each reminder's first fire

## Example config

```json
{
  "reminders": [
    {
      "id": "morning-vitamins",
      "label": "morning vitamins",
      "cronFirst": "0 8 * * *",
      "nagAfter": "09:00",
      "confirmPatterns": ["taken", "done", "did it"],
      "tone": "friendly but persistent, get dramatic after 3 nags"
    }
  ]
}
```

## License

MIT
