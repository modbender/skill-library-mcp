# Email Inbound Cron

Run every 15 minutes to check for new emails.

## Step 0: Load Full Skill Context (IMPORTANT)

Before processing, load the skill's documentation to understand capabilities, rules, and best practices:

```
read path="skills/email-resend/SKILL.md"
```

**Key rules from SKILL.md to follow:**
- Always use `draft-reply.py` for replying to emails (NOT `outbound.py`)
- Threading: use In-Reply-To and References headers for proper Gmail threading
- Acknowledge flow: reply to notification to mark as read
- Use proper message format with replyTo parameter

Also check for any skill-specific scripts:
```
ls skills/email-resend/scripts/
```

## Steps

### 1. Load User Preferences (Smart Fallback)

**Step 1:** Try explicit preferences file:
```
memory_get path="memory/email-preferences.md"
```

**Step 2:** If not found, use OpenClaw context (available in cron runtime):
- `context.chat_id` - Telegram chat ID
- `context.thread_id` - Telegram topic/thread ID
- `context.channel` - Delivery channel (telegram, discord, etc.)

**DO NOT** use memory_search to scan MEMORY.md, USER.md, TOOLS.md, or other memory files.

This approach:
- Uses explicit preferences if configured
- Falls back to runtime context (no file scanning)
- Avoids information leakage from sensitive files

### 2. Run Email Checker

```
python3 ~/.openclaw/workspace/skills/email-resend/scripts/inbound.py
```

Parse the JSON output for new emails.

### 3. Apply User Rules

Based on preferences found in step 1:
- If no telegram preferences found, use current context channel
- Apply any user-specified filtering rules (e.g., only notify for HIGH importance)
- Use the user's preferred notification channel

### 4. Produce Summary (DO NOT send individual notifications)

⚠️ IMPORTANT: Do NOT try to send individual email notifications via message tool. The cron delivery system will handle delivering the summary to your chat.

Instead, just produce a summary output:
```
📬 Email check complete: X new, Y pending, Z acknowledged
```

The cron delivery system will deliver this summary to your configured Telegram topic.

### 5. DO NOT Acknowledge

⚠️ CRITICAL: Do NOT auto-acknowledge emails. Leave them in pending state.

The user will explicitly acknowledge by replying to the notification message. The notification should include "Reply to acknowledge" instruction.
