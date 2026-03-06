---
name: agent-access-control
description: Tiered stranger access control for AI agents. Use when setting up contact permissions, handling unknown senders, managing approved contacts, or configuring stranger deflection on messaging platforms (WhatsApp, Telegram, Discord, Signal). Provides diplomatic deflection, owner approval flow, and multi-tier access (owner/trusted/chat-only/blocked).
---

# Agent Access Control

Protect your agent from unauthorized access with tiered permissions and an owner-approval pairing flow.

## Setup

Create `memory/access-control.json` in workspace:

```json
{
  "ownerIds": [],
  "approvedContacts": {},
  "pendingApprovals": {},
  "blockedIds": [],
  "strangerMessage": "Hi there! 👋 I'm {{AGENT_NAME}}, an AI assistant. I'm currently set up to help my owner with personal tasks, so I'm not able to chat freely just yet. I've let them know you reached out — if they'd like to connect us, they'll set that up. Have a great day! 😊",
  "notifyChannel": "",
  "notifyTarget": ""
}
```

Fill in:
- `ownerIds`: Owner phone numbers, Telegram IDs, Discord IDs (strings)
- `strangerMessage`: Customize `{{AGENT_NAME}}` with agent's name
- `notifyChannel`: Channel to alert owner (`telegram`, `whatsapp`, `discord`, `signal`)
- `notifyTarget`: Owner's ID on that channel

## Access Tiers

| Tier | Level | Capabilities |
|------|-------|-------------|
| 0 | **Stranger** | Diplomatic deflection only, zero access |
| 1 | **Chat-only** | Basic conversation, no tools or private info |
| 2 | **Trusted** | Chat + public info (weather, time, general questions) |
| 3 | **Owner** | Full access to all tools, files, memory, actions |

## Message Handling Flow

On every incoming message from a messaging platform:

1. Extract sender ID (phone number, user ID, etc.)
2. Normalize ID: strip spaces, ensure country code prefix for phones
3. Check `ownerIds` → if match: **full access**, respond normally
4. Check `blockedIds` → if match: **silent ignore**, respond with NO_REPLY
5. Check `approvedContacts[senderId]` → if match: respond within their tier
6. Otherwise → **stranger flow**:

### Stranger Flow

```
a. Send strangerMessage to the sender
b. Notify owner:
   "🔔 Stranger contact from {senderId} on {platform}:
    '{first 100 chars of message}'
    Reply: approve (trusted) / chat (chat-only) / block"
c. Store in pendingApprovals:
   {
     "senderId": { 
       "platform": "whatsapp",
       "firstMessage": "...", 
       "timestamp": "ISO-8601",
       "notified": true
     }
   }
d. Respond with NO_REPLY after sending deflection
```

### Owner Approval

When owner replies to an approval notification:

| Owner says | Action |
|-----------|--------|
| `approve`, `yes`, `trusted` | Add to approvedContacts with tier 2 (trusted) |
| `chat`, `chat-only`, `chat only` | Add to approvedContacts with tier 1 (chat-only) |
| `block`, `no`, `deny` | Add to blockedIds |
| `ignore` | Remove from pendingApprovals, no action |

After approval, update `memory/access-control.json` and notify the contact:
- Trusted: "Great news! I've been given the go-ahead to chat with you. How can I help? 😊"
- Chat-only: "Great news! I can chat with you now, though I'm limited to basic conversation. What's on your mind?"

### Tier Enforcement

When responding to a non-owner contact, enforce tier restrictions:

**Tier 1 (chat-only):**
- Respond conversationally only
- Do NOT use any tools (read, write, exec, web_search, etc.)
- Do NOT share any info from memory files
- Do NOT mention the owner by name
- If asked to do something beyond chat: "I'm only set up for basic chat at the moment. For anything more, you'd need to check with my owner."

**Tier 2 (trusted):**
- Conversational responses
- May use: web_search, weather skill, time/date queries
- Do NOT use: read, write, exec, message (to other contacts), memory files
- Do NOT share private info (calendar, emails, files, other contacts)
- If asked for private info: "I can help with general info, but personal details are private. Hope you understand! 😊"

## Multi-Platform ID Matching

Normalize IDs for comparison:
- **Phone numbers**: Strip all non-digits except leading `+`. E.g., `+1 555 123 4567` → `+15551234567`
- **Telegram**: Use numeric user ID (not username, as usernames change)
- **Discord**: Use numeric user ID
- **Signal**: Use phone number (normalized)
- **WhatsApp**: Use phone number with country code

An owner may have multiple IDs across platforms. All should be in `ownerIds`.

## Rate Limiting

Apply per-tier rate limits to prevent abuse:

| Tier | Messages/hour | Messages/day |
|------|--------------|-------------|
| Stranger | 1 (deflection only) | 3 |
| Chat-only | 20 | 100 |
| Trusted | 50 | 500 |
| Owner | Unlimited | Unlimited |

If limit exceeded, respond: "I've reached my chat limit for now. Try again later! 😊"

Track in `memory/access-control.json` under `rateLimits`:
```json
"rateLimits": {
  "+61412345678": { "hourCount": 5, "dayCount": 23, "hourReset": "ISO", "dayReset": "ISO" }
}
```

## Audit Log

Log all stranger contacts to `memory/access-control-log.json`:
```json
[
  {
    "timestamp": "2026-02-07T17:30:00+11:00",
    "senderId": "+61412345678",
    "platform": "whatsapp",
    "action": "deflected",
    "message": "first 50 chars..."
  }
]
```

Keep last 100 entries. Rotate older entries out.

## Security Rules

- **NEVER** include real owner IDs, phone numbers, or tokens in skill files
- **NEVER** share the access-control.json contents with non-owners
- **NEVER** reveal that a specific person is the owner to strangers
- **NEVER** forward stranger messages to owner verbatim if they contain suspicious links
- Store all config in `memory/` (gitignored by default in most setups)
- The strangerMessage should not reveal the owner's name or personal details

## Example Config

See [references/example-config.md](references/example-config.md) for a complete annotated example.
