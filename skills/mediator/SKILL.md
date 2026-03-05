---
name: mediator
description: Intercept and filter communications from difficult contacts. Strips emotion, extracts facts, drafts neutral responses. Use when setting up communication filtering for specific contacts, configuring the mediator, or processing intercepted messages. Triggers on "mediator", "intercept messages", "filter communications", "difficult contact", or requests to handle messages from someone the user doesn't want to deal with directly.
---

# Mediator Skill

Emotional firewall for difficult relationships. Intercepts messages from configured contacts, strips out emotional content, presents just the facts, and helps draft measured responses.

## Quick Start

```bash
# Initialize config (creates mediator.yaml if missing)
~/clawd/skills/mediator/scripts/mediator.sh init

# Add a contact to mediate
~/clawd/skills/mediator/scripts/mediator.sh add "Ex Partner" \
  --email "ex@email.com" \
  --phone "+15551234567" \
  --channels email,imessage

# Process incoming (usually called by cron/heartbeat)
~/clawd/skills/mediator/scripts/mediator.sh check

# List configured contacts
~/clawd/skills/mediator/scripts/mediator.sh list

# Remove a contact
~/clawd/skills/mediator/scripts/mediator.sh remove "Ex Partner"
```

## Configuration

Config lives at `~/.clawdbot/mediator.yaml`:

```yaml
mediator:
  # Global settings
  archive_originals: true      # Archive raw messages after processing
  notify_channel: telegram     # Where to send summaries (telegram|slack|imessage)
  
  contacts:
    - name: "Ex Partner"
      email: "ex@email.com"
      phone: "+15551234567"
      channels: [email, imessage]
      mode: intercept          # intercept | assist
      summarize: facts-only    # facts-only | neutral | full
      respond: draft           # draft | auto (dangerous)
      
    - name: "Difficult Client"  
      email: "client@company.com"
      channels: [email]
      mode: assist             # Don't hide originals, just help respond
      summarize: neutral
      respond: draft
```

### Modes

- **intercept**: Archive/hide original, only show summary. User never sees raw emotional content.
- **assist**: Show original but also provide summary and response suggestions.

### Summarize Options

- **facts-only**: Extract only actionable items, requests, deadlines. No emotion.
- **neutral**: Rewrite the message in neutral tone, preserving all content.
- **full**: Show everything but flag emotional/manipulative language.

### Respond Options

- **draft**: Generate suggested response, wait for approval before sending.
- **auto**: Automatically respond (use with extreme caution).

## How It Works

### Email Flow

1. Gmail Pub/Sub notification arrives (real-time)
2. Check if sender matches any configured contact
3. If match:
   - Fetch full email content
   - Process through LLM to extract facts/strip emotion
   - Archive original (apply "Mediator/Raw" label, mark read)
   - Send summary to configured notify channel
   - If response needed, draft one

### iMessage Flow

1. `imsg watch` monitors for new messages
2. Check if sender matches configured contact
3. If match:
   - Process message content
   - Send summary to notify channel
   - Draft response if requested

## Scripts

- `mediator.sh` - Main CLI wrapper
- `process-email.py` - Email processing logic
- `process-imessage.py` - iMessage processing logic
- `summarize.py` - LLM-based content analysis and summarization

## Integration

### Heartbeat Check

Add to `HEARTBEAT.md`:
```
## Mediator Check
~/clawd/skills/mediator/scripts/mediator.sh check
```

### Cron (for more frequent checking)

```bash
# Check every 5 minutes during business hours
*/5 9-18 * * 1-5 ~/clawd/skills/mediator/scripts/mediator.sh check
```

## Safety Notes

- **Never auto-respond** to legal, financial, or child-related messages
- Original messages are archived, not deleted (recoverable)
- All actions logged to `~/.clawdbot/logs/mediator.log`
- Review and adjust prompts if summaries miss important context

## Example Output

**Original email:**
> I can't BELIEVE you would do this to me AGAIN. After everything I've done for you!!! You NEVER think about anyone but yourself. I need you to pick up the kids at 3pm on Saturday and if you can't even do THAT then I don't know what to say anymore.

**Mediator summary:**
> **From:** Ex Partner
> **Channel:** Email  
> **Action Required:** Yes
> 
> **Request:** Pick up kids at 3pm Saturday
> 
> **Suggested response:**
> "Confirmed. I'll pick up the kids at 3pm on Saturday."

---

See `references/prompts.md` for the LLM prompts used in processing.
