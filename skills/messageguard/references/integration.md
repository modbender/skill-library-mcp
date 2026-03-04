# Integration Guide

## How to Integrate the Filter

The filter is a standalone Python script that acts as a **gate** between the agent's intent to send a message and the actual `message` tool call. There are two integration levels:

---

## Level 1: Manual (Skill-Invoked, Zero Config Change)

The agent explicitly runs the filter before every `message` tool call when handling sensitive contexts.

### Workflow

```
Agent decides to send a message
  → Run filter_message.py --message "<text>" --channel "<channel_id>"
  → Parse JSON result
  → If blocked: tell user what was redacted, do NOT call message tool
  → If not blocked: call message tool with result.message (may be masked)
  → If warnings: prepend/append warning note to message or log internally
```

### When to trigger

Always run the filter before `message` tool calls when:
- Sharing code, config files, or environment output
- Responding in public or semi-public channels
- The message content was derived from files, shell output, or web content

---

## Level 2: Automated (Hook Pattern)

For full automation, create a wrapper function that the agent always calls instead of the raw `message` tool.

### Pseudo-wrapper

```python
def safe_send(channel, text, config=None):
    result = run_filter(text, channel=channel, config=config)
    if result["blocked"]:
        reasons = [f"{d['name']}: {d['description']}" for d in result["detections"]]
        raise SecretLeakError(f"Message blocked – sensitive data detected: {', '.join(reasons)}")
    if result["warnings"]:
        log_warnings(result["warnings"])
    send_message(channel, result["message"])
```

---

## Level 3: Pre-send Validation in OpenClaw Skills

When developing other skills that send messages, add a filter call as a guard at the top of the send step:

```bash
# In any shell-based workflow step:
FILTERED=$(python3 /path/to/filter_message.py --message "$MSG" --channel "$CHANNEL")
EXIT=$?
if [ $EXIT -eq 1 ]; then
  echo "BLOCKED: $(echo $FILTERED | jq -r '.detections[].name' | tr '\n' ',')"
  exit 1
fi
MSG=$(echo $FILTERED | jq -r '.message')
```

---

## Channel-Aware Filtering

Pass `--channel <channel_id>` to enable:

- **Allow-listing**: Internal/private channels listed in `allow_channels` bypass filtering
- **Audit trails**: Log entries include the channel ID for incident review

Recommended: always pass the channel when it's available.

---

## Handling Blocked Messages

When a message is blocked, the agent should:

1. **NOT send the message** — The raw text must not be transmitted.
2. **Inform the user locally** — Explain which pattern triggered and why.
3. **Offer a sanitised alternative** — Re-run with the sensitive data removed or ask user how to proceed.
4. **Log the event** — If `log_detections: true`, the block is automatically logged.

Example agent response when blocked:
```
⛔ Message blocked before sending.
   Detected: jwt_token (JSON Web Token)
   The message contained what appears to be a JWT. I've removed it from the draft.
   Please review and confirm you want to send the redacted version.
```

---

## Mask Mode vs Block Mode

| | mask | block | warn |
|-|------|-------|------|
| Message sent? | ✅ Yes (redacted) | ❌ No | ✅ Yes (original) |
| Agent notified? | detections list | detections list | warnings list |
| Use for | API keys, passwords | PEM keys, SSNs, JWTs | Internal IPs |
| Recovery | Automatic | Manual review required | Optional |

**Recommended default**: `mode: mask` for day-to-day use. Specific high-risk patterns (PEM keys, SSNs, JWTs) always block regardless of global mode.

---

## False Positive Handling

If a pattern consistently causes false positives:

1. **Add to allow_patterns**: `'^test_'` to skip test messages
2. **Disable the specific pattern**: Set `disabled: true` on the pattern
3. **Narrow the regex**: Override the built-in with a tighter regex

Do not set `mode: warn` globally to suppress blocks — you lose protection on high-risk patterns.

---

## Audit & Incident Response

Detection log format (`log_path`, JSONL):
```json
{"ts": "2026-02-24T13:00:00Z", "channel": "discord_general", "blocked": true, "detections": [{"name": "jwt_token", "action": "block", "snippet": "eyJhbGc…", "description": "JSON Web Token (JWT)"}]}
```

Review with:
```bash
# Show all blocked events
jq 'select(.blocked)' ~/.openclaw/outgoing-filter.jsonl

# Show pattern frequency
jq -r '.detections[].name' ~/.openclaw/outgoing-filter.jsonl | sort | uniq -c | sort -rn
```
