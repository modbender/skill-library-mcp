# Research Skill — OpenClaw Integration

If you're running this skill inside [OpenClaw](https://openclaw.ai), you can schedule automatic result checks using the cron system.

## Auto-Check Cron for Deep Research

After creating a Parallel AI task, set up a one-shot cron job to poll for results and deliver them back to the conversation.

### Calculate the check time

```bash
# Get current timestamp in ms and add 15 minutes (900000 ms)
date +%s%3N  # Current time in epoch ms
# Example: 1770087600000 + 900000 = 1770088500000
```

**Always verify the scheduled time is in the future and has the correct year:**
```bash
date -d @$((1770088500000/1000))  # Should show a time ~15 min from now, correct year
```

### Schedule the check

```json
{
  "action": "add",
  "job": {
    "name": "Check research: <topic>",
    "schedule": {"kind": "at", "atMs": <current epoch ms + delay>},
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "Check research task <run_id>. Run: parallel-research result <run_id>. If complete, summarize key findings. If still running, reschedule another check in 10 min.",
      "deliver": true,
      "channel": "<source channel, e.g. discord>",
      "to": "<source chat/channel id>"
    },
    "deleteAfterRun": true
  }
}
```

### Key points

- Use the `cron` tool with `action: "add"`
- **ALWAYS verify `atMs` is correct** — run `date -d @$((atMs/1000))` to confirm year and time
- `atMs` should be ~10-15 min from now (ultra processor) or ~5 min (fast processors)
- `deleteAfterRun: true` removes the job after successful completion
- Deliver back to the same channel/topic that requested the research
- If still running, the cron job should create another check
- `PARALLEL_API_KEY` is available as env var — no need to inline it
