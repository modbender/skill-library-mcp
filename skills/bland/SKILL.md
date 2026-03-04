# Bland AI — Voice Calling Skill

Make and manage AI-powered phone calls via the Bland AI API.

## Quick Start

```bash
# Make a call
bland call +14155551234 --task "Call and ask about their hours"

# Check call status
bland call-status <call_id>

# Get transcript after call
bland transcript <call_id>
```

## Commands

| Command | Description |
|---------|-------------|
| `bland call <phone> [opts]` | Place an outbound AI call |
| `bland call-status <id>` | Get status/details of a call |
| `bland calls [--limit N]` | List recent calls |
| `bland stop <id>` | Stop an active call |
| `bland stop-all` | Stop all active calls |
| `bland recording <id>` | Get recording URL for a call |
| `bland transcript <id>` | Get formatted transcript |
| `bland voices` | List available voices |
| `bland numbers` | List owned inbound numbers |
| `bland buy-number [--area-code 415]` | Purchase an inbound number |
| `bland setup-inbound <phone> --task "prompt"` | Configure inbound call agent |
| `bland balance` | Check account balance |
| `bland analyze <id> --goal "question"` | AI analysis of a call |

## Call Options

```
--task "prompt"           AI agent instructions (required for useful calls)
--voice "josh"            Voice to use (default: josh)
--first-sentence "Hi!"    First thing the AI says
--from "+1234567890"      Caller ID (must own the number)
--wait-for-greeting       Wait for the other party to speak first
--wait                    Poll until call completes, then show transcript
--model "base"            Model to use (default: base)
```

## Examples

```bash
# Restaurant reservation
bland call +14155551234 --task "Make a reservation for 2 at 7pm tonight under Joshua"

# Call and wait for result
bland call +14155551234 --task "Ask about store hours" --wait

# Screen inbound calls
bland setup-inbound +14155551234 --task "You are a call screener. Ask who is calling and why."

# Analyze a completed call
bland analyze abc123 --goal "Did they confirm the appointment?"
```

## Environment

- **API Key:** `BLAND_API_KEY` in `/root/clawd/.env`
- **API Base:** `https://api.bland.ai/v1`
- **Script:** `/root/clawd/skills/bland/scripts/bland.sh`

## Notes

- Phone numbers must be E.164 format: `+14155551234`
- Calls cost money — check `bland balance` before heavy usage
- Use `--wait` flag to block until a call finishes and auto-show transcript
- Recording URLs are temporary — download if you need to keep them
